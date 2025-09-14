#!/usr/bin/env python3
"""
Comprehensive test of all quality improvements implemented for the debate progression system
"""

import sys
from pathlib import Path

# Add project root to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.evidence_validator import EvidenceValidator
from src.utils.topic_coherence_monitor import TopicCoherenceMonitor
from src.utils.debate_conclusion_detector import DebateConclusionDetector
from src.debate.progression_tracker import DebateProgressionTracker
from src.utils.agreement_detector import AgreementDetector

def test_all_quality_improvements():
    """Test all quality improvement systems working together"""
    
    print("🚀 COMPREHENSIVE QUALITY IMPROVEMENTS TEST")
    print("Testing all systems based on issues found in conversation_20250913_184248.md")
    print("=" * 80)
    print()
    
    # Initialize all systems
    evidence_validator = EvidenceValidator()
    topic_monitor = TopicCoherenceMonitor("What is consciousness and how can AI systems become genuinely sentient")
    conclusion_detector = DebateConclusionDetector()
    progression_tracker = DebateProgressionTracker()
    agreement_detector = AgreementDetector()
    
    test_results = {
        "future_dated_citations": False,
        "topic_drift_detection": False,
        "conclusion_detection": False,
        "repetitive_questioning": False,
        "evidence_coherence": False
    }
    
    print("🔍 TEST 1: FUTURE-DATED CITATION DETECTION")
    print("-" * 60)
    
    # Test future-dated citations (major issue from conversation)
    future_citation_message = """I believe AI consciousness is achievable. Research by Allen Institute (2025) 
    demonstrates the origins of consciousness. Studies by Hameroff (2024) show quantum effects in microtubules. 
    Additionally, work by Seidu et al. (2024) published in Diabetes Care provides insights."""
    
    evidence_validation = evidence_validator.validate_message_evidence(
        future_citation_message, 
        "AI consciousness and quantum theories"
    )
    
    future_dated_count = sum(1 for v in evidence_validation['validations'] 
                           if 'future-dated' in v.explanation.lower())
    irrelevant_count = evidence_validation['relevance_summary']['irrelevant']
    
    print(f"Citations found: {evidence_validation['total_citations']}")
    print(f"Future-dated citations: {future_dated_count}")
    print(f"Irrelevant citations: {irrelevant_count}")
    print(f"Evidence quality score: {evidence_validation['evidence_quality_score']:.2f}")
    
    if future_dated_count >= 2 and evidence_validation['evidence_quality_score'] == 0.0:
        test_results["future_dated_citations"] = True
        print("✅ PASSED: Future-dated citations properly detected and scored 0.0")
    else:
        print("❌ FAILED: Future-dated citations not properly handled")
    
    print()
    print("🔍 TEST 2: TOPIC DRIFT DETECTION")
    print("-" * 60)
    
    # Test topic drift (major issue from conversation)
    drift_messages = [
        ("Barbie", "I believe quantum consciousness is possible through microtubules in the brain."),
        ("Ken", "What evidence supports quantum consciousness? How does IIT relate?"),
        ("Barbie", "Brain-computer interfaces could help with appetite regulation and hunger control."),
        ("Ken", "How does hunger regulation relate to consciousness? This seems off-topic."),
        ("Barbie", "Swarm intelligence algorithms can optimize neural networks for diabetes monitoring.")
    ]
    
    drift_detected_count = 0
    for speaker, message in drift_messages:
        analysis = topic_monitor.analyze_topic_coherence(message, speaker)
        print(f"{speaker}: {message[:50]}...")
        print(f"  Relevance: {analysis.relevance_level.name}")
        
        if analysis.relevance_level.value >= 4:  # TOPIC_DRIFT or COMPLETELY_UNRELATED
            drift_detected_count += 1
            print(f"  ⚠️  DRIFT DETECTED: {analysis.drift_explanation}")
    
    should_intervene, intervention_msg = topic_monitor.should_intervene_for_drift()
    
    print(f"Drift instances detected: {drift_detected_count}")
    print(f"Should intervene: {should_intervene}")
    
    if drift_detected_count >= 2 and should_intervene:
        test_results["topic_drift_detection"] = True
        print("✅ PASSED: Topic drift properly detected with intervention")
    else:
        print("❌ FAILED: Topic drift detection not working properly")
    
    print()
    print("🔍 TEST 3: DEBATE CONCLUSION DETECTION")
    print("-" * 60)
    
    # Test conclusion detection
    conclusion_messages = [
        ("Barbie", "I believe AI consciousness requires quantum processing capabilities.", 1),
        ("Ken", "I challenge that assumption. What evidence supports quantum consciousness?", 2),
        ("Barbie", "Studies suggest microtubules could enable quantum effects in the brain.", 3),
        ("Ken", "That's speculative. How would we test for quantum consciousness?", 4),
        ("Barbie", "We could develop quantum-inspired algorithms and test emergent behaviors.", 5),
        ("Ken", "That's an interesting approach. I agree testing is crucial for validation.", 6),
        ("Barbie", "In conclusion, while we disagree on mechanisms, we both value testing.", 7),
        ("Ken", "Fair point. Overall, this discussion highlighted the complexity of consciousness.", 8)
    ]
    
    for speaker, message, round_num in conclusion_messages:
        conclusion_detector.analyze_message(message, speaker, round_num)
    
    conclusion_analysis = conclusion_detector.should_conclude_debate()
    
    print(f"Current stage: {conclusion_analysis.current_stage.name}")
    print(f"Should conclude: {conclusion_analysis.should_conclude}")
    print(f"Confidence: {conclusion_analysis.conclusion_confidence:.2f}")
    print(f"Reason: {conclusion_analysis.conclusion_reason}")
    
    if conclusion_analysis.should_conclude and conclusion_analysis.conclusion_confidence >= 0.8:
        test_results["conclusion_detection"] = True
        print("✅ PASSED: Natural conclusion properly detected")
    else:
        print("❌ FAILED: Conclusion detection not working properly")
    
    print()
    print("🔍 TEST 4: ENHANCED REPETITIVE QUESTIONING DETECTION")
    print("-" * 60)
    
    # Test repetitive questioning (original issue)
    repetitive_questions = [
        "Could you provide specific examples that support your claims?",
        "Can you share studies that validate your methodology?", 
        "Could you provide concrete evidence for your assertions?",
        "Can you share specific data that backs up your points?",
        "Could you provide more detailed explanations for your approach?"
    ]
    
    progression_tracker.advance_round()
    repetitive_patterns_found = []
    
    for i, question in enumerate(repetitive_questions):
        progression_tracker.advance_round()
        message = f"Hi Barbie! {question} I need more clarification on this."
        
        claims = progression_tracker.extract_claims_from_message(message, "Ken")
        rehashing = progression_tracker.detect_rehashing(message)
        
        question_patterns = [item for item in rehashing if item.get('type') == 'repetitive_question']
        repetitive_patterns_found.extend(question_patterns)
    
    print(f"Repetitive question patterns detected: {len(repetitive_patterns_found)}")
    for pattern in repetitive_patterns_found[:3]:  # Show first 3
        print(f"  • Pattern: {pattern.get('pattern')} (repeated {pattern['rehash_count']} times)")
    
    if len(repetitive_patterns_found) >= 2:
        test_results["repetitive_questioning"] = True
        print("✅ PASSED: Repetitive questioning patterns detected")
    else:
        print("❌ FAILED: Repetitive questioning not detected properly")
    
    print()
    print("🔍 TEST 5: EVIDENCE-CLAIM COHERENCE CHECKING")
    print("-" * 60)
    
    # Test coherence between evidence and claims
    coherence_test_message = """I believe AI consciousness is possible through quantum processes.
    Research by Seidu et al. (2024) on diabetes glucose monitoring demonstrates complex biological systems.
    Studies by Shi et al. (2024) on obesity pharmacotherapy show how medications affect cognitive function.
    This evidence clearly supports the quantum consciousness hypothesis in artificial intelligence."""
    
    coherence_validation = evidence_validator.validate_message_evidence(
        coherence_test_message,
        "AI consciousness and quantum theories"
    )
    
    health_ai_mismatches = 0
    for validation in coherence_validation['validations']:
        if ('diabetes' in validation.explanation.lower() or 'obesity' in validation.explanation.lower()) and \
           validation.relevance.name == 'IRRELEVANT':
            health_ai_mismatches += 1
    
    print(f"Health-to-AI topic mismatches detected: {health_ai_mismatches}")
    print(f"Overall evidence quality: {coherence_validation['evidence_quality_score']:.2f}")
    
    if health_ai_mismatches >= 2 and coherence_validation['evidence_quality_score'] <= 0.1:
        test_results["evidence_coherence"] = True
        print("✅ PASSED: Evidence-claim coherence issues properly detected")
    else:
        print("❌ FAILED: Evidence-claim coherence checking not working")
    
    print()
    return test_results


