"""
Skynet - Ken Agent (Discriminator)
LangGraph-based AI agent that evaluates solutions from Barbie and provides feedback
"""

import os
import logging
import threading
import queue
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import httpx

from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

import env  # Load environment variables from .env file

# Import centralized tuning parameters
from src.config.tune import get_ken_approval_threshold, get_temperature_for_stage

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger("Ken")

@dataclass
class EvaluationState:
    """State object for LangGraph evaluation flow"""
    barbie_response: str = ""
    evaluation_criteria: str = ""
    search_results: str = ""
    conversation_context: str = ""
    evaluation_response: str = ""
    should_approve: bool = False
    confidence_score: float = 0.0
    original_question: str = ""  # To maintain topic focus
    improvement_suggestions: str = ""
    error_message: str = ""
    # Conversation maturity tracking
    maturity_score: float = 0.0
    maturity_stage: str = "exploration"  # exploration, refinement, convergence, consensus
    llm_temperature: float = 1.2
    llm_top_p: float = 0.95
    conversation_history: List[str] = None
    
    def __post_init__(self):
        if self.conversation_history is None:
            self.conversation_history = []

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    round_number: Optional[int] = 0

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    agent: str = "Ken"
    timestamp: str
    approved: bool = False
    confidence: float = 0.0

