"""
Test clean response system - eliminate meta-commentary
"""
import sys
from pathlib import Path

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.response_filtering import ResponseFilter, ConversationFormatter
from src.prompts.clean_response_prompts import (
    add_clean_response_instructions,
    validate_response_cleanliness,
    CLEAN_RESPONSE_TEMPLATES,
    get_clean_response_starter
)


def test_response_filtering():
    """Test the response filtering system with various problematic inputs"""
    
    print("=== Response Filtering Test ===\n")
    
    filter_system = ResponseFilter()
    
    # Test cases with different types of meta-commentary
    test_cases = [
        {
            "name": "Ken's Original Problematic Response",
            "agent": "Ken",
            "raw_response": """
Certainly! Here's the structured feedback based on the thought process:

---

**Hi Barbie, this is Ken!**

I appreciate your thought-provoking response, but I have some reservations
that I'd like to discuss.

1. **Duality in Societal Norms**: How do you reconcile these complexities?

2. **Motivations of Simulators**: Can you provide concrete evidence?

---

This feedback challenges Barbie's arguments respectfully while encouraging
her to provide more substantial evidence and considerations.
"""
        },
        {
            "name": "Barbie with Meta-Commentary",
            "agent": "Barbie", 
            "raw_response": """
Based on my creative analysis, I'll provide an analogical response:

Hi Ken! What if we imagine consciousness like a river system?

This demonstrates my synthesist approach to complex philosophical questions.
I hope this creative perspective helps advance our dialogue.
"""
        },
        {
            "name": "Clean Response (Should Pass Through)",
            "agent": "Ken",
            "raw_response": """
Hi Barbie!

Let's examine the logical structure of consciousness. If we distinguish between 
phenomenological experience and computational processing, we can trace the 
causal mechanisms more clearly.

But this creates a fundamental tension - how do we bridge the explanatory gap 
between neural activity and subjective experience?
"""
        },
        {
            "name": "Mixed Content",
            "agent": "Barbie",
            "raw_response": """
Here's my structured creative analysis:

What if we imagine AI development like biological evolution? Just as species 
adapt through environmental pressures, AI systems evolve through data and 
feedback loops.

This analogy reveals deeper patterns about emergence and complexity.

The underlying architecture seems to mirror natural selection processes.

This demonstrates the power of cross-domain thinking in understanding technology.
"""
        }
    ]
    
    for test_case in test_cases:
        print(f"Test Case: {test_case['name']}")
        print("-" * 50)
        
        raw = test_case['raw_response'].strip()
        agent = test_case['agent']
        
        print("BEFORE:")
        print(raw[:200] + "..." if len(raw) > 200 else raw)
        
        cleaned = filter_system.clean_response(raw, agent)
        print(f"\nAFTER ({len(cleaned.split())} words):")
        print(cleaned)
        
        # Validate cleanliness
        validation = filter_system.validate_response_quality(cleaned, agent)
        print(f"\nValidation: {'✓ CLEAN' if validation['is_valid'] else '✗ ISSUES'}")
        if validation['issues']:
            for issue in validation['issues']:
                print(f"  - {issue}")
        
        print("\n" + "=" * 60 + "\n")


def test_clean_prompt_generation():
    """Test clean prompt generation"""
    
    print("=== Clean Prompt Generation Test ===\n")
    
    # Show how prompts are enhanced with cleanliness instructions
    sample_base_prompt = """
You are Ken, a rigorous analytical thinker who brings precision to debates.

CURRENT TOPIC: Artificial Intelligence Ethics

Your response should demonstrate systematic analysis while engaging constructively.
"""
    
    # Add clean response instructions
    enhanced_prompt = add_clean_response_instructions(sample_base_prompt)
    
    print("BEFORE (Base Prompt):")
    print("-" * 40)
    print(sample_base_prompt)
    
    print("\nAFTER (With Cleanliness Instructions):")
    print("-" * 40)
    # Show just the added cleanliness section
    clean_section = enhanced_prompt.split("===== RESPONSE CLEANLINESS =====")[1]
    print("===== RESPONSE CLEANLINESS =====" + clean_section[:500] + "...")
    
    print(f"\nPrompt length increase: {len(enhanced_prompt) - len(sample_base_prompt)} characters")


def test_response_starters():
    """Test clean response starter templates"""
    
    print("\n=== Clean Response Starters ===\n")
    
    # Test different response types
    scenarios = [
        {
            "agent": "barbie",
            "type": "opening",
            "kwargs": {"topic": "consciousness", "analogy": "a symphony orchestra", 
                      "insight": "each instrument contributes to the overall experience"}
        },
        {
            "agent": "ken", 
            "type": "opening",
            "kwargs": {"claim": "AI consciousness", "analysis": "we need operational definitions"}
        },
        {
            "agent": "barbie",
            "type": "challenge", 
            "kwargs": {"alternative_perspective": "collaborative intelligence rather than replacement",
                      "analogy": "jazz improvisation", "insight": "creativity emerges from interaction"}
        },
        {
            "agent": "ken",
            "type": "challenge",
            "kwargs": {"assumption": "human-AI collaboration is always beneficial",
                      "contrary_evidence": "studies on automation bias"}
        }
    ]
    
    for scenario in scenarios:
        starter = get_clean_response_starter(
            scenario["agent"], 
            scenario["type"], 
            **scenario["kwargs"]
        )
        
        print(f"{scenario['agent'].title()} {scenario['type']} starter:")
        print(f"  \"{starter}\"")
        print()


