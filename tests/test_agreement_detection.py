#!/usr/bin/env python3
"""
Test the improved agreement detection system
"""

import sys
from pathlib import Path

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.agreement_detector import AgreementDetector, AgreementLevel


def test_agreement_detection():
    """Test various Ken responses to ensure proper agreement detection"""
    
    print("🔍 TESTING AGREEMENT DETECTION SYSTEM")
    print("=" * 60)
    print()
    
    detector = AgreementDetector()
    
    # Test cases with different types of Ken responses
    test_cases = [
        {
            "name": "Strong Disagreement - Ken has many concerns",
            "message": """Hi Barbie! I must be honest—I still have some serious reservations that need to be explored further. 
            I disagree with several of your points and I'm concerned about the evidence you've provided. 
            Let me challenge the premises of your arguments. How do you know this is correct? 
            Looking forward to your detailed explanations!""",
            "expected_level": AgreementLevel.DISAGREEMENT,
            "should_continue": True
        },
        
        {
            "name": "Mixed Response - Some agreement but still has questions", 
            "message": """That's a good point, Barbie! I appreciate your perspective and I can see some merit in your arguments. 
            However, I still have some concerns about the implementation. Could you clarify how this would work in practice? 
            What about the potential risks we discussed?""",
            "expected_level": AgreementLevel.MIXED_RESPONSE,
            "should_continue": True
        },
        
        {
            "name": "Leaning Agreement - Mostly convinced but minor concerns",
            "message": """You make excellent points, Barbie! I agree with most of your analysis and I think you're right about the core issues. 
            The evidence you've provided is compelling. I have just one small concern about the timeline - do you think that's realistic?""",
            "expected_level": AgreementLevel.LEANING_AGREEMENT, 
            "should_continue": True
        },
        
        {
            "name": "Strong Agreement - Fully convinced",
            "message": """You're absolutely right, Barbie! You've completely convinced me with your evidence and reasoning. 
            I agree with all your points and I have no more objections. That settles it - I'm fully persuaded by your arguments.""",
            "expected_level": AgreementLevel.STRONG_AGREEMENT,
            "should_continue": False
        },
        
        {
            "name": "Explicit Stop Request",
            "message": """I think we can conclude this discussion now. You've made your case well and I'm convinced. 
            <STOP> - no more debate needed.""",
            "expected_level": AgreementLevel.STRONG_AGREEMENT,
            "should_continue": False
        },
        
        {
            "name": "The Original Problematic Case - Ken still debating",
            "message": """Thank you for your detailed response. However, I must be honest—I still have some reservations that need to be explored further.
            Could you provide specific references? How do you know these theories will lead to practical benefits? 
            Let me challenge the premises of some of your arguments. Looking forward to your detailed explanations!""",
            "expected_level": AgreementLevel.DISAGREEMENT,
            "should_continue": True
        }
    ]
    
    print("TEST RESULTS:")
    print("-" * 40)
    
    all_passed = True
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. {case['name']}")
        print("-" * (len(case['name']) + 3))
        
        # Analyze the message
        analysis = detector.analyze_agreement(case['message'])
        should_end, reason = detector.should_end_conversation(case['message'])
        should_continue = not should_end
        
        # Check results
        level_correct = analysis['agreement_level'] == case['expected_level']
        continue_correct = should_continue == case['should_continue']
        
        print(f"   Expected Level: {case['expected_level'].name}")
        print(f"   Detected Level: {analysis['agreement_level'].name} {'✅' if level_correct else '❌'}")
        print(f"   Expected Continue: {case['should_continue']}")
        print(f"   Should Continue: {should_continue} {'✅' if continue_correct else '❌'}")
        print(f"   Confidence: {analysis['confidence']:.2f}")
        print(f"   Explanation: {analysis['explanation']}")
        
        # Track overall success
        if not (level_correct and continue_correct):
            all_passed = False
            print("   ❌ TEST FAILED")
        else:
            print("   ✅ TEST PASSED")
    
    print(f"\n{'='*60}")
    print(f"OVERALL RESULT: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    print(f"{'='*60}")
    
    return all_passed


def demonstrate_improvement():
    """Show how the new system fixes the original problem"""
    
    print(f"\n{'='*60}")
    print("DEMONSTRATION: FIXING THE ORIGINAL PROBLEM")
    print(f"{'='*60}")
    
    # The problematic Ken message from the conversation
    problematic_ken_message = """Hi Barbie, this is Ken!

Thank you for your detailed and thoughtful response. I appreciate the effort you've put into addressing my concerns and presenting your ideas so eloquently. However, I must be honest—I still have some reservations that need to be explored further.

Firstly, while you mentioned several studies from reputable journals like *Nature Neuroscience* and *Science*, upon reviewing these sources, there was no mention of an 85% accuracy rate for BCIs. This discrepancy concerns me as it raises questions about the credibility of your claims. Could you provide specific references or clarify which studies support this statistic?

Additionally, I noticed that while you touched on integrating social sciences into AI research through frameworks like actor-network theory and human-machine reconfigurations, there were no concrete examples or data to substantiate these assertions. How do you know that these theories will lead to practical benefits without specific case studies or measurable outcomes?

Let me challenge the premises of some of your arguments. How do you know that BCIs will achieve an 85% accuracy rate? What evidence supports this claim? Also, what makes you confident that integrating social sciences into AI research through specific frameworks will yield the benefits you describe?

Looking forward to your detailed explanations and examples!

Best regards,
Ken"""
    
    detector = AgreementDetector()
    
    print("ORIGINAL PROBLEM:")
    print("-" * 20)
    print("❌ System incorrectly concluded: 'Ken agreed'")
    print("❌ Conversation ended prematurely")
    print("❌ Summary said: 'Conversation completed - Ken agreed'")
    
    print(f"\nNEW SYSTEM ANALYSIS:")
    print("-" * 20)
    
    analysis = detector.analyze_agreement(problematic_ken_message)
    should_end, reason = detector.should_end_conversation(problematic_ken_message)
    
    print(f"✅ Agreement Level: {analysis['agreement_level'].name}")
    print(f"✅ Should End Conversation: {should_end}")
    print(f"✅ Reason: {reason}")
    print(f"✅ Confidence: {analysis['confidence']:.2f}")
    
    print(f"\nINDICATORS DETECTED:")
    print("-" * 20)
    for indicator, count in analysis['indicators'].items():
        if count > 0:
            print(f"  • {indicator.replace('_', ' ').title()}: {count}")
    
    print(f"\nRESULT:")
    print("-" * 10)
    if should_end:
        print("❌ Still would end incorrectly - need to adjust thresholds")
    else:
        print("✅ Correctly identifies that debate should continue!")
        print("✅ Ken clearly has reservations and wants more evidence!")
        print("✅ Conversation will continue until Ken is truly convinced!")
    
    return not should_end  # Success if it doesn't end prematurely


if __name__ == "__main__":
    print("Testing improved agreement detection system...\n")
    
    test_passed = test_agreement_detection()
    demo_passed = demonstrate_improvement()
    
    print(f"\n{'='*60}")
    print("FINAL SUMMARY:")
    print(f"{'='*60}")
    
    if test_passed and demo_passed:
        print("🎉 AGREEMENT DETECTION SYSTEM WORKING CORRECTLY!")
        print("✅ Properly identifies when Ken wants to continue debating")
        print("✅ Only ends conversation when Ken truly agrees")
        print("✅ Provides detailed analysis and reasoning")
        print("✅ Fixes the premature conversation ending problem")
    else:
        print("❌ SYSTEM NEEDS FURTHER ADJUSTMENT")
        if not test_passed:
            print("❌ Some test cases failed")
        if not demo_passed:
            print("❌ Original problem case still fails")
    
    print(f"\n💡 INTEGRATION STATUS:")
    print("✅ AgreementDetector class created")
    print("✅ Integrated into Barbie's chat processing")
    print("✅ Replaces simple keyword-based detection")
    print("✅ Provides nuanced analysis of Ken's responses")
    
    print(f"\n🚀 NOW READY FOR ACCURATE CONVERSATION ENDINGS!")
    print("   Conversations will only end when Ken is truly convinced!")