#!/usr/bin/env python3
"""
Final Launch Test for Skynet
Tests the complete genesis workflow with real agents
"""

import threading
import time
import requests
import subprocess
import sys
from datetime import datetime

import env  # Load environment variables

def start_agent(agent_name, script_name, port):
    """Start an agent in the background"""
    print(f"🚀 Starting {agent_name} on port {port}...")
    
    # Start the agent process
    process = subprocess.Popen([
        sys.executable, script_name
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Wait for agent to start up
    for i in range(20):  # Wait up to 20 seconds
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            if response.status_code == 200:
                print(f"  ✅ {agent_name} is ready!")
                return process
        except:
            time.sleep(1)
    
    print(f"  ❌ {agent_name} failed to start")
    return None

def test_genesis_workflow():
    """Test the complete genesis workflow"""
    print("\n🧪 Testing Genesis Workflow")
    print("=" * 40)
    
    # Test question for the debate
    test_question = "What is the most important factor for building successful AI systems in 2025?"
    
    print(f"📝 Question: {test_question}")
    print("\n💭 Initiating Barbie-Ken debate...")
    
    try:
        # Send genesis request to Barbie
        genesis_payload = {
            "message": test_question,
            "conversation_id": f"launch_test_{int(time.time())}"
        }
        
        response = requests.post(
            "http://localhost:8001/v1/genesis", 
            json=genesis_payload,
            timeout=120  # Give it 2 minutes for the full debate
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🎉 Genesis workflow completed successfully!")
            print(f"💬 Final response: {result['response'][:200]}...")
            print(f"🆔 Conversation ID: {result['conversation_id']}")
            print(f"⏰ Timestamp: {result['timestamp']}")
            print(f"🤖 Agent: {result['agent']}")
            return True
        else:
            print(f"❌ Genesis request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error during genesis workflow: {e}")
        return False

def test_individual_endpoints():
    """Test individual agent endpoints"""
    print("\n🔍 Testing Individual Endpoints")
    print("=" * 40)
    
    # Test Barbie health
    try:
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"💖 Barbie Health: ✅ {health['status']}")
        else:
            print("💖 Barbie Health: ❌ Failed")
    except Exception as e:
        print(f"💖 Barbie Health: ❌ Error - {e}")
    
    # Test Ken health
    try:
        response = requests.get("http://localhost:8002/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"🎯 Ken Health: ✅ {health['status']}")
        else:
            print("🎯 Ken Health: ❌ Failed")
    except Exception as e:
        print(f"🎯 Ken Health: ❌ Error - {e}")
    
    # Test Ken direct evaluation
    print("\n🔬 Testing Ken evaluation...")
    try:
        ken_payload = {
            "message": "Hi! I am Barbie! Here's my test response for evaluation.",
            "conversation_id": "direct_test"
        }
        
        response = requests.post(
            "http://localhost:8002/v1/chat",
            json=ken_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Ken evaluation successful")
            print(f"  📊 Confidence: {result.get('confidence', 'N/A')}")
            print(f"  ✅ Approved: {result.get('approved', 'N/A')}")
            print(f"  💬 Response: {result['response'][:100]}...")
        else:
            print(f"  ❌ Ken evaluation failed: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Ken evaluation error: {e}")

def main():
    """Main launch test"""
    print("🤖 Skynet Launch Test")
    print("🚀 Testing Complete Genesis → Debate → Consensus Workflow")
    print("=" * 60)
    
    # Start both agents
    barbie_process = start_agent("Barbie", "barbie.py", 8001)
    ken_process = start_agent("Ken", "ken.py", 8002)
    
    if not barbie_process or not ken_process:
        print("❌ Failed to start agents")
        return False
    
    try:
        # Test individual endpoints first
        test_individual_endpoints()
        
        # Test the full genesis workflow
        success = test_genesis_workflow()
        
        print("\n" + "=" * 60)
        if success:
            print("🎉 LAUNCH SUCCESSFUL! Skynet is ready for action!")
            print("🤖 Barbie and Ken are communicating and debating properly")
            print("📡 All services are working correctly")
        else:
            print("⚠️  LAUNCH NEEDS ATTENTION")
            print("🔧 Check the error messages above")
        
        return success
        
    finally:
        # Cleanup processes
        print("\n🧹 Cleaning up...")
        if barbie_process:
            barbie_process.terminate()
            print("  Stopped Barbie")
        if ken_process:
            ken_process.terminate()
            print("  Stopped Ken")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)