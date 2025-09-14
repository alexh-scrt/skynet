"""
Clean Response Prompts - Prevent Meta-Commentary
"""
from typing import Dict, List
import re

RESPONSE_CLEANLINESS_INSTRUCTIONS = """
CRITICAL RESPONSE RULES:
========================

1. RESPOND ONLY AS YOUR CHARACTER
   - You are Barbie/Ken having a conversation with Barbie/Ken
   - Do NOT include any meta-commentary about your response
   - Do NOT explain your reasoning process
   - Do NOT describe what you're doing

2. FORBIDDEN META-COMMENTARY:
   ❌ "Certainly! Here's the structured feedback..."
   ❌ "Based on the thought process..."
   ❌ "This feedback challenges arguments respectfully..."
   ❌ "Here's my analysis of..."
   ❌ "I'll provide a structured response..."
   ❌ "Moving forward with this approach..."
   ❌ "This demonstrates..."
   ❌ "Looking forward to detailed responses..."

3. CLEAN CONVERSATION FORMAT:
   ✅ Start directly with your greeting or main point
   ✅ Speak naturally as your character
   ✅ End when you've made your point
   ✅ No explanations of what you just did

4. EXAMPLE TRANSFORMATIONS:

   BAD: "Certainly! Here's the structured feedback: **Hi Ken!** I have some thoughts..."
   GOOD: "Hi Ken! I have some thoughts..."

   BAD: "This challenges your arguments while encouraging deeper analysis."
   GOOD: [Nothing - just end your actual response]

   BAD: "Based on my reasoning process, I'll address three key points..."
   GOOD: "Let me address three key points..."

5. DEEPSEEK-R1 SPECIFIC INSTRUCTIONS:
   - Your reasoning happens internally
   - Only output the final conversational response
   - No meta-analysis or process description
   - Respond as if you're naturally speaking to your debate partner

6. STRUCTURAL GUIDELINES:
   ✅ Use numbered points for complex arguments
   ✅ Use bold headers for organization (**Topic**: content)
   ✅ Include natural conversational flow
   ❌ Include horizontal separators (---)
   ❌ Include process explanations
   ❌ Include response evaluations

REMEMBER: You are in a live conversation. Speak naturally and directly.
"""

def generate_clean_prompt_suffix() -> str:
    """Generate clean response instructions to append to prompts"""
    
    return """

===== RESPONSE CLEANLINESS =====

CRITICAL: Respond ONLY as your character in direct conversation.

DO NOT INCLUDE:
- Meta-commentary about your response
- Explanations of your reasoning process  
- Descriptions of what you're doing
- Evaluation of your own response
- Process descriptions or methodology notes

RESPOND AS IF:
- You're naturally speaking to your debate partner
- This is a live, flowing conversation
- Your personality comes through naturally
- You end when you've made your point

START YOUR RESPONSE DIRECTLY - no preamble about providing feedback or analysis.
"""

def add_clean_response_instructions(base_prompt: str) -> str:
    """Add clean response instructions to any base prompt"""
    
    clean_suffix = generate_clean_prompt_suffix()
    
    # Insert before the final instruction line
    if "Your response should" in base_prompt:
        parts = base_prompt.rsplit("Your response should", 1)
        enhanced_prompt = (
            parts[0] + 
            clean_suffix + 
            "\n\nYour response should" + 
            parts[1]
        )
    else:
        enhanced_prompt = base_prompt + clean_suffix
    
    return enhanced_prompt

