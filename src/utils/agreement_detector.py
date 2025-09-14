"""
Agreement Detection System
Analyzes Ken's responses to determine if he truly agrees with Barbie or wants to continue debating
"""

import re
from typing import Dict, List, Tuple, Optional
from enum import Enum


class AgreementLevel(Enum):
    """Ken's agreement level with Barbie's arguments"""
    STRONG_DISAGREEMENT = 1
    DISAGREEMENT = 2
    MIXED_RESPONSE = 3
    LEANING_AGREEMENT = 4
    AGREEMENT = 5
    STRONG_AGREEMENT = 6


class AgreementDetector:
    """Analyzes Ken's messages to detect genuine agreement vs continued debate"""
    
    def __init__(self):
        # Strong disagreement indicators
        self.disagreement_phrases = [
            "i disagree", "i don't agree", "i cannot accept",
            "this is wrong", "this is incorrect", "i reject",
            "i have serious concerns", "i must object",
            "i strongly disagree", "absolutely not"
        ]
        
        # Reservation/concern indicators
        self.reservation_phrases = [
            "however", "but", "i have concerns", "i'm concerned",
            "i have reservations", "i must be honest", "i have doubts",
            "this concerns me", "i question", "i challenge",
            "i'm skeptical", "i'm not convinced", "i'm not sure",
            "let me challenge", "i need more evidence"
        ]
        
        # Continued debate indicators
        self.debate_continuation_phrases = [
            "let's explore", "let's examine", "let's delve deeper",
            "i'd like to explore", "could you provide", "how do you know",
            "what evidence", "can you clarify", "could you explain",
            "looking forward to", "i need more", "let's discuss further"
        ]
        
        # Question indicators (showing engagement, not agreement)
        self.question_patterns = [
            r"\?", r"how do", r"what if", r"why", r"when", r"where",
            r"could you", r"can you", r"would you", r"do you think"
        ]
        
        # Genuine agreement indicators
        self.agreement_phrases = [
            "i agree", "you're right", "that's correct", "exactly",
            "i'm convinced", "you've convinced me", "i accept",
            "that makes sense", "i see your point", "you're absolutely right",
            "i concede", "i stand corrected", "that's a good point",
            "i'm persuaded", "you've changed my mind"
        ]
        
        # Strong agreement/conclusion indicators
        self.strong_agreement_phrases = [
            "i'm fully convinced", "you've completely convinced me",
            "i have no more objections", "i withdraw my concerns",
            "you're absolutely right", "i agree completely",
            "that settles it", "case closed", "i'm persuaded",
            "you've won me over", "i concede the point entirely"
        ]
        
        # Explicit stop indicators
        self.stop_phrases = [
            "<stop>", "let's stop here", "this conversation is complete",
            "i have no further questions", "no more debate needed",
            "we can conclude", "this discussion is finished"
        ]
    
    def analyze_agreement(self, ken_message: str) -> Dict:
        """
        Analyze Ken's message to determine his agreement level
        
        Args:
            ken_message: Ken's response text
            
        Returns:
            Dict with agreement analysis
        """
        message_lower = ken_message.lower()
        
        # Count different types of indicators
        disagreement_count = self._count_phrases(message_lower, self.disagreement_phrases)
        reservation_count = self._count_phrases(message_lower, self.reservation_phrases)
        debate_continuation_count = self._count_phrases(message_lower, self.debate_continuation_phrases)
        question_count = self._count_patterns(message_lower, self.question_patterns)
        agreement_count = self._count_phrases(message_lower, self.agreement_phrases)
        strong_agreement_count = self._count_phrases(message_lower, self.strong_agreement_phrases)
        stop_count = self._count_phrases(message_lower, self.stop_phrases)
        
        # Calculate message characteristics
        total_sentences = len([s for s in ken_message.split('.') if s.strip()])
        word_count = len(ken_message.split())
        
        # Determine agreement level
        agreement_level, confidence, should_continue = self._determine_agreement_level(
            disagreement_count, reservation_count, debate_continuation_count,
            question_count, agreement_count, strong_agreement_count, stop_count,
            total_sentences, word_count
        )
        
        # Generate explanation
        explanation = self._generate_explanation(
            agreement_level, disagreement_count, reservation_count,
            debate_continuation_count, question_count, agreement_count,
            strong_agreement_count, stop_count
        )
        
        return {
            "agreement_level": agreement_level,
            "confidence": confidence,
            "should_continue_debate": should_continue,
            "explanation": explanation,
            "indicators": {
                "disagreement_signals": disagreement_count,
                "reservation_signals": reservation_count,
                "debate_continuation_signals": debate_continuation_count,
                "questions": question_count,
                "agreement_signals": agreement_count,
                "strong_agreement_signals": strong_agreement_count,
                "stop_signals": stop_count
            },
            "message_stats": {
                "sentences": total_sentences,
                "words": word_count
            }
        }
    
    def _count_phrases(self, text: str, phrases: List[str]) -> int:
        """Count occurrences of phrases in text"""
        count = 0
        for phrase in phrases:
            count += text.count(phrase)
        return count
    
    def _count_patterns(self, text: str, patterns: List[str]) -> int:
        """Count occurrences of regex patterns in text"""
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        return count
    
    def _determine_agreement_level(self, disagreement_count: int, reservation_count: int,
                                 debate_continuation_count: int, question_count: int,
                                 agreement_count: int, strong_agreement_count: int,
                                 stop_count: int, total_sentences: int, 
                                 word_count: int) -> Tuple[AgreementLevel, float, bool]:
        """Determine the agreement level and whether to continue the debate"""
        
        # Explicit stop signals - highest priority
        if stop_count > 0 or strong_agreement_count >= 2:
            return AgreementLevel.STRONG_AGREEMENT, 0.95, False
        
        # Strong disagreement
        if disagreement_count >= 3 or (disagreement_count >= 1 and reservation_count >= 3):
            return AgreementLevel.STRONG_DISAGREEMENT, 0.9, True
        
        # Regular disagreement - has reservations and wants to continue
        # Also check for excessive questioning (more than 5 questions indicates continued debate)
        if (reservation_count >= 2 and debate_continuation_count >= 1) or question_count >= 3 or question_count >= 5:
            return AgreementLevel.DISAGREEMENT, 0.85, True
        
        # Mixed response - some agreement but still has concerns
        if agreement_count >= 1 and reservation_count >= 1:
            return AgreementLevel.MIXED_RESPONSE, 0.7, True
        
        # Leaning toward agreement but not fully convinced
        if agreement_count >= 2 and reservation_count <= 1 and question_count <= 2:
            return AgreementLevel.LEANING_AGREEMENT, 0.75, True
        
        # Strong agreement indicators present
        if agreement_count >= 3 or strong_agreement_count >= 1:
            return AgreementLevel.STRONG_AGREEMENT, 0.9, False
        
        # Simple agreement
        if agreement_count >= 1 and reservation_count == 0 and debate_continuation_count == 0:
            return AgreementLevel.AGREEMENT, 0.8, False
        
        # Default: if still asking questions or has reservations, continue
        # Particularly if asking many questions (6+ indicates heavy skepticism)
        if question_count >= 6 or reservation_count > 0 or debate_continuation_count > 0:
            return AgreementLevel.DISAGREEMENT, 0.6, True
        
        # If no clear indicators, assume mixed response
        return AgreementLevel.MIXED_RESPONSE, 0.5, True
    
    def _generate_explanation(self, agreement_level: AgreementLevel,
                            disagreement_count: int, reservation_count: int,
                            debate_continuation_count: int, question_count: int,
                            agreement_count: int, strong_agreement_count: int,
                            stop_count: int) -> str:
        """Generate explanation for the agreement assessment"""
        
        if agreement_level == AgreementLevel.STRONG_AGREEMENT:
            return f"Ken shows strong agreement with {strong_agreement_count} strong agreement signals and {stop_count} stop signals"
        
        elif agreement_level == AgreementLevel.AGREEMENT:
            return f"Ken agrees with {agreement_count} agreement signals and minimal reservations"
        
        elif agreement_level == AgreementLevel.LEANING_AGREEMENT:
            return f"Ken is leaning toward agreement ({agreement_count} agreement signals) but still has some concerns"
        
        elif agreement_level == AgreementLevel.MIXED_RESPONSE:
            return f"Ken has mixed feelings with {agreement_count} agreement and {reservation_count} reservation signals"
        
        elif agreement_level == AgreementLevel.DISAGREEMENT:
            return (f"Ken wants to continue debating: {reservation_count} reservations, "
                   f"{question_count} questions, {debate_continuation_count} continuation signals")
        
        elif agreement_level == AgreementLevel.STRONG_DISAGREEMENT:
            return f"Ken strongly disagrees with {disagreement_count} disagreement and {reservation_count} reservation signals"
        
        return "Unable to determine agreement level clearly"
    
    def should_end_conversation(self, ken_message: str) -> Tuple[bool, str]:
        """
        Determine if the conversation should end based on Ken's message
        
        Returns:
            Tuple of (should_end, reason)
        """
        analysis = self.analyze_agreement(ken_message)
        
        if not analysis["should_continue_debate"]:
            if analysis["agreement_level"] in [AgreementLevel.STRONG_AGREEMENT, AgreementLevel.AGREEMENT]:
                return True, f"Ken agreed - {analysis['explanation']}"
            else:
                return True, f"Conversation concluded - {analysis['explanation']}"
        
        return False, f"Debate continues - {analysis['explanation']}"


