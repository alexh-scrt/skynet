#!/usr/bin/env python3
"""
Test that both Barbie and Ken are actively using Tavily web search
"""

import time
import requests
import subprocess
import sys
import os
from datetime import datetime

import env

def clear_and_prepare_log():
    """Clear conversation log and prepare for test"""
    log_path = "./data/conversation/history.txt"
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    
    with open(log_path, "w") as f:
        f.write(f"=== TAVILY SEARCH TEST - {datetime.now().isoformat()} ===\n\n")
    
    return log_path

def start_agents_with_logging():
    """Start agents with visible logging to see search activity"""
    print("🚀 Starting agents with search logging...")
    
    # Start with visible stdout to see search activity
    barbie_process = subprocess.Popen([
        sys.executable, "barbie.py"
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    ken_process = subprocess.Popen([
        sys.executable, "ken.py"  
    ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    time.sleep(5)
    
    try:
        barbie_health = requests.get("http://localhost:8001/health", timeout=5)
        ken_health = requests.get("http://localhost:8002/health", timeout=5)
        
        if barbie_health.status_code == 200 and ken_health.status_code == 200:
            print("✅ Agents ready for search testing!")
            return barbie_process, ken_process
        else:
            print("❌ Agents not ready")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_tavily_search_usage():
    """Test Tavily search with a topic that should trigger research"""
    print("\n🔍 Testing Tavily Search Usage")
    print("=" * 40)
    
    # Use a topic that should definitely trigger web search
    research_topic = "What are the latest breakthrough developments in quantum computing in 2024 and their potential impact on artificial intelligence?"
    
    print(f"📝 Research Topic: {research_topic}")
    print("This topic should trigger extensive web search by both agents")
    
    payload = {
        "message": research_topic,
        "conversation_id": "tavily_search_test"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/v1/genesis",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✅ Genesis request sent successfully")
            print("⏳ Monitoring for search activity...")
            return True
        else:
            print(f"❌ Genesis request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def monitor_agent_logs(barbie_process, ken_process, duration=45):
    """Monitor agent logs for search activity"""
    print(f"\n📊 Monitoring agent logs for {duration} seconds...")
    
    barbie_search_activity = []
    ken_search_activity = []
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # Check Barbie logs
        try:
            barbie_output = barbie_process.stdout.readline()
            if barbie_output:
                if "search" in barbie_output.lower() or "tavily" in barbie_output.lower() or "research" in barbie_output.lower():
                    barbie_search_activity.append(barbie_output.strip())
                    print(f"🔍 Barbie Search: {barbie_output.strip()}")
        except:
            pass
        
        # Check Ken logs
        try:
            ken_output = ken_process.stdout.readline()
            if ken_output:
                if "search" in ken_output.lower() or "tavily" in ken_output.lower() or "research" in ken_output.lower():
                    ken_search_activity.append(ken_output.strip())
                    print(f"🎯 Ken Search: {ken_output.strip()}")
        except:
            pass
        
        time.sleep(0.5)
    
    return barbie_search_activity, ken_search_activity

def analyze_conversation_for_research(log_path):
    """Analyze conversation log for evidence of research usage"""
    print("\n📚 Analyzing Conversation for Research Evidence")
    print("=" * 50)
    
    try:
        with open(log_path, "r") as f:
            content = f.read()
        
        # Look for research indicators in the conversation
        research_indicators = [
            "according to", "research shows", "studies indicate", "data reveals",
            "recent findings", "latest research", "experts report", "analysis shows",
            "survey results", "published", "breakthrough", "development", "advancement",
            "quantum computing", "2024", "scientists", "researchers", "study", "evidence"
        ]
        
        search_evidence = []
        for indicator in research_indicators:
            if indicator.lower() in content.lower():
                # Find context around the indicator
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if indicator.lower() in line.lower():
                        context = ' '.join(lines[max(0, i-1):i+2])  # Line before and after
                        search_evidence.append((indicator, context[:100] + "..."))
        
        print(f"📊 Research Evidence Analysis:")
        print(f"  📝 Total conversation length: {len(content)} characters")
        print(f"  🔍 Research indicators found: {len(search_evidence)}")
        
        if search_evidence:
            print(f"  ✅ Evidence of research integration:")
            for indicator, context in search_evidence[:5]:  # Show first 5
                print(f"    - '{indicator}': {context}")
        else:
            print(f"  ❌ No research indicators found in conversation")
        
        # Check for specific quantum computing content
        quantum_mentions = content.lower().count("quantum")
        computing_mentions = content.lower().count("computing")
        ai_mentions = content.lower().count("artificial intelligence") + content.lower().count(" ai ")
        
        print(f"\n🔬 Topic-Specific Analysis:")
        print(f"  🔮 'Quantum' mentions: {quantum_mentions}")
        print(f"  💻 'Computing' mentions: {computing_mentions}")
        print(f"  🤖 'AI' mentions: {ai_mentions}")
        
        # Overall assessment
        research_score = len(search_evidence)
        topic_relevance = quantum_mentions + computing_mentions + ai_mentions
        
        print(f"\n🎯 Research Usage Assessment:")
        if research_score >= 3 and topic_relevance >= 5:
            print("✅ EXCELLENT - Strong evidence of research integration")
            return True
        elif research_score >= 1 and topic_relevance >= 2:
            print("✅ GOOD - Some evidence of research usage")
            return True
        else:
            print("❌ POOR - Limited or no evidence of research")
            return False
        
    except Exception as e:
        print(f"❌ Error analyzing conversation: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 Tavily Web Search Usage Test")
    print("Testing that both Barbie and Ken actively research topics")
    print("=" * 60)
    
    # Prepare
    log_path = clear_and_prepare_log()
    barbie_process, ken_process = start_agents_with_logging()
    
    if not barbie_process or not ken_process:
        print("❌ Failed to start agents")
        return False
    
    try:
        # Test search usage
        search_initiated = test_tavily_search_usage()
        
        if search_initiated:
            # Monitor for search activity
            barbie_searches, ken_searches = monitor_agent_logs(barbie_process, ken_process)
            
            print(f"\n📊 Search Activity Summary:")
            print(f"  🔍 Barbie search activities: {len(barbie_searches)}")
            print(f"  🎯 Ken search activities: {len(ken_searches)}")
            
            if barbie_searches:
                print(f"  📝 Barbie search examples:")
                for search in barbie_searches[:3]:
                    print(f"    - {search}")
            
            if ken_searches:
                print(f"  📝 Ken search examples:")
                for search in ken_searches[:3]:
                    print(f"    - {search}")
            
            # Wait a bit more for conversation to develop
            print("\n⏳ Allowing time for conversation development...")
            time.sleep(30)
            
            # Analyze conversation content
            research_integrated = analyze_conversation_for_research(log_path)
            
            # Overall assessment
            search_working = len(barbie_searches) > 0 or len(ken_searches) > 0
            
            if search_working and research_integrated:
                print("\n🎉 TAVILY SEARCH SUCCESS!")
                print("🔍 Both agents are actively using web search")
                print("📚 Research is being integrated into arguments")
            elif search_working:
                print("\n⚠️ PARTIAL SUCCESS")
                print("🔍 Search activity detected but limited integration")
            else:
                print("\n❌ SEARCH NOT WORKING")
                print("🔧 Agents are not using Tavily search effectively")
                
            return search_working and research_integrated
        else:
            print("❌ Failed to initiate search test")
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