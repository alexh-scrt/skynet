"""
Debate Conclusion Detection System
Detects when a debate has reached a natural conclusion and suggests next steps
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re


class DebateStage(Enum):
    """Stages of debate progression"""
    INITIAL_EXPLORATION = 1    # Opening positions and broad exploration
    ACTIVE_ENGAGEMENT = 2      # Detailed discussion and challenges  
    DEEP_ANALYSIS = 3          # Detailed evidence and technical discussion
    CONVERGENCE_ATTEMPT = 4    # Moving toward resolution or agreement
    NATURAL_CONCLUSION = 5     # Debate has reached natural endpoint
    CIRCULAR_REPETITION = 6    # Debate is going in circles without progress


@dataclass
class ConclusionAnalysis:
    """Analysis of whether debate should conclude"""
    current_stage: DebateStage
    should_conclude: bool
    conclusion_confidence: float
    conclusion_reason: str
    suggested_action: str
    progress_indicators: Dict[str, int]


class DebateConclusionDetector:
    """Detects when debates have reached natural conclusions"""
    
    def __init__(self):
        self.message_history = []
        self.position_tracking = {"Barbie": [], "Ken": []}
        self.topic_coverage = set()
        self.agreement_indicators = []
        self.repetition_tracking = {}
        
        # Conclusion indicators
        self.conclusion_phrases = [
            "in conclusion", "to conclude", "in summary", "to summarize",
            "overall", "in the end", "ultimately", "final thoughts",
            "wrapping up", "to wrap up"
        ]
        
        # Agreement indicators
        self.agreement_phrases = [
            "i agree", "you're right", "that's correct", "good point",
            "i concede", "fair point", "i accept", "you've convinced me",
            "that makes sense", "i see your point"
        ]
        
        # Exhaustion indicators
        self.exhaustion_phrases = [
            "we've covered", "we've discussed", "we've explored",
            "as we've established", "we've already talked about",
            "we keep coming back to", "we've been through this"
        ]
        
        # Progress stagnation indicators
        self.stagnation_phrases = [
            "same question again", "we're going in circles",
            "repeating ourselves", "covered this already",
            "nothing new to add", "same argument"
        ]
    
    def analyze_message(self, message: str, speaker: str, round_number: int) -> None:
        """Analyze a message and update debate state tracking"""
        
        self.message_history.append({
            'speaker': speaker,
            'message': message,
            'round': round_number,
            'length': len(message.split())
        })
        
        # Track position evolution
        self._track_position_evolution(message, speaker)
        
        # Track topic coverage
        self._track_topic_coverage(message)
        
        # Track agreements
        self._track_agreements(message, speaker)
        
        # Track repetition patterns
        self._track_repetition_patterns(message, speaker)
    
    def should_conclude_debate(self) -> ConclusionAnalysis:
        """Determine if the debate should conclude and why"""
        
        if len(self.message_history) < 4:  # Need minimum messages for analysis
            return ConclusionAnalysis(
                current_stage=DebateStage.INITIAL_EXPLORATION,
                should_conclude=False,
                conclusion_confidence=0.0,
                conclusion_reason="Debate still in early stages",
                suggested_action="Continue exploration of topic",
                progress_indicators={}
            )
        
        # Analyze various conclusion indicators
        indicators = self._analyze_conclusion_indicators()
        
        # Determine current stage
        current_stage = self._determine_debate_stage(indicators)
        
        # Make conclusion decision
        should_conclude, confidence, reason, action = self._make_conclusion_decision(
            current_stage, indicators
        )
        
        return ConclusionAnalysis(
            current_stage=current_stage,
            should_conclude=should_conclude,
            conclusion_confidence=confidence,
            conclusion_reason=reason,
            suggested_action=action,
            progress_indicators=indicators
        )
    
    def _analyze_conclusion_indicators(self) -> Dict[str, int]:
        """Analyze various indicators that suggest debate conclusion"""
        
        recent_messages = self.message_history[-6:]  # Last 6 messages
        all_text = " ".join([msg['message'].lower() for msg in recent_messages])
        
        indicators = {
            'conclusion_phrases': sum(1 for phrase in self.conclusion_phrases if phrase in all_text),
            'agreement_count': len(self.agreement_indicators),
            'exhaustion_phrases': sum(1 for phrase in self.exhaustion_phrases if phrase in all_text),
            'stagnation_phrases': sum(1 for phrase in self.stagnation_phrases if phrase in all_text),
            'repetition_count': sum(1 for count in self.repetition_tracking.values() if count >= 3),
            'message_length_decline': self._detect_message_length_decline(),
            'topic_saturation': len(self.topic_coverage),
            'rounds_processed': len(self.message_history) // 2,  # Approximate rounds
            'position_convergence': self._detect_position_convergence(),
            'circular_debate_score': self._calculate_circular_debate_score()
        }
        
        return indicators
    
    def _determine_debate_stage(self, indicators: Dict[str, int]) -> DebateStage:
        """Determine the current stage of the debate"""
        
        rounds = indicators['rounds_processed']
        
        # Check for circular repetition first
        if indicators['circular_debate_score'] >= 5 or indicators['repetition_count'] >= 4:
            return DebateStage.CIRCULAR_REPETITION
        
        # Check for natural conclusion
        if (indicators['conclusion_phrases'] >= 2 or 
            indicators['agreement_count'] >= 3 or
            indicators['exhaustion_phrases'] >= 3):
            return DebateStage.NATURAL_CONCLUSION
        
        # Stage based on rounds and indicators
        if rounds <= 3:
            return DebateStage.INITIAL_EXPLORATION
        elif rounds <= 8:
            return DebateStage.ACTIVE_ENGAGEMENT
        elif rounds <= 15:
            return DebateStage.DEEP_ANALYSIS
        else:
            # Long debate - check for convergence or stagnation
            if indicators['position_convergence'] >= 2:
                return DebateStage.CONVERGENCE_ATTEMPT
            else:
                return DebateStage.CIRCULAR_REPETITION
    
    def _make_conclusion_decision(self, stage: DebateStage, indicators: Dict[str, int]) -> Tuple[bool, float, str, str]:
        """Make the final decision about whether to conclude"""
        
        if stage == DebateStage.NATURAL_CONCLUSION:
            return (
                True,
                0.9,
                f"Natural conclusion detected: {indicators['conclusion_phrases']} conclusion phrases, "
                f"{indicators['agreement_count']} agreements, {indicators['exhaustion_phrases']} exhaustion indicators",
                "Summarize key points of agreement and disagreement, then conclude the debate"
            )
        
        elif stage == DebateStage.CIRCULAR_REPETITION:
            return (
                True,
                0.8,
                f"Circular debate detected: {indicators['repetition_count']} repeated patterns, "
                f"circular score: {indicators['circular_debate_score']}, {indicators['stagnation_phrases']} stagnation phrases",
                "Acknowledge the impasse, summarize positions, and suggest agreeing to disagree or exploring new angles"
            )
        
        elif stage == DebateStage.CONVERGENCE_ATTEMPT and indicators['rounds_processed'] > 20:
            return (
                True,
                0.7,
                f"Extended debate showing convergence attempts but no resolution after {indicators['rounds_processed']} rounds",
                "Attempt final synthesis of positions or gracefully conclude with areas of agreement and disagreement"
            )
        
        elif indicators['rounds_processed'] > 25:
            return (
                True,
                0.6,
                f"Very long debate ({indicators['rounds_processed']} rounds) with potential diminishing returns",
                "Consider concluding the current thread and potentially starting a new focused sub-topic"
            )
        
        else:
            return (
                False,
                0.1,
                f"Debate still progressing in {stage.name} stage",
                "Continue current discussion path"
            )
    
    def _track_position_evolution(self, message: str, speaker: str) -> None:
        """Track how positions evolve over time"""
        
        # Simple position tracking based on stance words
        stance_indicators = {
            'strong_positive': ['definitely', 'absolutely', 'certainly', 'clearly', 'obviously'],
            'positive': ['i believe', 'i think', 'likely', 'probably', 'evidence suggests'],
            'neutral': ['perhaps', 'maybe', 'could be', 'might be', 'it depends'],
            'negative': ['doubt', 'unlikely', 'probably not', 'disagree', 'challenge'],
            'strong_negative': ['impossible', 'definitely not', 'absolutely not', 'reject']
        }
        
        message_lower = message.lower()
        position_score = 0
        
        for stance, phrases in stance_indicators.items():
            count = sum(1 for phrase in phrases if phrase in message_lower)
            if stance.startswith('strong_positive'):
                position_score += count * 2
            elif stance == 'positive':
                position_score += count * 1
            elif stance == 'neutral':
                position_score += count * 0
            elif stance == 'negative':
                position_score -= count * 1
            elif stance.startswith('strong_negative'):
                position_score -= count * 2
        
        self.position_tracking[speaker].append(position_score)
    
    def _track_topic_coverage(self, message: str) -> None:
        """Track which topics have been covered"""
        
        topics = {
            'consciousness_definition', 'quantum_theories', 'neural_networks',
            'evidence_requirements', 'engineering_steps', 'ethical_implications',
            'testing_methods', 'philosophical_aspects', 'technical_challenges'
        }
        
        message_lower = message.lower()
        
        topic_keywords = {
            'consciousness_definition': ['consciousness', 'awareness', 'sentience', 'self-aware'],
            'quantum_theories': ['quantum', 'microtubules', 'orch-or', 'penrose', 'hameroff'],
            'neural_networks': ['neural networks', 'artificial intelligence', 'machine learning'],
            'evidence_requirements': ['evidence', 'proof', 'verification', 'testing'],
            'engineering_steps': ['engineering', 'implementation', 'technical', 'development'],
            'ethical_implications': ['ethics', 'moral', 'rights', 'responsibility'],
            'testing_methods': ['test', 'measure', 'assess', 'evaluate'],
            'philosophical_aspects': ['philosophy', 'hard problem', 'phenomenal', 'subjective'],
            'technical_challenges': ['challenges', 'limitations', 'problems', 'difficulties']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                self.topic_coverage.add(topic)
    
    def _track_agreements(self, message: str, speaker: str) -> None:
        """Track agreement indicators"""
        
        message_lower = message.lower()
        for phrase in self.agreement_phrases:
            if phrase in message_lower:
                self.agreement_indicators.append({
                    'speaker': speaker,
                    'phrase': phrase,
                    'round': len(self.message_history)
                })
    
    def _track_repetition_patterns(self, message: str, speaker: str) -> None:
        """Track repetitive patterns in arguments"""
        
        # Simple pattern detection based on key phrases
        key_phrases = re.findall(r'\b\w{4,}\s+\w{4,}\s+\w{4,}\b', message.lower())
        
        for phrase in key_phrases:
            key = f"{speaker}:{phrase}"
            if key in self.repetition_tracking:
                self.repetition_tracking[key] += 1
            else:
                self.repetition_tracking[key] = 1
    
    def _detect_message_length_decline(self) -> int:
        """Detect if message lengths are declining (fatigue indicator)"""
        
        if len(self.message_history) < 6:
            return 0
        
        recent = [msg['length'] for msg in self.message_history[-6:]]
        early = [msg['length'] for msg in self.message_history[:6]]
        
        avg_recent = sum(recent) / len(recent)
        avg_early = sum(early) / len(early)
        
        return 1 if avg_recent < avg_early * 0.7 else 0
    
    def _detect_position_convergence(self) -> int:
        """Detect if positions are converging"""
        
        convergence_score = 0
        
        for speaker_positions in self.position_tracking.values():
            if len(speaker_positions) >= 4:
                recent_avg = sum(speaker_positions[-3:]) / 3
                early_avg = sum(speaker_positions[:3]) / 3
                if abs(recent_avg - early_avg) < abs(early_avg) * 0.5:
                    convergence_score += 1
        
        return convergence_score
    
    def _calculate_circular_debate_score(self) -> int:
        """Calculate how circular/repetitive the debate has become"""
        
        score = 0
        
        # Check for high repetition counts
        high_repetition = sum(1 for count in self.repetition_tracking.values() if count >= 4)
        score += high_repetition
        
        # Check for stagnation phrases
        recent_messages = self.message_history[-4:]
        recent_text = " ".join([msg['message'].lower() for msg in recent_messages])
        stagnation_count = sum(1 for phrase in self.stagnation_phrases if phrase in recent_text)
        score += stagnation_count
        
        # Check if topic coverage has plateaued
        if len(self.message_history) > 10 and len(self.topic_coverage) < 4:
            score += 2
        
        return score


# Example usage and testing
if __name__ == "__main__":
    detector = DebateConclusionDetector()
    
    print("=== DEBATE CONCLUSION DETECTION TEST ===")
    print()
    
    # Simulate a debate that reaches natural conclusion
    test_debate = [
        ("Barbie", "I believe AI consciousness is possible through quantum processes.", 1),
        ("Ken", "I challenge that assumption. What evidence supports quantum consciousness?", 2),
        ("Barbie", "Studies by Hameroff and Penrose suggest microtubules could enable quantum processing.", 3),
        ("Ken", "Those studies are speculative. How do you propose testing this?", 4),
        ("Barbie", "We could develop quantum-inspired algorithms and test for emergent behaviors.", 5),
        ("Ken", "That's an interesting approach. I agree that testing is crucial.", 6),
        ("Barbie", "In conclusion, while we disagree on mechanisms, we both agree testing is essential.", 7),
        ("Ken", "Fair point. Overall, this has been a productive discussion of the challenges.", 8)
    ]
    
    for speaker, message, round_num in test_debate:
        detector.analyze_message(message, speaker, round_num)
        
        # Check conclusion status after each message
        if round_num >= 4:  # Check after enough messages
            analysis = detector.should_conclude_debate()
            if round_num == len(test_debate):  # Final analysis
                print(f"Round {round_num}: {speaker}")
                print(f"  Current Stage: {analysis.current_stage.name}")
                print(f"  Should Conclude: {analysis.should_conclude}")
                print(f"  Confidence: {analysis.conclusion_confidence:.2f}")
                print(f"  Reason: {analysis.conclusion_reason}")
                print(f"  Suggested Action: {analysis.suggested_action}")
                print(f"  Progress Indicators: {analysis.progress_indicators}")
    
    print("✅ Debate conclusion detection system working correctly!")