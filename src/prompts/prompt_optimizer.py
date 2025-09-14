"""
Prompt Optimization and Dynamic Selection
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum
import random


class DebatePhase(Enum):
    OPENING = "opening"
    EXPLORATION = "exploration"
    CHALLENGE = "challenge"
    SYNTHESIS = "synthesis"
    CONCLUSION = "conclusion"


class DebateTone(Enum):
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    PROVOCATIVE = "provocative"
    COLLABORATIVE = "collaborative"
    COMPETITIVE = "competitive"


class PromptOptimizer:
    """Dynamically optimizes prompts based on conversation state"""
    
    def __init__(self):
        self.phase_transitions = {
            DebatePhase.OPENING: [DebatePhase.EXPLORATION, DebatePhase.CHALLENGE],
            DebatePhase.EXPLORATION: [DebatePhase.CHALLENGE, DebatePhase.SYNTHESIS],
            DebatePhase.CHALLENGE: [DebatePhase.EXPLORATION, DebatePhase.SYNTHESIS],
            DebatePhase.SYNTHESIS: [DebatePhase.CONCLUSION, DebatePhase.EXPLORATION],
            DebatePhase.CONCLUSION: [DebatePhase.OPENING]  # New topic
        }
        
    def determine_phase(self, turn_number: int, resolution_rate: float, 
                       dispute_rate: float) -> DebatePhase:
        """Determine current debate phase based on metrics"""
        
        if turn_number <= 2:
            return DebatePhase.OPENING
        elif turn_number <= 5 and dispute_rate < 0.3:
            return DebatePhase.EXPLORATION
        elif dispute_rate > 0.5:
            return DebatePhase.CHALLENGE
        elif resolution_rate > 0.6:
            return DebatePhase.SYNTHESIS
        elif turn_number > 10 and resolution_rate > 0.4:
            return DebatePhase.CONCLUSION
        else:
            return DebatePhase.EXPLORATION
    
    def select_tone(self, agent: str, phase: DebatePhase, 
                    agreement_level: float) -> DebateTone:
        """Select appropriate tone based on phase and agreement"""
        
        tone_matrix = {
            DebatePhase.OPENING: {
                "Barbie": DebateTone.CREATIVE,
                "Ken": DebateTone.ANALYTICAL
            },
            DebatePhase.EXPLORATION: {
                "Barbie": DebateTone.PROVOCATIVE if agreement_level > 0.7 else DebateTone.CREATIVE,
                "Ken": DebateTone.ANALYTICAL if agreement_level < 0.5 else DebateTone.PROVOCATIVE
            },
            DebatePhase.CHALLENGE: {
                "Barbie": DebateTone.COMPETITIVE,
                "Ken": DebateTone.COMPETITIVE
            },
            DebatePhase.SYNTHESIS: {
                "Barbie": DebateTone.COLLABORATIVE,
                "Ken": DebateTone.COLLABORATIVE
            },
            DebatePhase.CONCLUSION: {
                "Barbie": DebateTone.COLLABORATIVE,
                "Ken": DebateTone.ANALYTICAL
            }
        }
        
        return tone_matrix.get(phase, {}).get(agent, DebateTone.ANALYTICAL)
    
    def generate_phase_instruction(self, phase: DebatePhase, tone: DebateTone) -> str:
        """Generate specific instructions for current phase and tone"""
        
        instructions = {
            (DebatePhase.OPENING, DebateTone.CREATIVE): 
                "Start with an unexpected angle or fascinating paradox. Make them think differently.",
            (DebatePhase.OPENING, DebateTone.ANALYTICAL): 
                "Establish clear definitions and logical framework. Set rigorous standards.",
            
            (DebatePhase.EXPLORATION, DebateTone.CREATIVE): 
                "Explore implications through analogies and thought experiments. Connect disparate ideas.",
            (DebatePhase.EXPLORATION, DebateTone.PROVOCATIVE): 
                "Challenge comfortable assumptions. Present uncomfortable truths or scenarios.",
            
            (DebatePhase.CHALLENGE, DebateTone.COMPETITIVE): 
                "Identify the weakest link in their argument chain. Demand evidence and rigor.",
            
            (DebatePhase.SYNTHESIS, DebateTone.COLLABORATIVE): 
                "Find the truth in both perspectives. Build a richer understanding together.",
            
            (DebatePhase.CONCLUSION, DebateTone.COLLABORATIVE): 
                "Summarize insights gained. Identify remaining questions and future directions.",
            (DebatePhase.CONCLUSION, DebateTone.ANALYTICAL): 
                "Evaluate which claims were supported. Assess the strength of conclusions reached."
        }
        
        return instructions.get((phase, tone), 
                               "Engage thoughtfully with precision and creativity.")
    
    def inject_variety(self, agent: str, previous_responses: List[str]) -> str:
        """Inject variety to prevent repetitive patterns"""
        
        variety_injections = {
            "Barbie": [
                "Try a completely different disciplinary lens this time.",
                "What would a child ask about this? What would an alien assume?",
                "Find the hidden beauty or elegance in this problem.",
                "What would happen if we inverted our assumptions?",
                "Connect this to a personal or emotional dimension."
            ],
            "Ken": [
                "Apply a different analytical framework this round.",
                "What are the statistical or probabilistic implications?",
                "Identify the cognitive biases at play here.",
                "What would a rigorous experiment look like?",
                "Consider the economic or game-theoretic perspective."
            ]
        }
        
        # Avoid recent patterns
        if len(previous_responses) >= 3:
            if all("however" in r.lower() for r in previous_responses[-3:]):
                return "Avoid 'however' - use different transition: 'That said', 'Interestingly', 'Note that'"
            if all(len(r) > 1000 for r in previous_responses[-3:]):
                return "Be more concise. Make your point in half the words."
            if all(len(r) < 200 for r in previous_responses[-3:]):
                return "Develop your ideas more fully. Add depth and nuance."
        
        return random.choice(variety_injections.get(agent, [""]))
    
    def suggest_rhetorical_device(self, agent: str, phase: DebatePhase) -> str:
        """Suggest a rhetorical device appropriate for the phase"""
        
        devices = {
            "Barbie": {
                DebatePhase.OPENING: "Use a striking analogy or pose a thought experiment",
                DebatePhase.EXPLORATION: "Build a cascade of implications - if X then Y then Z",
                DebatePhase.CHALLENGE: "Reframe their argument in a way that reveals new dimensions",
                DebatePhase.SYNTHESIS: "Find an elegant synthesis that transcends the dichotomy",
                DebatePhase.CONCLUSION: "Paint a vision of the future based on insights gained"
            },
            "Ken": {
                DebatePhase.OPENING: "Establish precise definitions and logical boundaries",
                DebatePhase.EXPLORATION: "Use systematic deconstruction - break it into components",
                DebatePhase.CHALLENGE: "Apply reductio ad absurdum or find the edge cases",
                DebatePhase.SYNTHESIS: "Identify the conditions under which each view is valid",
                DebatePhase.CONCLUSION: "Provide a rigorous summary of what was proven vs speculated"
            }
        }
        
        return devices.get(agent, {}).get(phase, "Use varied rhetorical approaches")
    
    def balance_debate(self, metrics: Dict) -> Dict[str, str]:
        """Provide balancing instructions based on debate metrics"""
        
        balance_instructions = {}
        
        # Check for imbalances
        if metrics.get("barbie_word_count", 0) > metrics.get("ken_word_count", 0) * 1.5:
            balance_instructions["Barbie"] = "Be more concise. Let Ken develop his points."
            balance_instructions["Ken"] = "Expand your arguments. Don't let Barbie dominate."
        elif metrics.get("ken_word_count", 0) > metrics.get("barbie_word_count", 0) * 1.5:
            balance_instructions["Ken"] = "Be more concise. Allow space for dialogue."
            balance_instructions["Barbie"] = "Develop your points more fully. Match Ken's depth."
        
        # Check for evidence imbalance
        if metrics.get("barbie_evidence_count", 0) < metrics.get("ken_evidence_count", 0) / 2:
            balance_instructions["Barbie"] = "Support your claims with more evidence."
        elif metrics.get("ken_evidence_count", 0) < metrics.get("barbie_evidence_count", 0) / 2:
            balance_instructions["Ken"] = "Back up your challenges with evidence."
        
        # Check for agreement level
        if metrics.get("agreement_rate", 0) > 0.8:
            balance_instructions["both"] = "Find points of productive disagreement. Challenge each other."
        elif metrics.get("agreement_rate", 0) < 0.2:
            balance_instructions["both"] = "Look for common ground. Build on agreements."
        
        return balance_instructions


class ResponseEvaluator:
    """Evaluates response quality and suggests improvements"""
    
    @staticmethod
    def score_response(response: str, criteria: Dict[str, float]) -> Tuple[float, List[str]]:
        """Score a response and provide feedback"""
        
        scores = []
        feedback = []
        
        # Check for specificity
        if any(phrase in response.lower() for phrase in ["for example", "specifically", "such as"]):
            scores.append(criteria.get("specificity", 1.0))
        else:
            feedback.append("Add specific examples")
            scores.append(0.5)
        
        # Check for evidence
        if any(phrase in response.lower() for phrase in ["study", "research", "data", "evidence"]):
            scores.append(criteria.get("evidence", 1.0))
        else:
            feedback.append("Include evidence or data")
            scores.append(0.3)
        
        # Check for engagement with opponent
        if any(phrase in response.lower() for phrase in ["you mentioned", "your point", "as you said"]):
            scores.append(criteria.get("engagement", 1.0))
        else:
            feedback.append("Directly address opponent's points")
            scores.append(0.4)
        
        # Check for novelty (not repeating same words too much)
        words = response.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 0
        if unique_ratio > 0.6:
            scores.append(criteria.get("novelty", 1.0))
        else:
            feedback.append("Avoid repetitive language")
            scores.append(0.6)
        
        # Check for structure
        if any(phrase in response.lower() for phrase in ["first", "second", "finally", "however", "therefore"]):
            scores.append(criteria.get("structure", 1.0))
        else:
            feedback.append("Improve argument structure")
            scores.append(0.7)
        
        overall_score = sum(scores) / len(scores) if scores else 0.5
        
        return overall_score, feedback


def create_dynamic_prompt(agent: str, conversation_state: Dict) -> str:
    """Create a fully dynamic prompt based on conversation state"""
    
    optimizer = PromptOptimizer()
    
    # Calculate metrics
    turn_number = conversation_state.get("turn_number", 1)
    resolution_rate = conversation_state.get("resolution_rate", 0.0)
    dispute_rate = conversation_state.get("dispute_rate", 0.0)
    agreement_level = conversation_state.get("agreement_level", 0.5)
    
    # Determine phase and tone
    phase = optimizer.determine_phase(turn_number, resolution_rate, dispute_rate)
    tone = optimizer.select_tone(agent, phase, agreement_level)
    
    # Build prompt components
    phase_instruction = optimizer.generate_phase_instruction(phase, tone)
    rhetorical_device = optimizer.suggest_rhetorical_device(agent, phase)
    variety_injection = optimizer.inject_variety(agent, 
                                                 conversation_state.get("previous_responses", []))
    
    # Combine into dynamic prompt
    dynamic_prompt = f"""
CURRENT PHASE: {phase.value.upper()}
TONE: {tone.value.upper()}

{phase_instruction}

RHETORICAL APPROACH: {rhetorical_device}

VARIETY INSTRUCTION: {variety_injection}

CONVERSATION STATE:
- Turn: {turn_number}
- Resolution Rate: {resolution_rate:.1%}
- Dispute Rate: {dispute_rate:.1%}
- Agreement Level: {agreement_level:.1%}

Remember: Each response should advance the conversation meaningfully. 
No repetition, no generic statements, no circular arguments.
"""
    
    return dynamic_prompt