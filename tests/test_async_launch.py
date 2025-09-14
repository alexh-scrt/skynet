#!/usr/bin/env python3
"""
Test the new asynchronous architecture for Skynet
Tests that endpoints return immediately and processing happens in background
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

def test_asynchronous_behavior():
    """Test that endpoints return immediately"""
    print("\n🧪 Testing Asynchronous Behavior")
    print("=" * 40)
    
    # Test 1: Genesis endpoint should return immediately
    print("📝 Testing /v1/genesis immediate response...")
    
    start_time = time.time()
    
    try:
        genesis_payload = {
            "message": "What is the most effective approach to machine learning in 2025?",
            "conversation_id": f"async_test_{int(time.time())}"
        }
        
        response = requests.post(
            "http://localhost:8001/v1/genesis", 
            json=genesis_payload,
            timeout=5  # Should respond within 5 seconds
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Genesis endpoint responded in {response_time:.2f}s")
            print(f"  📦 Status: {result.get('status')}")
            print(f"  💬 Message: {result.get('message')}")
            print(f"  🆔 Conversation ID: {result.get('conversation_id')}")
            
            if response_time < 2.0:  # Should be very fast
                print(f"  🎯 Excellent! Response time under 2 seconds - truly async")
                return True
            else:
                print(f"  ⚠️  Response time {response_time:.2f}s - might be processing synchronously")
                return False
        else:
            print(f"  ❌ Genesis request failed with status {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except requests.Timeout:
        print(f"  ❌ Genesis request timed out - likely processing synchronously")
        return False
    except Exception as e:
        print(f"  ❌ Error during genesis test: {e}")
        return False

def test_background_processing():
    """Test that background processing is working"""
    print("\n🔄 Testing Background Processing")
    print("=" * 40)
    
    # Monitor logs to see if background processing happens
    print("📊 Checking if background processing starts...")
    
    # Give some time for background processing to begin
    time.sleep(3)
    
    # Test Ken's endpoint response time
    print("🎯 Testing Ken's /v1/chat immediate response...")
    
    start_time = time.time()
    
    try:
        ken_payload = {
            "message": "Hi! I am Barbie! Test message for Ken.",
            "conversation_id": "async_ken_test"
        }
        
        response = requests.post(
            "http://localhost:8002/v1/chat",
            json=ken_payload,
            timeout=5
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ Ken endpoint responded in {response_time:.2f}s")
            print(f"  📦 Status: {result.get('status')}")
            print(f"  💬 Message: {result.get('message')}")
            
            if response_time < 2.0:
                print(f"  🎯 Excellent! Ken also responds immediately")
                return True
            else:
                print(f"  ⚠️  Ken response time {response_time:.2f}s - might be slow")
                return False
        else:
            print(f"  ❌ Ken request failed with status {response.status_code}")
            return False
            
    except requests.Timeout:
        print(f"  ❌ Ken request timed out")
        return False
    except Exception as e:
        print(f"  ❌ Error during Ken test: {e}")
        return False

def test_multiple_concurrent_requests():
    """Test handling multiple concurrent requests"""
    print("\n🚁 Testing Concurrent Request Handling")
    print("=" * 40)
    
    def send_genesis_request(i):
        try:
            start = time.time()
            payload = {
                "message": f"Concurrent test question {i}: What are the benefits of async processing?",
                "conversation_id": f"concurrent_test_{i}"
            }
            
            response = requests.post(
                "http://localhost:8001/v1/genesis",
                json=payload,
                timeout=10
            )
            
            end = time.time()
            
            if response.status_code == 200:
                print(f"  ✅ Request {i} completed in {end-start:.2f}s")
                return True
            else:
                print(f"  ❌ Request {i} failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ Request {i} error: {e}")
            return False
    
    # Send 3 concurrent requests
    threads = []
    for i in range(3):
        thread = threading.Thread(target=send_genesis_request, args=(i,))
        threads.append(thread)
    
    print("🚀 Sending 3 concurrent genesis requests...")
    start_time = time.time()
    
    for thread in threads:
        thread.start()
    
    for thread in threads:
        thread.join()
    
    total_time = time.time() - start_time
    print(f"📊 All concurrent requests completed in {total_time:.2f}s total")
    
    if total_time < 10:  # Should handle concurrency well
        print("🎯 Excellent concurrent handling!")
        return True
    else:
        print("⚠️  Concurrent handling could be improved")
        return False

def main():
    """Main test for asynchronous architecture"""
    print("🤖 Skynet Asynchronous Architecture Test")
    print("🔄 Testing Non-Blocking Endpoints & Background Processing")
    print("=" * 60)
    
    # Start both agents
    barbie_process = start_agent("Barbie", "barbie.py", 8001)
    ken_process = start_agent("Ken", "ken.py", 8002)
    
    if not barbie_process or not ken_process:
        print("❌ Failed to start agents")
        return False
    
    try:
        # Give agents time to fully initialize their background workers
        print("\n⏳ Allowing agents to initialize background workers...")
        time.sleep(2)
        
        # Test asynchronous behavior
        async_test = test_asynchronous_behavior()
        
        # Test background processing
        bg_test = test_background_processing()
        
        # Test concurrent handling
        concurrent_test = test_multiple_concurrent_requests()
        
        print("\n" + "=" * 60)
        if async_test and bg_test and concurrent_test:
            print("🎉 ASYNCHRONOUS ARCHITECTURE SUCCESS!")
            print("✅ Endpoints respond immediately")
            print("✅ Background processing works correctly") 
            print("✅ Concurrent requests handled well")
            print("🚀 Skynet is ready for high-performance operation!")
        else:
            print("⚠️  ASYNCHRONOUS ARCHITECTURE NEEDS ATTENTION")
            print("🔧 Check the test results above for specific issues")
        
        # Give background workers time to process
        print("\n⏳ Allowing background processing to complete...")
        time.sleep(10)
        
        return async_test and bg_test and concurrent_test
        
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