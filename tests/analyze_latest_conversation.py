#!/usr/bin/env python3
"""
Analysis of the latest conversation (conversation_20250913_184248.md) to identify new quality issues
"""

import sys
from pathlib import Path
import re
from typing import List, Dict, Tuple

# Add project root to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.evidence_validator import EvidenceValidator
from src.debate.progression_tracker import DebateProgressionTracker
from src.utils.agreement_detector import AgreementDetector

def analyze_conversation_quality():
    """Analyze the latest conversation for quality issues"""
    
    print("📊 CONVERSATION QUALITY ANALYSIS")
    print("Analyzing conversation_20250913_184248.md")
    print("=" * 60)
    
    # Read the conversation
    with open("/home/ubuntu/skynet/data/conversation/conversation_20250913_184248.md", "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract Barbie and Ken messages
    barbie_messages = re.findall(r'<Barbie>(.*?)</Barbie>', content, re.DOTALL)
    ken_messages = re.findall(r'<Ken>(.*?)</Ken>', content, re.DOTALL)
    
    print(f"Total messages analyzed:")
    print(f"  • Barbie: {len(barbie_messages)} messages")
    print(f"  • Ken: {len(ken_messages)} messages")
    print()
    
    # Initialize analysis systems
    evidence_validator = EvidenceValidator()
    tracker = DebateProgressionTracker()
    agreement_detector = AgreementDetector()
    
    issues_found = {
        "future_dated_citations": [],
        "topic_drift": [],
        "fabricated_sources": [],
        "coherence_issues": [],
        "repetitive_patterns": []
    }
    
    return analyze_specific_issues(barbie_messages, ken_messages, evidence_validator, tracker, issues_found)


def analyze_specific_issues(barbie_messages: List[str], ken_messages: List[str], 
                          evidence_validator: EvidenceValidator, tracker: DebateProgressionTracker,
                          issues_found: Dict) -> Dict:
    """Analyze specific quality issues in the conversation"""
    
    print("🔍 ISSUE 1: FUTURE-DATED CITATIONS")
    print("-" * 40)
    
    future_citations = []
    fabricated_sources = []
    
    for i, message in enumerate(barbie_messages):
        # Look for citations with dates 2024 or later
        citations = re.findall(r'([A-Za-z\s,]+(?:et\s+al\.)?)\s*\((\d{4})\)', message)
        for author, year in citations:
            if int(year) >= 2024:
                future_citations.append({
                    'author': author.strip(),
                    'year': year,
                    'message_index': i,
                    'context': message[max(0, message.find(f"({year})") - 50):message.find(f"({year})") + 60]
                })
        
        # Look for specific problematic sources mentioned
        if "Allen Institute (2025)" in message:
            fabricated_sources.append({
                'source': 'Allen Institute (2025)',
                'message_index': i,
                'issue': 'Future-dated, likely fabricated'
            })
        
        # Look for diabetes/obesity studies cited for consciousness topics
        diabetes_keywords = ['diabetes', 'glucose', 'obesity', 'pharmacotherapy']
        consciousness_keywords = ['consciousness', 'sentience', 'AI', 'quantum']
        
        has_diabetes = any(keyword in message.lower() for keyword in diabetes_keywords)
        has_consciousness = any(keyword in message.lower() for keyword in consciousness_keywords)
        
        if has_diabetes and has_consciousness:
            issues_found["coherence_issues"].append({
                'message_index': i,
                'issue': 'Diabetes/obesity studies cited for consciousness topics',
                'diabetes_terms': [k for k in diabetes_keywords if k in message.lower()],
                'consciousness_terms': [k for k in consciousness_keywords if k in message.lower()]
            })
    
    print(f"Future-dated citations found: {len(future_citations)}")
    for citation in future_citations[:5]:  # Show first 5
        print(f"  • {citation['author']} ({citation['year']})")
    
    print(f"Likely fabricated sources: {len(fabricated_sources)}")
    for source in fabricated_sources:
        print(f"  • {source['source']} - {source['issue']}")
    
    issues_found["future_dated_citations"] = future_citations
    issues_found["fabricated_sources"] = fabricated_sources
    
    print()
    print("🔍 ISSUE 2: TOPIC DRIFT ANALYSIS")
    print("-" * 40)
    
    # Analyze topic progression
    original_topic = "consciousness and AI sentience"
    topics_found = []
    
    for i, message in enumerate(barbie_messages + ken_messages):
        speaker = "Barbie" if i < len(barbie_messages) else "Ken"
        
        # Extract key topic indicators
        if "brain-computer interface" in message.lower() or "bci" in message.lower():
            topics_found.append({
                'message_index': i,
                'speaker': speaker,
                'topic': 'Brain-Computer Interfaces',
                'relevance_to_original': 'moderate'
            })
        
        if "hunger" in message.lower() or "appetite" in message.lower():
            topics_found.append({
                'message_index': i,
                'speaker': speaker,
                'topic': 'Hunger/Appetite Regulation',
                'relevance_to_original': 'low'
            })
        
        if "swarm intelligence" in message.lower():
            topics_found.append({
                'message_index': i,
                'speaker': speaker,
                'topic': 'Swarm Intelligence',
                'relevance_to_original': 'low'
            })
    
    print(f"Topic drift detected: {len(topics_found)} instances")
    current_topics = set(t['topic'] for t in topics_found)
    print(f"Topics discussed: {', '.join(current_topics)}")
    
    low_relevance = [t for t in topics_found if t['relevance_to_original'] == 'low']
    if low_relevance:
        print(f"Low relevance topics: {len(low_relevance)} instances")
        issues_found["topic_drift"] = low_relevance
    
    print()
    print("🔍 ISSUE 3: REPETITIVE QUESTIONING PATTERNS")
    print("-" * 40)
    
    # Analyze Ken's questioning patterns
    ken_questions = []
    for message in ken_messages:
        questions = [q.strip() for q in message.split('?') if q.strip() and len(q.strip()) > 20]
        ken_questions.extend(questions)
    
    # Group similar questions
    question_patterns = {}
    for question in ken_questions:
        # Extract question type
        if question.lower().startswith(('could you', 'can you')):
            pattern = 'could_you_provide'
        elif question.lower().startswith(('how do', 'how will')):
            pattern = 'how_questions'
        elif question.lower().startswith(('what evidence', 'what studies')):
            pattern = 'evidence_requests'
        else:
            pattern = 'other'
        
        if pattern in question_patterns:
            question_patterns[pattern] += 1
        else:
            question_patterns[pattern] = 1
    
    print(f"Total questions from Ken: {len(ken_questions)}")
    for pattern, count in question_patterns.items():
        print(f"  • {pattern}: {count} occurrences")
    
    repetitive_patterns = {p: c for p, c in question_patterns.items() if c >= 5}
    if repetitive_patterns:
        issues_found["repetitive_patterns"] = repetitive_patterns
    
    print()
    print("🔍 ISSUE 4: EVIDENCE-CLAIM COHERENCE")
    print("-" * 40)
    
    # Analyze coherence between claims and cited evidence
    coherence_issues = issues_found["coherence_issues"]
    
    print(f"Coherence issues found: {len(coherence_issues)}")
    for issue in coherence_issues:
        print(f"  • Message {issue['message_index']}: {issue['issue']}")
        print(f"    Health terms: {', '.join(issue['diabetes_terms'])}")
        print(f"    AI/consciousness terms: {', '.join(issue['consciousness_terms'])}")
    
    print()
    return issues_found


def generate_improvement_recommendations(issues_found: Dict) -> List[str]:
    """Generate specific recommendations based on issues found"""
    
    recommendations = []
    
    if issues_found["future_dated_citations"]:
        recommendations.append(
            "🔧 CITATION DATE VALIDATION: Add validation to flag citations from future dates (2024+) "
            "and require verification of source existence before acceptance."
        )
    
    if issues_found["fabricated_sources"]:
        recommendations.append(
            "🔧 SOURCE EXISTENCE VERIFICATION: Implement real-time source verification to check "
            "if cited studies actually exist in academic databases."
        )
    
    if issues_found["topic_drift"]:
        recommendations.append(
            "🔧 TOPIC COHERENCE MONITORING: Add system to detect when conversation drifts from "
            "original topic and gently guide back to core subject matter."
        )
    
    if issues_found["coherence_issues"]:
        recommendations.append(
            "🔧 EVIDENCE-CLAIM COHERENCE CHECKING: Enhance evidence validator to detect when "
            "studies from unrelated fields (e.g., diabetes) are cited for different topics (e.g., AI consciousness)."
        )
    
    if issues_found["repetitive_patterns"]:
        recommendations.append(
            "🔧 ENHANCED REPETITION DETECTION: The current system should catch repetitive "
            "questioning, but may need tuning for subtle pattern variations."
        )
    
    # General recommendations
    recommendations.extend([
        "🔧 DEBATE CONCLUSION DETECTION: Add system to detect when productive debate has reached "
        "natural conclusion and suggest summary or new direction.",
        
        "🔧 CITATION QUALITY SCORING: Implement comprehensive citation quality scoring that "
        "considers date validity, source credibility, and topic relevance together.",
        
        "🔧 PROGRESSIVE TOPIC NARROWING: Add mechanism to gradually narrow topic focus as "
        "debate progresses rather than allowing unlimited drift."
    ])
    
    return recommendations


def main():
    """Main analysis function"""
    
    issues_found = analyze_conversation_quality()
    
    print("=" * 60)
    print("🎯 IMPROVEMENT RECOMMENDATIONS")
    print("=" * 60)
    
    recommendations = generate_improvement_recommendations(issues_found)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec}")
        print()
    
    print("=" * 60)
    print("📈 PRIORITY FIXES NEEDED:")
    print("=" * 60)
    
    priority_issues = []
    
    if issues_found["future_dated_citations"]:
        priority_issues.append(f"HIGH: {len(issues_found['future_dated_citations'])} future-dated citations")
    
    if issues_found["fabricated_sources"]:
        priority_issues.append(f"HIGH: {len(issues_found['fabricated_sources'])} likely fabricated sources")
    
    if issues_found["coherence_issues"]:
        priority_issues.append(f"MEDIUM: {len(issues_found['coherence_issues'])} evidence-claim coherence issues")
    
    if issues_found["topic_drift"]:
        priority_issues.append(f"MEDIUM: {len(issues_found['topic_drift'])} topic drift instances")
    
    for issue in priority_issues:
        print(f"  • {issue}")
    
    if not priority_issues:
        print("  ✅ No major priority issues detected!")
    
    print()
    print("🚀 NEXT STEPS:")
    print("1. Implement citation date validation")
    print("2. Add real-time source existence checking")
    print("3. Enhance topic coherence monitoring")
    print("4. Improve evidence-claim relevance scoring")
    print("5. Add debate conclusion detection")
    
    return issues_found


if __name__ == "__main__":
    main()