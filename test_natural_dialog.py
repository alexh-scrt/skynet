#!/usr/bin/env python3
"""
Quick test to verify natural dialog prompt changes
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from barbie import BarbieAgent, ConversationState
from ken import KenAgent, EvaluationState

def test_barbie_natural_dialog():
    """Test Barbie's natural dialog prompts"""
    print("=" * 60)
    print("TESTING BARBIE'S NATURAL DIALOG PROMPTS")
    print("=" * 60)
    
    agent = BarbieAgent()
    
    # Test first message
    state = ConversationState()
    state.user_input = "What do you think about artificial consciousness?"
    state.round_number = 0
    state.maturity_stage = "exploration"
    
    prompt = agent.build_generation_prompt(state)
    
    print("FIRST MESSAGE PROMPT (should avoid formal introductions):")
    print("-" * 50)
    print(prompt)
    print()
    
    # Test follow-up message
    state.round_number = 1
    state.ken_feedback = "That's an interesting point. But what evidence supports this?"
    
    prompt = agent.build_generation_prompt(state)
    
    print("FOLLOW-UP MESSAGE PROMPT (should maintain natural flow):")
    print("-" * 50)
    print(prompt)
    print()

def test_ken_natural_dialog():
    """Test Ken's natural dialog prompts"""
    print("=" * 60)
    print("TESTING KEN'S NATURAL DIALOG PROMPTS")
    print("=" * 60)
    
    agent = KenAgent()
    
    # Test first evaluation
    state = EvaluationState()
    state.barbie_response = "I believe AI consciousness is possible through emergent complexity."
    state.confidence_score = 0.3
    state.maturity_stage = "exploration"
    state.evaluation_response = "The argument lacks specific evidence."
    state.search_results = "Various studies on consciousness theories..."
    
    # Simulate first Ken message
    is_first_ken_message = True
    prompt = agent._build_feedback_prompt(state, is_first_ken_message)
    
    print("FIRST KEN RESPONSE PROMPT (should avoid formal greetings):")
    print("-" * 50)
    print(prompt)
    print()
    
    # Test follow-up evaluation
    is_first_ken_message = False
    prompt = agent._build_feedback_prompt(state, is_first_ken_message)
    
    print("FOLLOW-UP KEN RESPONSE PROMPT (should maintain natural flow):")
    print("-" * 50)
    print(prompt)
    print()

def test_response_filtering():
    """Test that our response filter catches formal patterns"""
    print("=" * 60)
    print("TESTING RESPONSE FILTERING")
    print("=" * 60)
    
    from src.utils.response_filtering import ResponseFilter
    
    filter_system = ResponseFilter()
    
    # Test formal messages that should be filtered
    test_cases = [
        "Hi Barbie, this is Ken! I think your argument has merit...",
        "Hi, I'm Barbie! Let me share my thoughts on this topic...",
        "That's a great point. Looking forward to your response!",
        "I appreciate your perspective. Best regards, Ken",
        "Your analysis is thorough. Sincerely, Barbie"
    ]
    
    for i, test_response in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_response}")
        cleaned = filter_system.clean_response(test_response, "Ken")
        print(f"Filtered: {cleaned}")
        print(f"Removed: {test_response != cleaned}")
        print("-" * 30)

if __name__ == "__main__":
    test_barbie_natural_dialog()
    test_ken_natural_dialog() 
    test_response_filtering()
    print("\n✅ Natural dialog prompt testing completed!")