#!/usr/bin/env python3
"""
Test Runner for Skynet Distributed GAN System
Run this script to execute all unit and integration tests
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests for the Skynet system"""
    
    print("🧪 Running Skynet Distributed GAN Tests")
    print("=" * 50)
    
    # Change to the tests directory
    tests_dir = Path(__file__).parent
    os.chdir(tests_dir)
    
    # Test files to run
    test_files = [
        "test_memory.py",
        "test_source_verification.py", 
        "test_agent_personalities.py",
        "test_enhanced_prompts.py",
        "test_clean_responses.py",
        "test_verified_conversation.py",
        "test_conversation_logging.py",
        "test_thinking_content_removal.py",
        "test_debate_progression.py"
    ]
    
    total_passed = 0
    total_failed = 0
    
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"❌ Test file {test_file} not found!")
            continue
            
        print(f"\n🔍 Running {test_file}...")
        print("-" * 30)
        
        try:
            # Run Python test file directly
            result = subprocess.run([
                sys.executable, test_file
            ], capture_output=True, text=True)
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode == 0:
                print(f"✅ {test_file} - All tests passed!")
                # Count passed tests from output (look for "passed" or "✓")
                passed = result.stdout.count("passed") + result.stdout.count("✓")
                total_passed += max(1, passed)  # At least 1 if file ran successfully
            else:
                print(f"❌ {test_file} - Some tests failed!")
                total_failed += 1
                
        except Exception as e:
            print(f"❌ Error running {test_file}: {e}")
            total_failed += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    
    if total_failed == 0:
        print("\n🎉 All tests passed! Skynet is ready for action!")
        return 0
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Please check the output above.")
        return 1

def run_specific_test_class(test_class):
    """Run a specific test class"""
    print(f"🧪 Running specific test class: {test_class}")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "-v", 
            "-k", test_class,
            "--tb=short"
        ], capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running test class {test_class}: {e}")
        return False

if __name__ == "__main__":
    # Check if specific test class is requested
    if len(sys.argv) > 1:
        test_class = sys.argv[1]
        success = run_specific_test_class(test_class)
        sys.exit(0 if success else 1)
    else:
        # Run all tests
        exit_code = run_tests()
        sys.exit(exit_code)