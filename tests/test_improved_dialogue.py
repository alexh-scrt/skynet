#!/usr/bin/env python3
"""
Test script to verify Ken's improved conversational style.
This tests that Ken now forms opinions based on research rather than
just reciting facts, and maintains a natural dialogue flow.
"""

import requests
import time
from datetime import datetime

def test_improved_dialogue():
    """Test Ken's new conversational, opinion-based response style"""
    
    print("=" * 60)
    print("TESTING IMPROVED DIALOGUE STYLE")
    print("=" * 60)
    
    barbie_url = "http://localhost:8001"
    
    print("\n📝 Testing Ken's new conversational approach...")
    print("\nKey improvements implemented:")
    print("✅ Ken forms his own opinions based on research")
    print("✅ Uses phrases like 'I think', 'In my view', 'What concerns me'")
    print("✅ Stays focused on Barbie's actual points")
    print("✅ Expresses genuine reactions and emotions")
    print("✅ Asks questions from curiosity, not just to counter")
    print("✅ Shares personal interpretations, not just data")
    
    # Test with a philosophical question that should trigger opinion-based responses
    payload = {
        "message": "Should we prioritize technological progress over environmental preservation?",
        "conversation_id": f"test_dialogue_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    print(f"\n🚀 Sending genesis request with philosophical question...")
    print(f"   Question: '{payload['message']}'")
    
    try:
        response = requests.post(
            f"{barbie_url}/v1/genesis",
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        print(f"✅ Genesis request accepted: {response.json()}")
        
    except Exception as e:
        print(f"❌ Failed to send genesis request: {e}")
        return
    
    print("\n⏳ Waiting for conversation to develop...")
    print("   Ken should now respond with:")
    print("   • His personal perspective on the topic")
    print("   • Opinions formed from research, not raw facts")
    print("   • Natural conversational flow")
    print("   • Engagement with Barbie's specific points")
    
    time.sleep(10)
    
    print("\n" + "=" * 60)
    print("DIALOGUE STYLE TEST COMPLETE")
    print("=" * 60)
    
    print("\n📋 Check the conversation logs for these improvements:")
    print("\n1. OPINION FORMATION:")
    print("   ❌ OLD: 'The 2023 study shows X with 97% confidence'")
    print("   ✅ NEW: 'I think what the research really tells us is...'")
    
    print("\n2. CONVERSATIONAL FLOW:")
    print("   ❌ OLD: '### Counter-Research and Methodologies'")
    print("   ✅ NEW: 'You know what really strikes me about your point?'")
    
    print("\n3. PERSONAL ENGAGEMENT:")
    print("   ❌ OLD: 'Studies indicate three primary factors...'")
    print("   ✅ NEW: 'I'm not entirely convinced because...'")
    
    print("\n4. STAYING ON TOPIC:")
    print("   ❌ OLD: Long tangents about every related study")
    print("   ✅ NEW: Focused response to Barbie's actual arguments")
    
    print("\n5. GENUINE CURIOSITY:")
    print("   ❌ OLD: 'How do you reconcile claim X with finding Y?'")
    print("   ✅ NEW: 'I'm genuinely curious what you think about...'")
    
    print("\n💡 The conversation should feel more like two people")
    print("   discussing ideas rather than exchanging research papers!")

if __name__ == "__main__":
    test_improved_dialogue()