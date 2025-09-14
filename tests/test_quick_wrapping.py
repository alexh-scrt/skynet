#!/usr/bin/env python3
"""
Quick test of text wrapping by directly testing the logging function
"""

import os
from datetime import datetime
import env
from barbie import BarbieAgent

def test_direct_logging():
    """Test the logging function directly"""
    print("🧪 Testing text wrapping directly...")
    
    # Create log directory
    os.makedirs("./data/conversation", exist_ok=True)
    
    # Initialize Barbie (need the full instance for the logging function)
    print("🚀 Initializing Barbie...")
    barbie = BarbieAgent()
    
    # Test with a very long message
    long_message = """Hi, I'm Barbie! I'm super excited to dive into the fascinating world of machine learning algorithms with Ken. From my perspective, understanding these algorithms is crucial for creating innovative solutions that can transform industries and revolutionize our daily lives. Let's start with supervised learning, which is a type of machine learning where the algorithm is trained on labeled data. The goal is to learn a mapping between input data and the corresponding output labels, so the algorithm can make predictions on new, unseen data. A classic example of supervised learning is image classification, where an algorithm is trained to recognize objects in images, such as dogs, cats, or cars."""
    
    print("📝 Testing with long message...")
    print(f"Original message length: {len(long_message)} characters")
    
    # Test the logging function
    barbie.log_conversation_message("Barbie", long_message, "direct_test")
    
    # Read and analyze the result
    with open("./data/conversation/history.txt", "r") as f:
        content = f.read()
    
    print("\n📊 Analysis:")
    lines = content.split('\n')
    long_lines = [line for line in lines if len(line) > 80]
    
    print(f"Total lines: {len(lines)}")
    print(f"Lines over 80 chars: {len(long_lines)}")
    print(f"Max line length: {max(len(line) for line in lines)}")
    
    print("\n📜 Result:")
    print(content)
    
    if len(long_lines) == 0:
        print("\n✅ SUCCESS: All lines are 80 characters or less!")
        return True
    else:
        print(f"\n❌ FAILED: {len(long_lines)} lines exceed 80 characters")
        for i, line in enumerate(long_lines[:3]):
            print(f"  Long line {i+1}: {len(line)} chars")
        return False

if __name__ == "__main__":
    success = test_direct_logging()
    exit(0 if success else 1)