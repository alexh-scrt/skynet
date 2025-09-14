#!/usr/bin/env python3
"""
Test text wrapping functionality for conversation logging
"""

import time
import requests
import subprocess
import sys
import os
from datetime import datetime

import env

def clear_conversation_log():
    """Clear the conversation log file"""
    log_path = "./data/conversation/history.txt"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, "w") as f:
        f.write(f"=== TEXT WRAPPING TEST - {datetime.now().isoformat()} ===\n\n")
    
    return log_path

def start_agents():
    """Start both agents"""
    print("🚀 Starting agents for text wrapping test...")
    
    barbie_process = subprocess.Popen([
        sys.executable, "barbie.py"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    ken_process = subprocess.Popen([
        sys.executable, "ken.py"  
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(5)
    
    try:
        barbie_health = requests.get("http://localhost:8001/health", timeout=5)
        ken_health = requests.get("http://localhost:8002/health", timeout=5)
        
        if barbie_health.status_code == 200 and ken_health.status_code == 200:
            print("✅ Agents ready for wrapping test!")
            return barbie_process, ken_process
        else:
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_text_wrapping():
    """Send a request and check text wrapping in the log"""
    print("\n📝 Testing text wrapping...")
    
    # Send a question that should generate longer responses
    payload = {
        "message": "Please provide a detailed explanation of machine learning algorithms, including supervised learning, unsupervised learning, and reinforcement learning, with specific examples and applications for each type.",
        "conversation_id": "wrapping_test"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/v1/genesis",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Request sent successfully")
            
            # Wait for processing and response
            print("⏳ Waiting for response generation...")
            time.sleep(30)  # Give time for processing
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def analyze_text_wrapping(log_path):
    """Analyze the text wrapping in the conversation log"""
    print("\n🔍 Analyzing Text Wrapping")
    print("=" * 40)
    
    try:
        with open(log_path, "r") as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Analyze line lengths
        long_lines = []
        max_length = 0
        total_lines = 0
        
        for i, line in enumerate(lines):
            line_length = len(line)
            total_lines += 1
            
            if line_length > max_length:
                max_length = line_length
                
            if line_length > 80:
                long_lines.append((i + 1, line_length, line[:100] + "..." if len(line) > 100 else line))
        
        print(f"📊 Line Analysis:")
        print(f"  📏 Total lines: {total_lines}")
        print(f"  📏 Maximum line length: {max_length}")
        print(f"  📏 Lines over 80 characters: {len(long_lines)}")
        
        if len(long_lines) == 0:
            print("✅ All lines are 80 characters or less - wrapping working perfectly!")
        else:
            print(f"⚠️  Found {len(long_lines)} lines over 80 characters:")
            for line_num, length, preview in long_lines[:5]:  # Show first 5 long lines
                print(f"    Line {line_num}: {length} chars - {preview}")
        
        # Show a sample of the wrapped text
        print(f"\n📜 Sample of Wrapped Text:")
        print("-" * 80)
        sample_lines = lines[5:25]  # Skip header, show middle section
        for line in sample_lines:
            print(line)
        print("-" * 80)
        
        # Check readability
        print(f"\n📖 Readability Assessment:")
        if max_length <= 80:
            print("✅ Perfect - all lines within 80 character limit")
        elif max_length <= 90:
            print("✅ Good - most lines within acceptable range")
        else:
            print("⚠️ Some lines are too long for optimal readability")
        
        # Check for proper paragraph breaks
        paragraph_breaks = content.count('\n\n')
        print(f"📄 Paragraph breaks: {paragraph_breaks}")
        
        if paragraph_breaks > 0:
            print("✅ Proper paragraph formatting maintained")
        else:
            print("⚠️ May need better paragraph formatting")
        
        return len(long_lines) == 0
        
    except Exception as e:
        print(f"❌ Error analyzing wrapping: {e}")
        return False

def main():
    """Main test function"""
    print("📏 Text Wrapping Test for Conversation Logs")
    print("Testing 80-character line limit implementation")
    print("=" * 50)
    
    # Prepare
    log_path = clear_conversation_log()
    barbie_process, ken_process = start_agents()
    
    if not barbie_process or not ken_process:
        print("❌ Failed to start agents")
        return False
    
    try:
        # Test wrapping
        success = test_text_wrapping()
        
        if success:
            # Analyze results
            wrapping_good = analyze_text_wrapping(log_path)
            
            if wrapping_good:
                print("\n🎉 TEXT WRAPPING SUCCESS!")
                print("📏 All lines properly wrapped at 80 characters")
                print("📖 Conversation logs are now highly readable")
            else:
                print("\n⚠️ TEXT WRAPPING NEEDS REFINEMENT")
                print("🔧 Some lines may still exceed 80 characters")
                
            return wrapping_good
        else:
            print("❌ Failed to generate content for wrapping test")
            return False
    
    finally:
        print("\n🧹 Cleaning up...")
        if barbie_process:
            barbie_process.terminate()
        if ken_process:
            ken_process.terminate()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)