"""
Tests for debate progression mechanics
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.debate.progression_tracker import DebateProgressionTracker, ClaimStatus, ResolutionType
from src.debate.progression_prompts import ProgressionPromptGenerator


class TestDebateProgressionTracker:
    
    def test_claim_extraction(self):
        """Test extracting claims from messages"""
        tracker = DebateProgressionTracker()
        tracker.advance_round()
        
        # Test Barbie's message with claims
        barbie_message = ("I believe AI consciousness is possible. Research shows that neural networks "
                         "can exhibit emergent behaviors. The evidence indicates complexity leads to awareness.")
        
        claims = tracker.extract_claims_from_message(barbie_message, "Barbie")
        
        assert len(claims) >= 1
        assert any("consciousness is possible" in tracker.claims[cid].text for cid in claims)
    
    def test_response_analysis(self):
        """Test analyzing responses to claims"""
        tracker = DebateProgressionTracker()
        tracker.advance_round()
        
        # Add initial claim
        barbie_message = "I believe AI consciousness is possible through neural complexity."
        barbie_claims = tracker.extract_claims_from_message(barbie_message, "Barbie")
        
        tracker.advance_round()
        
        # Ken challenges the claim
        ken_message = "I disagree with the consciousness claim. What evidence supports this?"
        response_analysis = tracker.analyze_message_responses(ken_message, "Ken", barbie_claims)
        
        assert "challenges" in response_analysis
        assert response_analysis["speaker"] == "Ken"
    
    def test_rehashing_detection(self):
        """Test detection of rehashed claims"""
        tracker = DebateProgressionTracker()
        
        # Introduce claim multiple times
        claim_text = "AI consciousness requires neural complexity and emergence."
        
        for i in range(5):
            tracker.advance_round()
            tracker.extract_claims_from_message(claim_text, "Barbie")
        
        # Check rehashing detection
        rehash_warnings = tracker.detect_rehashing(claim_text)
        
        assert len(rehash_warnings) > 0
        assert any("excessive_rehash" in warning.get("status", "") for warning in rehash_warnings)
    
    def test_resolution_point_creation(self):
        """Test creating resolution points"""
        tracker = DebateProgressionTracker()
        tracker.advance_round()
        
        # Create a resolution
        resolution_id = tracker.create_resolution_point(
            "Neural networks can exhibit complex behaviors",
            ResolutionType.EVIDENCE_BASED,
            "Complexity indicates potential consciousness",
            "Complexity does not equal consciousness",
            agreed=True,
            evidence=["Studies on neural network emergence", "Complexity theory research"]
        )
        
        assert resolution_id in tracker.resolution_points
        assert tracker.resolution_points[resolution_id].agreed_by_both == True
        assert len(tracker.resolution_points[resolution_id].evidence_basis) == 2
    
    def test_progress_summary(self):
        """Test debate progress summarization"""
        tracker = DebateProgressionTracker()
        
        # Add some claims and resolutions
        tracker.advance_round()
        claims1 = tracker.extract_claims_from_message("I claim AI consciousness is possible.", "Barbie")
        
        tracker.advance_round() 
        claims2 = tracker.extract_claims_from_message("I challenge that assumption.", "Ken")
        
        # Create resolution
        tracker.create_resolution_point(
            "Definition of consciousness needs clarification",
            ResolutionType.DEFINITIONAL,
            "Consciousness as information processing",
            "Consciousness requires subjective experience",
            agreed=False
        )
        
        # Get progress summary
        summary = tracker.get_debate_progress_summary()
        
        assert "total_claims" in summary
        assert "resolution_points" in summary
        assert "progress_percentage" in summary
        assert summary["round"] == 2


class TestProgressionPromptGenerator:
    
    def test_progression_context_generation(self):
        """Test generating progression context"""
        tracker = DebateProgressionTracker()
        generator = ProgressionPromptGenerator(tracker)
        
        # Add some progression
        tracker.advance_round()
        tracker.extract_claims_from_message("AI systems can achieve consciousness.", "Barbie")
        
        tracker.advance_round()
        tracker.extract_claims_from_message("I disagree with consciousness claims.", "Ken")
        
        # Generate context
        context = generator.generate_progression_context("Barbie")
        
        assert "DEBATE PROGRESS STATUS" in context
        assert "Round" in context
        assert "Progress:" in context
    
    def test_barbie_progression_prompt(self):
        """Test generating progression-aware prompts for Barbie"""
        tracker = DebateProgressionTracker()
        generator = ProgressionPromptGenerator(tracker)
        
        # Simulate some debate progression
        tracker.advance_round()
        claims = tracker.extract_claims_from_message("Research shows AI consciousness is possible.", "Barbie")
        
        tracker.advance_round()
        ken_challenges = tracker.extract_claims_from_message("I challenge the research claims.", "Ken")
        
        # Generate enhanced prompt
        base_prompt = "You are Barbie, a creative AI agent."
        enhanced_prompt = generator.generate_barbie_progression_prompt(base_prompt)
        
        assert len(enhanced_prompt) > len(base_prompt)
        assert "DEBATE PROGRESS STATUS" in enhanced_prompt
        assert "PROGRESSION INSTRUCTIONS" in enhanced_prompt
    
    def test_ken_progression_prompt(self):
        """Test generating progression-aware prompts for Ken"""
        tracker = DebateProgressionTracker()
        generator = ProgressionPromptGenerator(tracker)
        
        # Add resolution point
        tracker.create_resolution_point(
            "AI complexity is measurable",
            ResolutionType.EVIDENCE_BASED,
            "Complexity metrics exist",
            "Metrics are insufficient",
            agreed=True
        )
        
        base_prompt = "You are Ken, an analytical AI agent."
        enhanced_prompt = generator.generate_ken_progression_prompt(base_prompt)
        
        assert "SETTLED AGREEMENTS" in enhanced_prompt
        assert "don't re-litigate" in enhanced_prompt
    
    def test_progression_summary_generation(self):
        """Test generating progression summaries"""
        tracker = DebateProgressionTracker()
        generator = ProgressionPromptGenerator(tracker)
        
        # Add some activity
        tracker.advance_round()
        tracker.extract_claims_from_message("Claims about AI safety.", "Barbie")
        
        tracker.create_resolution_point(
            "AI safety is important",
            ResolutionType.PRAGMATIC,
            "Safety measures needed",
            "Current measures sufficient",
            agreed=True
        )
        
        summary = generator.generate_progression_summary()
        
        assert "DEBATE PROGRESSION SUMMARY" in summary
        assert "Settled agreements:" in summary
        assert "AI safety is important" in summary


def test_integration_scenario():
    """Test complete integration scenario"""
    print("\n=== DEBATE PROGRESSION INTEGRATION TEST ===")
    
    # Initialize system
    tracker = DebateProgressionTracker()
    generator = ProgressionPromptGenerator(tracker)
    
    # Simulate a complete debate flow
    test_rounds = [
        ("Barbie", "I believe quantum computing will revolutionize AI development. "
                  "Research shows quantum advantages in machine learning algorithms."),
        
        ("Ken", "I challenge the quantum AI claims. What specific evidence supports "
               "quantum advantages? Current quantum computers are too noisy for practical AI."),
        
        ("Barbie", "Studies by IBM and Google demonstrate quantum speedups in optimization problems. "
                  "The evidence indicates quantum machine learning algorithms can outperform classical ones."),
        
        ("Ken", "I agree quantum optimization shows promise, but I question the generalizability. "
               "How do quantum algorithms handle real-world data with noise and errors?"),
        
        ("Barbie", "That's a fair point about noise. However, error correction advances are "
                  "addressing these issues. I agree we need more robust implementations.")
    ]
    
    print(f"Simulating {len(test_rounds)} rounds of debate...")
    
    for i, (speaker, message) in enumerate(test_rounds, 1):
        tracker.advance_round()
        print(f"\nRound {i}: {speaker}")
        
        # Extract claims
        claims = tracker.extract_claims_from_message(message, speaker)
        if claims:
            print(f"  Claims extracted: {len(claims)}")
        
        # Analyze responses (except first round)
        if i > 1:
            all_claims = list(tracker.claims.keys())
            analysis = tracker.analyze_message_responses(message, speaker, all_claims)
            if analysis['agreements']:
                print(f"  Agreements: {len(analysis['agreements'])}")
            if analysis['challenges']:
                print(f"  Challenges: {len(analysis['challenges'])}")
        
        # Check for rehashing
        rehash = tracker.detect_rehashing(message)
        if rehash:
            print(f"  Rehashing detected: {len(rehash)} issues")
    
    # Create resolution points based on the debate
    tracker.create_resolution_point(
        "Quantum optimization has advantages over classical methods",
        ResolutionType.EVIDENCE_BASED,
        "IBM and Google studies show speedups",
        "Advantages are demonstrated in specific cases",
        agreed=True,
        evidence=["IBM quantum optimization study", "Google quantum supremacy paper"]
    )
    
    tracker.create_resolution_point(
        "Quantum noise is a significant practical challenge",
        ResolutionType.EMPIRICAL,
        "Error correction advances will solve noise issues",
        "Current quantum systems too noisy for practical AI",
        agreed=False
    )
    
    # Final analysis
    print(f"\nFINAL ANALYSIS:")
    print("-" * 20)
    
    progress = tracker.get_debate_progress_summary()
    print(f"Progress: {progress['progress_percentage']:.1f}%")
    print(f"Total claims: {progress['total_claims']}")
    print(f"Settled claims: {progress['settled_claims']}")
    print(f"Active claims: {progress['active_claims']}")
    print(f"Resolution points: {progress['resolution_points']}")
    
    # Generate final prompts
    barbie_prompt = generator.generate_barbie_progression_prompt("You are Barbie.")
    ken_prompt = generator.generate_ken_progression_prompt("You are Ken.")
    
    print(f"\nBarbie prompt length: {len(barbie_prompt)} characters")
    print(f"Ken prompt length: {len(ken_prompt)} characters")
    
    # Check if prompts contain progression information
    assert "DEBATE PROGRESS STATUS" in barbie_prompt
    assert "DEBATE PROGRESS STATUS" in ken_prompt
    assert "SETTLED AGREEMENTS" in ken_prompt
    
    print(f"\n✅ Integration test passed!")
    print(f"✅ Debate progression tracking working correctly")
    print(f"✅ Resolution points created and tracked")
    print(f"✅ Progression-aware prompts generated")
    
    return True


if __name__ == "__main__":
    # Run integration test
    test_integration_scenario()
    print("\nDebate progression system ready for production!")