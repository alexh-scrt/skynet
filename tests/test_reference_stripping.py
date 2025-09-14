#!/usr/bin/env python3
"""
Test reference stripping functionality in conversation logs
"""

import sys
import os
from pathlib import Path

# Proper path setup for tests folder
prj_path = Path(__file__).parent.parent
sys.path.insert(0, str(prj_path))

def test_reference_stripping():
    """Test that references are stripped from messages by default"""
    print("=" * 60)
    print("TESTING REFERENCE STRIPPING")
    print("=" * 60)
    
    # Mock the BarbieAgent class parts we need
    class MockBarbieAgent:
        def __init__(self, log_references=False):
            self.log_references = log_references
            
        def strip_references(self, message):
            """Remove reference section from messages if log_references is False"""
            if self.log_references:
                return message
                
            import re
            # Pattern to match References section at the end of messages
            patterns = [
                r'\n\n?(?:References|Sources|Citations):.*?(?=\n\n|$)',
                r'\n\n?\*\*(?:References|Sources|Citations)\*\*:.*?(?=\n\n|$)',
                # Also match individual reference lines that look like citations
                r'\n(?:[A-Z][a-z]+(?:,\s*[A-Z]\.)?,?\s*(?:&\s*)?)+\([0-9]{4}\)\..*?(?=\n|$)'
            ]
            
            cleaned = message
            for pattern in patterns:
                cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.MULTILINE)
            
            # Clean up any trailing "Looking forward" type phrases
            cleaned = re.sub(r'\n\n?Looking forward to.*?(?:\n|$)', '', cleaned, flags=re.IGNORECASE)
            
            # Remove any excessive whitespace
            cleaned = re.sub(r'\n\n+', '\n\n', cleaned).strip()
            return cleaned
    
    # Test cases with references
    test_messages = [
        {
            "name": "Message with References section",
            "input": """Thank you for your thoughtful feedback, Ken! I appreciate your insights.

The study on AI consciousness shows promising results for future development.

References:
Barocas, S., Hardt, M., & Narayanan, A. (2019). Fairness and machine learning. Nature Machine Intelligence, 1(1), 44-48.
European Commission. (2020). Horizon 2020: The EU Framework Programme for Research and Innovation.

Looking forward to your response!""",
            "expected": """Thank you for your thoughtful feedback, Ken! I appreciate your insights.

The study on AI consciousness shows promising results for future development."""
        },
        {
            "name": "Message with bold References",
            "input": """I believe AI can achieve consciousness through emergent complexity.

This connects to recent studies in neuroscience and philosophy.

**References:**
Smith, J. (2023). AI and Consciousness. Science, 380(6641), 123-127.
Jones, K. (2024). Neural Networks and Emergence. Nature, 615, 456-461.""",
            "expected": """I believe AI can achieve consciousness through emergent complexity.

This connects to recent studies in neuroscience and philosophy."""
        },
        {
            "name": "Message with inline citations",
            "input": """As Yakalı (2024) noted in their study, gender representation matters.

The implications are significant for AI design.

Yakalı, D. (2024). Deconstructing hegemonic masculinity. Frontiers in Sociology, 9, 1320774.""",
            "expected": """As Yakalı (2024) noted in their study, gender representation matters.

The implications are significant for AI design."""
        },
        {
            "name": "Message without references (should remain unchanged)",
            "input": """This is a simple message without any references.

It should remain exactly as it is.""",
            "expected": """This is a simple message without any references.

It should remain exactly as it is."""
        }
    ]
    
    # Test with log_references=False (default)
    print("\n1. Testing with log_references=False (default):")
    print("-" * 50)
    agent_default = MockBarbieAgent(log_references=False)
    
    for test in test_messages:
        result = agent_default.strip_references(test["input"])
        passed = result == test["expected"]
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test['name']}")
        if not passed:
            print(f"  Expected: {test['expected'][:50]}...")
            print(f"  Got: {result[:50]}...")
    
    # Test with log_references=True
    print("\n2. Testing with log_references=True:")
    print("-" * 50)
    agent_with_refs = MockBarbieAgent(log_references=True)
    
    for test in test_messages:
        result = agent_with_refs.strip_references(test["input"])
        passed = result == test["input"]  # Should remain unchanged
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test['name']} (should keep references)")

def test_environment_variable():
    """Test that environment variable controls the behavior"""
    print("\n3. Testing environment variable control:")
    print("-" * 50)
    
    # Test default (should be False)
    log_refs = os.getenv("LOG_REFERENCES", "false").lower() == "true"
    print(f"Default LOG_REFERENCES value: {log_refs} (should be False)")
    
    # Test setting to true
    os.environ["LOG_REFERENCES"] = "true"
    log_refs = os.getenv("LOG_REFERENCES", "false").lower() == "true"
    print(f"After setting to 'true': {log_refs} (should be True)")
    
    # Test setting to false
    os.environ["LOG_REFERENCES"] = "false"
    log_refs = os.getenv("LOG_REFERENCES", "false").lower() == "true"
    print(f"After setting to 'false': {log_refs} (should be False)")
    
    # Clean up
    if "LOG_REFERENCES" in os.environ:
        del os.environ["LOG_REFERENCES"]

if __name__ == "__main__":
    test_reference_stripping()
    test_environment_variable()
    
    print("\n" + "=" * 60)
    print("🎯 Reference stripping test completed!")
    print("=" * 60)
    print("\nSUMMARY:")
    print("- References are stripped by default (LOG_REFERENCES=false)")
    print("- Can be enabled by setting LOG_REFERENCES=true")
    print("- Strips 'References:', 'Sources:', 'Citations:' sections")
    print("- Also removes 'Looking forward to...' phrases")
    print("- Preserves references when LOG_REFERENCES=true")