def show_improvement_summary(test_results):
    """Show summary of all improvements"""
    
    print("=" * 80)
    print("📊 COMPREHENSIVE QUALITY IMPROVEMENTS SUMMARY")
    print("=" * 80)
    
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    
    print(f"OVERALL SCORE: {passed_tests}/{total_tests} quality improvements working")
    print()
    
    improvements = [
        ("Future-Dated Citation Detection", test_results["future_dated_citations"], 
         "Flags citations from 2024+ as likely fabricated"),
        ("Topic Drift Detection & Correction", test_results["topic_drift_detection"],
         "Detects when conversation drifts from consciousness to unrelated topics"),
        ("Natural Conclusion Detection", test_results["conclusion_detection"],
         "Identifies when debates reach natural endpoints"),
        ("Enhanced Repetitive Questioning", test_results["repetitive_questioning"],
         "Detects when Ken asks the same types of questions repeatedly"),
        ("Evidence-Claim Coherence Checking", test_results["evidence_coherence"],
         "Identifies when health studies are cited for AI/consciousness topics")
    ]
    
    for improvement, passed, description in improvements:
        status = "✅ WORKING" if passed else "❌ NEEDS WORK"
        print(f"{status}: {improvement}")
        print(f"   {description}")
        print()
    
    print("🎯 IMPACT ON CONVERSATION QUALITY:")
    print("-" * 40)
    
    if passed_tests >= 4:
        print("🚀 EXCELLENT: Major quality improvements implemented successfully!")
        print("   • Future-dated citations will be immediately flagged")
        print("   • Topic drift will be detected and corrected") 
        print("   • Debates will conclude naturally when appropriate")
        print("   • Repetitive questioning patterns will be identified")
        print("   • Evidence relevance will be validated")
        print()
        print("📈 EXPECTED IMPROVEMENTS:")
        print("   • Fewer irrelevant citations (diabetes studies for AI topics)")
        print("   • Better conversation focus and coherence")
        print("   • Natural conclusion detection prevents endless debates")
        print("   • Enhanced pattern recognition prevents circular discussions")
        print("   • Higher quality evidence validation")
        
    elif passed_tests >= 3:
        print("✅ GOOD: Most quality improvements working correctly")
        print("   Additional testing may be needed for remaining issues")
        
    else:
        print("⚠️  PARTIAL: Some quality improvements need additional work")
        failed_systems = [name for name, passed in test_results.items() if not passed]
        print(f"   Systems needing attention: {', '.join(failed_systems)}")
    
    print()
    print("🔧 SYSTEMS INTEGRATED:")
    print("   • EvidenceValidator - Citation quality and relevance checking")
    print("   • TopicCoherenceMonitor - Topic drift detection and correction")
    print("   • DebateConclusionDetector - Natural conclusion identification")
    print("   • Enhanced ProgressionTracker - Repetitive pattern detection")
    print("   • Improved AgreementDetector - Better conversation ending logic")
    
    return passed_tests == total_tests


def main():
    """Main test function"""
    
    test_results = test_all_quality_improvements()
    all_systems_working = show_improvement_summary(test_results)
    
    print()
    print("=" * 80)
    print("🎯 FINAL ASSESSMENT")
    print("=" * 80)
    
    if all_systems_working:
        print("🎉 ALL QUALITY IMPROVEMENTS SUCCESSFUL!")
        print("The debate progression system now addresses all major issues identified in")
        print("conversation_20250913_184248.md and previous problematic conversations.")
        print()
        print("✅ READY FOR ENHANCED PRODUCTION USE")
        return True
    else:
        failed_count = sum(1 for result in test_results.values() if not result)
        print(f"⚠️  {failed_count} SYSTEMS NEED ADDITIONAL WORK")
        print("Review failed tests and implement additional fixes.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)