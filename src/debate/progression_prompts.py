"""
Debate Progression Prompts
Generates context-aware prompts based on debate progression state
"""

import sys
from pathlib import Path
prj_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(prj_root))

from typing import Dict, List, Optional
from src.debate.progression_tracker import DebateProgressionTracker, ClaimStatus, ResolutionType


class ProgressionPromptGenerator:
    """Generates prompts that guide debate progression and prevent rehashing"""
    
    def __init__(self, tracker: DebateProgressionTracker):
        self.tracker = tracker
    
    def generate_progression_context(self, speaker: str) -> str:
        """Generate context about debate progression for prompts"""
        progress = self.tracker.get_debate_progress_summary()
        guidance = self.tracker.generate_progression_guidance()
        
        context_parts = []
        
        # Current progress status
        context_parts.append(f"DEBATE PROGRESS STATUS (Round {progress['round']}):")
        context_parts.append(f"• Progress: {progress['progress_percentage']:.1f}% complete")
        context_parts.append(f"• Active claims being debated: {progress['active_claims']}")
        context_parts.append(f"• Settled claims: {progress['settled_claims']}")
        context_parts.append(f"• Resolution points established: {progress['resolution_points']}")
        
        # Settled agreements to avoid rehashing
        settled_resolutions = [r for r in self.tracker.resolution_points.values() if r.agreed_by_both]
        if settled_resolutions:
            context_parts.append(f"\nSETTLED AGREEMENTS (do not rehash these):")
            for resolution in settled_resolutions[-3:]:  # Show last 3
                context_parts.append(f"• {resolution.description} (Round {resolution.round_resolved})")
        
        # Active disagreements to focus on
        active_claims = [c for c in self.tracker.claims.values() 
                        if c.status in [ClaimStatus.DISPUTED, ClaimStatus.CHALLENGED]]
        if active_claims:
            context_parts.append(f"\nACTIVE CLAIMS TO RESOLVE:")
            for claim in active_claims[-3:]:  # Show last 3
                context_parts.append(f"• {claim.text[:80]}... ({claim.speaker}, Round {claim.round_introduced})")
        
        # Rehashing warnings
        if progress['rehash_warnings']:
            context_parts.append(f"\nREHASHING WARNINGS:")
            context_parts.append("The following points have been repeated multiple times:")
            for warning in progress['rehash_warnings'][-2:]:  # Show last 2
                if warning.get('type') == 'repetitive_question':
                    context_parts.append(f"• Question pattern '{warning.get('pattern', 'unknown')}' repeated {warning['rehash_count']} times")
                    context_parts.append(f"  Suggestion: {warning.get('suggestion', 'Provide new angles or accept previous answers')}")
                else:
                    context_parts.append(f"• {warning.get('claim', warning.get('text', 'Unknown'))[:60]}... (repeated {warning['rehash_count']} times)")
            context_parts.append("AVOID repeating these points. Instead, provide new evidence or move to related topics.")
        
        # Progression guidance
        if guidance['suggestions']:
            context_parts.append(f"\nPROGRESSION GUIDANCE:")
            for suggestion in guidance['suggestions']:
                context_parts.append(f"• {suggestion}")
        
        if guidance['next_steps']:
            context_parts.append(f"\nRECOMMENDED NEXT STEPS:")
            for step in guidance['next_steps']:
                context_parts.append(f"• {step}")
        
        return "\n".join(context_parts)
    
    def generate_barbie_progression_prompt(self, base_prompt: str) -> str:
        """Generate Barbie's prompt with progression context"""
        progression_context = self.generate_progression_context("Barbie")
        
        progression_instructions = self._get_barbie_progression_instructions()
        
        enhanced_prompt = f"""{base_prompt}

{progression_context}

DEBATE PROGRESSION INSTRUCTIONS FOR BARBIE:
{progression_instructions}

Remember: Move the debate forward constructively. Build on agreements, address unresolved claims with new evidence, and avoid rehashing settled points."""
        
        return enhanced_prompt
    
    def generate_ken_progression_prompt(self, base_prompt: str) -> str:
        """Generate Ken's prompt with progression context"""
        progression_context = self.generate_progression_context("Ken")
        
        progression_instructions = self._get_ken_progression_instructions()
        
        enhanced_prompt = f"""{base_prompt}

{progression_context}

DEBATE PROGRESSION INSTRUCTIONS FOR KEN:
{progression_instructions}

Remember: Challenge unresolved claims systematically. Acknowledge settled agreements and focus your analysis on remaining disputed points."""
        
        return enhanced_prompt
    
    def _get_barbie_progression_instructions(self) -> str:
        """Get progression-specific instructions for Barbie"""
        progress = self.tracker.get_debate_progress_summary()
        guidance = self.tracker.generate_progression_guidance()
        
        instructions = []
        
        # Stage-specific guidance
        if progress['progress_percentage'] < 30:
            instructions.append("EXPLORATION STAGE: Focus on introducing diverse perspectives and evidence")
            instructions.append("- Present multiple analogies and examples")
            instructions.append("- Establish common ground where possible")
            instructions.append("- Ask clarifying questions about Ken's position")
        
        elif progress['progress_percentage'] < 70:
            instructions.append("REFINEMENT STAGE: Deepen analysis of disputed claims")
            instructions.append("- Provide specific evidence for challenged claims")
            instructions.append("- Address Ken's logical challenges directly")
            instructions.append("- Synthesize agreements into larger frameworks")
        
        else:
            instructions.append("SYNTHESIS STAGE: Work toward resolution")
            instructions.append("- Identify remaining disagreements clearly")
            instructions.append("- Propose compromise positions where appropriate")
            instructions.append("- Summarize areas of consensus")
        
        # Rehashing prevention
        if progress['rehash_warnings']:
            instructions.append("ANTI-REHASHING: Avoid repeating settled points")
            instructions.append("- Do NOT restate claims that have been repeated >3 times")
            instructions.append("- Introduce NEW evidence or angles for persistent disagreements")
            instructions.append("- Acknowledge what has been settled and move forward")
        
        # Specific claim guidance
        active_claims = [c for c in self.tracker.claims.values() 
                        if c.status in [ClaimStatus.DISPUTED, ClaimStatus.CHALLENGED]]
        if active_claims:
            instructions.append("FOCUS AREAS: Address these unresolved claims:")
            for claim in active_claims[-2:]:  # Focus on last 2
                instructions.append(f"- {claim.text[:60]}... (needs {self._get_resolution_strategy(claim)})")
        
        return "\n".join(instructions)
    
    def _get_ken_progression_instructions(self) -> str:
        """Get progression-specific instructions for Ken"""
        progress = self.tracker.get_debate_progress_summary()
        
        instructions = []
        
        # Stage-specific guidance
        if progress['progress_percentage'] < 30:
            instructions.append("EXPLORATION STAGE: Systematically examine Barbie's claims")
            instructions.append("- Ask for definitions and clarifications")
            instructions.append("- Request specific evidence for broad assertions")
            instructions.append("- Identify logical assumptions to examine")
        
        elif progress['progress_percentage'] < 70:
            instructions.append("REFINEMENT STAGE: Deepen logical analysis")
            instructions.append("- Challenge evidence quality and relevance")
            instructions.append("- Examine edge cases and counterexamples")
            instructions.append("- Test logical consistency of Barbie's framework")
        
        else:
            instructions.append("SYNTHESIS STAGE: Evaluate remaining differences")
            instructions.append("- Clearly state your final position on disputed points")
            instructions.append("- Identify which differences are fundamental vs. resolvable")
            instructions.append("- Acknowledge areas where Barbie has convinced you")
        
        # Settled agreements
        settled_resolutions = [r for r in self.tracker.resolution_points.values() if r.agreed_by_both]
        if settled_resolutions:
            instructions.append("ACKNOWLEDGED AGREEMENTS (don't re-litigate):")
            for resolution in settled_resolutions[-2:]:
                instructions.append(f"- {resolution.description}")
        
        # Focus on unresolved
        unresolved_claims = [c for c in self.tracker.claims.values() 
                           if c.status in [ClaimStatus.DISPUTED, ClaimStatus.CHALLENGED]]
        if unresolved_claims:
            instructions.append("UNRESOLVED CLAIMS TO ADDRESS:")
            for claim in unresolved_claims[-2:]:
                challenge_type = self._get_challenge_strategy(claim)
                instructions.append(f"- {claim.text[:60]}... (challenge via {challenge_type})")
        
        return "\n".join(instructions)
    
    def _get_resolution_strategy(self, claim) -> str:
        """Suggest resolution strategy for a claim"""
        if claim.challenges:
            return "more evidence"
        elif claim.rehash_count > 2:
            return "new angle or agree to disagree"
        elif "evidence" in claim.text.lower():
            return "specific citations"
        elif "believe" in claim.text.lower():
            return "logical justification"
        else:
            return "clarification"
    
    def _get_challenge_strategy(self, claim) -> str:
        """Suggest challenge strategy for Ken"""
        if "evidence" in claim.text.lower():
            return "source verification"
        elif "research" in claim.text.lower():
            return "methodology questions"
        elif "believe" in claim.text.lower():
            return "logical consistency"
        elif "must" in claim.text.lower() or "will" in claim.text.lower():
            return "edge case analysis"
        else:
            return "definition clarification"
    
    def generate_progression_summary(self) -> str:
        """Generate a summary of debate progression for logging"""
        progress = self.tracker.get_debate_progress_summary()
        structure = self.tracker.export_debate_structure()
        
        summary_parts = []
        summary_parts.append(f"DEBATE PROGRESSION SUMMARY (Round {progress['round']}):")
        summary_parts.append(f"Progress: {progress['progress_percentage']:.1f}% complete")
        summary_parts.append(f"Claims tracked: {progress['total_claims']} ({progress['active_claims']} active)")
        summary_parts.append(f"Resolutions established: {progress['resolution_points']}")
        
        if progress['rehash_warnings']:
            summary_parts.append(f"Rehashing detected: {len(progress['rehash_warnings'])} claims repeated excessively")
        
        # List settled points
        settled = [r for r in self.tracker.resolution_points.values() if r.agreed_by_both]
        if settled:
            summary_parts.append("Settled agreements:")
            for resolution in settled:
                summary_parts.append(f"  • {resolution.description}")
        
        # List unresolved
        unresolved = [r for r in self.tracker.resolution_points.values() if not r.agreed_by_both]
        if unresolved:
            summary_parts.append("Unresolved disagreements:")
            for resolution in unresolved:
                summary_parts.append(f"  • {resolution.description}")
        
        return "\n".join(summary_parts)


