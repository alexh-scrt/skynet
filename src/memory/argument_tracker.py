"""
Argument Tracking Module
Tracks logical argument structures and relationships
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from enum import Enum


class ArgumentType(Enum):
    DEDUCTIVE = "deductive"
    INDUCTIVE = "inductive"
    ABDUCTIVE = "abductive"
    ANALOGICAL = "analogical"
    CAUSAL = "causal"


class ArgumentStrength(Enum):
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    FALLACIOUS = "fallacious"


@dataclass
class Premise:
    """A single premise in an argument"""
    content: str
    evidence: List[str] = field(default_factory=list)
    accepted: bool = False
    challenged: bool = False


@dataclass
class Argument:
    """Represents a logical argument structure"""
    id: str
    speaker: str
    argument_type: ArgumentType
    premises: List[Premise]
    conclusion: str
    strength: ArgumentStrength = ArgumentStrength.MODERATE
    rebuttals: List[str] = field(default_factory=list)
    supporting_arguments: List[str] = field(default_factory=list)
    
    def is_valid(self) -> bool:
        """Check if all premises are accepted"""
        return all(p.accepted for p in self.premises)
    
    def get_unchallenged_premises(self) -> List[Premise]:
        """Get premises that haven't been challenged"""
        return [p for p in self.premises if not p.challenged]


class ArgumentTracker:
    """Tracks and analyzes argument structures in conversation"""
    
    def __init__(self):
        self.arguments: Dict[str, Argument] = {}
        self.argument_chains: Dict[str, List[str]] = {}  # Maps arguments to their supporting arguments
        self.fallacies_detected: List[Dict] = []
        
    def add_argument(self, 
                    speaker: str,
                    argument_type: ArgumentType,
                    premises: List[str],
                    conclusion: str,
                    evidence: Dict[str, List[str]] = None) -> Argument:
        """Add a new argument to track"""
        arg_id = f"arg_{len(self.arguments) + 1}"
        
        premise_objects = []
        for p in premises:
            premise = Premise(
                content=p,
                evidence=evidence.get(p, []) if evidence else []
            )
            premise_objects.append(premise)
        
        argument = Argument(
            id=arg_id,
            speaker=speaker,
            argument_type=argument_type,
            premises=premise_objects,
            conclusion=conclusion
        )
        
        self.arguments[arg_id] = argument
        return argument
    
    def challenge_premise(self, arg_id: str, premise_index: int, challenge: str):
        """Challenge a specific premise in an argument"""
        if arg_id in self.arguments:
            if 0 <= premise_index < len(self.arguments[arg_id].premises):
                self.arguments[arg_id].premises[premise_index].challenged = True
                self.arguments[arg_id].rebuttals.append(challenge)
    
    def support_argument(self, arg_id: str, supporting_arg_id: str):
        """Link a supporting argument to another argument"""
        if arg_id in self.arguments and supporting_arg_id in self.arguments:
            self.arguments[arg_id].supporting_arguments.append(supporting_arg_id)
            
            if arg_id not in self.argument_chains:
                self.argument_chains[arg_id] = []
            self.argument_chains[arg_id].append(supporting_arg_id)
    
    def detect_fallacy(self, arg_id: str, fallacy_type: str, explanation: str):
        """Record a detected logical fallacy"""
        if arg_id in self.arguments:
            self.fallacies_detected.append({
                "argument_id": arg_id,
                "fallacy_type": fallacy_type,
                "explanation": explanation
            })
            self.arguments[arg_id].strength = ArgumentStrength.FALLACIOUS
    
    def evaluate_argument_strength(self, arg_id: str) -> ArgumentStrength:
        """Evaluate the strength of an argument"""
        if arg_id not in self.arguments:
            return ArgumentStrength.WEAK
        
        arg = self.arguments[arg_id]
        
        # Check for fallacies
        if any(f["argument_id"] == arg_id for f in self.fallacies_detected):
            return ArgumentStrength.FALLACIOUS
        
        # Check premise support
        supported_premises = sum(1 for p in arg.premises if p.evidence)
        total_premises = len(arg.premises)
        
        if total_premises == 0:
            return ArgumentStrength.WEAK
        
        support_ratio = supported_premises / total_premises
        
        # Check for rebuttals
        rebuttal_penalty = min(len(arg.rebuttals) * 0.1, 0.5)
        
        # Calculate final strength
        strength_score = support_ratio - rebuttal_penalty
        
        if strength_score > 0.7:
            return ArgumentStrength.STRONG
        elif strength_score > 0.4:
            return ArgumentStrength.MODERATE
        else:
            return ArgumentStrength.WEAK
    
    def get_strongest_arguments(self, speaker: str = None) -> List[Argument]:
        """Get the strongest arguments, optionally filtered by speaker"""
        args = list(self.arguments.values())
        
        if speaker:
            args = [a for a in args if a.speaker == speaker]
        
        # Evaluate and sort by strength
        for arg in args:
            arg.strength = self.evaluate_argument_strength(arg.id)
        
        return sorted(args, 
                     key=lambda a: (a.strength == ArgumentStrength.STRONG,
                                   a.strength == ArgumentStrength.MODERATE,
                                   len(a.supporting_arguments)),
                     reverse=True)
    
    def find_contradictions(self) -> List[Dict]:
        """Find contradicting conclusions between arguments"""
        contradictions = []
        args_list = list(self.arguments.values())
        
        for i, arg1 in enumerate(args_list):
            for arg2 in args_list[i+1:]:
                # Check if same speaker has contradicting conclusions
                if arg1.speaker == arg2.speaker:
                    # Check both patterns: "Not X" vs "X" and "X" vs "Not X"
                    conclusion1 = arg1.conclusion.lower().strip()
                    conclusion2 = arg2.conclusion.lower().strip()
                    
                    if (conclusion1.startswith("not ") and 
                        conclusion2 == conclusion1[4:]):
                        contradictions.append({
                            "speaker": arg1.speaker,
                            "arg1": arg1.id,
                            "arg2": arg2.id,
                            "contradiction": f"{arg1.conclusion} vs {arg2.conclusion}"
                        })
                    elif (conclusion2.startswith("not ") and 
                          conclusion1 == conclusion2[4:]):
                        contradictions.append({
                            "speaker": arg1.speaker,
                            "arg1": arg1.id,
                            "arg2": arg2.id,
                            "contradiction": f"{arg1.conclusion} vs {arg2.conclusion}"
                        })
        
        return contradictions
    
    def get_argument_summary(self) -> Dict:
        """Get a summary of all tracked arguments"""
        strong_args = [a for a in self.arguments.values() 
                      if self.evaluate_argument_strength(a.id) == ArgumentStrength.STRONG]
        
        return {
            "total_arguments": len(self.arguments),
            "strong_arguments": len(strong_args),
            "fallacies_detected": len(self.fallacies_detected),
            "contradictions": len(self.find_contradictions()),
            "argument_types": {
                t.value: len([a for a in self.arguments.values() if a.argument_type == t])
                for t in ArgumentType
            }
        }