"""
Conversation Memory Module
Tracks key points, arguments, and facts across conversation turns
"""
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Claim:
    """Represents a claim made during conversation"""
    id: str
    speaker: str
    content: str
    timestamp: datetime
    supporting_evidence: List[str] = field(default_factory=list)
    counter_arguments: List[str] = field(default_factory=list)
    status: str = "pending"  # pending, supported, refuted, disputed
    
    def to_dict(self):
        return {
            "id": self.id,
            "speaker": self.speaker,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "supporting_evidence": self.supporting_evidence,
            "counter_arguments": self.counter_arguments,
            "status": self.status
        }


@dataclass
class Topic:
    """Represents a discussion topic"""
    id: str
    title: str
    started_at: datetime
    claims: List[Claim] = field(default_factory=list)
    key_questions: List[str] = field(default_factory=list)
    resolved_points: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "started_at": self.started_at.isoformat(),
            "claims": [c.to_dict() for c in self.claims],
            "key_questions": self.key_questions,
            "resolved_points": self.resolved_points
        }


class ConversationMemory:
    """Maintains conversation state and history"""
    
    def __init__(self):
        self.topics: List[Topic] = []
        self.current_topic: Optional[Topic] = None
        self.fact_base: Dict[str, Dict] = {}  # Shared facts both agents agree on
        self.speaker_positions: Dict[str, List[str]] = {}  # Track each speaker's positions
        self.unresolved_questions: Set[str] = set()
        self.conversation_goals: List[str] = []
        
    def start_topic(self, topic_id: str, title: str) -> Topic:
        """Start a new discussion topic"""
        topic = Topic(
            id=topic_id,
            title=title,
            started_at=datetime.now()
        )
        self.topics.append(topic)
        self.current_topic = topic
        return topic
    
    def add_claim(self, speaker: str, content: str, evidence: List[str] = None) -> Claim:
        """Add a new claim to the current topic"""
        if not self.current_topic:
            raise ValueError("No active topic. Start a topic first.")
        
        claim = Claim(
            id=f"claim_{len(self.current_topic.claims) + 1}",
            speaker=speaker,
            content=content,
            timestamp=datetime.now(),
            supporting_evidence=evidence or []
        )
        
        self.current_topic.claims.append(claim)
        
        # Track speaker's position
        if speaker not in self.speaker_positions:
            self.speaker_positions[speaker] = []
        self.speaker_positions[speaker].append(content)
        
        return claim
    
    def add_counter_argument(self, claim_id: str, counter: str):
        """Add a counter-argument to an existing claim"""
        if not self.current_topic:
            return
        
        for claim in self.current_topic.claims:
            if claim.id == claim_id:
                claim.counter_arguments.append(counter)
                claim.status = "disputed"
                break
    
    def resolve_claim(self, claim_id: str, resolution: str):
        """Mark a claim as resolved"""
        if not self.current_topic:
            return
        
        for claim in self.current_topic.claims:
            if claim.id == claim_id:
                claim.status = "supported" if resolution == "accepted" else "refuted"
                self.current_topic.resolved_points.append(f"{claim.content} - {resolution}")
                break
    
    def add_fact(self, fact_id: str, fact_content: str, source: str):
        """Add a verified fact to the shared fact base"""
        self.fact_base[fact_id] = {
            "content": fact_content,
            "source": source,
            "added_at": datetime.now().isoformat()
        }
    
    def get_unaddressed_claims(self) -> List[Claim]:
        """Get claims that haven't been addressed"""
        if not self.current_topic:
            return []
        
        return [c for c in self.current_topic.claims if c.status == "pending"]
    
    def get_disputed_claims(self) -> List[Claim]:
        """Get claims that are currently disputed"""
        if not self.current_topic:
            return []
        
        return [c for c in self.current_topic.claims if c.status == "disputed"]
    
    def add_question(self, question: str):
        """Add a key question to explore"""
        if self.current_topic:
            self.current_topic.key_questions.append(question)
        self.unresolved_questions.add(question)
    
    def resolve_question(self, question: str):
        """Mark a question as resolved"""
        self.unresolved_questions.discard(question)
    
    def get_conversation_summary(self) -> Dict:
        """Get a summary of the conversation state"""
        return {
            "topics_discussed": len(self.topics),
            "current_topic": self.current_topic.title if self.current_topic else None,
            "total_claims": sum(len(t.claims) for t in self.topics),
            "resolved_points": sum(len(t.resolved_points) for t in self.topics),
            "unresolved_questions": list(self.unresolved_questions),
            "shared_facts": len(self.fact_base),
            "conversation_goals": self.conversation_goals
        }
    
    def should_change_topic(self) -> bool:
        """Determine if it's time to change topics"""
        if not self.current_topic:
            return True
        
        # Change topic if most claims are resolved or if stuck in dispute
        resolved_count = len([c for c in self.current_topic.claims if c.status in ["supported", "refuted"]])
        disputed_count = len([c for c in self.current_topic.claims if c.status == "disputed"])
        total_claims = len(self.current_topic.claims)
        
        if total_claims > 5:
            if resolved_count / total_claims > 0.7:
                return True  # Most claims resolved
            if disputed_count / total_claims > 0.5 and total_claims > 10:
                return True  # Too many disputes, move on
        
        return False
    
    def export_memory(self) -> str:
        """Export memory to JSON"""
        return json.dumps({
            "topics": [t.to_dict() for t in self.topics],
            "fact_base": self.fact_base,
            "speaker_positions": self.speaker_positions,
            "unresolved_questions": list(self.unresolved_questions),
            "conversation_goals": self.conversation_goals
        }, indent=2)
    
    def import_memory(self, memory_json: str):
        """Import memory from JSON"""
        data = json.loads(memory_json)
        # Restore memory state from JSON
        # Implementation would reconstruct objects from dictionaries
        pass