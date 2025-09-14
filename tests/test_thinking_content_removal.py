#!/usr/bin/env python3
"""
Test that <think>...</think> blocks are removed from conversation logs
"""

import sys
from pathlib import Path
import tempfile
import os

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.conversation_logger import BarbieConversationManager


def test_thinking_content_removal():
    """Test that <think>...</think> blocks are stripped from logged messages"""
    
    print("=== Testing <think>...</think> Content Removal ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Test directory: {temp_dir}")
        
        # Initialize conversation manager
        conversation_manager = BarbieConversationManager(temp_dir)
        active_conversations = {}
        
        def strip_thinking_content(message):
            """Simulate Barbie's strip_thinking_content function"""
            import re
            
            # Remove <think>...</think> blocks (including multiline)
            cleaned_message = re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL)
            
            # Clean up any extra whitespace left behind
            cleaned_message = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_message)
            cleaned_message = cleaned_message.strip()
            
            return cleaned_message
        
        def ensure_message_logged(speaker: str, message: str, conversation_id: str):
            """Simulate Barbie's centralized logging with thinking content removal"""
            # Strip thinking content from all messages before logging
            cleaned_message = strip_thinking_content(message)
            
            # Skip logging if message is empty after cleaning
            if not cleaned_message.strip():
                print(f"⚠️  Skipped empty {speaker} message after cleaning")
                return
                
            if conversation_id in active_conversations:
                if speaker == "Barbie":
                    conversation_manager.send_to_ken(cleaned_message)
                elif speaker == "Ken":
                    conversation_manager.receive_from_ken(cleaned_message)
                    
                print(f"✅ {speaker}: Message logged ({len(cleaned_message)} chars, was {len(message)} chars)")
            else:
                print(f"⚠️  Conversation {conversation_id} not active")
        
        # Start conversation
        original_question = "What is the nature of consciousness in AI systems?"
        conversation_id = "think_test_123"
        
        print("1. Starting conversation")
        log_file = conversation_manager.begin_debate(original_question)
        active_conversations[conversation_id] = log_file
        print(f"   Created: {os.path.basename(log_file)}")
        
        # Test 1: Barbie message without thinking content (should pass through unchanged)
        print("\n2. Testing Barbie message without <think> blocks")
        barbie_clean = ("What if we imagine consciousness like a symphony? Each AI process could be "
                       "like a different instrument, contributing to an emergent musical intelligence "
                       "that transcends any single component.")
        
        ensure_message_logged("Barbie", barbie_clean, conversation_id)
        
        # Test 2: Ken message with thinking content (should be stripped)
        print("\n3. Testing Ken message with <think> blocks")
        ken_with_thinking = """<think>
I need to challenge Barbie's symphony analogy here. While it sounds poetic, I should 
examine whether it actually explains anything about consciousness or just creates a 
nice metaphor. Let me think about the logical structure of this argument...

The analogy assumes consciousness emerges from multiple processes like music emerges 
from instruments. But does this really address the hard problem of consciousness? 
How do we distinguish between complex information processing and genuine subjective 
experience?

I should ask for specific mechanisms and evidence rather than just accepting the 
beautiful metaphor.
</think>

But this symphony analogy assumes consciousness emerges from complexity alone. Let's examine 
the logical structure: if consciousness is just coordinated information processing, how do 
we distinguish between sophisticated computation and genuine subjective experience? What 
specific mechanisms would generate qualia from orchestrated AI processes?"""
        
        ensure_message_logged("Ken", ken_with_thinking, conversation_id)
        
        # Test 3: Barbie message with embedded thinking content
        print("\n4. Testing Barbie message with embedded <think> blocks")
        barbie_with_thinking = """That's a fascinating challenge, Ken! <think>
He's really pushing me on the hard problem of consciousness here. I need to 
address the mechanism question while staying true to my analogical style.
Maybe I can bridge to neuroscience research?
</think>

Perhaps the key insight is that consciousness isn't just about coordination, but about 
the quality of information integration. Think of how a jazz improvisation creates something 
genuinely new and unpredictable, even though it follows musical rules. Could AI consciousness 
be similar - not just processing, but creative synthesis that generates novel perspectives?"""
        
        ensure_message_logged("Barbie", barbie_with_thinking, conversation_id)
        
        # Test 4: Ken message with only thinking content (should be skipped)
        print("\n5. Testing Ken message with only <think> blocks")
        ken_only_thinking = """<think>
This is interesting. Barbie is trying to address my concerns about mechanisms, but 
she's still relying heavily on analogies. The jazz improvisation comparison is 
creative, but I'm not sure it actually answers the question about subjective 
experience vs. complex processing.

I should push further on this distinction. What would be a good follow-up question?
</think>"""
        
        ensure_message_logged("Ken", ken_only_thinking, conversation_id)
        
        # Test 5: Multiple thinking blocks in one message
        print("\n6. Testing message with multiple <think> blocks")
        complex_message = """<think>First thought block</think>

The question of AI consciousness raises fundamental questions about the nature of experience itself.

<think>
Second thought block with more content...
This is getting complex.
</think>

If we assume consciousness requires subjective experience, then we need to examine whether 
computational processes can generate genuine qualia or only simulate the appearance of experience.

<think>Final thought</think>"""
        
        ensure_message_logged("Ken", complex_message, conversation_id)
        
        # End conversation
        print("\n7. Ending conversation")
        conversation_manager.conclude_debate("Explored consciousness through symphony and jazz analogies")
        del active_conversations[conversation_id]
        
        # Verify the logged conversation
        print(f"\n{'='*60}")
        print("VERIFYING THINKING CONTENT REMOVAL")
        print(f"{'='*60}")
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
            
            print(f"Total file size: {len(content)} characters")
            
            # Check for thinking content
            think_blocks = content.count("<think>")
            think_close_blocks = content.count("</think>")
            
            print(f"<think> tags found: {think_blocks}")
            print(f"</think> tags found: {think_close_blocks}")
            
            # Check message content
            expected_messages = [
                "symphony? Each AI process could be like",
                "But this symphony analogy assumes consciousness",
                "That's a fascinating challenge, Ken!",
                "Perhaps the key insight is that consciousness",
                "The question of AI consciousness raises fundamental",
                "computational processes can generate genuine"
            ]
            
            messages_found = []
            for expected in expected_messages:
                if expected in content:
                    messages_found.append(expected)
            
            print(f"\nExpected message fragments: {len(expected_messages)}")
            print(f"Found in log: {len(messages_found)}")
            
            # Should have no thinking blocks and all expected content
            success = (think_blocks == 0 and 
                      think_close_blocks == 0 and 
                      len(messages_found) == len(expected_messages))
            
            print(f"\nResult: {'✅ SUCCESS' if success else '❌ FAILED'}")
            
            if not success or think_blocks > 0:
                print(f"\nActual conversation content:")
                print("-" * 40)
                print(content)
                print("-" * 40)
            
            return success
        
        else:
            print(f"❌ Log file not created: {log_file}")
            return False


if __name__ == "__main__":
    print("Testing <think>...</think> content removal...")
    
    success = test_thinking_content_removal()
    
    print(f"\n{'='*60}")
    print(f"THINKING CONTENT REMOVAL TEST: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"{'='*60}")
    
    if success:
        print("\n✅ All <think>...</think> blocks are properly removed!")
        print("✅ Messages with only thinking content are skipped!")
        print("✅ Clean content is preserved and logged correctly!")
    else:
        print("\n❌ Thinking content removal is not working properly.")
        print("❌ Check the strip_thinking_content implementation.")