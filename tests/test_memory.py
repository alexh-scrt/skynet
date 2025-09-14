"""
Tests for conversation memory and argument tracking
"""
import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.memory.conversation_memory import ConversationMemory, Claim, Topic
from src.memory.argument_tracker import ArgumentTracker, ArgumentType, ArgumentStrength


class TestConversationMemory:
    def test_start_topic(self):
        memory = ConversationMemory()
        topic = memory.start_topic("topic_1", "AI and Society")
        
        assert topic.id == "topic_1"
        assert topic.title == "AI and Society"
        assert memory.current_topic == topic
        assert len(memory.topics) == 1
    
    def test_add_claim(self):
        memory = ConversationMemory()
        memory.start_topic("topic_1", "AI and Society")
        
        claim = memory.add_claim(
            "Barbie", 
            "AI can simulate societal norms",
            ["Study X shows AI modeling behavior"]
        )
        
        assert claim.speaker == "Barbie"
        assert claim.content == "AI can simulate societal norms"
        assert len(claim.supporting_evidence) == 1
        assert claim.status == "pending"
    
    def test_counter_argument(self):
        memory = ConversationMemory()
        memory.start_topic("topic_1", "AI and Society")
        
        claim = memory.add_claim("Barbie", "AI can simulate societal norms")
        memory.add_counter_argument(claim.id, "But AI lacks true understanding")
        
        assert len(claim.counter_arguments) == 1
        assert claim.status == "disputed"
    
    def test_resolve_claim(self):
        memory = ConversationMemory()
        memory.start_topic("topic_1", "AI and Society")
        
        claim = memory.add_claim("Barbie", "AI can simulate societal norms")
        memory.resolve_claim(claim.id, "accepted")
        
        assert claim.status == "supported"
        assert len(memory.current_topic.resolved_points) == 1
    
    def test_fact_base(self):
        memory = ConversationMemory()
        memory.add_fact(
            "fact_1",
            "BCIs have 85% accuracy rate",
            "Nature Neuroscience 2024"
        )
        
        assert "fact_1" in memory.fact_base
        assert memory.fact_base["fact_1"]["source"] == "Nature Neuroscience 2024"
    
    def test_should_change_topic(self):
        memory = ConversationMemory()
        memory.start_topic("topic_1", "AI and Society")
        
        # Add many resolved claims
        for i in range(10):
            claim = memory.add_claim("Barbie", f"Claim {i}")
            memory.resolve_claim(claim.id, "accepted")
        
        # Should suggest topic change when most claims resolved
        assert memory.should_change_topic() == True


class TestArgumentTracker:
    def test_add_argument(self):
        tracker = ArgumentTracker()
        
        arg = tracker.add_argument(
            speaker="Ken",
            argument_type=ArgumentType.DEDUCTIVE,
            premises=["All humans are mortal", "Socrates is human"],
            conclusion="Socrates is mortal",
            evidence={"All humans are mortal": ["Common knowledge"]}
        )
        
        assert arg.speaker == "Ken"
        assert arg.argument_type == ArgumentType.DEDUCTIVE
        assert len(arg.premises) == 2
        assert arg.conclusion == "Socrates is mortal"
    
    def test_challenge_premise(self):
        tracker = ArgumentTracker()
        
        arg = tracker.add_argument(
            speaker="Ken",
            argument_type=ArgumentType.DEDUCTIVE,
            premises=["AI can think", "Thinking requires consciousness"],
            conclusion="AI has consciousness"
        )
        
        tracker.challenge_premise(arg.id, 0, "AI doesn't truly think")
        
        assert arg.premises[0].challenged == True
        assert len(arg.rebuttals) == 1
    
    def test_detect_fallacy(self):
        tracker = ArgumentTracker()
        
        arg = tracker.add_argument(
            speaker="Barbie",
            argument_type=ArgumentType.INDUCTIVE,
            premises=["Some AIs make mistakes"],
            conclusion="All AIs are unreliable"
        )
        
        tracker.detect_fallacy(
            arg.id,
            "Hasty Generalization",
            "Drawing broad conclusion from limited examples"
        )
        
        assert len(tracker.fallacies_detected) == 1
        assert arg.strength == ArgumentStrength.FALLACIOUS
    
    def test_evaluate_strength(self):
        tracker = ArgumentTracker()
        
        # Strong argument with evidence
        arg1 = tracker.add_argument(
            speaker="Ken",
            argument_type=ArgumentType.DEDUCTIVE,
            premises=["Premise 1", "Premise 2"],
            conclusion="Conclusion",
            evidence={
                "Premise 1": ["Evidence A", "Evidence B"],
                "Premise 2": ["Evidence C"]
            }
        )
        
        strength1 = tracker.evaluate_argument_strength(arg1.id)
        assert strength1 == ArgumentStrength.STRONG
        
        # Weak argument without evidence
        arg2 = tracker.add_argument(
            speaker="Barbie",
            argument_type=ArgumentType.INDUCTIVE,
            premises=["Unsupported premise"],
            conclusion="Weak conclusion"
        )
        
        strength2 = tracker.evaluate_argument_strength(arg2.id)
        assert strength2 == ArgumentStrength.WEAK
    
    def test_find_contradictions(self):
        tracker = ArgumentTracker()
        
        tracker.add_argument(
            speaker="Ken",
            argument_type=ArgumentType.DEDUCTIVE,
            premises=["Evidence A"],
            conclusion="AI is beneficial"
        )
        
        tracker.add_argument(
            speaker="Ken",
            argument_type=ArgumentType.DEDUCTIVE,
            premises=["Evidence B"],
            conclusion="Not AI is beneficial"
        )
        
        contradictions = tracker.find_contradictions()
        assert len(contradictions) == 1
        assert contradictions[0]["speaker"] == "Ken"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])