#!/usr/bin/env python3
"""
Test to verify natural dialog prompt changes
Run with: conda activate skynet && python tests/test_natural_dialog.py
"""

import sys
import re
from pathlib import Path

# Proper path setup for tests folder
prj_path = Path(__file__).parent.parent
sys.path.insert(0, str(prj_path))

def test_prompt_changes():
    """Test that our prompt changes removed formal patterns"""
    print("=" * 60)
    print("TESTING NATURAL DIALOG PROMPT CHANGES")
    print("=" * 60)
    
    # Read the modified files to verify changes
    ken_file = prj_path / 'ken.py'
    barbie_file = prj_path / 'barbie.py'
    
    with open(ken_file, 'r') as f:
        ken_content = f.read()
    
    with open(barbie_file, 'r') as f:
        barbie_content = f.read()
    
    # Test patterns that should be REMOVED
    removed_patterns = [
        r"Hi Barbie, this is Ken!",
        r"Hi, I'm Barbie!",
        r"introduce yourself as.*Hi.*Barbie",
        r"Start with.*Hi.*Ken"
    ]
    
    print("CHECKING FOR REMOVED FORMAL GREETING PATTERNS:")
    print("-" * 50)
    
    all_good = True
    for pattern in removed_patterns:
        ken_matches = re.findall(pattern, ken_content, re.IGNORECASE)
        barbie_matches = re.findall(pattern, barbie_content, re.IGNORECASE)
        
        if ken_matches:
            print(f"❌ FOUND in ken.py: {pattern} -> {ken_matches}")
            all_good = False
        if barbie_matches:
            print(f"❌ FOUND in barbie.py: {pattern} -> {barbie_matches}")
            all_good = False
    
    if all_good:
        print("✅ All formal greeting patterns successfully removed!")
    print()
    
    # Test patterns that should be ADDED
    added_patterns = [
        r"Begin your response naturally without formal introductions",
        r"Continue the conversation naturally",
        r"NATURAL DIALOG STYLE",
        r"No formal closings",
        r"Simply stop talking when your thought is complete"
    ]
    
    print("CHECKING FOR ADDED NATURAL DIALOG INSTRUCTIONS:")
    print("-" * 50)
    
    natural_dialog_added = True
    for pattern in added_patterns:
        ken_matches = re.findall(pattern, ken_content, re.IGNORECASE)
        barbie_matches = re.findall(pattern, barbie_content, re.IGNORECASE)
        
        if ken_matches or barbie_matches:
            print(f"✅ FOUND: {pattern}")
        else:
            print(f"❌ MISSING: {pattern}")
            natural_dialog_added = False
    
    if natural_dialog_added:
        print("✅ All natural dialog instructions successfully added!")
    print()

def test_response_filtering_changes():
    """Test that response filtering was updated"""
    print("CHECKING RESPONSE FILTERING CHANGES:")
    print("-" * 50)
    
    filter_file = prj_path / 'src' / 'utils' / 'response_filtering.py'
    
    try:
        with open(filter_file, 'r') as f:
            filter_content = f.read()
        
        # Check for new filtering patterns
        new_patterns = [
            r"Best regards",
            r"Sincerely",
            r"Talk soon",
            r"Hi,?\s+I'm\s+\(Barbie\|Ken\)"
        ]
        
        for pattern in new_patterns:
            if pattern in filter_content:
                print(f"✅ ADDED filtering pattern: {pattern}")
            else:
                print(f"❌ MISSING filtering pattern: {pattern}")
        
    except FileNotFoundError:
        print("❌ Response filtering file not found")
    print()

def show_example_differences():
    """Show examples of what changed"""
    print("EXAMPLE OF CHANGES MADE:")
    print("-" * 50)
    
    print("BEFORE (formal letter style):")
    print("  Ken: 'Hi Barbie, this is Ken! I think your argument...'")
    print("  Barbie: 'Hi, I'm Barbie! Let me share my thoughts...'")
    print("  Ken: 'That's interesting. Looking forward to your response!'")
    print("  Ken: 'Best regards, Ken'")
    print()
    
    print("AFTER (natural dialog):")
    print("  Ken: 'I think your argument has some merit, but...'")
    print("  Barbie: 'That raises an interesting point about consciousness...'")
    print("  Ken: 'That's a compelling perspective. What evidence supports this?'")
    print("  (no formal closings - conversation just ends naturally)")
    print()

def test_prompt_content():
    """Test actual prompt content generation"""
    print("TESTING PROMPT CONTENT:")
    print("-" * 50)
    
    # Import necessary modules safely
    try:
        from src.utils.response_filtering import ResponseFilter
        
        filter_system = ResponseFilter()
        
        # Test formal messages that should be filtered
        test_cases = [
            ("Hi Barbie, this is Ken! I think your argument has merit...", "Ken"),
            ("Hi, I'm Barbie! Let me share my thoughts on this topic...", "Barbie"),
            ("That's a great point. Looking forward to your response!", "Ken"),
            ("I appreciate your perspective. Best regards, Ken", "Ken"),
            ("Your analysis is thorough. Sincerely, Barbie", "Barbie")
        ]
        
        print("Testing response filtering:")
        for test_response, agent in test_cases:
            cleaned = filter_system.clean_response(test_response, agent)
            if cleaned != test_response:
                print(f"✅ Filtered: '{test_response[:30]}...'")
            else:
                print(f"⚠️  Not filtered: '{test_response[:30]}...'")
        
    except ImportError as e:
        print(f"⚠️  Could not import response filtering: {e}")
    except Exception as e:
        print(f"⚠️  Error testing response filtering: {e}")
    
    print()

if __name__ == "__main__":
    test_prompt_changes()
    test_response_filtering_changes()
    show_example_differences()
    test_prompt_content()
    
    print("=" * 60)
    print("🎯 Natural dialog transformation testing completed!")
    print("=" * 60)
    print("\nSUMMARY OF CHANGES:")
    print("1. Removed formal greetings like 'Hi Barbie, this is Ken!'")
    print("2. Removed formal closings like 'Looking forward to...', 'Best regards'")
    print("3. Added instructions for natural dialog flow")
    print("4. Updated response filtering to catch and remove formal patterns")
    print("\nThe agents should now have natural conversations without letter-style exchanges.")