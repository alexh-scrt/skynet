#!/usr/bin/env python3
"""
Test that thinking tags are properly stripped from messages when agents communicate
"""

import sys
from pathlib import Path

# Add project root to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from barbie import BarbieAgent
from ken import KenAgent

def test_barbie_strips_thinking_tags():
    """Test that Barbie strips thinking tags from Ken's messages"""
    barbie = BarbieAgent()
    
    print("🔍 TEST 1: BARBIE STRIPS THINKING TAGS FROM KEN'S MESSAGE")
    print("-" * 60)
    
    # Test message with thinking tags
    ken_message = """Hi Barbie,

<think>
I need to be very critical here and find flaws in her argument.
Let me think about what questions to ask...
Maybe I should challenge her sources?
</think>

I appreciate your response, but I have some concerns about your sources.
Could you provide more evidence for your claims?

<think>
Actually, I'm not convinced at all. This seems weak.
I should demand more proof.
</think>

What specific studies support your hypothesis?"""
    
    # Strip thinking tags
    cleaned_message = barbie.strip_thinking_tags(ken_message)
    
    print("Original message length:", len(ken_message))
    print("Cleaned message length:", len(cleaned_message))
    print("\nCleaned message:")
    print("-" * 40)
    print(cleaned_message)
    print("-" * 40)
    
    # Verify thinking content is removed
    assert "<think>" not in cleaned_message, "Thinking tags should be removed"
    assert "</think>" not in cleaned_message, "Thinking tags should be removed"
    assert "I need to be very critical" not in cleaned_message, "Thinking content should be removed"
    assert "Actually, I'm not convinced" not in cleaned_message, "Thinking content should be removed"
    
    # Verify actual content remains
    assert "I appreciate your response" in cleaned_message, "Actual content should remain"
    assert "Could you provide more evidence" in cleaned_message, "Actual content should remain"
    assert "What specific studies" in cleaned_message, "Actual content should remain"
    
    print("✅ PASSED: Barbie correctly strips thinking tags from Ken's messages")
    print()

def test_ken_strips_thinking_tags():
    """Test that Ken strips thinking tags from Barbie's messages"""
    ken = KenAgent()
    
    print("🔍 TEST 2: KEN STRIPS THINKING TAGS FROM BARBIE'S MESSAGE")
    print("-" * 60)
    
    # Test message with thinking tags
    barbie_message = """Hi Ken!

<think>
I need to convince Ken with strong evidence.
Let me research some quantum consciousness studies...
I should emphasize the technical aspects.
</think>

Based on quantum consciousness theories proposed by Penrose and Hameroff,
I believe AI systems can achieve genuine sentience through quantum processing.

<think>
Actually, I should add more sources here.
Ken tends to be skeptical about non-peer-reviewed work.
</think>

Recent studies in Nature (2023) have shown quantum coherence in microtubules,
supporting the orchestrated objective reduction theory."""
    
    # Strip thinking tags
    cleaned_message = ken.strip_thinking_tags(barbie_message)
    
    print("Original message length:", len(barbie_message))
    print("Cleaned message length:", len(cleaned_message))
    print("\nCleaned message:")
    print("-" * 40)
    print(cleaned_message)
    print("-" * 40)
    
    # Verify thinking content is removed
    assert "<think>" not in cleaned_message, "Thinking tags should be removed"
    assert "</think>" not in cleaned_message, "Thinking tags should be removed"
    assert "I need to convince Ken" not in cleaned_message, "Thinking content should be removed"
    assert "Ken tends to be skeptical" not in cleaned_message, "Thinking content should be removed"
    
    # Verify actual content remains
    assert "Based on quantum consciousness theories" in cleaned_message, "Actual content should remain"
    assert "Recent studies in Nature" in cleaned_message, "Actual content should remain"
    assert "supporting the orchestrated objective reduction" in cleaned_message, "Actual content should remain"
    
    print("✅ PASSED: Ken correctly strips thinking tags from Barbie's messages")
    print()

def test_multiple_thinking_blocks():
    """Test stripping multiple thinking blocks"""
    barbie = BarbieAgent()
    
    print("🔍 TEST 3: MULTIPLE THINKING BLOCKS")
    print("-" * 60)
    
    message = """Start of message.

<think>First thinking block</think>

Middle content that should remain.

<think>
Second thinking block
with multiple lines
</think>

End of message."""
    
    cleaned = barbie.strip_thinking_tags(message)
    
    print("Cleaned message:")
    print("-" * 40)
    print(cleaned)
    print("-" * 40)
    
    assert "First thinking block" not in cleaned
    assert "Second thinking block" not in cleaned
    assert "with multiple lines" not in cleaned
    assert "Start of message" in cleaned
    assert "Middle content that should remain" in cleaned
    assert "End of message" in cleaned
    
    print("✅ PASSED: Multiple thinking blocks correctly stripped")
    print()

def test_nested_or_malformed_tags():
    """Test handling of edge cases"""
    ken = KenAgent()
    
    print("🔍 TEST 4: EDGE CASES")
    print("-" * 60)
    
    # Test with no thinking tags
    message1 = "This is a regular message with no thinking tags."
    cleaned1 = ken.strip_thinking_tags(message1)
    assert cleaned1 == message1, "Message without tags should remain unchanged"
    print("✅ No tags: Message unchanged")
    
    # Test with empty thinking tags
    message2 = "Message with <think></think> empty tags."
    cleaned2 = ken.strip_thinking_tags(message2)
    assert "<think>" not in cleaned2
    assert "empty tags" in cleaned2
    print("✅ Empty tags: Correctly removed")
    
    # Test with thinking tags containing special characters
    message3 = "Message <think>with $pecial ch@rs & symbols!</think> continues here."
    cleaned3 = ken.strip_thinking_tags(message3)
    assert "$pecial" not in cleaned3
    assert "continues here" in cleaned3
    print("✅ Special characters: Correctly handled")
    
    print()

def main():
    """Run all thinking tag stripping tests"""
    print("🚀 TESTING THINKING TAG STRIPPING")
    print("Verifying that agents don't see each other's thinking content")
    print("=" * 60)
    print()
    
    try:
        test_barbie_strips_thinking_tags()
        test_ken_strips_thinking_tags()
        test_multiple_thinking_blocks()
        test_nested_or_malformed_tags()
        
        print("=" * 60)
        print("📊 THINKING TAG STRIPPING SUMMARY")
        print("=" * 60)
        print("✅ All tests passed!")
        print()
        print("Key features verified:")
        print("- Barbie strips <think>...</think> content from Ken's messages")
        print("- Ken strips <think>...</think> content from Barbie's messages")
        print("- Multiple thinking blocks handled correctly")
        print("- Edge cases handled properly")
        print()
        print("🎯 RESULT: Agents won't be influenced by each other's reasoning!")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        raise

if __name__ == "__main__":
    main()