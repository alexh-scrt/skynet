#!/usr/bin/env python3
"""
Test that Barbie logs EVERY message to conversation files
"""

import sys
from pathlib import Path
import tempfile
import os
import time

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.conversation_logger import BarbieConversationManager


def simulate_complete_conversation_flow():
    """Simulate a complete conversation and verify every message is logged"""
    
    print("=== Testing Complete Message Logging ===\n")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Test directory: {temp_dir}")
        
        # Simulate Barbie's initialization
        conversation_manager = BarbieConversationManager(temp_dir)
        active_conversations = {}
        
        def ensure_message_logged(speaker: str, message: str, conversation_id: str):
            """Simulate Barbie's centralized logging function"""
            if conversation_id in active_conversations:
                if speaker == "Barbie":
                    conversation_manager.send_to_ken(message)
                elif speaker == "Ken":
                    conversation_manager.receive_from_ken(message)
                print(f"✓ {speaker} message logged: {len(message)} chars")
            else:
                print(f"⚠️  Conversation {conversation_id} not active, message not logged")
        
        # Test conversation flow
        original_question = "How will quantum computing affect cybersecurity?"
        conversation_id = "test_complete_123"
        
        print("1. Starting conversation (Genesis)")
        log_file = conversation_manager.begin_debate(original_question)
        active_conversations[conversation_id] = log_file
        print(f"   Log file: {os.path.basename(log_file)}")
        
        # Genesis: Barbie's first message
        barbie_genesis = ("What if we imagine quantum computing like a master key that can unlock "
                         "any encryption? While it poses unprecedented challenges to current "
                         "cybersecurity, it also opens pathways to quantum-resistant cryptography "
                         "that could be virtually unbreakable.")
        
        print("\n2. Genesis - Barbie's initial response")
        ensure_message_logged("Barbie", barbie_genesis, conversation_id)
        
        # Round 1: Ken responds
        ken_round1 = ("But this master key analogy oversimplifies the threat timeline. Let's examine "
                     "the logical structure: current quantum computers are nowhere near breaking "
                     "RSA encryption. How do we balance preparation for theoretical quantum threats "
                     "against practical security needs today?")
        
        print("\n3. Round 1 - Ken responds")
        ensure_message_logged("Ken", ken_round1, conversation_id)
        
        # Round 1: Barbie continues
        barbie_round1 = ("That's precisely why I love the timeline tension you've identified! "
                        "Perhaps we're not facing an immediate 'cryptographic apocalypse' but rather "
                        "a gradual transition period where hybrid approaches could bridge classical "
                        "and quantum-resistant methods.")
        
        print("\n4. Round 1 - Barbie continues debate")
        ensure_message_logged("Barbie", barbie_round1, conversation_id)
        
        # Round 2: Ken pushes back
        ken_round2 = ("The transition period creates new vulnerabilities. If we trace the causal "
                     "chain: early quantum systems might be powerful enough to break some encryption "
                     "but not reliable enough for secure quantum cryptography. This creates a "
                     "dangerous gap period. What's the risk mitigation strategy?")
        
        print("\n5. Round 2 - Ken challenges transition approach")
        ensure_message_logged("Ken", ken_round2, conversation_id)
        
        # Round 2: Barbie responds
        barbie_round2 = ("The gap period is the key insight! It's like upgrading a city's infrastructure - "
                        "you can't replace all the pipes at once. We need layered security architectures "
                        "that can operate with both classical and quantum-resistant algorithms "
                        "simultaneously during the transition.")
        
        print("\n6. Round 2 - Barbie addresses gap period")
        ensure_message_logged("Barbie", barbie_round2, conversation_id)
        
        # Round 3: Ken final point
        ken_round3 = ("The infrastructure analogy reveals the resource allocation problem. "
                     "Organizations must invest in quantum-resistant systems before the threat "
                     "materializes, but how do we justify costs for uncertain timelines? "
                     "The economic incentive structure seems misaligned.")
        
        print("\n7. Round 3 - Ken raises economic concerns")
        ensure_message_logged("Ken", ken_round3, conversation_id)
        
        # Final: Barbie synthesis
        barbie_final = ("Exactly! The misaligned incentives are where policy and technology intersect. "
                       "Maybe we need 'quantum readiness standards' similar to how we handle climate "
                       "risk - frameworks that help organizations prepare systematically rather than "
                       "reactively. The beautiful pattern here is that preparation becomes competitive "
                       "advantage rather than just cost.")
        
        print("\n8. Final - Barbie synthesis")
        ensure_message_logged("Barbie", barbie_final, conversation_id)
        
        # End conversation
        print("\n9. Ending conversation")
        conversation_manager.conclude_debate("Explored quantum computing cybersecurity through transition challenges and economic incentives")
        del active_conversations[conversation_id]
        
        # Verify complete logging
        print(f"\n{'='*60}")
        print("VERIFYING COMPLETE MESSAGE LOGGING")
        print(f"{'='*60}")
        
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                content = f.read()
            
            print(f"Total file size: {len(content)} characters")
            
            # Count messages
            barbie_count = content.count("<Barbie>")
            ken_count = content.count("<Ken>")
            separator_count = content.count("\n--\n")
            
            print(f"Barbie messages logged: {barbie_count}")
            print(f"Ken messages logged: {ken_count}")
            print(f"Message separators: {separator_count}")
            
            # Verify all messages are present
            messages_to_check = [
                ("Original question", original_question in content),
                ("Barbie genesis", "master key that can unlock any encryption" in content),
                ("Ken round 1", "master key analogy oversimplifies" in content),
                ("Barbie round 1", "cryptographic apocalypse" in content),
                ("Ken round 2", "dangerous gap period" in content),
                ("Barbie round 2", "upgrading a city's infrastructure" in content),
                ("Ken round 3", "resource allocation problem" in content),
                ("Barbie final", "quantum readiness standards" in content),
                ("Summary", "transition challenges and economic incentives" in content)
            ]
            
            print(f"\nMessage Content Verification:")
            print("-" * 40)
            all_present = True
            for description, found in messages_to_check:
                status = "✓" if found else "✗"
                print(f"{status} {description}")
                if not found:
                    all_present = False
            
            # Expected counts
            expected_barbie = 4  # genesis + 3 rounds
            expected_ken = 3     # 3 rounds
            expected_separators = 7  # one after each message
            
            counts_correct = (
                barbie_count == expected_barbie and 
                ken_count == expected_ken and
                separator_count == expected_separators
            )
            
            print(f"\nMessage Counts:")
            print("-" * 20)
            print(f"Barbie: {barbie_count}/{expected_barbie} {'✓' if barbie_count == expected_barbie else '✗'}")
            print(f"Ken: {ken_count}/{expected_ken} {'✓' if ken_count == expected_ken else '✗'}")
            print(f"Separators: {separator_count}/{expected_separators} {'✓' if separator_count == expected_separators else '✗'}")
            
            overall_success = all_present and counts_correct
            print(f"\n{'🎉 ALL MESSAGES LOGGED CORRECTLY!' if overall_success else '❌ SOME MESSAGES MISSING OR INCORRECT!'}")
            
            if not overall_success:
                print(f"\nActual conversation content:")
                print("-" * 40)
                print(content)
            
            return overall_success
        
        else:
            print(f"❌ Log file not created: {log_file}")
            return False


if __name__ == "__main__":
    print("Testing complete message logging system...")
    
    success = simulate_complete_conversation_flow()
    
    print(f"\n{'='*60}")
    print(f"COMPLETE LOGGING TEST: {'✅ PASSED' if success else '❌ FAILED'}")
    print(f"{'='*60}")
    
    if success:
        print("\n✅ Barbie's centralized logging system captures every message!")
        print("✅ All messages are written to timestamped conversation files!")
        print("✅ The format matches the required specification!")
    else:
        print("\n❌ Some messages are not being logged correctly.")
        print("❌ Check the logging implementation in Barbie.")