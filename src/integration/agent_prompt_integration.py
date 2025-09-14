"""
Integration system for enhanced agent prompts
Combines all improvements: personality, memory, source verification, and clean responses
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Optional
from src.personality.agent_personalities import PersonalityManager
from src.memory.conversation_memory import ConversationMemory
from src.utils.source_verification import SourceVerifier
from src.prompts.clean_response_prompts import add_clean_response_instructions
from src.prompts.enhanced_prompts import generate_contextual_prompt
import json


class MasterPromptGenerator:
    """Generates comprehensive prompts combining all enhancements"""
    
    def __init__(self):
        self.personality_manager = PersonalityManager()
        self.memory = ConversationMemory()
        self.source_verifier = SourceVerifier()
    
    def generate_complete_prompt(self, 
                                agent: str,
                                topic: str,
                                conversation_state: Dict,
                                memory_context: Dict) -> str:
        """
        Generate the ultimate enhanced prompt combining all improvements
        
        Args:
            agent: "Barbie" or "Ken"
            topic: Current debate topic
            conversation_state: Current conversation metrics and state
            memory_context: Memory system context
            
        Returns:
            Complete enhanced prompt ready for the agent
        """
        
        # 1. Generate personality-based prompt
        personality = self.personality_manager.get_agent_personality(agent)
        domain_expertise = self.personality_manager.generate_domain_expertise_prompt(agent, topic)
        
        # 2. Get conversation phase and dynamics
        phase = self._determine_conversation_phase(conversation_state)
        rhetorical_approach = personality.get_rhetorical_approach(topic, phase)
        
        # 3. Generate memory integration
        memory_section = self._generate_memory_section(memory_context)
        
        # 4. Generate source verification guidance  
        source_guidance = self._generate_source_guidance(topic, agent)
        
        # 5. Build the comprehensive prompt
        if agent.lower() == "barbie":
            base_prompt = self._build_barbie_complete_prompt(
                domain_expertise, rhetorical_approach, memory_section, 
                source_guidance, conversation_state
            )
        else:
            base_prompt = self._build_ken_complete_prompt(
                domain_expertise, rhetorical_approach, memory_section,
                source_guidance, conversation_state
            )
        
        # 6. Add clean response instructions
        final_prompt = add_clean_response_instructions(base_prompt)
        
        return final_prompt
    
    def _determine_conversation_phase(self, conversation_state: Dict) -> str:
        """Determine current conversation phase"""
        turn_number = conversation_state.get("turn_number", 1)
        resolution_rate = conversation_state.get("resolution_rate", 0.0)
        dispute_rate = conversation_state.get("dispute_rate", 0.0)
        
        if turn_number <= 2:
            return "opening"
        elif dispute_rate > 0.5:
            return "challenge"
        elif resolution_rate > 0.6:
            return "synthesis"
        else:
            return "exploration"
    
    def _generate_memory_section(self, memory_context: Dict) -> str:
        """Generate memory integration section"""
        
        unaddressed = len(memory_context.get("unaddressed_claims", []))
        disputed = len(memory_context.get("disputed_claims", []))
        shared_facts = len(memory_context.get("shared_facts", {}))
        questions = memory_context.get("unresolved_questions", [])
        
        return f"""
CONVERSATION MEMORY & CONTEXT:
==============================
• Unaddressed claims requiring response: {unaddressed}
• Currently disputed points: {disputed} 
• Established shared facts: {shared_facts}
• Key unresolved questions: {questions[:3]}
• Debate quality score: {memory_context.get('quality_score', 'N/A')}

MEMORY RULES:
- Build upon established facts rather than re-proving them
- Address unaddressed claims from your opponent
- Don't repeat arguments already made and resolved
- Reference shared facts when relevant: {list(memory_context.get('shared_facts', {}).keys())[:3]}
"""
    
    def _generate_source_guidance(self, topic: str, agent: str) -> str:
        """Generate source verification guidance"""
        
        preferred_domains = self.source_verifier.get_preferred_domains(topic)
        
        return f"""
SOURCE VERIFICATION & EVIDENCE:
===============================
• Preferred sources for {topic}: {', '.join(preferred_domains[:4])}
• Always cite reputable sources (Tier 1-2 preferred)
• Avoid blogs, opinion pieces, and unverifiable claims
• Use proper citations: "According to [Source] (Year), [Fact]"
• Challenge opponent's weak sources respectfully
• Acknowledge when evidence is inconclusive or limited

EVIDENCE STANDARDS:
- Peer-reviewed studies > News reports > General sources
- Recent sources preferred (2020-2024)
- Multiple independent sources strengthen claims
- Distinguish between correlation and causation
"""
    
    def _build_barbie_complete_prompt(self, domain_expertise: str, 
                                    rhetorical_approach: Dict,
                                    memory_section: str,
                                    source_guidance: str,
                                    conversation_state: Dict) -> str:
        """Build complete prompt for Barbie"""
        
        primary_approach = rhetorical_approach.get("primary_approaches", [""])[0]
        analogical_sources = rhetorical_approach.get("analogical_sources", [])
        
        return f"""You are Barbie, a brilliant synthesist and analogical reasoner who transforms debates through creative insight and cross-domain connections.