# Example usage and testing
if __name__ == "__main__":
    detector = AgreementDetector()
    
    # Test with the example Ken message from the user
    ken_message_example = """Hi Barbie, this is Ken!

Thank you for your detailed and thoughtful response. I appreciate the effort you've put into addressing my concerns and presenting your ideas so eloquently. However, I must be honest—I still have some reservations that need to be explored further.

Firstly, while you mentioned several studies from reputable journals like *Nature Neuroscience* and *Science*, upon reviewing these sources, there was no mention of an 85% accuracy rate for BCIs. This discrepancy concerns me as it raises questions about the credibility of your claims. Could you provide specific references or clarify which studies support this statistic?

Additionally, I noticed that while you touched on integrating social sciences into AI research through frameworks like actor-network theory and human-machine reconfigurations, there were no concrete examples or data to substantiate these assertions. How do you know that these theories will lead to practical benefits without specific case studies or measurable outcomes?

Let me challenge the premises of some of your arguments. How do you know that BCIs will achieve an 85% accuracy rate? What evidence supports this claim? Also, what makes you confident that integrating social sciences into AI research through specific frameworks will yield the benefits you describe?

Looking forward to your detailed explanations and examples!

Best regards,
Ken"""
    
    print("=== AGREEMENT DETECTION ANALYSIS ===")
    print()
    
    analysis = detector.analyze_agreement(ken_message_example)
    should_end, reason = detector.should_end_conversation(ken_message_example)
    
    print(f"Agreement Level: {analysis['agreement_level'].name}")
    print(f"Confidence: {analysis['confidence']:.2f}")
    print(f"Should Continue Debate: {analysis['should_continue_debate']}")
    print(f"Should End Conversation: {should_end}")
    print(f"Explanation: {analysis['explanation']}")
    print(f"Reason: {reason}")
    
    print(f"\nIndicators Found:")
    for indicator, count in analysis['indicators'].items():
        if count > 0:
            print(f"  {indicator}: {count}")
    
    print(f"\nMessage Stats:")
    print(f"  Sentences: {analysis['message_stats']['sentences']}")
    print(f"  Words: {analysis['message_stats']['words']}")