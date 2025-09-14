"""
Debate Progression Mechanics
Tracks settled claims, prevents rehashing, and manages debate flow
"""

from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re
import hashlib


class ClaimStatus(Enum):
    """Status of a claim in the debate"""
    PROPOSED = "proposed"           # Newly introduced claim
    DISPUTED = "disputed"           # Being actively debated
    SUPPORTED = "supported"         # Has supporting evidence
    CHALLENGED = "challenged"       # Under challenge by opponent
    SETTLED_AGREED = "settled_agreed"       # Both parties agree
    SETTLED_DISAGREED = "settled_disagreed" # Agreed to disagree
    ABANDONED = "abandoned"         # No longer being pursued


class ResolutionType(Enum):
    """Types of resolution points in debate"""
    EVIDENCE_BASED = "evidence_based"       # Resolved by evidence
    LOGICAL = "logical"                     # Resolved by logic
    DEFINITIONAL = "definitional"           # Resolved by defining terms
    EMPIRICAL = "empirical"                 # Resolved by data/studies
    PRAGMATIC = "pragmatic"                 # Resolved by practical considerations
    PHILOSOPHICAL = "philosophical"         # Fundamental worldview differences


@dataclass
class Claim:
    """A specific claim made in the debate"""
    id: str
    text: str
    speaker: str  # "Barbie" or "Ken"
    round_introduced: int
    status: ClaimStatus
    supporting_evidence: List[str] = field(default_factory=list)
    challenges: List[str] = field(default_factory=list)
    resolution_type: Optional[ResolutionType] = None
    settled_round: Optional[int] = None
    rehash_count: int = 0
    last_mentioned_round: int = 0


@dataclass
class ResolutionPoint:
    """A point of resolution in the debate"""
    id: str
    description: str
    resolution_type: ResolutionType
    round_resolved: int
    agreed_by_both: bool
    barbie_position: str
    ken_position: str
    evidence_basis: List[str] = field(default_factory=list)


@dataclass
class DebateSegment:
    """A thematic segment of the debate"""
    id: str
    topic: str
    start_round: int
    end_round: Optional[int]
    claims: List[str] = field(default_factory=list)  # Claim IDs
    resolution_points: List[str] = field(default_factory=list)  # Resolution IDs
    progress_score: float = 0.0  # 0-1 scale of progress toward resolution


