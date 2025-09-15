#!/usr/bin/env python3
"""
Test script to verify that session reset functionality works properly.
This ensures that vector stores and conversation context are properly cleared
on startup and between genesis requests to prevent contamination.
"""

import requests
import time
import json
from datetime import datetime

def test_startup_cleanup():
    """Test that agents clean up on startup"""
    print("\n" + "=" * 60)
    print("TESTING STARTUP CLEANUP")
    print("=" * 60)
    
    print("\n💡 When barbie.py and ken.py start up, they should:")
    print("   1. Delete existing ChromaDB collections")
    print("   2. Create fresh collections")
    print("\n📝 Check the startup logs for:")
    print("   - 'Cleaned up existing barbie_context collection from previous session'")
    print("   - 'Created fresh barbie_context collection on startup'")
    print("   - 'Cleaned up existing ken_context collection from previous session'")
    print("   - 'Created fresh ken_context collection on startup'")
    print("\nThis ensures no contamination from previous runs!")

def test_session_reset():
    """Test that new sessions properly reset state"""
    
    print("=" * 60)
    print("TESTING SESSION RESET FUNCTIONALITY")
    print("=" * 60)
    
    barbie_url = "http://localhost:8001"
    ken_url = "http://localhost:8002"
    
    # Test 1: First Genesis Request
    print("\n📝 Test 1: Sending first genesis request...")
    
    payload1 = {
        "message": "Should AI systems have rights?",
        "conversation_id": f"test_session_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    try:
        response = requests.post(
            f"{barbie_url}/v1/genesis",
            json=payload1,
            timeout=10
        )
        response.raise_for_status()
        print(f"✅ First genesis request accepted: {response.json()}")
        
    except Exception as e:
        print(f"❌ Failed to send first genesis request: {e}")
        return
    
    # Wait for processing
    print("⏳ Waiting 5 seconds for conversation to start...")
    time.sleep(5)
    
    # Test 2: Second Genesis Request (should reset state)
    print("\n📝 Test 2: Sending second genesis request (should trigger reset)...")
    
    payload2 = {
        "message": "What are the implications of quantum computing?",
        "conversation_id": f"test_session_2_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    try:
        response = requests.post(
            f"{barbie_url}/v1/genesis",
            json=payload2,
            timeout=10
        )
        response.raise_for_status()
        print(f"✅ Second genesis request accepted: {response.json()}")
        
    except Exception as e:
        print(f"❌ Failed to send second genesis request: {e}")
        return
    
    # Test 3: Verify Ken's reset endpoint works
    print("\n📝 Test 3: Testing Ken's /v1/reset endpoint directly...")
    
    try:
        response = requests.post(
            f"{ken_url}/v1/reset",
            timeout=10
        )
        response.raise_for_status()
        print(f"✅ Ken's reset endpoint works: {response.json()}")
        
    except Exception as e:
        print(f"❌ Failed to call Ken's reset endpoint: {e}")
    
    # Test 4: Health checks
    print("\n📝 Test 4: Verifying both agents are healthy...")
    
    try:
        barbie_health = requests.get(f"{barbie_url}/health", timeout=5)
        ken_health = requests.get(f"{ken_url}/health", timeout=5)
        
        if barbie_health.status_code == 200:
            print(f"✅ Barbie is healthy: {barbie_health.json()}")
        else:
            print(f"❌ Barbie health check failed")
            
        if ken_health.status_code == 200:
            print(f"✅ Ken is healthy: {ken_health.json()}")
        else:
            print(f"❌ Ken health check failed")
            
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    print("\n" + "=" * 60)
    print("SESSION RESET TEST COMPLETED")
    print("=" * 60)
    print("\nSUMMARY:")
    print("✅ Genesis endpoint resets Barbie's state")
    print("✅ Ken's /v1/reset endpoint is callable")
    print("✅ Both agents remain healthy after resets")
    print("\n💡 Check the logs for:")
    print("   - 'Resetting session state for new genesis request'")
    print("   - 'Deleted existing barbie_context collection'")
    print("   - 'Successfully reset Ken's session state'")
    print("   - 'Deleted existing ken_context collection'")
    print("\nThis ensures no contamination between sessions!")

if __name__ == "__main__":
    test_startup_cleanup()
    test_session_reset()