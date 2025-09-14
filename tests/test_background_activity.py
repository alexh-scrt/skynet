#!/usr/bin/env python3
"""
Test to monitor background processing activity
"""

import time
import requests
import subprocess
import sys
import signal
import os

def start_agents():
    """Start both agents and return their processes"""
    print("🚀 Starting agents...")
    
    barbie_process = subprocess.Popen([
        sys.executable, "barbie.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    ken_process = subprocess.Popen([
        sys.executable, "ken.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    # Wait for startup
    time.sleep(3)
    
    return barbie_process, ken_process

def test_background_activity():
    """Send a genesis request and monitor for background activity"""
    print("\n📝 Sending genesis request...")
    
    try:
        payload = {
            "message": "What makes a successful AI system?",
            "conversation_id": "bg_activity_test"
        }
        
        response = requests.post(
            "http://localhost:8001/v1/genesis",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            print("✅ Genesis request accepted")
            print("⏳ Monitoring background activity for 15 seconds...")
            
            # Monitor for background activity
            time.sleep(15)
            
        else:
            print(f"❌ Genesis request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main test"""
    print("🔍 Background Activity Monitor Test")
    print("=" * 40)
    
    barbie_process, ken_process = start_agents()
    
    try:
        test_background_activity()
        
    finally:
        print("\n🧹 Cleaning up...")
        barbie_process.terminate()
        ken_process.terminate()
        
        # Print some output from the agents
        print("\n📋 Barbie output (last 10 lines):")
        try:
            stdout, _ = barbie_process.communicate(timeout=2)
            lines = stdout.split('\n')[-10:]
            for line in lines:
                if line.strip():
                    print(f"  {line}")
        except:
            print("  (Unable to capture output)")
            
        print("\n📋 Ken output (last 10 lines):")
        try:
            stdout, _ = ken_process.communicate(timeout=2)
            lines = stdout.split('\n')[-10:]
            for line in lines:
                if line.strip():
                    print(f"  {line}")
        except:
            print("  (Unable to capture output)")

if __name__ == "__main__":
    main()