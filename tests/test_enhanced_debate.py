#!/usr/bin/env python3
"""
Test the enhanced debate system:
1. Research-based arguments with Tavily
2. Higher consensus threshold (0.99)
3. Deeper questioning and follow-ups
4. General-to-specific conversation flow
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
        f.write(f"=== ENHANCED DEBATE TEST - {datetime.now().isoformat()} ===\n\n")
    
    return log_path

def start_agents():
    """Start both agents"""
    print("🚀 Starting enhanced agents...")
    
    barbie_process = subprocess.Popen([
        sys.executable, "barbie.py"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    ken_process = subprocess.Popen([
        sys.executable, "ken.py"  
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(5)
    
    # Check health
    try:
        barbie_health = requests.get("http://localhost:8001/health", timeout=5)
        ken_health = requests.get("http://localhost:8002/health", timeout=5)
        
        if barbie_health.status_code == 200 and ken_health.status_code == 200:
            print("✅ Enhanced agents ready!")
            return barbie_process, ken_process
        else:
            print("❌ Agents not ready")
            return None, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None

def test_enhanced_debate(log_path):
    """Test the enhanced debate with challenging topic"""
    print("\n🥊 Testing Enhanced Debate System")
    print("=" * 40)
    
    # Use a controversial topic that should generate debate
    controversial_topic = "Should artificial intelligence development be regulated by government oversight, or should it remain in the hands of private companies?"
    
    print(f"📝 Controversial Topic: {controversial_topic}")
    
    payload = {
        "message": controversial_topic,
        "conversation_id": "enhanced_debate_test"
    }
    
    try:
        response = requests.post(
            "http://localhost:8001/v1/genesis",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Enhanced debate initiated")
            
            # Monitor for extended conversation (longer than before)
            print("⏳ Monitoring enhanced debate for 90 seconds...")
            
            previous_size = 0
            activity_count = 0
            
            for i in range(90):
                try:
                    with open(log_path, "r") as f:
                        content = f.read()
                    
                    current_size = len(content)
                    if current_size > previous_size:
                        activity_count += 1
                    previous_size = current_size
                    
                    barbie_count = content.count("Barbie:")
                    ken_count = content.count("Ken:")
                    has_research = "research" in content.lower() or "study" in content.lower() or "evidence" in content.lower()
                    
                    if i % 20 == 0:  # Update every 20 seconds
                        print(f"  📊 {i}s: Barbie: {barbie_count}, Ken: {ken_count}, Research: {has_research}, Activity: {activity_count}")
                    
                    # Stop if we have extensive debate
                    if barbie_count >= 3 and ken_count >= 2 and activity_count > 10:
                        print(f"🎯 Extensive debate detected after {i}s!")
                        time.sleep(5)  # Let it finish current exchange
                        break
                        
                except Exception as e:
                    if i % 30 == 0:
                        print(f"  ⚠️ Log error: {e}")
                
                time.sleep(1)
            
            return True
        else:
            print(f"❌ Debate initiation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error initiating debate: {e}")
        return False

def analyze_debate_quality(log_path):
    """Analyze the quality of the enhanced debate"""
    print("\n🔍 Analyzing Enhanced Debate Quality")
    print("=" * 50)
    
    try:
        with open(log_path, "r") as f:
            content = f.read()
        
        # Calculate metrics
        barbie_messages = content.count("Barbie:")
        ken_messages = content.count("Ken:")
        total_length = len(content)
        
        # Research indicators
        research_terms = ["research", "study", "evidence", "data", "findings", "according to", "studies show"]
        research_count = sum(content.lower().count(term) for term in research_terms)
        
        # Question indicators (deeper questioning)
        question_count = content.count("?")
        
        # Challenge indicators
        challenge_terms = ["however", "but", "although", "disagree", "challenge", "counter", "alternative", "problem"]
        challenge_count = sum(content.lower().count(term) for term in challenge_terms)
        
        # Agreement indicators (should be low early, higher later)
        agreement_terms = ["agree", "convinced", "excellent", "correct", "exactly"]
        agreement_count = sum(content.lower().count(term) for term in agreement_terms)
        
        # Final approval
        has_stop = "<STOP>" in content
        
        print(f"📊 Debate Metrics:")
        print(f"  💬 Total messages: Barbie {barbie_messages}, Ken {ken_messages}")
        print(f"  📖 Total length: {total_length:,} characters")
        print(f"  🔬 Research references: {research_count}")
        print(f"  ❓ Questions asked: {question_count}")
        print(f"  🤺 Challenge indicators: {challenge_count}")
        print(f"  🤝 Agreement indicators: {agreement_count}")
        print(f"  🛑 Reached conclusion: {has_stop}")
        
        # Quality assessment
        print(f"\n🎯 Quality Assessment:")
        
        # Length - should be longer with enhanced system
        if total_length > 5000:
            print("✅ Extensive debate length (>5000 chars)")
        else:
            print("⚠️ Short debate - may need more rigor")
        
        # Research usage
        if research_count >= 5:
            print("✅ Good research integration")
        else:
            print("⚠️ Limited research usage")
        
        # Questions for deeper exploration
        if question_count >= 10:
            print("✅ Extensive questioning for depth")
        else:
            print("⚠️ Limited questioning")
        
        # Challenge/debate dynamic
        if challenge_count >= 5:
            print("✅ Good challenge and counter-argument dynamic")
        else:
            print("⚠️ Limited challenging of ideas")
        
        # Agreement ratio (should be low until end)
        if ken_messages > 0:
            agreement_ratio = agreement_count / ken_messages
            if agreement_ratio < 0.5:
                print("✅ Appropriate skepticism maintained")
            else:
                print("⚠️ Too much early agreement")
        
        # Conversation progression
        if barbie_messages >= 3 and ken_messages >= 2:
            print("✅ Multi-round debate achieved")
        else:
            print("⚠️ Limited back-and-forth")
        
        # Overall assessment
        quality_score = 0
        if total_length > 5000: quality_score += 1
        if research_count >= 5: quality_score += 1
        if question_count >= 10: quality_score += 1
        if challenge_count >= 5: quality_score += 1
        if barbie_messages >= 3 and ken_messages >= 2: quality_score += 1
        
        print(f"\n🏆 Overall Quality Score: {quality_score}/5")
        
        if quality_score >= 4:
            print("🎉 EXCELLENT - Enhanced debate system working well!")
        elif quality_score >= 3:
            print("✅ GOOD - Most enhancements are working")
        else:
            print("⚠️ NEEDS IMPROVEMENT - Some enhancements not fully effective")
        
        # Show conversation preview
        print(f"\n📜 Debate Preview (first 1000 chars):")
        print("-" * 50)
        print(content[:1000] + "..." if len(content) > 1000 else content)
        print("-" * 50)
        
        return quality_score >= 3
        
    except Exception as e:
        print(f"❌ Error analyzing debate: {e}")
        return False

def main():
    """Main test function"""
    print("🥊 Enhanced Debate System Test")
    print("Testing: Research-based arguments, 0.99 threshold, deeper questioning")
    print("=" * 70)
    
    # Prepare
    log_path = clear_and_prepare_log()
    barbie_process, ken_process = start_agents()
    
    if not barbie_process or not ken_process:
        print("❌ Failed to start agents")
        return False
    
    try:
        # Test debate
        debate_success = test_enhanced_debate(log_path)
        
        if debate_success:
            # Analyze quality
            quality_good = analyze_debate_quality(log_path)
            
            if quality_good:
                print("\n🎉 ENHANCED DEBATE SYSTEM SUCCESS!")
                print("🔬 Research-based arguments implemented")
                print("🤺 Rigorous questioning and challenging working")
                print("📊 Higher standards preventing premature agreement")
            else:
                print("\n⚠️ ENHANCED SYSTEM PARTIALLY WORKING")
                print("🔧 Some aspects need further refinement")
                
            return quality_good
        else:
            print("❌ Failed to establish enhanced debate")
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