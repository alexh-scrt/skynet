"""
Enhanced Conversation Module with Memory Integration
Shows how Barbie and Ken can use memory tracking for better conversations
"""
from typing import Dict, List, Optional
from src.memory.conversation_memory import ConversationMemory
from src.memory.argument_tracker import ArgumentTracker, ArgumentType
import json


class EnhancedConversationManager:
    """Manages enhanced conversations with memory and argument tracking"""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.argument_tracker = ArgumentTracker()
        self.conversation_id = None
        
    def start_conversation(self, conversation_id: str, topic: str, goals: List[str] = None):
        """Initialize a new conversation"""
        self.conversation_id = conversation_id
        self.memory.start_topic(f"topic_{conversation_id}", topic)
        
        if goals:
            self.memory.conversation_goals = goals
            
        return {
            "conversation_id": conversation_id,
            "topic": topic,
            "goals": goals or []
        }
    
    def process_agent_response(self, speaker: str, response_text: str, metadata: Dict = None) -> Dict:
        """Process an agent's response and update memory"""
        
        # Extract claims from response (simplified - could use NLP)
        if "claim:" in response_text.lower():
            claim_text = response_text.split("claim:")[-1].strip()
            evidence = metadata.get("evidence", []) if metadata else []
            claim = self.memory.add_claim(speaker, claim_text, evidence)
            
            # Track as an argument if structured
            if metadata and "argument_type" in metadata:
                arg = self.argument_tracker.add_argument(
                    speaker=speaker,
                    argument_type=ArgumentType[metadata["argument_type"].upper()],
                    premises=metadata.get("premises", []),
                    conclusion=claim_text,
                    evidence=metadata.get("evidence_map", {})
                )
                
                return {
                    "type": "argument",
                    "claim_id": claim.id,
                    "argument_id": arg.id,
                    "strength": self.argument_tracker.evaluate_argument_strength(arg.id).value
                }
        
        # Handle counter-arguments
        if "counter:" in response_text.lower() and metadata and "target_claim" in metadata:
            counter_text = response_text.split("counter:")[-1].strip()
            self.memory.add_counter_argument(metadata["target_claim"], counter_text)
            
            if "target_argument" in metadata:
                self.argument_tracker.challenge_premise(
                    metadata["target_argument"],
                    metadata.get("premise_index", 0),
                    counter_text
                )
            
            return {
                "type": "counter_argument",
                "target": metadata["target_claim"],
                "counter": counter_text
            }
        
        # Handle resolution/agreement
        if "agree:" in response_text.lower() and metadata and "claim_id" in metadata:
            self.memory.resolve_claim(metadata["claim_id"], "accepted")
            return {
                "type": "resolution",
                "claim_id": metadata["claim_id"],
                "result": "accepted"
            }
        
        return {"type": "statement", "content": response_text}
    
    def get_conversation_context(self, for_speaker: str) -> Dict:
        """Get relevant context for an agent to respond"""
        
        # Get unaddressed claims from the other speaker
        unaddressed = self.memory.get_unaddressed_claims()
        other_claims = [c for c in unaddressed if c.speaker != for_speaker]
        
        # Get disputed claims that need resolution
        disputed = self.memory.get_disputed_claims()
        
        # Get strongest arguments from both sides
        strong_args = self.argument_tracker.get_strongest_arguments()
        
        # Check for contradictions
        contradictions = self.argument_tracker.find_contradictions()
        
        return {
            "unaddressed_claims": [c.to_dict() for c in other_claims],
            "disputed_claims": [c.to_dict() for c in disputed],
            "strong_arguments": [
                {
                    "id": arg.id,
                    "speaker": arg.speaker,
                    "conclusion": arg.conclusion,
                    "strength": arg.strength.value
                }
                for arg in strong_args[:3]  # Top 3 arguments
            ],
            "contradictions": contradictions,
            "shared_facts": self.memory.fact_base,
            "unresolved_questions": list(self.memory.unresolved_questions),
            "conversation_goals": self.memory.conversation_goals,
            "should_change_topic": self.memory.should_change_topic()
        }
    
    def suggest_next_action(self, speaker: str) -> str:
        """Suggest what the agent should do next"""
        context = self.get_conversation_context(speaker)
        
        # Priority 1: Address unresolved claims
        if context["unaddressed_claims"]:
            return f"respond_to_claim:{context['unaddressed_claims'][0]['id']}"
        
        # Priority 2: Resolve disputes
        if context["disputed_claims"]:
            return f"provide_evidence:{context['disputed_claims'][0]['id']}"
        
        # Priority 3: Address contradictions
        if context["contradictions"]:
            for contradiction in context["contradictions"]:
                if contradiction["speaker"] == speaker:
                    return f"resolve_contradiction:{contradiction['arg1']},{contradiction['arg2']}"
        
        # Priority 4: Answer unresolved questions
        if context["unresolved_questions"]:
            return f"answer_question:{context['unresolved_questions'][0]}"
        
        # Priority 5: Change topic if needed
        if context["should_change_topic"]:
            return "suggest_new_topic"
        
        # Default: Make a new claim or argument
        return "make_new_claim"
    
    def add_verified_fact(self, fact_id: str, fact_content: str, source: str):
        """Add a fact that both agents agree on"""
        self.memory.add_fact(fact_id, fact_content, source)
    
    def get_summary(self) -> Dict:
        """Get a summary of the conversation"""
        memory_summary = self.memory.get_conversation_summary()
        argument_summary = self.argument_tracker.get_argument_summary()
        
        return {
            **memory_summary,
            **argument_summary,
            "conversation_id": self.conversation_id
        }
    
    def export_conversation(self) -> str:
        """Export the full conversation state"""
        return json.dumps({
            "memory": json.loads(self.memory.export_memory()),
            "arguments": {
                arg_id: {
                    "speaker": arg.speaker,
                    "type": arg.argument_type.value,
                    "premises": [p.content for p in arg.premises],
                    "conclusion": arg.conclusion,
                    "strength": arg.strength.value
                }
                for arg_id, arg in self.argument_tracker.arguments.items()
            },
            "summary": self.get_summary()
        }, indent=2)


class AgentResponseBuilder:
    """Helper to build structured responses for agents"""
    
    @staticmethod
    def build_claim_response(speaker: str, claim: str, evidence: List[str] = None,
                            argument_type: str = None, premises: List[str] = None) -> Dict:
        """Build a structured claim response"""
        response = f"Claim: {claim}"
        
        metadata = {
            "evidence": evidence or [],
        }
        
        if argument_type and premises:
            metadata["argument_type"] = argument_type
            metadata["premises"] = premises
            metadata["evidence_map"] = {p: evidence for p in premises} if evidence else {}
        
        return {
            "speaker": speaker,
            "response": response,
            "metadata": metadata
        }
    
    @staticmethod
    def build_counter_response(speaker: str, counter: str, target_claim: str,
                              target_argument: str = None, premise_index: int = 0) -> Dict:
        """Build a structured counter-argument response"""
        response = f"Counter: {counter}"
        
        metadata = {
            "target_claim": target_claim
        }
        
        if target_argument:
            metadata["target_argument"] = target_argument
            metadata["premise_index"] = premise_index
        
        return {
            "speaker": speaker,
            "response": response,
            "metadata": metadata
        }
    
    @staticmethod
    def build_agreement_response(speaker: str, claim_id: str, reason: str = "") -> Dict:
        """Build a structured agreement response"""
        response = f"Agree: I accept this claim. {reason}"
        
        return {
            "speaker": speaker,
            "response": response,
            "metadata": {"claim_id": claim_id}
        }