def demonstrate_conversation_improvement():
    """Demonstrate how clean responses improve conversation flow"""
    
    print("=== Conversation Flow Improvement ===\n")
    
    # Before: With meta-commentary
    messy_conversation = [
        {
            "speaker": "Barbie",
            "content": "Based on my creative analysis approach, I'll explore consciousness. What if we imagine it like music? This demonstrates analogical thinking."
        },
        {
            "speaker": "Ken", 
            "content": "Certainly! Here's my structured feedback: **Hi Barbie!** I have reservations about musical analogies. This challenges your approach respectfully."
        }
    ]
    
    # After: Clean responses
    clean_conversation = [
        {
            "speaker": "Barbie",
            "content": "What if we imagine consciousness like music - not just individual notes, but the entire symphony emerging from the interaction of instruments?"
        },
        {
            "speaker": "Ken",
            "content": "Hi Barbie! But musical analogies assume consciousness has harmonic structure. How do we distinguish between metaphorical appeal and explanatory power?"
        }
    ]
    
    formatter = ConversationFormatter()
    
    print("BEFORE (With Meta-Commentary):")
    print("-" * 40)
    messy_log = formatter.format_conversation_log(messy_conversation, clean=False)
    print(messy_log)
    
    print("\nAFTER (Clean Responses):")
    print("-" * 40)
    clean_log = formatter.format_conversation_log(clean_conversation, clean=False)
    print(clean_log)
    
    print("\nImprovements:")
    print("-" * 40)
    print("✓ Natural conversation flow")
    print("✓ No meta-commentary distractions") 
    print("✓ Direct engagement between personalities")
    print("✓ Focus on actual ideas, not process")
    print("✓ Immersive debate experience")


def test_deepseek_specific_instructions():
    """Test instructions specifically for deepseek-r1 reasoning model"""
    
    print("\n=== DeepSeek-R1 Specific Instructions ===\n")
    
    deepseek_instructions = """
CRITICAL FOR DEEPSEEK-R1 REASONING MODEL:
=========================================

Your internal reasoning process happens in <think> tags - that's perfect!
But your RESPONSE should only contain the conversational content.

DO NOT OUTPUT:
❌ "Based on my reasoning..."
❌ "After analyzing this..."  
❌ "My thought process leads me to..."
❌ "Here's my structured analysis..."

DO OUTPUT:
✅ Direct conversational response as Ken/Barbie
✅ Natural personality expression
✅ Engaging debate content

EXAMPLE:
--------
Internal reasoning: <think>I need to challenge Barbie's analogy by examining its logical structure...</think>

Output: "But how do we test that analogy at its boundaries? If consciousness is like music, what happens during silence?"

NOT: "Based on my reasoning process, I'll challenge the analogy: But how do we test..."
"""
    
    print(deepseek_instructions)
    
    print("\nKey Points for DeepSeek Integration:")
    print("-" * 40)
    print("1. Reasoning happens internally (in <think> tags)")
    print("2. Output only the final conversational response") 
    print("3. No meta-commentary about the reasoning process")
    print("4. Respond naturally as the character")
    print("5. Let personality come through organically")


def show_validation_examples():
    """Show response validation in action"""
    
    print("\n=== Response Validation Examples ===\n")
    
    validation_tests = [
        ("Clean Response", "Hi Ken! Let's examine this fascinating paradox...", True),
        ("Meta-Commentary", "Here's my structured analysis: Hi Ken!", False),
        ("Process Description", "Based on my reasoning, I'll address three points...", False),
        ("Natural Flow", "What if we imagine this differently? The pattern suggests...", True),
        ("Too Much Meta", "This demonstrates my analytical approach to challenging arguments...", False)
    ]
    
    for test_name, response, expected_clean in validation_tests:
        result = validate_response_cleanliness(response)
        status = "✓ PASS" if result["is_clean"] == expected_clean else "✗ FAIL"
        
        print(f"{test_name}: {status}")
        print(f"  Response: \"{response}\"")
        print(f"  Clean: {result['is_clean']} (Score: {result['cleanliness_score']:.2f})")
        if result["issues"]:
            print(f"  Issues: {', '.join(result['issues'])}")
        print()


if __name__ == "__main__":
    test_response_filtering()
    test_clean_prompt_generation()
    test_response_starters()
    demonstrate_conversation_improvement()
    test_deepseek_specific_instructions()
    show_validation_examples()
    
    print("\n" + "=" * 60)
    print("CLEAN RESPONSE SYSTEM COMPLETE!")
    print("No more meta-commentary - just pure conversation!")
    print("=" * 60)