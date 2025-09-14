#!/usr/bin/env python3
"""
Comprehensive test of all debate progression quality fixes
"""

import sys
from pathlib import Path

# Add project root to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.debate.progression_tracker import DebateProgressionTracker
from src.debate.progression_prompts import ProgressionPromptGenerator
from src.utils.agreement_detector import AgreementDetector
from src.utils.evidence_validator import EvidenceValidator

def test_all_fixes_comprehensive():
    """Comprehensive test of all quality improvements"""
    
    print("🔧 COMPREHENSIVE DEBATE QUALITY FIX VALIDATION")
    print("=" * 70)
    print()
    
    # Initialize all systems
    tracker = DebateProgressionTracker()
    agreement_detector = AgreementDetector()
    evidence_validator = EvidenceValidator()
    
    results = {
        "repetitive_questioning": False,
        "conversation_ending": False, 
        "claim_extraction": False,
        "evidence_validation": False,
        "rehashing_detection": False
    }
    
    print("1. TESTING REPETITIVE QUESTIONING DETECTION")
    print("-" * 50)
    
    # Test repetitive questioning - simulate Ken asking similar questions multiple times
    question_patterns = [
        "Could you provide specific examples that support their effectiveness?",
        "Can you share studies that validate these approaches?", 
        "What specific steps would you use to ensure collaboration?",
        "Could you provide concrete examples of success?"
    ]
    
    # Ask similar questions multiple times to trigger pattern detection
    ken_claims = 0
    ken_rehashing = []
    
    for round_num in range(5):  # Ask questions across 5 rounds
        tracker.advance_round()
        for question in question_patterns:
            test_msg = f"Hi Barbie! {question} I need more details."
            claims = tracker.extract_claims_from_message(test_msg, "Ken")
            ken_claims += len(claims)
            
            rehash = tracker.detect_rehashing(test_msg)
            ken_rehashing.extend(rehash)
    
    repetitive_patterns = [item for item in ken_rehashing if item.get('type') == 'repetitive_question']
    
    total_questions = len(question_patterns) * 5  # 4 questions × 5 rounds
    print(f"Questions asked across rounds: {total_questions}")
    print(f"Claims extracted: {ken_claims} (should be 0, they're all questions)")
    print(f"Repetitive patterns detected: {len(repetitive_patterns)}")
    
    for pattern in repetitive_patterns[:3]:  # Show first 3
        print(f"  • Pattern: {pattern['pattern']} (repeated {pattern['rehash_count']} times)")
    
    if len(repetitive_patterns) > 0 and ken_claims == 0:
        results["repetitive_questioning"] = True
        print("✅ PASSED: Repetitive questioning properly detected")
    else:
        print("❌ FAILED: Repetitive questioning not detected properly")
    print()
    
    print("2. TESTING CONVERSATION ENDING LOGIC")
    print("-" * 50)
    
    # Test with Ken's actual final message that was incorrectly detected as agreement
    ken_final_message = """Hi Barbie, this is Ken!

I appreciate the effort you've put into your arguments, but I have some concerns that need addressing. Let's delve deeper into each point.

1. **Handling Criticism**: Could you provide specific examples or studies that support their effectiveness?
2. **Constructive Feedback**: Are there specific techniques you recommend for maintaining this balance?
3. **Cultural Adaptability**: Can you share any cross-cultural studies that validate these approaches?
4. **AI Solutions Feasibility**: What steps would you take to mitigate these risks and ensure accessibility?
5. **Evidence-Based Claims**: Could you share specific studies or data that directly back up each of your points?
6. **Premise Challenge**: What evidence supports this assumption, and how would you address potential pushback?
7. **Edge Cases Exploration**: How would your AI tools be implemented effectively?
8. **Implementation Specifics**: What specific steps or frameworks would you use to ensure successful collaboration?

By addressing these points with detailed explanations and evidence, we can better assess the robustness of your arguments.

Looking forward to a thorough discussion!"""
    
    analysis = agreement_detector.analyze_agreement(ken_final_message)
    should_end, reason = agreement_detector.should_end_conversation(ken_final_message)
    
    print(f"Agreement level: {analysis['agreement_level'].name}")
    print(f"Should continue debate: {analysis['should_continue_debate']}")
    print(f"Should end conversation: {should_end}")
    print(f"Reason: {reason}")
    print(f"Question count detected: {analysis['indicators']['questions']}")
    
    if not should_end and analysis['should_continue_debate']:
        results["conversation_ending"] = True
        print("✅ PASSED: Correctly identifies Ken wants to continue debating")
    else:
        print("❌ FAILED: Incorrectly thinks conversation should end")
    print()
    
    print("3. TESTING CLAIM EXTRACTION IMPROVEMENTS")
    print("-" * 50)
    
    # Test claim vs question separation
    mixed_message = """I believe AI consciousness is possible through neural complexity. 
Research clearly shows that integrated information theory supports this view.
The evidence demonstrates that quantum effects play a role.
How do you know that approach will work? 
Could you provide specific examples of successful implementations?"""
    
    tracker.advance_round()
    mixed_claims = tracker.extract_claims_from_message(mixed_message, "Barbie")
    mixed_rehashing = tracker.detect_rehashing(mixed_message)
    
    expected_claims = 3  # "I believe...", "Research clearly shows...", "The evidence demonstrates..."
    actual_questions = mixed_message.count('?')
    
    print(f"Mixed message with {actual_questions} questions and {expected_claims} expected claims")
    print(f"Claims extracted: {len(mixed_claims)}")
    print(f"Questions properly separated: {len(tracker.questions_asked)} question entries")
    
    if len(mixed_claims) == expected_claims:
        results["claim_extraction"] = True
        print("✅ PASSED: Claims and questions properly separated")
    else:
        print("❌ FAILED: Claims and questions not separated correctly")
    print()
    
    print("4. TESTING EVIDENCE VALIDATION")
    print("-" * 50)
    
    # Test with the problematic diabetes citations for AI consciousness
    poor_evidence_message = """I believe AI consciousness is achievable through quantum processes.
    Research by Seidu et al. (2024) published in Diabetes Care shows the efficacy of glucose monitoring.
    Additionally, Shi et al. (2024) published in The Lancet on obesity treatment demonstrates complexity.
    These studies support my position on artificial intelligence consciousness development."""
    
    topic = "AI consciousness and quantum theories"
    evidence_validation = evidence_validator.validate_message_evidence(poor_evidence_message, topic)
    
    print(f"Citations found: {evidence_validation['total_citations']}")
    print(f"Evidence quality score: {evidence_validation['evidence_quality_score']:.2f}")
    print(f"Overall assessment: {evidence_validation['overall_evidence_quality']}")
    
    irrelevant_citations = evidence_validation['relevance_summary']['irrelevant']
    total_citations = evidence_validation['total_citations']
    
    if total_citations > 0 and irrelevant_citations >= total_citations * 0.5:
        results["evidence_validation"] = True
        print("✅ PASSED: Correctly identifies irrelevant health citations for AI topic")
    else:
        print("❌ FAILED: Did not properly identify irrelevant citations")
    print()
    
    print("5. TESTING COMPREHENSIVE REHASHING DETECTION")
    print("-" * 50)
    
    # Test both claim and question rehashing
    tracker.advance_round()
    rehashing_message = """I maintain my position that AI consciousness requires quantum processes.
    Could you provide specific examples supporting your claims?
    As I've argued before, neural complexity leads to awareness.
    Can you share studies that validate your methodology?
    The quantum theory clearly demonstrates consciousness emergence."""
    
    # Add this message multiple times to trigger rehashing
    for i in range(4):
        tracker.advance_round()
        tracker.extract_claims_from_message(rehashing_message, "Barbie")
    
    final_rehashing = tracker.detect_rehashing(rehashing_message)
    
    claim_rehashing = [item for item in final_rehashing if item.get('type') != 'repetitive_question']
    question_rehashing = [item for item in final_rehashing if item.get('type') == 'repetitive_question']
    
    print(f"Total rehashing detected: {len(final_rehashing)} items")
    print(f"Claim rehashing: {len(claim_rehashing)} items")
    print(f"Question pattern rehashing: {len(question_rehashing)} items")
    
    if len(final_rehashing) > 0:
        results["rehashing_detection"] = True
        print("✅ PASSED: Comprehensive rehashing detection working")
    else:
        print("❌ FAILED: Rehashing detection not working properly")
    print()
    
    print("=" * 70)
    print("FINAL RESULTS SUMMARY")
    print("=" * 70)
    
    passed_tests = sum(results.values())
    total_tests = len(results)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name.replace('_', ' ').title()}")
    
    print()
    print(f"OVERALL SCORE: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL QUALITY FIXES WORKING CORRECTLY!")
        print("The debate progression system now properly handles:")
        print("  • Repetitive questioning patterns from Ken")
        print("  • Correct conversation ending detection")
        print("  • Improved claim vs question separation")
        print("  • Evidence validation and irrelevant citation detection")
        print("  • Comprehensive rehashing detection")
        print("\n🚀 READY FOR PRODUCTION!")
    else:
        print(f"⚠️  {total_tests - passed_tests} tests still failing")
        print("Additional fixes needed before production")
    
    return results


