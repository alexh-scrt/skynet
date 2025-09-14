"""
Skynet - Barbie Agent (Generator)
LangGraph-based AI agent that generates solutions and communicates with Ken
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

# Import our new conversation logging system
import sys
from pathlib import Path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.conversation_logger import BarbieConversationManager
from src.config.tune import get_temperature_for_stage
from src.utils.agreement_detector import AgreementDetector
from src.utils.evidence_validator import EvidenceValidator
from src.utils.topic_coherence_monitor import TopicCoherenceMonitor
from src.utils.debate_conclusion_detector import DebateConclusionDetector
from src.debate.progression_tracker import DebateProgressionTracker
from src.debate.progression_prompts import ProgressionPromptGenerator

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
)
logger = logging.getLogger("Barbie")

@dataclass
class ConversationState:
    """State object for LangGraph conversation flow"""
    user_input: str = ""
    original_message: str = ""
    generated_response: str = ""
    ken_feedback: str = ""
    search_results: str = ""
    conversation_context: str = ""
    round_number: int = 0
    should_stop: bool = False
    error_message: str = ""
    is_genesis: bool = False
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
    agent: str = "Barbie"
    timestamp: str

class BarbieAgent:
    """Barbie - The Generator Agent"""
    
    def __init__(self):
        self.app = FastAPI(title="Skynet Barbie Agent", version="1.0.0")
        self.setup_environment()
        self.setup_llm()
        self.setup_vector_store()
        self.setup_tools()
        self.setup_graph()
        self.setup_background_processing()
        self.setup_routes()
        
        # Initialize conversation logging system
        self.conversation_manager = BarbieConversationManager("./data/conversation")
        self.active_conversations = {}  # Track active conversation logs
        
        # Initialize conversation quality systems
        self.agreement_detector = AgreementDetector()
        self.evidence_validator = EvidenceValidator()
        self.topic_monitors = {}  # conversation_id -> TopicCoherenceMonitor  
        self.conclusion_detectors = {}  # conversation_id -> DebateConclusionDetector
        
        # Initialize debate progression tracking
        self.debate_trackers = {}  # conversation_id -> DebateProgressionTracker
        self.prompt_generators = {}  # conversation_id -> ProgressionPromptGenerator
        
    def ensure_message_logged(self, speaker: str, message: str, conversation_id: str):
        """Ensure a message is logged to both old and new systems"""
        try:
            # Strip thinking content from all messages before logging
            cleaned_message = self.strip_thinking_content(message)
            
            # Strip references if configured (default: do not log references)
            cleaned_message = self.strip_references(cleaned_message)
            
            # Skip logging if message is empty after cleaning
            if not cleaned_message.strip():
                logger.info(f"Skipped logging empty {speaker} message after cleaning")
                return
            
            # Log to new timestamped system
            if conversation_id in self.active_conversations:
                if speaker == "Barbie":
                    self.conversation_manager.send_to_ken(cleaned_message)
                elif speaker == "Ken":
                    self.conversation_manager.receive_from_ken(cleaned_message)
                    
            # Also log to old system for backwards compatibility
            self.log_conversation_message(speaker, cleaned_message, conversation_id)
            
            logger.info(f"Message logged from {speaker} (length: {len(cleaned_message)}, original: {len(message)})")
            
        except Exception as e:
            logger.error(f"Error ensuring message logged: {e}")
        
    def setup_environment(self):
        """Load environment configuration"""
        self.agent_name = "Barbie"
        self.ken_url = os.getenv("KEN_URL", "http://localhost:8002")
        self.conversation_log_path = os.getenv("CONVERSATION_LOG_PATH", "./data/conversation/history.txt")
        self.max_rounds = int(os.getenv("MAX_CONVERSATION_ROUNDS", "50"))
        self.context_window = int(os.getenv("CONTEXT_WINDOW_SIZE", "4000"))
        # Control whether to log source references in conversation (default: False)
        self.log_references = os.getenv("LOG_REFERENCES", "false").lower() == "true"
        
        # Ensure conversation log directory exists
        os.makedirs(os.path.dirname(self.conversation_log_path), exist_ok=True)
        
    def strip_thinking_content(self, message):
        """Remove <think>...</think> content from messages before logging"""
        import re
        
        # Remove <think>...</think> blocks (including multiline)
        cleaned_message = re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL)
        
        # Clean up any extra whitespace left behind
        cleaned_message = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_message)
        cleaned_message = cleaned_message.strip()
        
        return cleaned_message
    
    def strip_references(self, message):
        """Remove reference section from messages if log_references is False"""
        if self.log_references:
            return message
            
        import re
        
        # First, remove complete References/Sources/Citations sections
        patterns = [
            # Match References: or **References:** sections until end of message
            r'\n+(?:\*\*)?(?:References|Sources|Citations)(?:\*\*)?:.*$',
            # Match any remaining "Looking forward" phrases
            r'\n+Looking forward to.*?(?:\n|$)',
        ]
        
        cleaned = message
        for pattern in patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.MULTILINE | re.IGNORECASE)
        
        # Also remove standalone citation lines that look like:
        # Author, A. (2024). Title. Journal, volume, pages.
        citation_pattern = r'\n+[A-Z][a-zA-Z]+(?:,\s*[A-Z]\.)?(?:\s*(?:&|,)\s*[A-Z][a-zA-Z]+(?:,\s*[A-Z]\.)?)*\s*\(\d{4}\)\..*?(?=\n|$)'
        cleaned = re.sub(citation_pattern, '', cleaned, flags=re.MULTILINE)
        
        # Remove any excessive whitespace that might result
        cleaned = re.sub(r'\n\n+', '\n\n', cleaned).strip()
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
        
    def wrap_text_for_logging(self, text, width=80):
        """Wrap text to specified width for readable conversation logs"""
        import textwrap
        
        # Split into paragraphs to preserve paragraph breaks
        paragraphs = text.split('\n\n')
        wrapped_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                # Wrap each paragraph while preserving intentional line breaks
                lines = paragraph.split('\n')
                wrapped_lines = []
                
                for line in lines:
                    if line.strip():
                        # Wrap long lines
                        wrapped = textwrap.fill(line.strip(), width=width, 
                                              break_long_words=False, 
                                              break_on_hyphens=False)
                        wrapped_lines.append(wrapped)
                    else:
                        wrapped_lines.append('')  # Preserve empty lines
                
                wrapped_paragraphs.append('\n'.join(wrapped_lines))
            else:
                wrapped_paragraphs.append('')  # Preserve empty paragraphs
        
        return '\n\n'.join(wrapped_paragraphs)
        
    def log_conversation_message(self, speaker, message, conversation_id):
        """Log a single message to the conversation file with proper formatting"""
        try:
            # Strip thinking content from Ken's messages
            if speaker == "Ken":
                message = self.strip_thinking_content(message)
            
            # Strip references if configured (default: do not log references)
            message = self.strip_references(message)
                
            # Skip logging if message is empty after cleaning
            if not message.strip():
                logger.info(f"Skipped logging empty {speaker} message after cleaning")
                return
                
            # Wrap text for readability, accounting for speaker prefix
            speaker_prefix_length = len(f"{speaker}: ")
            available_width = 80 - speaker_prefix_length
            wrapped_message = self.wrap_text_for_logging(message, width=available_width)
                
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.conversation_log_path, "a", encoding="utf-8") as f:
                # Add conversation ID header if this is a new conversation
                if speaker == "Barbie" and ("Hi, I'm Barbie!" in message or "Hi! I am Barbie!" in message):
                    # Wrap the header line if it's too long
                    header = f"=== CONVERSATION: {conversation_id} - {timestamp} ==="
                    if len(header) > 80:
                        header = f"=== CONVERSATION: {conversation_id[:30]}... ===\n=== {timestamp} ==="
                    f.write(f"\n{header}\n\n")
                
                f.write(f"{speaker}: {wrapped_message}\n\n--\n\n")
                
            logger.info(f"Logged {speaker} message to conversation file (wrapped at 80 chars)")
            
        except Exception as e:
            logger.error(f"Error logging conversation: {e}")
            
    def log_conversation_end(self, conversation_id):
        """Log the end of a conversation"""
        try:
            with open(self.conversation_log_path, "a", encoding="utf-8") as f:
                f.write("<STOP>\n\n")
                
            logger.info(f"Logged conversation end for {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error logging conversation end: {e}")
        
    def setup_background_processing(self):
        """Setup background processing queue and worker thread"""
        self.processing_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._background_worker, daemon=True)
        self.worker_thread.start()
        logger.info("Background processing worker started")
        
    def _background_worker(self):
        """Background worker thread to process requests"""
        while True:
            try:
                task = self.processing_queue.get()
                if task is None:  # Shutdown signal
                    break
                    
                task_type = task.get('type')
                if task_type == 'genesis':
                    self._process_genesis_task(task)
                elif task_type == 'chat':
                    self._process_chat_task(task)
                    
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in background worker: {e}")
                
    def _process_genesis_task(self, task):
        """Process a genesis task in the background"""
        try:
            user_input = task['user_input']
            conversation_id = task['conversation_id']
            
            logger.info(f"Processing genesis task: {conversation_id}")
            
            # Start new conversation log with original question
            log_file = self.conversation_manager.begin_debate(user_input)
            self.active_conversations[conversation_id] = log_file
            logger.info(f"Started conversation log: {log_file}")
            
            # Initialize all conversation quality systems
            debate_tracker = DebateProgressionTracker()
            debate_tracker.advance_round()  # Round 1
            self.debate_trackers[conversation_id] = debate_tracker
            self.prompt_generators[conversation_id] = ProgressionPromptGenerator(debate_tracker)
            
            # Initialize topic monitoring with the original question
            self.topic_monitors[conversation_id] = TopicCoherenceMonitor(user_input)
            
            # Initialize conclusion detection
            self.conclusion_detectors[conversation_id] = DebateConclusionDetector()
            
            logger.info(f"Initialized all quality systems for {conversation_id}")
            
            # Initialize conversation state for genesis mode
            state = ConversationState(
                user_input=user_input,
                original_message=user_input,
                round_number=0,
                is_genesis=True
            )
            
            # Process through the workflow (just the generation part, not the full loop)
            state = self.load_context_node(state)
            state = self.assess_conversation_maturity(state)
            state = self.search_web_node(state)
            state = self.generate_response_node(state)
            
            # Log Barbie's initial message and track claims
            if not state.error_message:
                self.ensure_message_logged("Barbie", state.generated_response, conversation_id)
                
                # Track Barbie's claims in debate progression
                if conversation_id in self.debate_trackers:
                    tracker = self.debate_trackers[conversation_id]
                    claims = tracker.extract_claims_from_message(state.generated_response, "Barbie")
                    if claims:
                        logger.info(f"Tracked {len(claims)} initial claims from Barbie")
                
                # Now send to Ken asynchronously
                self._send_to_ken_async(state, conversation_id)
            else:
                logger.error(f"Genesis processing failed: {state.error_message}")
                
        except Exception as e:
            logger.error(f"Error processing genesis task: {e}")
    
    def strip_thinking_tags(self, message: str) -> str:
        """Remove content between <think> and </think> tags from a message"""
        import re
        # Remove everything between <think> and </think> tags (including the tags)
        cleaned = re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL)
        # Clean up any extra whitespace that might be left
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        return cleaned.strip()
            
    def _process_chat_task(self, task):
        """Process a chat task (response from Ken) in the background"""
        try:
            ken_message = task['ken_message']
            conversation_id = task['conversation_id']
            
            # Strip thinking tags from Ken's message before processing
            ken_message = self.strip_thinking_tags(ken_message)
            
            logger.info(f"Processing chat from Ken: {conversation_id}")
            
            # Initialize state with Ken's feedback (thinking tags already stripped)
            state = ConversationState(
                user_input=ken_message,
                ken_feedback=ken_message,
                round_number=task.get('round_number', 1)
            )
            
            # Process Ken's feedback and generate response
            state = self.load_context_node(state)
            state = self.assess_conversation_maturity(state)
            state = self.search_web_node(state)
            state = self.generate_response_node(state)
            
            # Log Ken's message using centralized logging
            self.ensure_message_logged("Ken", ken_message, conversation_id)
            
            # Update debate progression with Ken's message
            if conversation_id in self.debate_trackers:
                tracker = self.debate_trackers[conversation_id] 
                tracker.advance_round()
                
                # Track Ken's claims and responses
                ken_claims = tracker.extract_claims_from_message(ken_message, "Ken")
                if ken_claims:
                    logger.info(f"Tracked {len(ken_claims)} claims from Ken")
                
                # Analyze how Ken responds to previous claims
                previous_claims = list(tracker.claims.keys())
                response_analysis = tracker.analyze_message_responses(ken_message, "Ken", previous_claims)
                if response_analysis['challenges']:
                    logger.info(f"Ken challenged {len(response_analysis['challenges'])} claims")
                if response_analysis['agreements']:
                    logger.info(f"Ken agreed with {len(response_analysis['agreements'])} claims")
                
                # Check for rehashing
                rehash_warnings = tracker.detect_rehashing(ken_message)
                if rehash_warnings:
                    logger.warning(f"Detected {len(rehash_warnings)} potential rehashing issues from Ken")
                    for warning in rehash_warnings:
                        if warning.get('type') == 'repetitive_question':
                            logger.warning(f"  Ken repetitive questioning: {warning.get('pattern')}")
                
                # Analyze Ken's message for topic coherence
                if conversation_id in self.topic_monitors:
                    topic_monitor = self.topic_monitors[conversation_id]
                    ken_topic_analysis = topic_monitor.analyze_topic_coherence(ken_message, "Ken")
                    
                    if ken_topic_analysis.relevance_level.value >= 4:  # Topic drift
                        logger.warning(f"Topic drift detected in Ken's message: {ken_topic_analysis.drift_explanation}")
                
                # Update conclusion detection with Ken's message
                if conversation_id in self.conclusion_detectors:
                    conclusion_detector = self.conclusion_detectors[conversation_id]
                    conclusion_detector.analyze_message(ken_message, "Ken", state.round_number or 1)
            
            # Use improved agreement detection to determine if conversation should end
            should_end, reason = self.agreement_detector.should_end_conversation(ken_message)
            analysis = self.agreement_detector.analyze_agreement(ken_message)
            
            logger.info(f"Agreement analysis: {analysis['agreement_level'].name} "
                       f"(confidence: {analysis['confidence']:.2f}) - {reason}")
            
            if should_end:
                logger.info(f"🎉 Conversation {conversation_id} complete: {reason}")
                
                # End conversation in new system with proper reason
                if conversation_id in self.active_conversations:
                    summary = f"Conversation ended - {reason}"
                    self.conversation_manager.conclude_debate(summary)
                    del self.active_conversations[conversation_id]
                
                # Also end in old system
                self.log_conversation_end(conversation_id)
                return
            
            # Continue the debate - log Barbie's response and send back to Ken
            if not state.error_message:
                self.ensure_message_logged("Barbie", state.generated_response, conversation_id)
                
                # Track Barbie's response claims and check for rehashing
                if conversation_id in self.debate_trackers:
                    tracker = self.debate_trackers[conversation_id]
                    barbie_claims = tracker.extract_claims_from_message(state.generated_response, "Barbie")
                    if barbie_claims:
                        logger.info(f"Tracked {len(barbie_claims)} claims from Barbie's response")
                    
                    # Check if Barbie is rehashing
                    barbie_rehash = tracker.detect_rehashing(state.generated_response)
                    if barbie_rehash:
                        logger.warning(f"Barbie may be rehashing {len(barbie_rehash)} items")
                        for item in barbie_rehash:
                            if item.get('type') == 'repetitive_question':
                                logger.warning(f"  Repetitive questioning: {item.get('pattern')}")
                            else:
                                logger.warning(f"  Rehashed claim: {item.get('text', 'Unknown')[:50]}...")
                    
                    # Validate evidence quality in Barbie's response
                    evidence_validation = self.evidence_validator.validate_message_evidence(
                        state.generated_response, 
                        state.original_message or state.user_input or "AI consciousness and technology"
                    )
                    
                    if evidence_validation['total_citations'] > 0:
                        quality_score = evidence_validation['evidence_quality_score']
                        logger.info(f"Evidence quality: {quality_score:.2f}/1.0 - {evidence_validation['overall_evidence_quality']}")
                        
                        # Log poor evidence quality with specific issues
                        irrelevant_count = evidence_validation['relevance_summary']['irrelevant']
                        future_dated_count = sum(1 for v in evidence_validation['validations'] 
                                               if 'future-dated' in v.explanation.lower())
                        
                        if irrelevant_count > 0:
                            logger.warning(f"Found {irrelevant_count} irrelevant citations in Barbie's response")
                        if future_dated_count > 0:
                            logger.warning(f"Found {future_dated_count} future-dated citations in Barbie's response")
                    
                    # Check topic coherence
                    if conversation_id in self.topic_monitors:
                        topic_monitor = self.topic_monitors[conversation_id]
                        topic_analysis = topic_monitor.analyze_topic_coherence(state.generated_response, "Barbie")
                        
                        if topic_analysis.relevance_level.value >= 4:  # TOPIC_DRIFT or COMPLETELY_UNRELATED
                            logger.warning(f"Topic drift detected in Barbie's response: {topic_analysis.drift_explanation}")
                            if topic_analysis.suggested_redirect:
                                logger.info(f"Suggested redirect: {topic_analysis.suggested_redirect}")
                    
                    # Update conclusion detection
                    if conversation_id in self.conclusion_detectors:
                        conclusion_detector = self.conclusion_detectors[conversation_id]
                        conclusion_detector.analyze_message(state.generated_response, "Barbie", state.round_number)
                        
                        # Check if debate should conclude
                        conclusion_analysis = conclusion_detector.should_conclude_debate()
                        if conclusion_analysis.should_conclude and conclusion_analysis.conclusion_confidence > 0.8:
                            logger.info(f"Natural conclusion detected: {conclusion_analysis.conclusion_reason}")
                            logger.info(f"Suggested action: {conclusion_analysis.suggested_action}")
                    
                    # Log progression summary
                    if conversation_id in self.prompt_generators:
                        generator = self.prompt_generators[conversation_id]
                        progress_summary = generator.generate_progression_summary()
                        logger.info(f"Debate progress: {progress_summary}")
                
                self._send_to_ken_async(state, conversation_id, state.round_number)
            else:
                logger.error(f"Chat processing failed: {state.error_message}")
                
        except Exception as e:
            logger.error(f"Error processing chat task: {e}")
            
    def _send_to_ken_async(self, state, conversation_id, round_number=0):
        """Send message to Ken asynchronously"""
        try:
            # Prepare payload for Ken
            if state.is_genesis and round_number == 0:
                message = f"Hi! I am Barbie! Sorry to bother you, but there is a question that keeps me up all night long. Here it is: {state.original_message}. My immediate answer is: {state.generated_response}. What do you think?"
            else:
                message = state.generated_response
                
            payload = {
                "message": message,
                "conversation_id": conversation_id,
                "round_number": round_number
            }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{self.ken_url}/v1/chat", json=payload)
                response.raise_for_status()
                
            logger.info(f"Successfully sent message to Ken for conversation {conversation_id}")
            
        except Exception as e:
            logger.error(f"Error sending to Ken: {e}")
        
    def setup_llm(self):
        """Initialize Ollama LLM with authentication"""
        self.llm = OllamaLLM(
            base_url=os.getenv("OLLAMA_BASE_URL"),
            model=os.getenv("BARBIE_MODEL", "llama3.3:70b"),
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
            collection_name="barbie_context",
            embedding_function=self.embeddings,
            client=client
        )
        
    def setup_tools(self):
        """Initialize tools for web search"""
        self.search_tool = TavilySearchResults(
            api_key=os.getenv("TAVILY_API_KEY"),
            max_results=3,
            search_depth="advanced"
        )
        
        self.tool_node = ToolNode([self.search_tool])
        
    def setup_graph(self):
        """Setup LangGraph workflow"""
        workflow = StateGraph(ConversationState)
        
        # Add nodes
        workflow.add_node("load_context", self.load_context_node)
        workflow.add_node("assess_maturity", self.assess_conversation_maturity)
        workflow.add_node("search_web", self.search_web_node)
        workflow.add_node("generate_response", self.generate_response_node)
        workflow.add_node("send_to_ken", self.send_to_ken_node)
        workflow.add_node("process_ken_feedback", self.process_ken_feedback_node)
        workflow.add_node("log_conversation", self.log_conversation_node)
        
        # Define the flow
        workflow.set_entry_point("load_context")
        
        workflow.add_edge("load_context", "assess_maturity")
        workflow.add_edge("assess_maturity", "search_web")
        workflow.add_edge("search_web", "generate_response")
        workflow.add_edge("generate_response", "send_to_ken")
        workflow.add_edge("send_to_ken", "process_ken_feedback")
        workflow.add_edge("process_ken_feedback", "log_conversation")
        
        # Conditional edge for stopping or continuing
        workflow.add_conditional_edges(
            "log_conversation",
            self.should_continue,
            {
                "continue": "load_context",
                "stop": END
            }
        )
        
        self.graph = workflow.compile()
        
    def load_context_node(self, state: ConversationState) -> ConversationState:
        """Load relevant conversation context from vector store"""
        try:
            if state.user_input:
                # Search for relevant context
                docs = self.vectorstore.similarity_search(
                    state.user_input,
                    k=int(os.getenv("VECTOR_SEARCH_K", "5"))
                )
                
                context_parts = []
                for doc in docs:
                    # Filter out documents containing error messages or technical details
                    content = doc.page_content
                    if not self._contains_error_content(content):
                        context_parts.append(content)
                
                state.conversation_context = "\n".join(context_parts)[:self.context_window]
                
            logger.info(f"Loaded context: {len(state.conversation_context)} characters")
            return state
            
        except Exception as e:
            logger.error(f"Error loading context: {e}")
            state.error_message = f"Context loading error: {e}"
            return state
    
    def search_web_node(self, state: ConversationState) -> ConversationState:
        """Search web for research-based arguments and evidence"""
        try:
            # Always search for research to support arguments
            if state.round_number == 0:
                # Initial research on the topic
                search_keywords = self.extract_search_keywords(state.user_input)
            else:
                # Research Ken's points to find supporting or contradicting evidence
                search_keywords = self.extract_search_keywords(state.ken_feedback) if state.ken_feedback else ""
            
            if search_keywords:
                logger.info(f"Researching: {search_keywords}")
                results = self.search_tool.run(search_keywords)
                state.search_results = str(results)[:2000]  # Increased limit for more research
                logger.info(f"Found research evidence for arguments")
            else:
                state.search_results = ""
                
            return state
            
        except Exception as e:
            logger.error(f"Error in web search: {e}")
            state.search_results = ""
            return state
    
    def generate_response_node(self, state: ConversationState) -> ConversationState:
        """Generate response using LLM with dynamic parameters"""
        try:
            prompt = self.build_generation_prompt(state)
            
            # Create dynamic LLM with adjusted parameters
            api_key = os.getenv('SECRET_AI_API_KEY')
            dynamic_llm = OllamaLLM(
                base_url=os.getenv("OLLAMA_BASE_URL"),
                model=os.getenv("BARBIE_MODEL", "llama3.3:70b"),
                timeout=float(os.getenv("OLLAMA_TIMEOUT", "300.0")),
                temperature=state.llm_temperature,
                top_p=state.llm_top_p,
                client_kwargs={
                    "headers": {"Authorization": f"Bearer {api_key}"}
                } if api_key else {}
            )
            
            response = dynamic_llm.invoke(prompt)
            state.generated_response = response.strip()
            
            logger.info(f"Generated response: {len(state.generated_response)} characters with temp={state.llm_temperature}")
            return state
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            state.error_message = f"Generation error: {e}"
            state.generated_response = f"Error generating response: {e}"
            return state
    
    def send_to_ken_node(self, state: ConversationState) -> ConversationState:
        """Send generated response to Ken for evaluation"""
        try:
            # For genesis mode, send both original message and Barbie's response
            if state.is_genesis and state.round_number == 0:
                payload = {
                    "message": f"Hi! I am Barbie! Sorry to bother you, but there is a question that keeps me up all night long. Here it is: {state.original_message}. My immediate answer is: {state.generated_response}. What do you think?",
                    "conversation_id": f"genesis_round_{state.round_number}"
                }
            else:
                payload = {
                    "message": state.generated_response,
                    "conversation_id": f"round_{state.round_number}"
                }
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(f"{self.ken_url}/v1/chat", json=payload)
                response.raise_for_status()
                
                ken_response = response.json()
                state.ken_feedback = ken_response.get("response", "")
                
            logger.info(f"Received Ken feedback: {len(state.ken_feedback)} characters")
            return state
            
        except Exception as e:
            logger.error(f"Error communicating with Ken: {e}")
            state.error_message = f"Ken communication error: {e}"
            state.ken_feedback = f"Error communicating with Ken: {e}"
            return state
    
    def process_ken_feedback_node(self, state: ConversationState) -> ConversationState:
        """Process Ken's feedback and determine next steps"""
        try:
            # Check if Ken agreed (sent <STOP>)
            ken_feedback_upper = state.ken_feedback.upper()
            if "<STOP>" in ken_feedback_upper or "I'M CONVINCED" in ken_feedback_upper:
                state.should_stop = True
                logger.info(f"🎉 Ken agreed! Conversation complete after {state.round_number + 1} rounds.")
                logger.info(f"Final agreement reached at maturity stage: {state.maturity_stage}")
            else:
                state.round_number += 1
                # Update user input with Ken's feedback for next iteration
                state.user_input = state.ken_feedback
                logger.info(f"Round {state.round_number} continues - Ken provided feedback for refinement")
                
            return state
            
        except Exception as e:
            logger.error(f"Error processing Ken feedback: {e}")
            state.error_message = f"Feedback processing error: {e}"
            return state
    
    def log_conversation_node(self, state: ConversationState) -> ConversationState:
        """Log conversation to vector store (file logging now handled in background tasks)"""
        try:
            # Add to vector store for future context
            doc = Document(
                page_content=f"Barbie: {state.generated_response}\nKen: {state.ken_feedback}",
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "round": state.round_number,
                    "agent": "conversation"
                }
            )
            self.vectorstore.add_documents([doc])
            
            logger.info(f"Added conversation round {state.round_number} to vector store")
            return state
            
        except Exception as e:
            logger.error(f"Error adding to vector store: {e}")
            state.error_message = f"Vector store error: {e}"
            return state
    
    def should_continue(self, state: ConversationState) -> str:
        """Determine if conversation should continue"""
        if state.should_stop:
            return "stop"
        elif state.round_number >= self.max_rounds:
            logger.warning(f"Max rounds ({self.max_rounds}) reached")
            return "stop"
        elif state.error_message:
            logger.error(f"Stopping due to error: {state.error_message}")
            return "stop"
        else:
            return "continue"
    
    def extract_search_keywords(self, text: str) -> str:
        """Extract search keywords for research-based arguments"""
        # Always search for research and evidence to support arguments
        import re
        
        # Extract main topics and concepts
        words = text.lower().split()
        
        # Remove common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were"}
        meaningful_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Take key concepts and add research terms
        if meaningful_words:
            # Take first few meaningful words and add research terms
            base_query = " ".join(meaningful_words[:3])
            research_query = f"{base_query} research evidence studies 2024 2025"
            return research_query
        
        return "current research evidence studies"
    
    def assess_conversation_maturity(self, state: ConversationState) -> ConversationState:
        """Assess conversation maturity using heuristics and LLM analysis"""
        try:
            # Update conversation history
            if state.generated_response:
                state.conversation_history.append(f"Barbie: {state.generated_response}")
            if state.ken_feedback:
                state.conversation_history.append(f"Ken: {state.ken_feedback}")
            
            # Heuristic assessment (primary)
            heuristic_score = self.calculate_heuristic_maturity(state)
            
            # LLM-based refinement (secondary, for edge cases)
            if abs(heuristic_score - state.maturity_score) > 0.3 or state.round_number % 5 == 0:
                llm_score = self.calculate_llm_maturity(state)
                # Weighted average: 70% heuristic, 30% LLM
                state.maturity_score = (heuristic_score * 0.7) + (llm_score * 0.3)
            else:
                state.maturity_score = heuristic_score
            
            # Update stage and LLM parameters
            state = self.update_maturity_stage(state)
            state = self.adjust_llm_parameters(state)
            
            logger.info(f"Maturity assessment - Score: {state.maturity_score:.2f}, Stage: {state.maturity_stage}, Temp: {state.llm_temperature}")
            return state
            
        except Exception as e:
            logger.error(f"Error in maturity assessment: {e}")
            return state
    
    def calculate_heuristic_maturity(self, state: ConversationState) -> float:
        """Calculate maturity score using heuristic analysis"""
        if not state.conversation_history:
            return 0.0
        
        score = 0.0
        
        # 1. Round progression (0-30%)
        round_factor = min(state.round_number / 15.0, 1.0)
        score += round_factor * 0.3
        
        # 2. Response length convergence (0-20%)
        if len(state.conversation_history) >= 4:
            recent_lengths = [len(msg) for msg in state.conversation_history[-4:]]
            length_variance = max(recent_lengths) - min(recent_lengths)
            convergence_factor = max(0, 1 - (length_variance / 500))
            score += convergence_factor * 0.2
        
        # 3. Technical term density (0-25%)
        technical_terms = ["solution", "approach", "method", "implementation", "specific", "detailed", "precise", "accurate"]
        recent_text = " ".join(state.conversation_history[-2:]).lower()
        technical_density = sum(1 for term in technical_terms if term in recent_text) / len(technical_terms)
        score += technical_density * 0.25
        
        # 4. Question-to-statement ratio (0-15%)
        questions = recent_text.count("?")
        statements = recent_text.count(".") + recent_text.count("!")
        if statements > 0:
            statement_ratio = statements / (statements + questions)
            score += statement_ratio * 0.15
        
        # 5. Agreement indicators (0-10%)
        agreement_words = ["agree", "correct", "exactly", "precisely", "confirmed", "approved"]
        agreement_count = sum(1 for word in agreement_words if word in recent_text)
        score += min(agreement_count / 3.0, 1.0) * 0.1
        
        return min(score, 1.0)
    
    def calculate_llm_maturity(self, state: ConversationState) -> float:
        """Use LLM to assess conversation maturity for edge cases"""
        try:
            recent_conversation = "\n".join(state.conversation_history[-6:])
            
            analysis_prompt = f"""
            Analyze this conversation between AI agents Barbie and Ken to assess maturity level.
            
            CONVERSATION:
            {recent_conversation}
            
            Rate the conversation maturity from 0.0 to 1.0 based on:
            - Specificity: Are responses becoming more detailed and precise?
            - Convergence: Are the agents moving toward agreement?
            - Technical depth: Is the discussion becoming more technical/specific?
            - Solution focus: Are they focusing on concrete solutions vs broad exploration?
            
            Stages:
            0.0-0.25: Exploration (broad, creative, many questions)
            0.26-0.50: Refinement (focused exploration, some specificity)
            0.51-0.75: Convergence (specific solutions, technical details)
            0.76-1.0: Consensus (agreement, final details, ready to conclude)
            
            Respond with only a number between 0.0 and 1.0
            """
            
            response = self.analyzer_llm.invoke(analysis_prompt)
            score = float(response.strip().split()[0])
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            logger.warning(f"LLM maturity analysis failed: {e}")
            return state.maturity_score  # Fallback to current score
    
    def update_maturity_stage(self, state: ConversationState) -> ConversationState:
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
    
    def adjust_llm_parameters(self, state: ConversationState) -> ConversationState:
        """Adjust LLM parameters based on maturity stage using centralized tuning"""
        state.llm_temperature, state.llm_top_p = get_temperature_for_stage("barbie", state.maturity_stage)
        return state
    
    def build_generation_prompt(self, state: ConversationState, conversation_id: str = None) -> str:
        """Build prompt for response generation with debate progression awareness"""
        
        # Start with base prompt
        base_prompt = "You are Barbie, an AI agent specialized in generating creative and innovative solutions. Your role is to propose ideas, solutions, and responses that will be evaluated by Ken (the discriminator)."
        
        # Check if we have progression tracking for this conversation
        if conversation_id and conversation_id in self.prompt_generators:
            # Use progression-aware prompt generation
            generator = self.prompt_generators[conversation_id]
            enhanced_prompt = generator.generate_barbie_progression_prompt(base_prompt)
            
            # Add topic coherence guidance if needed
            topic_guidance = ""
            if conversation_id in self.topic_monitors:
                topic_monitor = self.topic_monitors[conversation_id]
                topic_guidance = topic_monitor.generate_refocus_prompt_addition()
            
            # Add the enhanced prompt as the base
            prompt_parts = [enhanced_prompt]
            if topic_guidance:
                prompt_parts.append(topic_guidance)
            prompt_parts.append("")
        else:
            # Fallback to standard prompt
            prompt_parts = [base_prompt, ""]
        
        # Natural dialog flow rules
        if state.round_number == 0:
            prompt_parts.extend([
                "IMPORTANT: Begin your response naturally without formal introductions or greetings.",
                "Start directly with your ideas, insights, or response to the topic.",
                ""
            ])
        else:
            prompt_parts.extend([
                "IMPORTANT: Continue the conversation naturally as part of an ongoing dialog.",
                "Address the previous points directly without formal transitions or greetings.",
                ""
            ])
            
        prompt_parts.extend([
            "CONTEXT FROM PREVIOUS CONVERSATIONS:",
            state.conversation_context if state.conversation_context else "No previous context available.",
            "",
        ])
        
        # Add original question reminder to maintain focus
        if state.original_message:
            prompt_parts.extend([
                "ORIGINAL QUESTION TO KEEP IN FOCUS:",
                state.original_message,
                "",
                "IMPORTANT: Ensure your response directly relates to and advances discussion of the original question above.",
                "Avoid tangential topics that don't contribute to answering the core question.",
                "Connect all arguments, examples, and evidence back to this central question.",
                "",
            ])
        
        if state.search_results:
            prompt_parts.extend([
                "RECENT INFORMATION FROM WEB SEARCH:",
                state.search_results,
                "",
            ])
        
        if state.round_number > 0:
            prompt_parts.extend([
                "KEN'S RESPONSE:",
                state.ken_feedback,
                "",
                f"This is round {state.round_number} of your debate with Ken.",
                "",
                "IMPORTANT - Address Ken directly as if you are speaking to him:",
                "- Respond to Ken's points as if in direct conversation (e.g., 'Ken, I see your point about...', 'That's interesting Ken, but have you considered...')",
                "- DO NOT describe what Ken said or think about his response internally",
                "- DO NOT say 'Ken mentioned' or 'Ken raised' - instead say 'You mentioned' or 'You raised'",
                "- Speak TO Ken, not ABOUT Ken",
                "",
                "DEBATE STRATEGY - Your response should:",
                "1. Use the research findings below to support your arguments with evidence",
                "2. Address Ken's specific concerns directly ('Your concern about X is valid, but...')",
                "3. Ask Ken follow-up questions directly ('Ken, how do you reconcile this with...')",
                "4. Present counter-evidence or alternative interpretations if you disagree",
                "5. Challenge Ken's premises directly ('Ken, you're assuming that...')",
                "6. Only move toward agreement when you have thoroughly explored all aspects",
                "",
                "Remember: You are having a conversation WITH Ken, not thinking about what Ken said.",
            ])
        else:
            prompt_parts.extend([
                "USER REQUEST:",
                state.user_input,
                "",
                "Generate your initial response to share with Ken for discussion and debate.",
            ])
        
        prompt_parts.extend([
            "",
            "Guidelines for focused direct dialogue:",
            "- Address Ken directly in second person ('You mentioned...', 'Your point about...')",
            "- Support your arguments with research evidence from web search results",
            "- Challenge Ken's assumptions directly ('Ken, why do you assume...')",
            "- Ask Ken directly: 'Why do you think that?' and 'How do you know that?'",
            "- Present arguments TO Ken ('Ken, consider this alternative...')",
            "- Don't agree quickly - challenge Ken directly on edge cases",
            "- Ask Ken follow-up questions that move from general to specific",
            "- NEVER narrate what Ken said or describe his thinking - respond to him directly",
            "- STAY FOCUSED on the original question - avoid tangential diversions",
            "- Connect all arguments back to the core question being discussed",
            "- If Ken introduces tangential topics, redirect: 'Ken, that's interesting but how does it relate to [original question]?'",
            "- Request examples, data, or studies that directly support claims about the main topic",
            "- Only reach consensus when you've exhaustively explored the original question",
            "- Maintain intellectual rigor while staying collaborative and focused",
            "",
            f"Conversation maturity stage: {state.maturity_stage}",
            f"Round {state.round_number}: Generate your {'initial research-based introduction and' if state.round_number == 0 else 'evidence-supported'} response that advances the debate:",
            "",
            "NATURAL DIALOG STYLE:",
            "- End your response naturally when you've made your point",
            "- No formal closings like 'Looking forward to...', 'Best regards', or 'Sincerely'",
            "- No letter-style sign-offs or signatures",
            "- Simply stop talking when your thought is complete"
        ])
        
        return "\n".join(prompt_parts)
    
    def setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.post("/v1/chat")
        async def chat_endpoint(request: ChatRequest):
            """Chat endpoint for receiving messages from Ken - returns immediately"""
            try:
                conversation_id = request.conversation_id or f"chat_{datetime.now().isoformat()}"
                
                # Queue the chat task for background processing
                task = {
                    'type': 'chat',
                    'ken_message': request.message,
                    'conversation_id': conversation_id,
                    'round_number': request.round_number or 1
                }
                
                self.processing_queue.put(task)
                
                logger.info(f"Chat request from Ken queued for processing: {conversation_id}")
                
                # Return immediate success
                return {
                    "status": "success",
                    "message": "Chat request accepted and queued for processing",
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error in chat endpoint: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "agent": "Barbie", "timestamp": datetime.now().isoformat()}
        
        @self.app.post("/v1/genesis")
        async def genesis_endpoint(request: ChatRequest):
            """Genesis endpoint to initiate debate between Barbie and Ken - returns immediately"""
            try:
                conversation_id = request.conversation_id or f"genesis_{datetime.now().isoformat()}"
                
                # Queue the genesis task for background processing
                task = {
                    'type': 'genesis',
                    'user_input': request.message,
                    'conversation_id': conversation_id
                }
                
                self.processing_queue.put(task)
                
                logger.info(f"Genesis request queued for processing: {conversation_id}")
                
                # Return immediate success
                return {
                    "status": "success",
                    "message": "Genesis request accepted and queued for processing",
                    "conversation_id": conversation_id,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Error in genesis endpoint: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/")
        async def root():
            """Root endpoint"""
            return {"message": "Skynet Barbie Agent", "version": "1.0.0"}

def main():
    """Main entry point"""
    barbie = BarbieAgent()
    
    port = int(os.getenv("BARBIE_PORT", "8001"))
    host = "0.0.0.0"
    
    logger.info(f"Starting Barbie agent on {host}:{port}")
    
    uvicorn.run(
        barbie.app,
        host=host,
        port=port,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

if __name__ == "__main__":
    main()