class DebateProgressionTracker:
    """Tracks debate progression, settled claims, and prevents rehashing"""
    
    def __init__(self):
        self.claims: Dict[str, Claim] = {}
        self.resolution_points: Dict[str, ResolutionPoint] = {}
        self.debate_segments: Dict[str, DebateSegment] = {}
        self.current_round = 0
        self.current_segment: Optional[str] = None
        self.rehash_threshold = 3  # Max times a claim can be rehashed
        self.progress_history: List[Dict] = []
        self.questions_asked = {}  # Track questions to detect repetitive questioning
        self.question_patterns = {}  # Pattern -> count to detect repetitive question types
        
        # Pattern matching for claim detection
        self.claim_patterns = [
            r"I claim that",
            r"I argue that",
            r"My position is",
            r"I believe",
            r"It's clear that",
            r"The evidence shows",
            r"Studies indicate",
            r"Research demonstrates"
        ]
        
        # Resolution indicators
        self.agreement_patterns = [
            r"I agree",
            r"You're right",
            r"That's correct",
            r"I accept",
            r"Fair point",
            r"I concede"
        ]
        
        self.challenge_patterns = [
            r"I challenge",
            r"I disagree",
            r"That's incorrect",
            r"I question",
            r"I dispute",
            r"But what about"
        ]
    
    def advance_round(self) -> None:
        """Advance to the next round of debate"""
        self.current_round += 1
    
    def extract_claims_from_message(self, message: str, speaker: str) -> List[str]:
        """Extract new claims from a message"""
        claims = []
        sentences = [s.strip() for s in message.split('.') if s.strip()]
        
        # Also split on question marks to handle questions better
        question_sentences = []
        for sent in sentences:
            if '?' in sent:
                parts = sent.split('?')
                for part in parts:
                    if part.strip():
                        question_sentences.append(part.strip() + '?')
            else:
                question_sentences.append(sent)
        
        sentences = question_sentences
        
        for sentence in sentences:
            # Skip pure questions - they're not claims
            if sentence.strip().endswith('?'):
                # Track questions separately for repetition detection
                self._track_question(sentence, speaker)
                continue
                
            # Check if sentence contains a claim pattern
            is_claim = False
            for pattern in self.claim_patterns:
                if re.search(pattern, sentence, re.IGNORECASE):
                    is_claim = True
                    break
            
            # Also detect strong assertions
            if not is_claim:
                strong_words = ['must', 'will', 'cannot', 'always', 'never', 'clearly', 'obviously']
                if any(word in sentence.lower() for word in strong_words):
                    is_claim = True
            
            if is_claim and len(sentence) > 20:  # Filter out very short statements
                claim_id = self._generate_claim_id(sentence)
                
                # Check if this claim already exists (prevent duplicates)
                if claim_id not in self.claims:
                    claim = Claim(
                        id=claim_id,
                        text=sentence,
                        speaker=speaker,
                        round_introduced=self.current_round,
                        status=ClaimStatus.PROPOSED,
                        last_mentioned_round=self.current_round
                    )
                    self.claims[claim_id] = claim
                    claims.append(claim_id)
                else:
                    # Update existing claim
                    self.claims[claim_id].last_mentioned_round = self.current_round
                    self.claims[claim_id].rehash_count += 1
        
        return claims
    
    def analyze_message_responses(self, message: str, speaker: str, responding_to: List[str]) -> Dict:
        """Analyze how a message responds to previous claims"""
        agreements = []
        challenges = []
        new_evidence = []
        
        message_lower = message.lower()
        
        # Check for agreement patterns
        for pattern in self.agreement_patterns:
            if re.search(pattern, message_lower):
                # Find which claims this might be agreeing to
                for claim_id in responding_to:
                    if claim_id in self.claims:
                        agreements.append(claim_id)
                        self.claims[claim_id].status = ClaimStatus.SUPPORTED
        
        # Check for challenge patterns
        for pattern in self.challenge_patterns:
            if re.search(pattern, message_lower):
                for claim_id in responding_to:
                    if claim_id in self.claims:
                        challenges.append(claim_id)
                        self.claims[claim_id].status = ClaimStatus.CHALLENGED
                        self.claims[claim_id].challenges.append(message)
        
        # Look for evidence (citations, studies, data)
        evidence_patterns = [r'study', r'research', r'data', r'evidence', r'according to', r'shows that']
        for pattern in evidence_patterns:
            if re.search(pattern, message_lower):
                new_evidence.append(pattern)
        
        return {
            'agreements': agreements,
            'challenges': challenges,
            'evidence_provided': new_evidence,
            'speaker': speaker,
            'round': self.current_round
        }
    
    def detect_rehashing(self, message: str) -> List[Dict]:
        """Detect if message is rehashing previously settled points or repeating question patterns"""
        rehashed_items = []
        
        # Check for rehashed claims
        for claim_id, claim in self.claims.items():
            # Check if claim is being mentioned again
            if claim.text.lower() in message.lower() or self._similar_text(claim.text, message):
                if claim.status in [ClaimStatus.SETTLED_AGREED, ClaimStatus.SETTLED_DISAGREED]:
                    rehashed_items.append({
                        'type': 'settled_claim',
                        'claim_id': claim_id,
                        'claim_text': claim.text,
                        'status': claim.status.value,
                        'settled_round': claim.settled_round,
                        'rehash_count': claim.rehash_count
                    })
                elif claim.rehash_count >= self.rehash_threshold:
                    rehashed_items.append({
                        'type': 'excessive_claim',
                        'claim_id': claim_id,
                        'claim_text': claim.text,
                        'status': 'excessive_rehash',
                        'rehash_count': claim.rehash_count,
                        'suggestion': 'Consider moving to new aspect or concluding this point'
                    })
        
        # Check for repetitive questioning patterns
        questions = [s.strip() for s in message.split('?') if s.strip() and len(s.strip()) > 10]
        for question in questions:
            # Extract question type (e.g., "how do you", "what evidence", "could you provide")
            question_type = self._extract_question_type(question)
            if question_type:
                if question_type in self.question_patterns:
                    self.question_patterns[question_type] += 1
                    if self.question_patterns[question_type] >= self.rehash_threshold:
                        rehashed_items.append({
                            'type': 'repetitive_question',
                            'pattern': question_type,
                            'text': question[:100] + ("..." if len(question) > 100 else ""),
                            'rehash_count': self.question_patterns[question_type],
                            'status': 'repetitive_questioning',
                            'suggestion': f'This type of question has been asked {self.question_patterns[question_type]} times. Consider accepting previous answers or asking more specific follow-ups.'
                        })
                else:
                    self.question_patterns[question_type] = 1
        
        return rehashed_items
    
    def create_resolution_point(self, description: str, resolution_type: ResolutionType,
                              barbie_position: str, ken_position: str, 
                              agreed: bool, evidence: List[str] = None) -> str:
        """Create a resolution point"""
        resolution_id = self._generate_resolution_id(description)
        
        resolution = ResolutionPoint(
            id=resolution_id,
            description=description,
            resolution_type=resolution_type,
            round_resolved=self.current_round,
            agreed_by_both=agreed,
            barbie_position=barbie_position,
            ken_position=ken_position,
            evidence_basis=evidence or []
        )
        
        self.resolution_points[resolution_id] = resolution
        
        # Update related claims as settled
        for claim_id, claim in self.claims.items():
            if claim.status in [ClaimStatus.DISPUTED, ClaimStatus.CHALLENGED]:
                if self._similar_text(claim.text, description):
                    claim.status = ClaimStatus.SETTLED_AGREED if agreed else ClaimStatus.SETTLED_DISAGREED
                    claim.settled_round = self.current_round
                    claim.resolution_type = resolution_type
        
        return resolution_id
    
    def get_debate_progress_summary(self) -> Dict:
        """Get a summary of debate progress"""
        total_claims = len(self.claims)
        settled_claims = len([c for c in self.claims.values() 
                            if c.status in [ClaimStatus.SETTLED_AGREED, ClaimStatus.SETTLED_DISAGREED]])
        active_claims = len([c for c in self.claims.values() 
                           if c.status in [ClaimStatus.DISPUTED, ClaimStatus.CHALLENGED]])
        
        progress_percentage = (settled_claims / total_claims * 100) if total_claims > 0 else 0
        
        rehash_warnings = []
        for claim in self.claims.values():
            if claim.rehash_count >= self.rehash_threshold:
                rehash_warnings.append({
                    'claim': claim.text[:100] + "..." if len(claim.text) > 100 else claim.text,
                    'rehash_count': claim.rehash_count,
                    'speaker': claim.speaker
                })
        
        return {
            'round': self.current_round,
            'total_claims': total_claims,
            'settled_claims': settled_claims,
            'active_claims': active_claims,
            'progress_percentage': progress_percentage,
            'resolution_points': len(self.resolution_points),
            'rehash_warnings': rehash_warnings,
            'settled_resolutions': [r for r in self.resolution_points.values() if r.agreed_by_both],
            'unresolved_disagreements': [r for r in self.resolution_points.values() if not r.agreed_by_both]
        }
    
    def generate_progression_guidance(self) -> Dict:
        """Generate guidance for improving debate progression"""
        summary = self.get_debate_progress_summary()
        guidance = {
            'suggestions': [],
            'warnings': [],
            'next_steps': []
        }
        
        # Check for excessive rehashing
        if summary['rehash_warnings']:
            guidance['warnings'].append(f"Detecting rehashing of {len(summary['rehash_warnings'])} claims")
            guidance['suggestions'].append("Consider focusing on new evidence or moving to adjacent topics")
        
        # Check for stagnant claims
        stagnant_claims = [c for c in self.claims.values() 
                          if c.status == ClaimStatus.DISPUTED and 
                          self.current_round - c.round_introduced > 5]
        
        if stagnant_claims:
            guidance['warnings'].append(f"{len(stagnant_claims)} claims have been disputed for >5 rounds")
            guidance['suggestions'].append("Consider requesting specific evidence or agreeing to disagree")
        
        # Progress suggestions
        if summary['progress_percentage'] < 30:
            guidance['next_steps'].append("Focus on establishing common ground and shared definitions")
        elif summary['progress_percentage'] < 60:
            guidance['next_steps'].append("Work toward resolution of key disputed points")
        else:
            guidance['next_steps'].append("Synthesize agreements and identify remaining differences")
        
        return guidance
    
    def _generate_claim_id(self, text: str) -> str:
        """Generate unique ID for a claim"""
        return hashlib.md5(text.lower().encode()).hexdigest()[:8]
    
    def _generate_resolution_id(self, description: str) -> str:
        """Generate unique ID for a resolution point"""
        return f"res_{hashlib.md5(description.encode()).hexdigest()[:8]}"
    
    def _similar_text(self, text1: str, text2: str, threshold: float = 0.3) -> bool:
        """Check if two texts are similar (simple word overlap)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return False
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0
        return similarity >= threshold
    
    def _track_question(self, question: str, speaker: str):
        """Track questions asked for repetition detection"""
        question_key = f"{speaker}:{question.lower().strip()}"
        if question_key in self.questions_asked:
            self.questions_asked[question_key] += 1
        else:
            self.questions_asked[question_key] = 1
    
    def _extract_question_type(self, question: str) -> Optional[str]:
        """Extract the type/pattern of a question"""
        question_lower = question.lower().strip()
        
        # Common question patterns
        patterns = [
            (r"how do you (know|plan|propose|think|suggest)", "how_do_you"),
            (r"what (evidence|studies|data|research)", "what_evidence"),
            (r"could you (provide|clarify|explain|elaborate)", "could_you_provide"),
            (r"can you (share|provide|explain|clarify)", "can_you_share"),
            (r"what (specific|concrete|practical)", "what_specific"),
            (r"how (feasible|practical|realistic)", "how_feasible"),
            (r"what (steps|approach|methodology)", "what_methodology"),
            (r"(are there|do you have) (any|specific) (examples|cases|studies)", "examples_request"),
            (r"what makes you (confident|think|believe)", "what_makes_you"),
            (r"how will you (address|handle|ensure)", "how_will_you"),
            (r"what (potential|edge) (cases|problems|issues)", "what_problems")
        ]
        
        for pattern, pattern_type in patterns:
            if re.search(pattern, question_lower):
                return pattern_type
        
        # Generic question type based on first words
        first_words = question_lower.split()[:3]
        if len(first_words) >= 2:
            return "_".join(first_words[:2])
        
        return None
    
    def export_debate_structure(self) -> Dict:
        """Export the complete debate structure for analysis"""
        return {
            'metadata': {
                'current_round': self.current_round,
                'total_claims': len(self.claims),
                'total_resolutions': len(self.resolution_points),
                'export_timestamp': datetime.now().isoformat()
            },
            'claims': {cid: {
                'text': c.text,
                'speaker': c.speaker,
                'status': c.status.value,
                'round_introduced': c.round_introduced,
                'rehash_count': c.rehash_count,
                'challenges': len(c.challenges)
            } for cid, c in self.claims.items()},
            'resolutions': {rid: {
                'description': r.description,
                'type': r.resolution_type.value,
                'agreed': r.agreed_by_both,
                'round': r.round_resolved,
                'barbie_position': r.barbie_position,
                'ken_position': r.ken_position
            } for rid, r in self.resolution_points.items()},
            'progress_summary': self.get_debate_progress_summary()
        }


# Example usage and testing
if __name__ == "__main__":
    tracker = DebateProgressionTracker()
    
    print("=== DEBATE PROGRESSION TRACKER DEMO ===\n")
    
    # Simulate a debate progression
    tracker.advance_round()  # Round 1
    
    # Barbie makes initial claims
    barbie_msg1 = "I believe AI consciousness is possible. Research shows that neural networks can exhibit emergent behaviors. The evidence indicates that complexity leads to awareness."
    claims1 = tracker.extract_claims_from_message(barbie_msg1, "Barbie")
    print(f"Round {tracker.current_round}: Barbie introduced {len(claims1)} claims")
    
    tracker.advance_round()  # Round 2
    
    # Ken challenges
    ken_msg1 = "I challenge the assumption that complexity equals consciousness. I disagree with the claim about neural networks. What evidence supports emergent awareness?"
    claims2 = tracker.extract_claims_from_message(ken_msg1, "Ken")
    response1 = tracker.analyze_message_responses(ken_msg1, "Ken", claims1)
    print(f"Round {tracker.current_round}: Ken challenged {len(response1['challenges'])} claims")
    
    tracker.advance_round()  # Round 3
    
    # Barbie provides evidence
    barbie_msg2 = "Studies by Tononi show that integrated information theory supports my position. I agree that we need better definitions, but the research demonstrates measurable consciousness indicators."
    response2 = tracker.analyze_message_responses(barbie_msg2, "Barbie", claims2)
    print(f"Round {tracker.current_round}: Barbie provided {len(response2['evidence_provided'])} evidence points")
    
    # Create a resolution point
    resolution_id = tracker.create_resolution_point(
        "Definition of consciousness requires clarification",
        ResolutionType.DEFINITIONAL,
        "Consciousness as integrated information processing",
        "Consciousness requires subjective experience",
        agreed=False,
        evidence=["Tononi IIT studies", "Philosophical arguments"]
    )
    print(f"Created resolution point: {resolution_id}")
    
    # Check progress
    progress = tracker.get_debate_progress_summary()
    guidance = tracker.generate_progression_guidance()
    
    print(f"\nDEBATE PROGRESS:")
    print(f"Progress: {progress['progress_percentage']:.1f}%")
    print(f"Active claims: {progress['active_claims']}")
    print(f"Settled claims: {progress['settled_claims']}")
    print(f"Resolution points: {progress['resolution_points']}")
    
    if guidance['suggestions']:
        print(f"\nGUIDANCE:")
        for suggestion in guidance['suggestions']:
            print(f"• {suggestion}")
    
    # Test rehashing detection
    tracker.advance_round()  # Round 4
    
    # Simulate rehashing
    for i in range(4):
        tracker.advance_round()
        rehash_msg = "I believe AI consciousness is possible. The evidence shows complexity leads to awareness."
        tracker.extract_claims_from_message(rehash_msg, "Barbie")
    
    rehash_warnings = tracker.detect_rehashing(rehash_msg)
    print(f"\nREHASH DETECTION:")
    print(f"Found {len(rehash_warnings)} potential rehashing issues")
    
    for warning in rehash_warnings:
        print(f"• {warning['claim_text'][:50]}... (rehashed {warning['rehash_count']} times)")
    
    print(f"\nDEBATE STRUCTURE EXPORT:")
    structure = tracker.export_debate_structure()
    print(f"Total rounds: {structure['metadata']['current_round']}")
    print(f"Claims tracked: {structure['metadata']['total_claims']}")
    print(f"Resolutions created: {structure['metadata']['total_resolutions']}")
    
    print("\n" + "="*50)
    print("Debate Progression Tracker ready for integration!")
    print("="*50)