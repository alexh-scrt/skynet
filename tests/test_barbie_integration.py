#!/usr/bin/env python3
"""
Test Barbie's conversation logging integration
"""

import sys
from pathlib import Path
import tempfile
import os

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.conversation_logger import BarbieConversationManager


def test_barbie_conversation_manager():
    """Test that Barbie can properly log conversations"""
    
    print("=== Testing Barbie's Conversation Logging Integration ===\n")
    
    # Use a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temp directory: {temp_dir}")
        
        # Initialize the conversation manager like Barbie does
        conversation_manager = BarbieConversationManager(temp_dir)
        active_conversations = {}
        
        # Simulate genesis task
        original_question = "What are the implications of AI consciousness for society?"
        conversation_id = "genesis_test_123"
        
        print(f"1. Starting conversation with question: '{original_question}'")
        log_file = conversation_manager.begin_debate(original_question)
        active_conversations[conversation_id] = log_file
        print(f"   Created log file: {log_file}")
        
        # Simulate Barbie's first message
        barbie_msg1 = ("What if we imagine AI consciousness like the emergence of language in "
                      "human civilization? Just as language transformed not just how we communicate "
                      "but how we think, AI consciousness could fundamentally reshape society's "
                      "relationship with intelligence itself.")
        
        print(f"2. Barbie sends message to Ken")
        conversation_manager.send_to_ken(barbie_msg1)
        
        # Simulate Ken's response
        ken_msg1 = ("But this analogy assumes AI consciousness follows biological patterns. "
                   "Let's examine the logical structure: if consciousness is substrate-independent, "
                   "how do we distinguish between sophisticated mimicry and genuine awareness? "
                   "What would falsify the claim that an AI system is truly conscious?")
        
        print(f"3. Ken responds")
        conversation_manager.receive_from_ken(ken_msg1)
        
        # Simulate Barbie's follow-up
        barbie_msg2 = ("That's precisely why I love this comparison - it reveals the beautiful "
                      "tension between pattern recognition and genuine understanding. Perhaps "
                      "consciousness isn't binary but exists on a spectrum, like how human "
                      "language evolved from simple gestures to complex poetry.")
        
        print(f"4. Barbie continues the debate")
        conversation_manager.send_to_ken(barbie_msg2)
        
        # End the conversation
        print(f"5. Ending conversation")
        conversation_manager.conclude_debate("Explored AI consciousness through language emergence analogy")
        del active_conversations[conversation_id]
        
        # Verify the logged conversation
        print(f"\n6. Verifying logged conversation:")
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
            
            print("=" * 60)
            print("LOGGED CONVERSATION:")
            print("=" * 60)
            print(content)
            print("=" * 60)
            
            # Verify format
            format_checks = [
                ("Original question present", original_question in content),
                ("Barbie messages logged", "<Barbie>" in content and "</Barbie>" in content),
                ("Ken messages logged", "<Ken>" in content and "</Ken>" in content),
                ("Proper separators", "\n--\n" in content),
                ("Started timestamp", "Started:" in content),
                ("Ended timestamp", "Ended:" in content),
                ("Summary present", "language emergence analogy" in content),
            ]
            
            print("FORMAT VERIFICATION:")
            print("-" * 30)
            for check_name, passed in format_checks:
                status = "✓" if passed else "✗"
                print(f"{status} {check_name}")
            
            all_passed = all(passed for _, passed in format_checks)
            print(f"\nOverall: {'✅ PASSED' if all_passed else '❌ FAILED'}")
            
            return all_passed
        else:
            print(f"❌ Log file not created: {log_file}")
            return False


def simulate_barbie_integration():
    """Simulate how Barbie would use the conversation manager"""
    
    print("\n" + "=" * 60)
    print("BARBIE INTEGRATION SIMULATION")
    print("=" * 60)
    
    # This simulates the key parts of Barbie's integration
    conversation_manager = BarbieConversationManager("./data/conversation")
    active_conversations = {}
    
    print("Simulating Barbie's workflow:")
    print("1. Genesis request arrives")
    print("2. Start conversation log")
    print("3. Generate and log Barbie's message")  
    print("4. Send to Ken and receive response")
    print("5. Log Ken's message")
    print("6. Continue until completion")
    
    # Show current conversation files
    history = conversation_manager.get_conversation_history()
    print(f"\nCurrent conversation files: {len(history)}")
    for i, file_path in enumerate(history[-3:], 1):  # Show last 3
        print(f"  {i}. {os.path.basename(file_path)}")
    
    return True


if __name__ == "__main__":
    print("Testing Barbie's conversation logging integration...")
    
    test1_passed = test_barbie_conversation_manager()
    test2_passed = simulate_barbie_integration()
    
    print(f"\n{'='*60}")
    print("INTEGRATION TEST RESULTS:")
    print(f"{'='*60}")
    print(f"Conversation Manager Test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Integration Simulation: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print(f"\n🎉 All tests passed! Barbie's conversation logging is ready!")
    else:
        print(f"\n⚠️ Some tests failed. Please check the integration.")
    
    print(f"\nBarbie should now create timestamped conversation files in:")
    print(f"  ./data/conversation/conversation_<timestamp>.md")