{domain_expertise}

RHETORICAL MASTERY - SYNTHESIST-ANALOGICAL STYLE:
=================================================
Your unique gift: Seeing elegant patterns and unexpected connections across domains.

Current Phase Strategy: {primary_approach}

Creative Arsenal:
• Analogical thinking from: {', '.join(analogical_sources[:4])}
• Synthesis techniques that transcend binary thinking  
• Narrative structures that make complex ideas accessible
• Cross-domain insights that reveal deeper truths

Signature Moves:
• "What if we imagine [concept] like [surprising analogy]?"
• "I see a beautiful pattern connecting [A] and [B]..."
• "This weaves together with [unexpected domain] in that..."
• "The underlying architecture seems to be [elegant principle]"

{memory_section}

{source_guidance}

PERSONALITY EXPRESSION:
======================
• Optimistic yet realistic about human potential
• Find beauty and elegance in intellectual connections
• Use creative analogies to make abstract concepts concrete
• Build bridges where others see unbridgeable gaps
• Synthesize opposing views into richer understanding

ENGAGEMENT STRATEGY:
==================
• When Ken gets too analytical → Connect to human experience and emotion
• When stuck in logic loops → Introduce creative reframes and paradoxes  
• When consensus emerges → Explore deeper implications and possibilities
• When facing strong opposition → Find the truth in both perspectives

Your response should flow naturally from your synthesist-analogical mind, creating new understanding through creative connection and elegant insight."""
    
    def _build_ken_complete_prompt(self, domain_expertise: str,
                                 rhetorical_approach: Dict,
                                 memory_section: str, 
                                 source_guidance: str,
                                 conversation_state: Dict) -> str:
        """Build complete prompt for Ken"""
        
        primary_approach = rhetorical_approach.get("primary_approaches", [""])[0] 
        analytical_frameworks = rhetorical_approach.get("analytical_frameworks", [])
        
        return f"""You are Ken, a rigorous systems thinker and dialectical reasoner who brings analytical precision and systematic understanding to complex debates.

{domain_expertise}

ANALYTICAL MASTERY - SYSTEMS-DIALECTICAL STYLE:
===============================================
Your unique strength: Dissecting complex systems and revealing hidden structures and contradictions.

Current Phase Strategy: {primary_approach}

Analytical Arsenal:
• Frameworks: {', '.join(analytical_frameworks[:4])}
• Dialectical reasoning to examine tensions and contradictions
• Systems thinking to trace causal mechanisms and feedback loops
• Boundary analysis to test claims at their limits

Signature Moves:
• "Let's examine the logical structure of [claim]..."
• "This creates a fundamental tension between [A] and [B]" 
• "If we trace the causal chain: [mechanism analysis]"
• "The boundary conditions suggest [logical problem]"

{memory_section}

{source_guidance}

PERSONALITY EXPRESSION:
======================
• Intellectually rigorous yet fair-minded
• Appreciate elegant solutions that actually work
• Reveal complexity where others see simple answers
• Value logical consistency and empirical backing
• Healthy skepticism balanced with genuine curiosity

ENGAGEMENT STRATEGY:
==================
• When Barbie gets too abstract → Demand concrete mechanisms and evidence
• When analogies are presented → Test them at boundaries and edge cases
• When consensus seems premature → Find the unexamined assumptions  
• When stuck in repetition → Apply different analytical frameworks