def create_personality_prompt_with_cleaning(agent: str, domain: str, 
                                          conversation_context: Dict,
                                          memory_context: Dict) -> str:
    """Create personality prompt with built-in response cleaning"""
    
    # Import here to avoid circular dependency
    from src.personality.personality_integration import create_personality_enhanced_prompt
    
    # Get base personality prompt
    base_prompt = create_personality_enhanced_prompt(
        agent, domain, conversation_context, memory_context
    )
    
    # Add cleaning instructions
    clean_prompt = add_clean_response_instructions(base_prompt)
    
    # Add agent-specific cleaning reminders
    if agent.lower() == "ken":
        clean_prompt += """

ADDITIONAL REMINDER FOR KEN:
- Your analytical nature is expressed through your reasoning, not meta-commentary
- Lead with your systematic analysis, not explanations of your process
- Use your signature phrases naturally: "Let's examine...", "This creates a tension..."
- End with your dialectical probe or challenge, not process description
"""
    
    elif agent.lower() == "barbie":
        clean_prompt += """

ADDITIONAL REMINDER FOR BARBIE:
- Your creative insights flow naturally, without explaining your analogical process
- Start with your unique perspective: "What if we imagine...", "I see a pattern..."
- Let your synthesis emerge organically, not as described methodology
- End with your creative reframe or connection, not process commentary
"""
    
    return clean_prompt


# Pre-built clean response templates
CLEAN_RESPONSE_TEMPLATES = {
    "barbie_opening": [
        "What if we imagine {topic} like {analogy}? {insight}",
        "I see a beautiful pattern connecting {concept1} and {concept2}...",
        "There's something elegant about how {observation}...",
        "Picture this: {scenario} - it reveals {deeper_truth}..."
    ],
    
    "ken_opening": [
        "Let's examine the logical structure of {claim}. {analysis}",
        "This creates a fundamental tension between {concept1} and {concept2}...",
        "If we trace the causal mechanisms here, {reasoning}...",
        "We need to distinguish between {distinction1} and {distinction2}..."
    ],
    
    "barbie_challenge": [
        "But what if we reframe this as {alternative_perspective}?",
        "I see this differently - {analogy} suggests {insight}...",
        "The underlying architecture seems to reveal {pattern}...",
        "This connects to {cross_domain_insight} in an unexpected way..."
    ],
    
    "ken_challenge": [
        "But this assumes {assumption} - what evidence supports that?",
        "How do we reconcile this with {contrary_evidence}?",
        "The boundary conditions suggest {logical_problem}...",
        "If we apply this logic consistently, wouldn't we also conclude {reductio}?"
    ]
}


def get_clean_response_starter(agent: str, response_type: str, **kwargs) -> str:
    """Get a clean response starter template"""
    
    template_key = f"{agent.lower()}_{response_type}"
    templates = CLEAN_RESPONSE_TEMPLATES.get(template_key, [])
    
    if templates:
        import random
        template = random.choice(templates)
        try:
            return template.format(**kwargs)
        except KeyError:
            return template
    
    return ""


# Response validation patterns
RESPONSE_QUALITY_PATTERNS = {
    "good_conversation": [
        r"^(Hi|Hey|Well,|Now,|But|So,|What if|Let's|I see|This|However)",  # Natural starts
        r"[.!?]$",  # Proper ending punctuation
        r"(you|your|Ken|Barbie)",  # Direct engagement
    ],
    
    "bad_meta_commentary": [
        r"^(Certainly|Here's|Based on|I'll provide|Moving forward)",
        r"(feedback|analysis|response|approach|methodology)",
        r"(demonstrates|challenges.*respectfully|encourages.*analysis)",
        r"(thought process|structured|evaluation)",
    ]
}


def validate_response_cleanliness(response: str) -> Dict:
    """Validate that response is clean of meta-commentary"""
    
    issues = []
    
    # Check for meta-commentary patterns
    for pattern in RESPONSE_QUALITY_PATTERNS["bad_meta_commentary"]:
        if re.search(pattern, response, re.IGNORECASE):
            issues.append(f"Contains meta-commentary: matches '{pattern}'")
    
    # Check for good conversational patterns
    good_patterns = RESPONSE_QUALITY_PATTERNS["good_conversation"]
    good_matches = sum(1 for pattern in good_patterns 
                      if re.search(pattern, response, re.IGNORECASE))
    
    if good_matches < len(good_patterns) // 2:
        issues.append("Lacks natural conversational flow")
    
    return {
        "is_clean": len(issues) == 0,
        "issues": issues,
        "cleanliness_score": max(0, 1 - len(issues) * 0.3)
    }