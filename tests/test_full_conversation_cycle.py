#!/usr/bin/env python3
"""
Test a full conversation cycle with proper logging
"""

import time
import requests
import subprocess
import sys
import os
from datetime import datetime

import env

def test_full_conversation():
    """Test the full conversation cycle"""
    print("🔄 Full Conversation Cycle Test")
    print("=" * 40)
    
    # Clear and prepare log file
    log_path = "./data/conversation/history.txt"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, "w") as f:
        f.write(f"=== FULL CYCLE TEST - {datetime.now().isoformat()} ===\n\n")
    
    print("🚀 Starting agents...")
    
    # Start agents
    barbie_process = subprocess.Popen([
        sys.executable, "barbie.py"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    ken_process = subprocess.Popen([
        sys.executable, "ken.py"  
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Wait for startup
    time.sleep(5)
    
    try:
        # Send genesis request
        print("📝 Sending genesis request...")
        payload = {
            "message": "What makes AI systems trustworthy?",
            "conversation_id": "full_cycle_test"
        }
        
        response = requests.post(
            "http://localhost:8001/v1/genesis",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Genesis request sent successfully")
            
            # Monitor the log file for 60 seconds
            print("⏳ Monitoring conversation for 60 seconds...")
            
            for i in range(60):
                try:
                    with open(log_path, "r") as f:
                        content = f.read()
                    
                    barbie_count = content.count("Barbie:")
                    ken_count = content.count("Ken:")
                    
                    if i % 10 == 0:  # Update every 10 seconds
                        print(f"  📊 {i}s: Barbie messages: {barbie_count}, Ken messages: {ken_count}")
                    
                    # Check if we have a good conversation going
                    if barbie_count >= 2 and ken_count >= 1:
                        print(f"🎉 Good conversation detected! Barbie: {barbie_count}, Ken: {ken_count}")
                        break
                        
                except Exception as e:
                    if i % 20 == 0:
                        print(f"  ⚠️  Log read error: {e}")
                
                time.sleep(1)
            
            # Show final results
            print("\n📜 Final Conversation Log:")
            print("=" * 50)
            
            try:
                with open(log_path, "r") as f:
                    content = f.read()
                print(content)
                
                # Final analysis
                barbie_final = content.count("Barbie:")
                ken_final = content.count("Ken:")
                has_stop = "<STOP>" in content
                
                print("\n🔍 Final Analysis:")
                print(f"📊 Total Barbie messages: {barbie_final}")
                print(f"📊 Total Ken messages: {ken_final}")
                print(f"🛑 Has <STOP> marker: {has_stop}")
                
                if barbie_final > 0 and ken_final > 0:
                    print("✅ Successful conversation cycle with proper logging!")
                else:
                    print("⚠️  Incomplete conversation cycle")
                    
            except Exception as e:
                print(f"❌ Error reading final log: {e}")
                
        else:
            print(f"❌ Genesis request failed: {response.status_code}")
    
    finally:
        print("\n🧹 Cleaning up...")
        barbie_process.terminate()
        ken_process.terminate()

if __name__ == "__main__":
    test_full_conversation()