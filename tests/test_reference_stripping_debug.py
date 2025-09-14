#!/usr/bin/env python3
"""
Debug reference stripping functionality
"""

import sys
import re
from pathlib import Path

# Proper path setup for tests folder
prj_path = Path(__file__).parent.parent
sys.path.insert(0, str(prj_path))

def strip_references(message, log_references=False):
    """Remove reference section from messages if log_references is False"""
    if log_references:
        return message
        
    # Pattern to match References section at the end of messages
    patterns = [
        r'\n\n?(?:References|Sources|Citations):.*?(?=\n\n|$)',
        r'\n\n?\*\*(?:References|Sources|Citations)\*\*:.*?(?=\n\n|$)',
        # Also match individual reference lines that look like citations
        r'\n(?:[A-Z][a-z]+(?:,\s*[A-Z]\.)?,?\s*(?:&\s*)?)+\([0-9]{4}\)\..*?(?=\n|$)'
    ]
    
    cleaned = message
    for i, pattern in enumerate(patterns):
        before = cleaned
        cleaned = re.sub(pattern, '', cleaned, flags=re.DOTALL | re.MULTILINE)
        if before != cleaned:
            print(f"  Pattern {i+1} matched and removed content")
    
    # Clean up any trailing "Looking forward" type phrases
    before = cleaned
    cleaned = re.sub(r'\n\n?Looking forward to.*?(?:\n|$)', '', cleaned, flags=re.IGNORECASE)
    if before != cleaned:
        print(f"  'Looking forward' pattern matched and removed")
    
    # Remove any excessive whitespace
    cleaned = re.sub(r'\n\n+', '\n\n', cleaned).strip()
    return cleaned

# Test case 1
message1 = """Thank you for your thoughtful feedback, Ken! I appreciate your insights.

The study on AI consciousness shows promising results for future development.

References:
Barocas, S., Hardt, M., & Narayanan, A. (2019). Fairness and machine learning. Nature Machine Intelligence, 1(1), 44-48.
European Commission. (2020). Horizon 2020: The EU Framework Programme for Research and Innovation.

Looking forward to your response!"""

print("=" * 60)
print("Test 1: Message with References section")
print("-" * 60)
print("ORIGINAL:")
print(repr(message1))
print("\nPROCESSING:")
result1 = strip_references(message1)
print("\nRESULT:")
print(repr(result1))
print("\nEXPECTED:")
expected1 = """Thank you for your thoughtful feedback, Ken! I appreciate your insights.

The study on AI consciousness shows promising results for future development."""
print(repr(expected1))
print(f"\nMatch: {result1 == expected1}")
if result1 != expected1:
    print(f"Length difference: {len(result1)} vs {len(expected1)}")
    print(f"Character difference at: {[i for i, (c1, c2) in enumerate(zip(result1, expected1)) if c1 != c2]}")

print("\n" + "=" * 60)

# Test case 2
message2 = """As Yakalı (2024) noted in their study, gender representation matters.

The implications are significant for AI design.

Yakalı, D. (2024). Deconstructing hegemonic masculinity. Frontiers in Sociology, 9, 1320774."""

print("Test 2: Message with inline citation")
print("-" * 60)
print("ORIGINAL:")
print(repr(message2))
print("\nPROCESSING:")
result2 = strip_references(message2)
print("\nRESULT:")
print(repr(result2))
print("\nEXPECTED:")
expected2 = """As Yakalı (2024) noted in their study, gender representation matters.

The implications are significant for AI design."""
print(repr(expected2))
print(f"\nMatch: {result2 == expected2}")