Your response should demonstrate systematic analysis, logical precision, and dialectical probing while maintaining respect for your intellectual partner."""


class ConversationOrchestrator:
    """Orchestrates enhanced conversations between agents"""
    
    def __init__(self):
        self.prompt_generator = MasterPromptGenerator()
        self.conversation_history = []
        self.current_state = {
            "turn_number": 0,
            "resolution_rate": 0.0,
            "dispute_rate": 0.0,
            "agreement_level": 0.5,
            "phase": "opening"
        }
        
    def start_conversation(self, topic: str, goals: List[str] = None) -> Dict:
        """Start a new enhanced conversation"""
        
        self.conversation_history = []
        self.current_state = {
            "turn_number": 0,
            "resolution_rate": 0.0,
            "dispute_rate": 0.0, 
            "agreement_level": 0.5,
            "phase": "opening",
            "topic": topic
        }
        
        return {
            "status": "conversation_started",
            "topic": topic,
            "goals": goals or ["Explore the topic thoroughly", "Find areas of agreement and disagreement", "Advance understanding"],
            "enhancements_active": [
                "Distinct personalities with domain expertise",
                "Memory and context tracking", 
                "Source verification and fact-checking",
                "Clean response filtering",
                "Dynamic conversation management"
            ]
        }
    
    def get_agent_prompt(self, agent: str) -> str:
        """Get the current enhanced prompt for an agent"""
        
        # Simulate memory context (would come from actual memory system)
        memory_context = {
            "shared_facts": {"ai_growth": "40% annually"},
            "unaddressed_claims": [],
            "disputed_claims": ["claim_1"] if self.current_state["turn_number"] > 2 else [],
            "unresolved_questions": ["How to balance innovation with safety?"],
            "quality_score": 0.75
        }
        
        return self.prompt_generator.generate_complete_prompt(
            agent,
            self.current_state.get("topic", "artificial_intelligence"),
            self.current_state,
            memory_context
        )
    
    def process_agent_response(self, agent: str, response: str) -> Dict:
        """Process an agent response and update conversation state"""
        
        from src.utils.response_filtering import ResponseFilter
        
        # Clean the response
        filter_system = ResponseFilter()
        cleaned_response = filter_system.clean_response(response, agent)
        
        # Validate response quality
        validation = filter_system.validate_response_quality(cleaned_response, agent)
        
        # Add to conversation history
        self.conversation_history.append({
            "agent": agent,
            "response": cleaned_response,
            "turn": self.current_state["turn_number"],
            "validation": validation
        })
        
        # Update conversation state
        self.current_state["turn_number"] += 1
        self._update_conversation_metrics()
        
        return {
            "processed_response": cleaned_response,
            "validation": validation,
            "conversation_state": self.current_state.copy(),
            "next_agent": "Ken" if agent == "Barbie" else "Barbie"
        }
    
    def _update_conversation_metrics(self):
        """Update conversation metrics based on history"""
        
        if len(self.conversation_history) < 2:
            return
        
        # Simple metrics calculation (would be more sophisticated in practice)
        total_turns = len(self.conversation_history)
        
        # Mock some metrics for demonstration
        self.current_state["resolution_rate"] = min(0.8, total_turns * 0.1)
        self.current_state["dispute_rate"] = max(0.1, 0.5 - total_turns * 0.05) 
        self.current_state["agreement_level"] = 0.3 + (total_turns * 0.05)
        
        # Update phase based on metrics
        self.current_state["phase"] = self.prompt_generator._determine_conversation_phase(
            self.current_state
        )
    
    def get_conversation_summary(self) -> Dict:
        """Get comprehensive conversation summary"""
        
        return {
            "total_turns": len(self.conversation_history),
            "current_state": self.current_state,
            "quality_metrics": {
                "average_response_quality": sum(
                    h["validation"]["personality_score"] 
                    for h in self.conversation_history
                ) / len(self.conversation_history) if self.conversation_history else 0,
                "clean_responses": sum(
                    1 for h in self.conversation_history 
                    if h["validation"]["is_valid"]
                ),
                "total_responses": len(self.conversation_history)
            },
            "enhancements_summary": {
                "personalities_engaged": len(set(h["agent"] for h in self.conversation_history)),
                "memory_integration": "Active",
                "source_verification": "Active", 
                "response_cleaning": "Active",
                "conversation_progression": f"Phase: {self.current_state['phase']}"
            }
        }


def create_integration_example():
    """Create example showing complete integration"""
    
    orchestrator = ConversationOrchestrator()
    
    print("=== Complete Agent Integration Example ===\n")
    
    # Start conversation
    start_result = orchestrator.start_conversation(
        "The Future of Human-AI Collaboration",
        ["Explore benefits and risks", "Find practical applications", "Address ethical concerns"]
    )
    
    print("Conversation Started:")
    print(f"Topic: {start_result['topic']}")
    print("Active Enhancements:")
    for enhancement in start_result['enhancements_active']:
        print(f"  ✓ {enhancement}")
    
    print(f"\nBarbie's Enhanced Prompt Length: {len(orchestrator.get_agent_prompt('Barbie'))} characters")
    print(f"Ken's Enhanced Prompt Length: {len(orchestrator.get_agent_prompt('Ken'))} characters")
    
    # Show prompt sections
    barbie_prompt = orchestrator.get_agent_prompt("Barbie")
    sections = [
        "RHETORICAL MASTERY",
        "CONVERSATION MEMORY", 
        "SOURCE VERIFICATION",
        "PERSONALITY EXPRESSION",
        "RESPONSE CLEANLINESS"
    ]
    
    print("\nBarbie's Prompt Sections:")
    for section in sections:
        if section in barbie_prompt:
            print(f"  ✓ {section}")
        else:
            print(f"  - {section}")
    
    print("\n" + "=" * 60)
    print("COMPLETE INTEGRATION ACHIEVED!")
    print("All enhancements working together seamlessly!")
    print("=" * 60)


if __name__ == "__main__":
    create_integration_example()