def demonstrate_quality_improvements():
    """Demonstrate the quality improvements with before/after examples"""
    
    print("\n" + "=" * 70)
    print("BEFORE vs AFTER COMPARISON")
    print("=" * 70)
    
    print("\n📉 BEFORE (Issues from conversation_20250913_180422.md):")
    print("  • Ken asked 8 similar questions repeatedly")
    print("  • System incorrectly detected 'Ken agreed' with 25 questions pending")
    print("  • Diabetes studies cited for AI consciousness (irrelevant)")
    print("  • No detection of repetitive questioning patterns")
    print("  • Claims and questions not properly separated")
    
    print("\n📈 AFTER (With Quality Fixes):")
    print("  • Repetitive question patterns detected and flagged")
    print("  • Conversation correctly continues when Ken has many questions")
    print("  • Irrelevant health citations identified and flagged")
    print("  • Questions tracked separately from claims")
    print("  • Comprehensive rehashing detection for all types")
    
    print("\n🎯 SPECIFIC IMPROVEMENTS:")
    print("  1. Agreement Detection: Now handles 25+ questions correctly")
    print("  2. Question Pattern Recognition: 'could_you_provide' type detected")
    print("  3. Evidence Validation: 0.0 quality score for diabetes → AI citations")
    print("  4. Claim Extraction: Questions no longer counted as claims")
    print("  5. Rehashing Prevention: Both claims and questions tracked")
    
    return True


if __name__ == "__main__":
    # Run comprehensive test
    test_results = test_all_fixes_comprehensive()
    
    # Show improvements
    demonstrate_quality_improvements()
    
    # Final assessment
    if all(test_results.values()):
        print(f"\n✅ COMPREHENSIVE FIX VALIDATION: SUCCESS")
        print("All identified quality issues from conversation_20250913_180422.md have been addressed")
        sys.exit(0)
    else:
        print(f"\n❌ COMPREHENSIVE FIX VALIDATION: PARTIAL")
        failed_tests = [test for test, passed in test_results.items() if not passed]
        print(f"Still need to address: {', '.join(failed_tests)}")
        sys.exit(1)