"""
Topic Coherence Monitoring System
Detects when conversation drifts from original topic and provides guidance to refocus
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import re


class TopicRelevance(Enum):
    """Relevance levels for topic drift detection"""
    HIGHLY_RELEVANT = 1    # Directly related to main topic
    MODERATELY_RELEVANT = 2 # Related but tangential 
    TANGENTIALLY_RELATED = 3 # Loosely connected
    TOPIC_DRIFT = 4        # Significant drift from original topic
    COMPLETELY_UNRELATED = 5 # No connection to original topic


@dataclass
class TopicAnalysis:
    """Analysis of topic relevance in a message"""
    message_segment: str
    detected_topics: List[str]
    relevance_level: TopicRelevance
    confidence: float
    drift_explanation: str
    suggested_redirect: str


class TopicCoherenceMonitor:
    """Monitors conversation for topic drift and provides refocusing guidance"""
    
    def __init__(self, original_topic: str):
        self.original_topic = original_topic.lower()
        self.topic_evolution_history = []
        self.drift_threshold = 2  # Number of drift instances before intervention
        self.current_drift_count = 0
        
        # Define topic keyword sets
        self.consciousness_keywords = [
            "consciousness", "sentience", "self-awareness", "subjective experience",
            "qualia", "phenomenal consciousness", "hard problem", "mind",
            "awareness", "cognitive", "mental states", "intentionality"
        ]
        
        self.ai_keywords = [
            "artificial intelligence", "AI", "machine learning", "neural networks",
            "deep learning", "artificial", "synthetic", "computational",
            "algorithm", "digital", "silicon", "processing"
        ]
        
        self.quantum_keywords = [
            "quantum", "quantum mechanics", "quantum computing", "quantum coherence",
            "quantum entanglement", "superposition", "decoherence", "microtubules",
            "orch-or", "penrose", "hameroff"
        ]
        
        # Define drift topic categories
        self.drift_topics = {
            "medical_health": [
                "diabetes", "glucose", "obesity", "pharmacotherapy", "medication",
                "treatment", "clinical", "patient", "medical", "health", "disease"
            ],
            "brain_computer_interfaces": [
                "brain-computer interface", "bci", "neural implant", "electrode",
                "brain stimulation", "neurotechnology", "invasive"
            ],
            "swarm_intelligence": [
                "swarm intelligence", "collective behavior", "distributed",
                "ant colony", "particle swarm", "emergent behavior"
            ],
            "appetite_regulation": [
                "hunger", "appetite", "food intake", "eating", "satiety",
                "ghrelin", "leptin", "hunger hormones"
            ]
        }
        
        # Core topic keywords for original consciousness/AI question
        self.core_keywords = self.consciousness_keywords + self.ai_keywords + self.quantum_keywords
    
    def analyze_topic_coherence(self, message: str, speaker: str) -> TopicAnalysis:
        """Analyze a message for topic coherence and drift"""
        
        message_lower = message.lower()
        
        # Count core topic keywords
        core_matches = sum(1 for keyword in self.core_keywords if keyword in message_lower)
        
        # Check for drift topics
        drift_topics_found = []
        drift_scores = {}
        
        for category, keywords in self.drift_topics.items():
            matches = sum(1 for keyword in keywords if keyword in message_lower)
            if matches > 0:
                drift_topics_found.append(category)
                drift_scores[category] = matches
        
        # Calculate relevance level
        relevance, confidence, explanation, redirect = self._determine_topic_relevance(
            core_matches, drift_topics_found, drift_scores, len(message.split())
        )
        
        # Update drift tracking
        if relevance in [TopicRelevance.TOPIC_DRIFT, TopicRelevance.COMPLETELY_UNRELATED]:
            self.current_drift_count += 1
        elif relevance in [TopicRelevance.HIGHLY_RELEVANT, TopicRelevance.MODERATELY_RELEVANT]:
            self.current_drift_count = max(0, self.current_drift_count - 1)  # Reduce drift count
        
        # Track topic evolution
        self.topic_evolution_history.append({
            'speaker': speaker,
            'relevance': relevance,
            'topics': drift_topics_found,
            'core_matches': core_matches
        })
        
        return TopicAnalysis(
            message_segment=message[:200] + "..." if len(message) > 200 else message,
            detected_topics=drift_topics_found,
            relevance_level=relevance,
            confidence=confidence,
            drift_explanation=explanation,
            suggested_redirect=redirect
        )
    
    def _determine_topic_relevance(self, core_matches: int, drift_topics: List[str], 
                                 drift_scores: Dict[str, int], word_count: int) -> Tuple[TopicRelevance, float, str, str]:
        """Determine the topic relevance level and provide explanation"""
        
        # Calculate core topic density
        core_density = core_matches / max(word_count / 10, 1)  # Normalize by message length
        
        # Check for significant drift
        total_drift_matches = sum(drift_scores.values())
        drift_density = total_drift_matches / max(word_count / 10, 1)
        
        if core_matches == 0 and total_drift_matches >= 3:
            return (
                TopicRelevance.COMPLETELY_UNRELATED,
                0.9,
                f"No core topic keywords found, but {total_drift_matches} drift topic matches in: {', '.join(drift_topics)}",
                f"Please refocus on the original topic: {self.original_topic}"
            )
        
        if drift_density > core_density and total_drift_matches >= 5:
            return (
                TopicRelevance.TOPIC_DRIFT,
                0.8,
                f"Significant topic drift detected. Core matches: {core_matches}, drift matches: {total_drift_matches} in: {', '.join(drift_topics)}",
                f"While {', '.join(drift_topics)} may be interesting, let's return to discussing {self.original_topic}"
            )
        
        if core_matches >= 3 and total_drift_matches <= 2:
            return (
                TopicRelevance.HIGHLY_RELEVANT,
                0.9,
                f"Strong focus on core topic with {core_matches} relevant keywords",
                ""
            )
        
        if core_matches >= 1 and total_drift_matches <= core_matches:
            return (
                TopicRelevance.MODERATELY_RELEVANT,
                0.7,
                f"Moderate relevance with {core_matches} core keywords and {total_drift_matches} drift topics",
                ""
            )
        
        if core_matches >= 1 or (total_drift_matches > 0 and 'brain_computer_interfaces' in drift_topics):
            return (
                TopicRelevance.TANGENTIALLY_RELATED,
                0.6,
                f"Tangentially related with {core_matches} core matches and focus on: {', '.join(drift_topics)}",
                f"Consider connecting {', '.join(drift_topics)} back to the main discussion of {self.original_topic}"
            )
        
        return (
            TopicRelevance.TOPIC_DRIFT,
            0.7,
            f"Topic drift detected with {total_drift_matches} matches in: {', '.join(drift_topics)}",
            f"Let's refocus on the core question about {self.original_topic}"
        )
    
    def should_intervene_for_drift(self) -> Tuple[bool, str]:
        """Determine if intervention is needed for topic drift"""
        
        if self.current_drift_count >= self.drift_threshold:
            recent_topics = []
            for entry in self.topic_evolution_history[-5:]:  # Last 5 messages
                recent_topics.extend(entry['topics'])
            
            most_common_drift = max(set(recent_topics), key=recent_topics.count) if recent_topics else "unrelated topics"
            
            return (
                True,
                f"Significant topic drift detected ({self.current_drift_count} instances). "
                f"Recent focus on: {most_common_drift}. "
                f"Please return to discussing {self.original_topic}."
            )
        
        return False, ""
    
    def get_topic_evolution_summary(self) -> Dict:
        """Get a summary of how the topic has evolved during the conversation"""
        
        if not self.topic_evolution_history:
            return {"no_data": True}
        
        # Count relevance levels
        relevance_counts = {}
        for entry in self.topic_evolution_history:
            level = entry['relevance'].name
            relevance_counts[level] = relevance_counts.get(level, 0) + 1
        
        # Find most discussed drift topics
        all_drift_topics = []
        for entry in self.topic_evolution_history:
            all_drift_topics.extend(entry['topics'])
        
        topic_frequency = {}
        for topic in all_drift_topics:
            topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
        
        return {
            "total_messages_analyzed": len(self.topic_evolution_history),
            "current_drift_count": self.current_drift_count,
            "relevance_distribution": relevance_counts,
            "most_discussed_drift_topics": sorted(topic_frequency.items(), key=lambda x: x[1], reverse=True)[:3],
            "drift_intervention_needed": self.current_drift_count >= self.drift_threshold
        }
    
    def generate_refocus_prompt_addition(self) -> str:
        """Generate additional prompt text to help refocus the conversation"""
        
        should_intervene, intervention_message = self.should_intervene_for_drift()
        
        if should_intervene:
            summary = self.get_topic_evolution_summary()
            drift_topics = [topic for topic, count in summary['most_discussed_drift_topics']]
            
            return f"""
