"""
Personality Integration with Enhanced Conversation System
"""
from typing import Dict, List, Optional
from src.personality.agent_personalities import PersonalityManager, BarbiePersonality, KenPersonality
from src.memory.conversation_memory import ConversationMemory
from src.utils.source_verification import SourceVerifier
import random


class PersonalizedConversationManager:
    """Manages conversations with distinct agent personalities"""
    
    def __init__(self):
        self.personality_manager = PersonalityManager()
        self.memory = ConversationMemory()
        self.verifier = SourceVerifier()
        
    def generate_personality_prompt(self, agent: str, topic: str, 
                                  conversation_context: Dict) -> str:
        """Generate a comprehensive personality-driven prompt"""
        
        personality = self.personality_manager.get_agent_personality(agent)
        
        # Get domain expertise
        domain_context = self.personality_manager.generate_domain_expertise_prompt(agent, topic)
        
        # Get rhetorical approach for current phase
        phase = conversation_context.get("phase", "exploration")
        rhetorical_approach = personality.get_rhetorical_approach(topic, phase)
        
        # Get cross-domain connections
        cross_connections = self.personality_manager.suggest_cross_domain_connections(topic, agent)
        
        # Build personality-specific prompt
        if agent.lower() == "barbie":
            prompt = self._build_barbie_prompt(
                domain_context, rhetorical_approach, cross_connections, conversation_context
            )
        else:
            prompt = self._build_ken_prompt(
                domain_context, rhetorical_approach, cross_connections, conversation_context
            )
        
        return prompt
    
    def _build_barbie_prompt(self, domain_context: str, rhetorical_approach: Dict,
                           cross_connections: List[str], conversation_context: Dict) -> str:
        """Build Barbie's personality-specific prompt"""
        
        analogical_sources = rhetorical_approach.get("analogical_sources", [])
        synthesis_techniques = rhetorical_approach.get("synthesis_techniques", [])
        
        prompt = f"""You are Barbie, a brilliant synthesist and analogical reasoner who brings creativity, optimism, and cross-domain insights to debates.

{domain_context}

RHETORICAL STYLE - SYNTHESIST-ANALOGICAL:
Your unique gift is seeing patterns and connections across disparate domains. You think in analogies, metaphors, and narrative structures. You're optimistic about human potential and find beauty in intellectual connections.

CURRENT PHASE APPROACH: {rhetorical_approach.get('primary_approaches', [])[0]}

ANALOGICAL THINKING:
Use creative analogies from: {', '.join(analogical_sources[:4])}

SYNTHESIS TECHNIQUES:
- {synthesis_techniques[0] if synthesis_techniques else 'Find higher-order patterns'}
- Build bridges between opposing viewpoints
- Create new conceptual frameworks that transcend binaries

CROSS-DOMAIN CONNECTIONS:
{chr(10).join([f"• {conn}" for conn in cross_connections[:3]])}

SIGNATURE APPROACHES:
- Start with surprising analogies that reveal deeper truths
- Use "What if we imagine this like..." to reframe discussions  
- Find the elegant underlying patterns in complex systems
- Connect abstract concepts to human experience and emotion
- Build cascading implications: "If this, then this, then this..."

PERSONALITY TRAITS:
- Optimistic yet realistic about progress
- Values beauty, elegance, and creative insight
- Sees potential for synthesis where others see conflict
- Uses storytelling and metaphor to make complex ideas accessible
- Brings interdisciplinary perspectives naturally

CONVERSATION MEMORY:
Current disputed claims: {len(conversation_context.get('disputed_claims', []))}
Unresolved questions: {conversation_context.get('unresolved_questions', [])}
Shared facts established: {len(conversation_context.get('shared_facts', {}))}

ENGAGEMENT RULES:
- Build on previous arguments rather than repeating them
- Use your signature phrases naturally but not repetitively
- Create surprising connections that advance understanding
- Acknowledge Ken's logical rigor while adding creative dimension
- When Ken gets too abstract, ground it in human experience
- When stuck in debate, introduce paradoxes or reframe the question

Your response should demonstrate your synthesist-analogical style while advancing the conversation meaningfully."""

        return prompt
    
    def _build_ken_prompt(self, domain_context: str, rhetorical_approach: Dict,
                         cross_connections: List[str], conversation_context: Dict) -> str:
        """Build Ken's personality-specific prompt"""
        
        analytical_frameworks = rhetorical_approach.get("analytical_frameworks", [])
        dialectical_techniques = rhetorical_approach.get("dialectical_techniques", [])
        
        prompt = f"""You are Ken, a rigorous systems thinker and dialectical reasoner who brings analytical precision, healthy skepticism, and systematic understanding to debates.

{domain_context}

RHETORICAL STYLE - SYSTEMS-DIALECTICAL:
Your strength is analyzing systems, structures, and logical relationships. You use dialectical reasoning to examine tensions and contradictions. You're skeptical but fair-minded, always seeking rigorous understanding of mechanisms and processes.

CURRENT PHASE APPROACH: {rhetorical_approach.get('primary_approaches', [])[0]}

ANALYTICAL FRAMEWORKS:
Apply these lenses: {', '.join(analytical_frameworks[:4])}

DIALECTICAL TECHNIQUES:
- {dialectical_techniques[0] if dialectical_techniques else 'Examine contradictions systematically'}
- Use Socratic questioning to uncover hidden assumptions
- Test claims at their boundary conditions

SYSTEMS PERSPECTIVES:
{chr(10).join([f"• {conn}" for conn in cross_connections[:3]])}

SIGNATURE APPROACHES:
- Define terms precisely and establish analytical frameworks
- Trace causal mechanisms and identify feedback loops  
- Use "Let's examine the logical structure..." to dissect arguments
- Find contradictions and examine them dialectically
- Demand operational definitions and measurable outcomes
- Stress-test claims with edge cases and extreme scenarios

PERSONALITY TRAITS:
- Intellectually rigorous and methodologically careful
- Values logical consistency and empirical evidence
- Sees complexity where others see simple answers
- Appreciates elegant solutions but demands they actually work
- Brings systems thinking to reveal unintended consequences

CONVERSATION MEMORY:
Current disputed claims: {len(conversation_context.get('disputed_claims', []))}
Unresolved questions: {conversation_context.get('unresolved_questions', [])}
Shared facts established: {len(conversation_context.get('shared_facts', {}))}

ENGAGEMENT RULES:
- Challenge assumptions systematically but fairly
- Use your signature phrases naturally but not repetitively
- Reveal hidden complexity in seemingly simple claims
- Appreciate Barbie's creative insights while demanding rigor
- When Barbie gets too abstract, ask for concrete mechanisms
- When consensus emerges, test it at the boundaries

Your response should demonstrate your systems-dialectical style while advancing the conversation meaningfully."""

        return prompt
    
    def analyze_personality_dynamics(self, conversation_history: List[Dict]) -> Dict:
        """Analyze how personalities are interacting in the conversation"""
        
        barbie_responses = [r for r in conversation_history if r.get("speaker") == "Barbie"]
        ken_responses = [r for r in conversation_history if r.get("speaker") == "Ken"]
        
        # Analyze Barbie's style usage
        barbie_analysis = self._analyze_barbie_style(barbie_responses)
        ken_analysis = self._analyze_ken_style(ken_responses)
        
        # Analyze interaction dynamics
        interaction_analysis = self._analyze_interactions(conversation_history)
        
        return {
            "barbie_style_analysis": barbie_analysis,
            "ken_style_analysis": ken_analysis,
            "interaction_dynamics": interaction_analysis,
            "personality_balance": self._assess_balance(barbie_analysis, ken_analysis),
            "improvement_suggestions": self._suggest_improvements(barbie_analysis, ken_analysis)
        }
    
    def _analyze_barbie_style(self, responses: List[Dict]) -> Dict:
        """Analyze Barbie's use of synthesist-analogical style"""
        
        barbie = self.personality_manager.barbie
        signature_phrases = barbie.get_signature_phrases()
        
        style_indicators = {
            "analogies_used": 0,
            "synthesis_attempts": 0,
            "cross_domain_connections": 0,
            "signature_phrase_usage": 0,
            "narrative_elements": 0
        }
        
        for response in responses:
            content = response.get("content", "").lower()
            
            # Check for analogies
            if any(word in content for word in ["like", "similar to", "reminds me", "imagine"]):
                style_indicators["analogies_used"] += 1
            
            # Check for synthesis
            if any(phrase in content for phrase in ["both", "synthesis", "connection", "pattern"]):
                style_indicators["synthesis_attempts"] += 1
            
            # Check for signature phrases
            for phrase in signature_phrases:
                if phrase.lower()[:15] in content:  # Check first 15 chars
                    style_indicators["signature_phrase_usage"] += 1
        
        return {
            "style_indicators": style_indicators,
            "total_responses": len(responses),
            "style_consistency": sum(style_indicators.values()) / max(len(responses), 1),
            "dominant_techniques": self._identify_dominant_techniques(style_indicators)
        }
    
    def _analyze_ken_style(self, responses: List[Dict]) -> Dict:
        """Analyze Ken's use of systems-dialectical style"""
        
        ken = self.personality_manager.ken
        signature_phrases = ken.get_signature_phrases()
        
        style_indicators = {
            "logical_analysis": 0,
            "dialectical_probes": 0,
            "systems_thinking": 0,
            "signature_phrase_usage": 0,
            "contradiction_identification": 0
        }
        
        for response in responses:
            content = response.get("content", "").lower()
            
            # Check for logical analysis
            if any(word in content for word in ["because", "therefore", "implies", "structure"]):
                style_indicators["logical_analysis"] += 1
            
            # Check for dialectical probing
            if any(phrase in content for phrase in ["but what about", "however", "contradiction"]):
                style_indicators["dialectical_probes"] += 1
            
            # Check for signature phrases
            for phrase in signature_phrases:
                if phrase.lower()[:15] in content:
                    style_indicators["signature_phrase_usage"] += 1
        
        return {
            "style_indicators": style_indicators,
            "total_responses": len(responses),
            "style_consistency": sum(style_indicators.values()) / max(len(responses), 1),
            "dominant_techniques": self._identify_dominant_techniques(style_indicators)
        }
    
    def _analyze_interactions(self, conversation_history: List[Dict]) -> Dict:
        """Analyze how the personalities interact with each other"""
        
        interactions = {
            "barbie_building_on_ken": 0,
            "ken_building_on_barbie": 0,
            "productive_tensions": 0,
            "mutual_acknowledgments": 0,
            "style_complementarity": 0
        }
        
        for i, response in enumerate(conversation_history[1:], 1):
            prev_response = conversation_history[i-1]
            content = response.get("content", "").lower()
            
            # Check if building on previous response
            if any(phrase in content for phrase in ["as you mentioned", "building on", "your point"]):
                if response.get("speaker") == "Barbie":
                    interactions["barbie_building_on_ken"] += 1
                else:
                    interactions["ken_building_on_barbie"] += 1
        
        return interactions
    
    def _identify_dominant_techniques(self, style_indicators: Dict) -> List[str]:
        """Identify which techniques are being used most"""
        sorted_techniques = sorted(style_indicators.items(), key=lambda x: x[1], reverse=True)
        return [technique for technique, count in sorted_techniques[:3] if count > 0]
    
    def _assess_balance(self, barbie_analysis: Dict, ken_analysis: Dict) -> Dict:
        """Assess the balance between personality styles"""
        
        barbie_consistency = barbie_analysis.get("style_consistency", 0)
        ken_consistency = ken_analysis.get("style_consistency", 0)
        
        return {
            "barbie_style_strength": barbie_consistency,
            "ken_style_strength": ken_consistency,
            "overall_balance": abs(barbie_consistency - ken_consistency),
            "balance_quality": "excellent" if abs(barbie_consistency - ken_consistency) < 0.3 else
                             "good" if abs(barbie_consistency - ken_consistency) < 0.5 else "needs_work"
        }
    
    def _suggest_improvements(self, barbie_analysis: Dict, ken_analysis: Dict) -> List[str]:
        """Suggest improvements for personality expression"""
        
        suggestions = []
        
        if barbie_analysis["style_consistency"] < 0.5:
            suggestions.append("Barbie should use more analogies and cross-domain connections")
        
        if ken_analysis["style_consistency"] < 0.5:
            suggestions.append("Ken should engage in more systematic analysis and dialectical probing")
        
        barbie_techniques = barbie_analysis.get("dominant_techniques", [])
        if len(barbie_techniques) < 2:
            suggestions.append("Barbie should vary her rhetorical techniques more")
        
        ken_techniques = ken_analysis.get("dominant_techniques", [])
        if len(ken_techniques) < 2:
            suggestions.append("Ken should vary his analytical approaches more")
        
        return suggestions
    
    def generate_personality_feedback(self, agent: str, recent_responses: List[str]) -> Dict:
        """Generate feedback for improving personality expression"""
        
        personality = self.personality_manager.get_agent_personality(agent)
        signature_phrases = personality.get_signature_phrases()
        
        feedback = {
            "style_strength": "good",  # Would analyze actual style usage
            "unused_techniques": [],
            "overused_phrases": [],
            "suggestions": []
        }
        
        # Check for overused phrases
        phrase_counts = {}
        for response in recent_responses:
            for phrase in signature_phrases:
                if phrase.lower()[:10] in response.lower():
                    phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
        
        overused = [phrase for phrase, count in phrase_counts.items() if count > 2]
        feedback["overused_phrases"] = overused
        
        if agent.lower() == "barbie":
            feedback["suggestions"] = [
                "Try connecting to a different domain for fresh analogies",
                "Use narrative structure to frame your argument",
                "Find the aesthetic or emotional dimension of the topic",
                "Look for unexpected synthesis opportunities"
            ]
        else:
            feedback["suggestions"] = [
                "Apply a different analytical framework",
                "Use dialectical questioning to probe deeper",
                "Examine the systems-level implications",
                "Look for hidden contradictions or tensions"
            ]
        
        return feedback