# Example usage
if __name__ == "__main__":
    import sys
    from pathlib import Path
    prj_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(prj_root))
    
    from src.debate.progression_tracker import DebateProgressionTracker
    
    print("=== PROGRESSION PROMPTS DEMO ===\n")
    
    # Create tracker and simulate some debate
    tracker = DebateProgressionTracker()
    
    # Simulate progression
    tracker.advance_round()
    claims1 = tracker.extract_claims_from_message(
        "I believe AI consciousness is achievable. Research shows neural networks exhibit emergent behaviors.",
        "Barbie"
    )
    
    tracker.advance_round()
    tracker.extract_claims_from_message(
        "I challenge the consciousness claim. What evidence supports neural network awareness?",
        "Ken"
    )
    
    # Create resolution
    tracker.create_resolution_point(
        "Neural networks show complex behaviors",
        ResolutionType.EVIDENCE_BASED,
        "Complexity indicates consciousness potential",
        "Complexity does not equal consciousness", 
        agreed=True
    )
    
    # Generate prompts
    generator = ProgressionPromptGenerator(tracker)
    
    base_barbie_prompt = "You are Barbie, a creative AI agent focused on synthesis."
    enhanced_barbie_prompt = generator.generate_barbie_progression_prompt(base_barbie_prompt)
    
    print("ENHANCED BARBIE PROMPT:")
    print("-" * 40)
    print(enhanced_barbie_prompt[:500] + "...")
    
    print(f"\nPROGRESSION SUMMARY:")
    print("-" * 25)
    summary = generator.generate_progression_summary()
    print(summary)
    
    print(f"\n{'='*50}")
    print("Progression Prompts ready for integration!")
    print("="*50)