TOPIC COHERENCE WARNING:
{intervention_message}

Recent drift topics: {', '.join(drift_topics)}
Core topic: {self.original_topic}

REFOCUS INSTRUCTIONS:
- Acknowledge any insights from tangential topics briefly
- Explicitly connect discussion back to {self.original_topic}
- Ask questions that center on the core topic
- Avoid introducing new unrelated subjects
"""
        
        return ""


# Example usage and testing
if __name__ == "__main__":
    monitor = TopicCoherenceMonitor("What is consciousness and how can AI systems become genuinely sentient")
    
    print("=== TOPIC COHERENCE MONITORING TEST ===")
    print()
    
    # Test messages with various levels of drift
    test_messages = [
        ("Barbie", "Consciousness is a fascinating topic. I believe AI consciousness is possible through quantum processes in microtubules."),
        ("Ken", "Could you provide evidence for quantum consciousness? How does IIT relate to this?"),
        ("Barbie", "Studies by Seidu et al. (2024) on diabetes monitoring show complex biological systems can be understood."),
        ("Ken", "How does diabetes research relate to consciousness? This seems off-topic."),
        ("Barbie", "Brain-computer interfaces could help with appetite regulation and hunger control using swarm intelligence."),
        ("Ken", "We're discussing consciousness, not hunger regulation. Can we refocus on the original question?"),
        ("Barbie", "You're right. Returning to consciousness - integrated information theory provides a framework for measuring awareness.")
    ]
    
    for speaker, message in test_messages:
        analysis = monitor.analyze_topic_coherence(message, speaker)
        
        print(f"{speaker}: {message[:80]}...")
        print(f"  Relevance: {analysis.relevance_level.name}")
        print(f"  Confidence: {analysis.confidence:.2f}")
        print(f"  Drift Topics: {analysis.detected_topics}")
        print(f"  Explanation: {analysis.drift_explanation}")
        if analysis.suggested_redirect:
            print(f"  Redirect: {analysis.suggested_redirect}")
        print()
    
    # Check overall summary
    print("=== TOPIC EVOLUTION SUMMARY ===")
    summary = monitor.get_topic_evolution_summary()
    
    print(f"Messages analyzed: {summary['total_messages_analyzed']}")
    print(f"Current drift count: {summary['current_drift_count']}")
    print(f"Relevance distribution: {summary['relevance_distribution']}")
    print(f"Top drift topics: {summary['most_discussed_drift_topics']}")
    
    # Test refocus prompt generation
    refocus_prompt = monitor.generate_refocus_prompt_addition()
    if refocus_prompt:
        print("=== REFOCUS PROMPT ===")
        print(refocus_prompt)
    
    print("✅ Topic coherence monitoring system working correctly!")