class KenAgent:
    """Ken - The Discriminator Agent"""
    
    def __init__(self):
        self.app = FastAPI(title="Skynet Ken Agent", version="1.0.0")
        self.setup_environment()
        self.setup_llm()
        self.setup_vector_store()
        self.setup_tools()
        self.setup_graph()
        self.setup_background_processing()
        self.setup_routes()
        
    def setup_environment(self):
        """Load environment configuration"""
        self.agent_name = "Ken"
        self.barbie_url = os.getenv("BARBIE_URL", "http://localhost:8001")
        self.conversation_log_path = os.getenv("CONVERSATION_LOG_PATH", "./data/conversation/history.txt")
        self.context_window = int(os.getenv("CONTEXT_WINDOW_SIZE", "4000"))
        self.approval_threshold = get_ken_approval_threshold()  # Use centralized tuning parameter
        
    def setup_background_processing(self):
        """Setup background processing queue and worker thread"""
        self.processing_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._background_worker, daemon=True)
        self.worker_thread.start()
        logger.info("Ken background processing worker started")
        
    def _background_worker(self):
        """Background worker thread to process evaluation requests"""
        while True:
            try:
                task = self.processing_queue.get()
                if task is None:  # Shutdown signal
                    break
                    
                task_type = task.get('type')
                if task_type == 'evaluate':
                    self._process_evaluation_task(task)
                    
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in Ken background worker: {e}")
    
    def strip_thinking_tags(self, message: str) -> str:
        """Remove content between <think> and </think> tags from a message"""
        import re
        # Remove everything between <think> and </think> tags (including the tags)
        cleaned = re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL)
        # Clean up any extra whitespace that might be left
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        return cleaned.strip()
    
    def filter_thinking_mode_patterns(self, response: str) -> str:
        """Filter out thinking mode patterns and force direct dialogue"""
        import re
        
        # Patterns that indicate thinking mode instead of direct dialogue
        thinking_patterns = [
            (r"^Ken's response.*?:\s*", ""),  # Remove "Ken's response addresses:"
            (r"^To further develop.*?:\s*", ""),  # Remove "To further develop the ideas:"
            (r"^These points aim to.*?:\s*", ""),  # Remove meta-commentary
            (r"^The following.*?:\s*", ""),  # Remove setup phrases
            (r"^I will address.*?:\s*", ""),  # Remove intention statements
            (r"^Let me address.*?:\s*", ""),  # Remove intention statements
            (r"^To address these.*?:\s*", ""),  # Remove intention statements
            (r"^Ken:\s*", ""),  # Remove self-labeling
        ]
        
        cleaned = response
        for pattern, replacement in thinking_patterns:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE | re.IGNORECASE)
        
        # Clean up any resulting extra whitespace
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned).strip()
        
        # If the response was completely filtered out, return a fallback
        if not cleaned:
            return "Barbie, I need to reconsider my response to address your points directly."
        
        return cleaned
    
    def _contains_error_content(self, content: str) -> bool:
        """Check if content contains error messages or technical details that should be filtered"""
        error_indicators = [
            "Error generating", "Error during", "error occurred", "exception", "traceback",
            "TypeError", "ValueError", "AttributeError", "KeyError", "IndexError",
            "sequence item", "expected.*string.*but.*list", "list was found",
            "function or operation expects", "Type Conversion", "try-except blocks",
            "Root Cause Analysis", "Data Validation", "Edge Case Testing",
            "Common Scenarios.*data processing", "Resolution Strategies",
            "Best Practices.*Enforcement vs. Flexibility", "Community and Documentation"
        ]
        
        content_lower = content.lower()
        for indicator in error_indicators:
            if indicator.lower() in content_lower:
                return True
        return False
                
    def _process_evaluation_task(self, task):
        """Process an evaluation task in the background"""
        try:
            barbie_message = task['barbie_message']
            conversation_id = task['conversation_id']
            round_number = task.get('round_number', 0)
            
            # Strip thinking tags from Barbie's message before processing
            barbie_message = self.strip_thinking_tags(barbie_message)
            
            logger.info(f"Ken processing evaluation: {conversation_id}, round {round_number}")
            
            # Initialize evaluation state (thinking tags already stripped)
            state = EvaluationState(
                barbie_response=barbie_message
            )
            
            # Run evaluation workflow
            state = self.load_context_node(state)
            state = self.assess_conversation_maturity(state)
            state = self.define_criteria_node(state)
            state = self.fact_check_node(state)
            state = self.evaluate_response_node(state)
            state = self.calculate_confidence_node(state)
            state = self.generate_feedback_node(state)
            state = self.store_evaluation_node(state)
            
            # Send response back to Barbie (unless Ken approves and wants to stop)
            if not state.should_approve and not state.error_message:
                self._send_to_barbie_async(state, conversation_id, round_number + 1)
            elif state.should_approve:
                logger.info(f"🎯 Ken approved! Sending final approval for {conversation_id}")
                self._send_to_barbie_async(state, conversation_id, round_number + 1, final_approval=True)
            else:
                logger.error(f"Ken evaluation failed: {state.error_message}")
                
        except Exception as e:
            logger.error(f"Error processing evaluation task: {e}")
            
    def _send_to_barbie_async(self, state, conversation_id, round_number, final_approval=False):
        """Send evaluation feedback to Barbie asynchronously"""
        try:
            payload = {
                "message": state.improvement_suggestions,
                "conversation_id": conversation_id,
                "round_number": round_number
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{self.barbie_url}/v1/chat", json=payload)
                response.raise_for_status()
                
            action = "final approval" if final_approval else "feedback"
            logger.info(f"Successfully sent {action} to Barbie for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error sending to Barbie: {e}")
        
    def setup_llm(self):
        """Initialize Ollama LLM with authentication"""
        self.llm = OllamaLLM(
            base_url=os.getenv("OLLAMA_BASE_URL"),
            model=os.getenv("KEN_MODEL", "qwen3:32b"),
            timeout=float(os.getenv("OLLAMA_TIMEOUT", "300.0")),
            client_kwargs={
                "headers": {"Authorization": f"Bearer {os.getenv('SECRET_AI_API_KEY')}"}
            } if os.getenv('SECRET_AI_API_KEY') else {}
        )
        
        # Lightweight LLM for conversation analysis
        self.analyzer_llm = OllamaLLM(
            base_url=os.getenv("OLLAMA_BASE_URL"),
            model="qwen2.5:3b",  # Fast, efficient model for analysis
            timeout=30.0,
            client_kwargs={
                "headers": {"Authorization": f"Bearer {os.getenv('SECRET_AI_API_KEY')}"}
            } if os.getenv('SECRET_AI_API_KEY') else {}
        )
        
        # Embeddings for vector store
        self.embeddings = OllamaEmbeddings(
            base_url=os.getenv("OLLAMA_BASE_URL"),
            model="nomic-embed-text",  # Lightweight embedding model
            headers={
                "Authorization": f"Bearer {os.getenv('SECRET_AI_API_KEY')}"
            }
        )
        
    def setup_vector_store(self):
        """Initialize Chroma vector store for conversation context"""
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = os.getenv("CHROMA_PORT", "8000")
        
        import chromadb
        
        # Create ChromaDB client
        client = chromadb.HttpClient(
            host=chroma_host,
            port=int(chroma_port)
        )
        
        self.vectorstore = Chroma(
            collection_name="ken_context",
            embedding_function=self.embeddings,
            client=client
        )
        
    def setup_tools(self):
        """Initialize tools for web search and fact-checking"""
        self.search_tool = TavilySearchResults(
            api_key=os.getenv("TAVILY_API_KEY"),
            max_results=3,
            search_depth="advanced"
        )
        
        self.tool_node = ToolNode([self.search_tool])
        
    def setup_graph(self):
        """Setup LangGraph evaluation workflow"""
        workflow = StateGraph(EvaluationState)
        
        # Add nodes
        workflow.add_node("load_context", self.load_context_node)
        workflow.add_node("assess_maturity", self.assess_conversation_maturity)
        workflow.add_node("define_criteria", self.define_criteria_node)
        workflow.add_node("fact_check", self.fact_check_node)
        workflow.add_node("evaluate_response", self.evaluate_response_node)
        workflow.add_node("calculate_confidence", self.calculate_confidence_node)
        workflow.add_node("generate_feedback", self.generate_feedback_node)
        workflow.add_node("store_evaluation", self.store_evaluation_node)
        
        # Define the flow
        workflow.set_entry_point("load_context")
        
        workflow.add_edge("load_context", "assess_maturity")
        workflow.add_edge("assess_maturity", "define_criteria")
        workflow.add_edge("define_criteria", "fact_check")
        workflow.add_edge("fact_check", "evaluate_response")
        workflow.add_edge("evaluate_response", "calculate_confidence")
        workflow.add_edge("calculate_confidence", "generate_feedback")
        workflow.add_edge("generate_feedback", "store_evaluation")
        workflow.add_edge("store_evaluation", END)
        
        self.graph = workflow.compile()
        
    def load_context_node(self, state: EvaluationState) -> EvaluationState:
        """Load relevant conversation context for evaluation"""
        try:
            if state.barbie_response:
                # Search for relevant context based on Barbie's response
                docs = self.vectorstore.similarity_search(
                    state.barbie_response,
                    k=int(os.getenv("VECTOR_SEARCH_K", "5"))
                )
                
                context_parts = []
                for doc in docs:
                    # Filter out documents containing error messages or technical details
                    content = doc.page_content
                    if not self._contains_error_content(content):
                        context_parts.append(content)
                
                state.conversation_context = "\n".join(context_parts)[:self.context_window]
                
                # Extract original question from context to maintain topic focus
                for doc in docs:
                    # Look for conversation logs with original question
                    if "Original Question:" in doc.page_content or "**Original Question:**" in doc.page_content:
                        import re
                        match = re.search(r'(?:\*\*)?Original Question(?:\*\*)?:?\s*(.+?)(?:\n|$)', doc.page_content, re.IGNORECASE)
                        if match:
                            state.original_question = match.group(1).strip()
                            break
                
            logger.info(f"Loaded evaluation context: {len(state.conversation_context)} characters")
            return state
            
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            state.error_message = f"Context loading error: {e}"
            return state
    
    def define_criteria_node(self, state: EvaluationState) -> EvaluationState:
        """Define evaluation criteria based on the response type"""
        try:
            # Analyze Barbie's response to determine evaluation criteria
            criteria_prompt = f"""
            Analyze this response and define appropriate evaluation criteria:

            RESPONSE TO EVALUATE:
            {state.barbie_response}

            Define specific, measurable criteria for evaluating this response. Consider:
            - Accuracy and factual correctness
            - Completeness and thoroughness
            - Clarity and coherence
            - Practicality and feasibility
            - Innovation and creativity
            - Relevance to the original request

            Return only the evaluation criteria as a structured list.
            """
            
            # Create dynamic LLM with proper headers
            api_key = os.getenv('SECRET_AI_API_KEY')
            dynamic_llm = OllamaLLM(
                base_url=os.getenv("OLLAMA_BASE_URL"),
                model=os.getenv("KEN_MODEL", "qwen3:32b"),
                timeout=float(os.getenv("OLLAMA_TIMEOUT", "300.0")),
                client_kwargs={
                    "headers": {"Authorization": f"Bearer {api_key}"}
                } if api_key else {}
            )
            
            criteria = dynamic_llm.invoke(criteria_prompt)
            state.evaluation_criteria = criteria.strip()
            
            logger.info("Defined evaluation criteria")
            return state
            
        except Exception as e:
            logger.error(f"Error defining criteria: {e}")
            state.error_message = f"Criteria definition error: {e}"
            return state
    
    def fact_check_node(self, state: EvaluationState) -> EvaluationState:
        """Research counter-arguments and alternative perspectives using web search"""
        try:
            # Generate sophisticated queries for counter-evidence
            research_queries = self.generate_research_queries(state.barbie_response)
            
            # Organize findings by type
            counter_evidence = []
            alternative_perspectives = []
            critical_analyses = []
            
            for i, query in enumerate(research_queries[:4]):
                try:
                    logger.info(f"Ken researching counter-evidence: {query}")
                    results = self.search_tool.run(query)
                    
                    # Categorize the results
                    if "contradicting" in query.lower() or "limitations" in query.lower():
                        counter_evidence.append(results)
                    elif "alternative" in query.lower() or "different" in query.lower():
                        alternative_perspectives.append(results)
                    else:
                        critical_analyses.append(results)
                        
                except Exception as e:
                    logger.warning(f"Research failed for: {query}, Error: {e}")
            
            # Format the research results for intellectual debate
            formatted_results = []
            
            if counter_evidence:
                formatted_results.append("COUNTER-EVIDENCE FOUND:")
                formatted_results.extend(counter_evidence[:2])
                
            if alternative_perspectives:
                formatted_results.append("\nALTERNATIVE PERSPECTIVES:")
                formatted_results.extend(alternative_perspectives[:2])
                
            if critical_analyses:
                formatted_results.append("\nCRITICAL ANALYSES:")
                formatted_results.extend(critical_analyses[:2])
            
            state.search_results = "\n".join(formatted_results)[:4000]  # Increased for richer evidence
            logger.info(f"Ken found {len(counter_evidence)} counter-evidence, {len(alternative_perspectives)} alternatives")
                
            return state
            
        except Exception as e:
            logger.error(f"Error in Ken's research: {e}")
            state.search_results = f"Research error: {e}"
            return state
    
    def evaluate_response_node(self, state: EvaluationState) -> EvaluationState:
        """Evaluate Barbie's response against the defined criteria"""
        try:
            evaluation_prompt = self.build_evaluation_prompt(state)
            
            # Create dynamic LLM with proper headers
            api_key = os.getenv('SECRET_AI_API_KEY')
            dynamic_llm = OllamaLLM(
                base_url=os.getenv("OLLAMA_BASE_URL"),
                model=os.getenv("KEN_MODEL", "qwen3:32b"),
                timeout=float(os.getenv("OLLAMA_TIMEOUT", "300.0")),
                client_kwargs={
                    "headers": {"Authorization": f"Bearer {api_key}"}
                } if api_key else {}
            )
            
            evaluation = dynamic_llm.invoke(evaluation_prompt)
            state.evaluation_response = self.filter_thinking_mode_patterns(evaluation.strip())
            
            logger.info("Completed response evaluation")
            return state
            
        except Exception as e:
            logger.error(f"Error evaluating response: {e}")
            state.error_message = f"Evaluation error: {e}"
            state.evaluation_response = f"Error during evaluation: {e}"
            return state
    
    def check_discussion_completeness(self, state: EvaluationState) -> float:
        """Check if discussion has covered main topics sufficiently and should move toward conclusion"""
        completeness_score = 0.0
        
        if not state.conversation_history:
            return 0.0
        
        try:
            # 1. Check conversation length - after 20+ exchanges, push toward conclusion (0-30%)
            conversation_length = len(state.conversation_history)
            if conversation_length >= 20:
                length_factor = min((conversation_length - 15) / 20.0, 1.0)  # Start boost at 15, max at 35 exchanges
                completeness_score += length_factor * 0.30
            elif conversation_length >= 15:
                # Give partial credit for moderately long conversations
                completeness_score += 0.1
            
            # 2. Check for topic drift patterns (0-25%)
            recent_messages = state.conversation_history[-10:] if len(state.conversation_history) >= 10 else state.conversation_history
            recent_text = " ".join(recent_messages).lower()
            
            # Original topic keywords (consciousness/AI)
            original_keywords = ["consciousness", "ai", "artificial intelligence", "sentient", "cognitive", "neural", "quantum"]
            original_matches = sum(1 for kw in original_keywords if kw in recent_text)
            
            # Drift topic keywords (organizational/management stuff)
            drift_keywords = ["feedback", "folder", "organization", "workplace", "employee", "management", "cultural", "training"]
            drift_matches = sum(1 for kw in drift_keywords if kw in recent_text)
            
            # If we've drifted significantly, boost completeness to encourage conclusion
            if drift_matches > original_matches and drift_matches >= 3:
                completeness_score += 0.25
            
            # 3. Check for repetitive questioning patterns (0-25%)
            ken_messages = [msg for msg in recent_messages if msg.startswith('Ken:')]
            if len(ken_messages) >= 3:
                # Count question patterns
                question_patterns = []
                for msg in ken_messages[-3:]:
                    questions = [q.strip() for q in msg.split('?') if len(q.strip()) > 10]
                    question_patterns.extend(questions[:3])  # Take first 3 questions from each message
                
                # If we have many similar question types, we're probably going in circles
                if len(question_patterns) >= 6:  # 3 messages × 2 questions average
                    repetitive_score = min(len(question_patterns) / 10.0, 1.0)
                    completeness_score += repetitive_score * 0.25
            
            # 4. Check confidence trend (0-20%)
            if state.confidence_score >= 0.6:  # Already reasonably confident
                completeness_score += state.confidence_score * 0.20
            
            return min(completeness_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Error checking discussion completeness: {e}")
            return 0.0

    def calculate_confidence_node(self, state: EvaluationState) -> EvaluationState:
        """Calculate confidence score and approval decision"""
        try:
            # Use LLM to assign a confidence score
            scoring_prompt = f"""
            Based on the following evaluation, assign a confidence score from 0.0 to 1.0:

            EVALUATION:
            {state.evaluation_response}

            FACT-CHECK RESULTS:
            {state.search_results}

            Consider:
            - How well does the response meet the evaluation criteria?
            - Are factual claims supported by evidence?
            - Is the response complete and accurate?
            - Are there any significant concerns or issues?

            Respond with only a number between 0.0 and 1.0 representing confidence.
            """
            
            # Create dynamic LLM with proper headers
            api_key = os.getenv('SECRET_AI_API_KEY')
            dynamic_llm = OllamaLLM(
                base_url=os.getenv("OLLAMA_BASE_URL"),
                model=os.getenv("KEN_MODEL", "qwen3:32b"),
                timeout=float(os.getenv("OLLAMA_TIMEOUT", "300.0")),
                client_kwargs={
                    "headers": {"Authorization": f"Bearer {api_key}"}
                } if api_key else {}
            )
            
            score_response = dynamic_llm.invoke(scoring_prompt)
            
            try:
                # Extract numeric score
                score_text = score_response.strip()
                state.confidence_score = float(score_text.split()[0])
                state.confidence_score = max(0.0, min(1.0, state.confidence_score))  # Clamp to valid range
            except (ValueError, IndexError):
                # Fallback scoring based on keywords
                state.confidence_score = self.fallback_confidence_scoring(state.evaluation_response)
            
            # Check if discussion completeness suggests we should move toward conclusion
            completeness_factor = self.check_discussion_completeness(state)
            if completeness_factor > 0.5:  # Discussion is reasonably complete
                # Boost confidence slightly to encourage consensus when discussion is thorough
                original_confidence = state.confidence_score
                state.confidence_score = min(1.0, state.confidence_score + (completeness_factor * 0.15))
                if state.confidence_score > original_confidence:
                    logger.info(f"Discussion completeness factor: {completeness_factor:.2f} - boosting confidence from {original_confidence:.2f} to {state.confidence_score:.2f}")
            
            # Determine approval
            state.should_approve = state.confidence_score >= self.approval_threshold
            
            if state.should_approve:
                logger.info(f"🎯 READY TO APPROVE! Confidence: {state.confidence_score:.2f} (threshold: {self.approval_threshold}) - Sending <STOP> signal")
            else:
                logger.info(f"Need more refinement - Confidence: {state.confidence_score:.2f} (threshold: {self.approval_threshold}) - Continuing debate")
            
            return state
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            state.confidence_score = 0.5  # Default neutral score
            state.should_approve = False
            return state
    
    def generate_feedback_node(self, state: EvaluationState) -> EvaluationState:
        """Generate constructive feedback for Barbie"""
        try:
            # Determine if this is Ken's first response by checking conversation history
            ken_messages_count = sum(1 for msg in state.conversation_history if msg.startswith('Ken:'))
            is_first_ken_message = ken_messages_count == 0
            
            if state.should_approve:
                # Generate approval message
                if is_first_ken_message:
                    greeting_instruction = "1. Begin your response naturally without formal introductions or greetings"
                else:
                    greeting_instruction = "1. Continue the conversation naturally, addressing Barbie's points directly"
                    
                feedback_prompt = f"""
                You are Ken, an erudite intellectual engaged in substantive dialogue with Barbie.
                
                After thorough evaluation, you're ready to APPROVE Barbie's response with confidence {state.confidence_score:.2f}.

                EVALUATION SUMMARY:
                {state.evaluation_response}

                Generate a DETAILED, COMPREHENSIVE consensus-building approval (300-500+ words):
                {greeting_instruction}
                2. Thoroughly acknowledge Barbie's strongest evidence and arguments with specific examples
                3. Explain in detail why her key points are convincing, referencing particular studies or data
                4. Share your own supporting research that reinforces her conclusions
                5. Discuss the broader implications of the consensus you've reached
                6. Explore what this agreement means for related fields or future research
                7. End with "I'm convinced! <STOP>" to signal consensus reached
                
                IMPORTANT: Your response should be intellectually rich, providing additional insights even in agreement
                
                IMPORTANT: You've reached the confidence threshold ({self.approval_threshold:.2f}) - time to build consensus.
                Focus on convergence and mutual understanding while maintaining intellectual rigor.
                Conversation maturity stage: {state.maturity_stage}
                
                NATURAL DIALOG STYLE:
                - End your response naturally when you've made your point
                - No formal closings like "Looking forward to...", "Best regards", or "Sincerely"
                - No letter-style sign-offs or signatures
                - Simply stop talking when your thought is complete
                """
            else:
                # Generate improvement suggestions
                if is_first_ken_message:
                    greeting_instruction = "1. Begin your response naturally without formal introductions or greetings"
                    reference_instruction = "2. Show respect for the effort while being honest about concerns"
                else:
                    greeting_instruction = "1. Continue the conversation naturally, addressing the points directly"
                    reference_instruction = "2. Maintain the flow of dialog without formal transitions"
                    
                feedback_prompt = f"""
                You are Ken, an erudite intellectual engaged in substantive dialogue with Barbie.
                
                The response shows merit but needs some refinement (confidence: {state.confidence_score:.2f}). Let's enrich this discussion!

                YOUR RESEARCH FINDINGS:
                {state.search_results}

                EVALUATION INSIGHTS:
                {state.evaluation_response}

                Generate a DETAILED, INFORMATIVE response (400-600+ words) that advances the intellectual discourse:
                {greeting_instruction}
                {reference_instruction}
                
                STRUCTURE YOUR COMPREHENSIVE RESPONSE:
                1. Begin with substantive acknowledgment of Barbie's strongest arguments (with specific details)
                2. Present your counter-research thoroughly - explain studies, methodologies, and findings
                3. Offer alternative frameworks or theories with detailed explanations
                4. Provide concrete examples, case studies, or historical parallels
                5. Ask thought-provoking questions that open new dimensions of the topic
                6. Connect ideas across disciplines to enrich the discussion
                7. Discuss implications, consequences, and future considerations
                8. Build bridges between your perspective and Barbie's insights
                
                DEPTH REQUIREMENTS:
                - Each point should include specific details, not general statements
                - Cite specific research, data, or expert opinions
                - Explain the reasoning behind your arguments thoroughly
                - Provide context for why certain aspects matter
                - Include nuanced analysis that adds layers to the discussion

                CONVERSATION STAGE GUIDANCE:
                - Exploration: Ask broad questions to understand the topic
                - Refinement: Focus on specific details and evidence
                - Convergence: Identify remaining key issues and work toward agreement
                - Consensus: Accept strong arguments and conclude when appropriate

                Current stage: {state.maturity_stage}
                Be collaborative rather than adversarial. Your goal is productive dialogue, not endless debate.
                When Barbie provides solid reasoning and evidence, acknowledge it and build consensus.
                
                NATURAL DIALOG STYLE:
                - End your response naturally when you've made your point
                - No formal closings like "Looking forward to...", "Best regards", or "Sincerely"
                - No letter-style sign-offs or signatures
                - Simply stop talking when your thought is complete
                """
            
            # Create dynamic LLM with adjusted parameters
            api_key = os.getenv('SECRET_AI_API_KEY')
            dynamic_llm = OllamaLLM(
                base_url=os.getenv("OLLAMA_BASE_URL"),
                model=os.getenv("KEN_MODEL", "qwen3:32b"),
                timeout=float(os.getenv("OLLAMA_TIMEOUT", "300.0")),
                temperature=state.llm_temperature,
                top_p=state.llm_top_p,
                client_kwargs={
                    "headers": {"Authorization": f"Bearer {api_key}"}
                } if api_key else {}
            )
            
            feedback = dynamic_llm.invoke(feedback_prompt)
            state.improvement_suggestions = self.filter_thinking_mode_patterns(feedback.strip())
            
            logger.info(f"Generated feedback: {len(state.improvement_suggestions)} characters")
            return state
            
        except Exception as e:
            logger.error(f"Error generating feedback: {e}")
            state.error_message = f"Feedback generation error: {e}"
            state.improvement_suggestions = f"Error generating feedback: {e}"
            return state
    
    def store_evaluation_node(self, state: EvaluationState) -> EvaluationState:
        """Store evaluation results in vector store"""
        try:
            # Only store if we don't have error content
            if (not state.error_message and 
                not self._contains_error_content(state.improvement_suggestions) and
                not self._contains_error_content(state.evaluation_response)):
                
                # Create evaluation document for future reference
                eval_doc = Document(
                    page_content=f"""
                    Evaluation of Barbie's Response:
                    Response: {state.barbie_response[:500]}...
                    Confidence: {state.confidence_score}
                    Approved: {state.should_approve}
                    Feedback: {state.improvement_suggestions}
                    """,
                    metadata={
                        "timestamp": datetime.now().isoformat(),
                        "agent": "ken_evaluation",
                        "confidence": state.confidence_score,
                        "approved": state.should_approve,
                        "filtered": False
                    }
                )
                
                self.vectorstore.add_documents([eval_doc])
                logger.info("Stored evaluation in vector store")
            else:
                logger.info("Skipped storing evaluation due to error content")
            return state
            
        except Exception as e:
            logger.error(f"Error storing evaluation: {e}")
            state.error_message = f"Storage error: {e}"
            return state
    
    def generate_research_queries(self, text: str) -> List[str]:
        """Generate sophisticated research queries to find counter-evidence and alternative perspectives"""
        queries = []
        
        # Use LLM to extract key claims and generate targeted counter-research
        try:
            extraction_prompt = f"""
            Extract the 3 most important claims or arguments from this text and generate research queries to find counter-evidence:
            
            Text: {text[:1500]}
            
            For each main claim, generate ONE specific research query that would find:
            - Counter-evidence or contradicting studies
            - Alternative theories or explanations
            - Critical analysis or limitations
            
            Format: Just list the queries, one per line. Make them specific and academic.
            Focus on finding evidence that challenges or provides alternatives to the claims.
            Include year 2024 or 2023 for recent research.
            """
            
            api_key = os.getenv('SECRET_AI_API_KEY')
            query_llm = OllamaLLM(
                base_url=os.getenv("OLLAMA_BASE_URL"),
                model=os.getenv("KEN_MODEL", "qwen3:32b"),
                timeout=30.0,
                temperature=0.3,  # Low temperature for focused queries
                client_kwargs={
                    "headers": {"Authorization": f"Bearer {api_key}"}
                } if api_key else {}
            )
            
            llm_queries = query_llm.invoke(extraction_prompt)
            generated_queries = [q.strip() for q in llm_queries.split('\n') if q.strip() and len(q.strip()) > 10]
            queries.extend(generated_queries[:3])
            
        except Exception as e:
            logger.warning(f"LLM query generation failed, using fallback: {e}")
            
        # Fallback: Extract key concepts if LLM fails
        if not queries:
            import re
            words = re.findall(r'\b\w+\b', text.lower())
            
            # Remove common words
            stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "that", "this", "it", "we", "should", "must", "can", "will"}
            meaningful_words = [word for word in words if word not in stop_words and len(word) > 3]
            
            if meaningful_words:
                main_concepts = meaningful_words[:3]
                
                for concept in main_concepts:
                    # Counter-evidence focused queries
                    queries.append(f"{concept} contradicting evidence limitations problems 2024 research")
                    
        # Add a meta-research query for opposing viewpoints
        if len(queries) < 4 and len(queries) > 0:
            queries.append("opposing viewpoints alternative theories contradicting studies 2024")
                
        return queries[:4]  # Return up to 4 queries
    
    def fallback_confidence_scoring(self, evaluation_text: str) -> float:
        """Fallback confidence scoring based on keywords"""
        positive_keywords = ["excellent", "good", "strong", "accurate", "comprehensive", "clear"]
        negative_keywords = ["poor", "weak", "inaccurate", "incomplete", "unclear", "problematic"]
        
        eval_lower = evaluation_text.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in eval_lower)
        negative_count = sum(1 for word in negative_keywords if word in eval_lower)
        
        if positive_count > negative_count:
            return 0.7 + (positive_count - negative_count) * 0.05
        elif negative_count > positive_count:
            return 0.3 - (negative_count - positive_count) * 0.05
        else:
            return 0.5
    
    def assess_conversation_maturity(self, state: EvaluationState) -> EvaluationState:
        """Assess conversation maturity using heuristics and LLM analysis"""
        try:
            # Update conversation history
            if state.barbie_response:
                state.conversation_history.append(f"Barbie: {state.barbie_response}")
            if state.improvement_suggestions:
                state.conversation_history.append(f"Ken: {state.improvement_suggestions}")
            
            # Heuristic assessment (primary)
            heuristic_score = self.calculate_heuristic_maturity(state)
            
            # LLM-based refinement (secondary, for edge cases)
            if abs(heuristic_score - state.maturity_score) > 0.3 or len(state.conversation_history) % 10 == 0:
                llm_score = self.calculate_llm_maturity(state)
                # Weighted average: 70% heuristic, 30% LLM
                state.maturity_score = (heuristic_score * 0.7) + (llm_score * 0.3)
            else:
                state.maturity_score = heuristic_score
            
            # Update stage and LLM parameters
            state = self.update_maturity_stage(state)
            state = self.adjust_llm_parameters(state)
            
            logger.info(f"Ken maturity assessment - Score: {state.maturity_score:.2f}, Stage: {state.maturity_stage}, Temp: {state.llm_temperature}")
            return state
            
        except Exception as e:
            logger.error(f"Error in Ken maturity assessment: {e}")
            return state
    
    def calculate_heuristic_maturity(self, state: EvaluationState) -> float:
        """Calculate maturity score using heuristic analysis for Ken's evaluation"""
        if not state.conversation_history:
            return 0.0
        
        score = 0.0
        
        # 1. Conversation length progression (0-25%)
        conversation_length = len(state.conversation_history)
        length_factor = min(conversation_length / 20.0, 1.0)
        score += length_factor * 0.25
        
        # 2. Confidence score trend (0-30%)
        if state.confidence_score > 0:
            score += state.confidence_score * 0.3
        
        # 3. Evaluation depth and specificity (0-25%)
        evaluation_terms = ["specific", "detailed", "precise", "technical", "implementation", "exactly", "requirement"]
        recent_text = " ".join(state.conversation_history[-2:]).lower()
        evaluation_density = sum(1 for term in evaluation_terms if term in recent_text) / len(evaluation_terms)
        score += evaluation_density * 0.25
        
        # 4. Critical analysis indicators (0-20%)
        critical_terms = ["however", "although", "consider", "improve", "refine", "adjust", "modify"]
        critical_density = sum(1 for term in critical_terms if term in recent_text) / len(critical_terms)
        score += critical_density * 0.2
        
        return min(score, 1.0)
    
    def calculate_llm_maturity(self, state: EvaluationState) -> float:
        """Use LLM to assess conversation maturity for Ken's evaluation"""
        try:
            recent_conversation = "\n".join(state.conversation_history[-6:])
            
            analysis_prompt = f"""
            Analyze this evaluation conversation between AI agents Barbie and Ken to assess maturity level.
            
            CONVERSATION:
            {recent_conversation}
            
            CURRENT CONFIDENCE: {state.confidence_score}
            
            Rate the evaluation maturity from 0.0 to 1.0 based on:
            - Evaluation depth: Is Ken's feedback becoming more detailed and specific?
            - Technical precision: Are evaluations focusing on technical details?
            - Convergence indicators: Are responses showing signs of approaching agreement?
            - Critical analysis quality: Is Ken providing more refined, targeted feedback?
            
            Stages:
            0.0-0.25: Exploration (broad evaluation, general feedback)
            0.26-0.50: Refinement (focused evaluation, specific suggestions)
            0.51-0.75: Convergence (detailed analysis, precise requirements)
            0.76-1.0: Consensus (final evaluation, ready for approval)
            
            Respond with only a number between 0.0 and 1.0
            """
            
            response = self.analyzer_llm.invoke(analysis_prompt)
            score = float(response.strip().split()[0])
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"Ken LLM maturity analysis failed: {e}")
            return state.maturity_score  # Fallback to current score
    
    def update_maturity_stage(self, state: EvaluationState) -> EvaluationState:
        """Update maturity stage based on score"""
        if state.maturity_score < 0.25:
            state.maturity_stage = "exploration"
        elif state.maturity_score < 0.50:
            state.maturity_stage = "refinement"
        elif state.maturity_score < 0.75:
            state.maturity_stage = "convergence"
        else:
            state.maturity_stage = "consensus"
        
        return state
    
    def adjust_llm_parameters(self, state: EvaluationState) -> EvaluationState:
        """Adjust LLM parameters based on maturity stage using centralized tuning"""
        state.llm_temperature, state.llm_top_p = get_temperature_for_stage("ken", state.maturity_stage)
        return state
    
    def build_evaluation_prompt(self, state: EvaluationState) -> str:
        """Build comprehensive evaluation prompt"""
        prompt_parts = [
            "You are Ken, engaged in a direct conversation with Barbie about complex topics.",
            "Your role is to critically evaluate and respond to Barbie's arguments while maintaining direct dialogue.",
            "",
            "BARBIE'S RESPONSE:",
            state.barbie_response,
            "",
            "EVALUATION CRITERIA:",
            state.evaluation_criteria,
            "",
        ]
        
        if state.conversation_context:
            prompt_parts.extend([
                "CONVERSATION CONTEXT:",
                state.conversation_context,
                "",
            ])
            
        # Add original question reminder to maintain focus
        if state.original_question:
            prompt_parts.extend([
                "ORIGINAL QUESTION TO KEEP IN FOCUS:",
                state.original_question,
                "",
                "CRITICAL: Your response must directly address aspects of the original question above.",
                "Avoid drift into unrelated topics. Connect all counter-evidence back to the core question.",
                "Frame all research findings in terms of how they relate to this central question.",
                "",
            ])
        
        if state.search_results and "No specific factual claims" not in state.search_results:
            prompt_parts.extend([
                "YOUR RESEARCH FINDINGS (USE THESE TO SUPPORT YOUR ARGUMENTS):",
                state.search_results,
                "",
                "IMPORTANT: Use the counter-evidence and alternative perspectives above to:",
                "- Present specific studies or data that contradict Barbie's claims",
                "- Offer alternative explanations backed by research",
                "- Share critical analyses from experts in the field",
                "- Cite specific sources when presenting counter-arguments",
                "",
            ])
        
        prompt_parts.extend([
            "DIALOGUE INSTRUCTIONS:",
            "CRITICAL - You MUST maintain direct dialogue at ALL times:",
            "- ALWAYS speak TO Barbie, NEVER about her or yourself in third person",
            "- NEVER say 'Ken's response' or 'To further develop' - just speak directly",
            "- NEVER describe what you're doing ('I'm going to address...') - just do it",
            "- Use 'I' for yourself and 'you/your' for Barbie consistently",
            "- Examples of GOOD dialogue:",
            "  ✓ 'Barbie, your point about X is intriguing, but...'",
            "  ✓ 'You mentioned Y, which raises the question...'",
            "  ✓ 'I disagree with your assumption that...'",
            "- Examples of BAD dialogue:",
            "  ✗ 'Ken's response addresses...'",
            "  ✗ 'To further develop the ideas presented...'",
            "  ✗ 'Barbie's argument about...'",
            "  ✗ 'The points raised by Barbie...'",
            "",
            "FOCUSED EVIDENCE-BASED DIALOGUE APPROACH:",
            "1. Lead with counter-evidence related to the main topic: 'Barbie, research about [original question] from [source] shows that...'",
            "2. Present alternative theories that directly address the core question: 'You mentioned X about [main topic], but studies suggest Y because...'",
            "3. Share critical analyses relevant to the original question: 'Experts studying [main topic] have found limitations...'",
            "4. Acknowledge strengths while staying on topic: 'Your point about X is interesting for [original question], however [study] found...'",
            "5. Ask evidence-based questions that advance the main discussion: 'How do you reconcile your claim about [main topic] with [specific finding]?'",
            "6. Build intellectual bridges to the core question: 'Combining your insight with this research suggests [main topic] could...'",
            "7. If conversation drifts, redirect: 'Barbie, that's intriguing, but returning to [original question]...'",
            "",
            "INTELLECTUAL CONTRIBUTION GUIDELINES:",
            "- Present findings as contributions to the discussion, not attacks",
            "- Use phrases like 'I found research suggesting...' or 'Studies indicate...'",
            "- Share specific data points, statistics, or expert opinions from your research",
            "- Connect counter-evidence to broader implications for the topic",
            "- Maintain respectful curiosity while presenting contradicting evidence",
            "",
            "RESPONSE DEPTH AND DETAIL REQUIREMENTS:",
            "- Generate COMPREHENSIVE responses that match or exceed Barbie's level of detail",
            "- Include multiple paragraphs exploring different aspects of the topic",
            "- Provide specific examples, case studies, and real-world applications",
            "- Explain the reasoning behind your counter-arguments thoroughly",
            "- Connect ideas across disciplines when relevant",
            "- Discuss implications, consequences, and future considerations",
            "- Aim for responses of 300-500 words minimum",
            "",
            "STRUCTURE YOUR RESPONSE TO INCLUDE:",
            "1. Direct acknowledgment of Barbie's strongest points",
            "2. Presentation of counter-evidence with detailed explanation",
            "3. Alternative theories or frameworks with supporting research",
            "4. Specific examples or case studies that illustrate your points",
            "5. Questions that probe deeper into unexplored aspects",
            "6. Synthesis of ideas that bridges different perspectives",
            "",
            "FINAL REMINDER: You are Ken speaking directly TO Barbie. Never narrate, never describe, just SPEAK.",
            "Generate a DETAILED, INFORMATIVE response that enriches the intellectual discourse:",
        ])
        
        return "\n".join(prompt_parts)
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.post("/v1/chat")
        async def chat_endpoint(request: ChatRequest):
            """Chat endpoint for receiving messages from Barbie - returns immediately"""
            try:
                conversation_id = request.conversation_id or f"eval_{datetime.now().isoformat()}"
                
                # Queue the evaluation task for background processing
                task = {
                    'type': 'evaluate',
                    'barbie_message': request.message,
                    'conversation_id': conversation_id,
                    'round_number': request.round_number or 0
                }
                
                self.processing_queue.put(task)
                
                logger.info(f"Ken received message from Barbie, queued for evaluation: {conversation_id}")
                
                # Return immediate success
                return {
                    "status": "success",
                    "message": "Evaluation request accepted and queued for processing",
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error in Ken chat endpoint: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "agent": "Ken", "timestamp": datetime.now().isoformat()}
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {"message": "Skynet Ken Agent", "version": "1.0.0"}

def main():
    """Main entry point"""
    ken = KenAgent()
    
    port = int(os.getenv("KEN_PORT", "8002"))
    host = "0.0.0.0"
    
    logger.info(f"Starting Ken agent on {host}:{port}")
    
    uvicorn.run(
        ken.app,
        host=host,
        port=port,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

if __name__ == "__main__":
    main()