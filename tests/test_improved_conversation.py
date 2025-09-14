#!/usr/bin/env python3
"""
Test the improved conversation flow:
1. Strip <think>...</think> content from Ken's responses
2. Only introduce themselves in first message  
3. Refer to each other by name in subsequent messages
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
        f.write(f"=== IMPROVED CONVERSATION TEST - {datetime.now().isoformat()} ===\n\n")
    
    return log_path

def start_agents():
    """Start both agents"""
    print("🚀 Starting agents...")
    
    barbie_process = subprocess.Popen([
        sys.executable, "barbie.py"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    ken_process = subprocess.Popen([
        sys.executable, "ken.py"  
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for startup
    time.sleep(5)
    
    # Verify they're running
    try:
        barbie_health = requests.get("http://localhost:8001/health", timeout=5)
        ken_health = requests.get("http://localhost:8002/health", timeout=5)
        
        if barbie_health.status_code == 200 and ken_health.status_code == 200:
            print("✅ Both agents ready!")
            return barbie_process, ken_process
        else:
            print("❌ Agents not responding")
            return None, None
            
    except Exception as e:
        print(f"❌ Error checking agents: {e}")
        return None, None

def send_genesis_and_monitor(log_path):
    """Send genesis request and monitor conversation"""
    print("\n📝 Sending genesis request...")
    
    payload = {
        "message": "How can we ensure AI systems remain beneficial to humanity?",
        "conversation_id": "improved_test"
    }
    
    response = requests.post(
        "http://localhost:8001/v1/genesis",
        json=payload,
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ Genesis request sent")
        
        # Monitor for conversation activity
        print("⏳ Monitoring conversation for 45 seconds...")
        
        for i in range(45):
            try:
                with open(log_path, "r") as f:
                    content = f.read()
                
                barbie_count = content.count("Barbie:")
                ken_count = content.count("Ken:")
                
                if i % 15 == 0:  # Update every 15 seconds
                    print(f"  📊 {i}s: Barbie: {barbie_count}, Ken: {ken_count}")
                
                # Stop if we have good conversation
                if barbie_count >= 2 and ken_count >= 1:
                    print(f"🎉 Good conversation detected after {i}s!")
                    break
                    
            except Exception as e:
                if i % 20 == 0:
                    print(f"  ⚠️  Log error: {e}")
            
            time.sleep(1)
            
        return True
    else:
        print(f"❌ Genesis failed: {response.status_code}")
        return False

def analyze_conversation_improvements(log_path):
    """Analyze the conversation for improvements"""
    print("\n🔍 Analyzing Conversation Improvements")
    print("=" * 50)
    
    try:
        with open(log_path, "r") as f:
            content = f.read()
        
        print("📜 Conversation Log:")
        print("-" * 30)
        print(content)
        print("-" * 30)
        
        # Analysis
        print("\n🔍 Improvement Analysis:")
        
        # 1. Check for thinking content removal
        think_tags = content.count("<think>")
        if think_tags == 0:
            print("✅ No <think> tags found in log - thinking content properly stripped")
        else:
            print(f"❌ Found {think_tags} <think> tags - thinking content not stripped")
        
        # 2. Check introduction patterns
        barbie_intros = content.count("Hi, I'm Barbie!")
        ken_intros = content.count("Hi Barbie, this is Ken!")
        
        print(f"📊 Barbie introductions: {barbie_intros}")
        print(f"📊 Ken introductions: {ken_intros}")
        
        if barbie_intros <= 1 and ken_intros <= 1:
            print("✅ Agents only introduced themselves once")
        else:
            print("❌ Agents are repeating introductions")
        
        # 3. Check for name references
        barbie_mentions_ken = content.count("Ken") - ken_intros  # Subtract introduction mentions
        ken_mentions_barbie = content.count("Barbie") - barbie_intros
        
        print(f"📊 Barbie mentions Ken: {barbie_mentions_ken} times")
        print(f"📊 Ken mentions Barbie: {ken_mentions_barbie} times")
        
        if barbie_mentions_ken > 0 or ken_mentions_barbie > 0:
            print("✅ Agents refer to each other by name")
        else:
            print("⚠️  Limited name references found")
        
        # 4. Check conversation quality
        barbie_messages = content.count("Barbie:")
        ken_messages = content.count("Ken:")
        has_stop = "<STOP>" in content
        
        print(f"📊 Total messages - Barbie: {barbie_messages}, Ken: {ken_messages}")
        print(f"🛑 Conversation ended properly: {has_stop}")
        
        # Overall assessment
        print("\n🎯 Overall Assessment:")
        improvements_working = (
            think_tags == 0 and  # No thinking content
            barbie_intros <= 1 and ken_intros <= 1 and  # Single introductions
            (barbie_mentions_ken > 0 or ken_mentions_barbie > 0) and  # Name references
            barbie_messages > 0 and ken_messages > 0  # Both agents participated
        )
        
        if improvements_working:
            print("🎉 All conversation improvements are working correctly!")
            print("✅ Thinking content stripped")
            print("✅ Single introductions only")
            print("✅ Name references present")
            print("✅ Good conversation flow")
        else:
            print("⚠️  Some improvements need attention")
            
        return improvements_working
        
    except Exception as e:
        print(f"❌ Error analyzing conversation: {e}")
        return False

def main():
    """Main test function"""
    print("🎭 Improved Conversation Flow Test")
    print("=" * 40)
    
    # Clear log and start agents
    log_path = clear_conversation_log()
    barbie_process, ken_process = start_agents()
    
    if not barbie_process or not ken_process:
        print("❌ Failed to start agents")
        return False
    
    try:
        # Send genesis and monitor
        success = send_genesis_and_monitor(log_path)
        
        if success:
            # Analyze improvements
            improvements_working = analyze_conversation_improvements(log_path)
            
            if improvements_working:
                print("\n🎉 CONVERSATION IMPROVEMENTS SUCCESS!")
                print("🔧 All requested improvements implemented correctly")
            else:
                print("\n⚠️  CONVERSATION IMPROVEMENTS NEED ATTENTION")
                print("🔧 Review the analysis above")
                
            return improvements_working
        else:
            print("❌ Failed to establish conversation")
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