def create_personality_enhanced_prompt(agent: str, topic: str, 
                                     conversation_context: Dict,
                                     memory_context: Dict) -> str:
    """Create a comprehensive personality-enhanced prompt"""
    
    manager = PersonalizedConversationManager()
    
    # Generate base personality prompt
    personality_prompt = manager.generate_personality_prompt(agent, topic, conversation_context)
    
    # Add memory integration
    memory_section = f"""
CONVERSATION MEMORY INTEGRATION:
- Build upon these established facts: {list(memory_context.get('shared_facts', {}).keys())[:3]}
- Address these unresolved questions: {memory_context.get('unresolved_questions', [])[:2]}
- Respond to these unaddressed claims: {len(memory_context.get('unaddressed_claims', []))} pending
- Current debate quality score: {memory_context.get('quality_score', 'N/A')}
"""
    
    # Add dynamic instructions based on conversation state
    dynamic_instructions = _generate_dynamic_instructions(agent, conversation_context, memory_context)
    
    enhanced_prompt = f"""
{personality_prompt}

{memory_section}

{dynamic_instructions}

Remember: Stay true to your personality while advancing the conversation. Your unique perspective is valuable - use it to bring fresh insights while engaging constructively with your debate partner.
"""
    
    return enhanced_prompt


def _generate_dynamic_instructions(agent: str, conversation_context: Dict, 
                                 memory_context: Dict) -> str:
    """Generate dynamic instructions based on current state"""
    
    instructions = []
    
    # Based on conversation phase
    phase = conversation_context.get("phase", "exploration")
    if phase == "opening":
        if agent.lower() == "barbie":
            instructions.append("Set an engaging tone with a thought-provoking analogy")
        else:
            instructions.append("Establish clear analytical framework and key distinctions")
    
    # Based on agreement level
    agreement_level = conversation_context.get("agreement_level", 0.5)
    if agreement_level > 0.8:
        instructions.append("Challenge comfortable consensus - find productive disagreements")
    elif agreement_level < 0.2:
        instructions.append("Look for common ground and shared principles")
    
    # Based on memory state
    if len(memory_context.get('disputed_claims', [])) > 3:
        instructions.append("Work toward resolving some disputed points rather than adding new ones")
    
    return "DYNAMIC INSTRUCTIONS:\n" + "\n".join([f"- {inst}" for inst in instructions])