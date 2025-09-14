"""
Test verified conversation system
"""
import sys
from pathlib import Path

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.conversation.verified_conversation import VerifiedConversationManager, SmartFactChecker
from src.utils.source_verification import SourceTier


def test_verified_conversation():
    """Test the verified conversation system"""
    
    print("=== Verified Conversation System Demo ===\n")
    
    manager = VerifiedConversationManager()
    manager.memory.start_topic("verified_debate", "AI and Healthcare")
    
    # Barbie makes a claim with sources
    print("1. Barbie makes a claim with evidence:")
    print("-" * 50)
    
    barbie_sources = [
        {
            "title": "AI Improves Radiology Accuracy by 23%",
            "url": "https://www.nejm.org/ai-radiology-2024",
            "published_date": "2024-02-15",
            "author": "Chen, L. et al."
        },
        {
            "title": "Machine Learning in Medical Diagnosis",
            "url": "https://www.nature.com/articles/ai-diagnosis",
            "published_date": "2024-01-10",
            "author": "Rodriguez, M."
        },
        {
            "title": "My Thoughts on AI in Medicine",
            "url": "https://medium.com/@blogger/ai-medicine",
            "published_date": "2024-03-01"
        }
    ]
    
    barbie_claim = "AI can improve medical diagnosis accuracy by over 20%"
    
    verification = manager.verify_agent_claim(
        "Barbie",
        barbie_claim,
        barbie_sources,
        topic="medicine"
    )
    
    print(f"Claim: {barbie_claim}")
    print(f"Verification Status: {verification['verification_status']}")
    print(f"Credibility Score: {verification['credibility_score']:.2f}")
    print(f"Verified Sources: {verification['verified_sources']}")
    print(f"Filtered Out: {verification['filtered_out']} (low credibility)")
    print(f"Needs Better Evidence: {verification['requires_better_evidence']}")
    
    print("\nAccepted Sources:")
    for i, source in enumerate(verification['supporting_sources'], 1):
        quality = source['quality']
        print(f"  {i}. [{quality['tier']}] {source['title']}")
        print(f"     Credibility: {quality['credibility_score']:.2f}")
        if quality['warnings']:
            print(f"     ⚠️  {', '.join(quality['warnings'])}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Ken challenges with counter-evidence
    print("2. Ken challenges with counter-evidence:")
    print("-" * 50)
    
    ken_counter_sources = [
        {
            "title": "Limitations of AI in Clinical Practice",
            "url": "https://www.bmj.com/ai-limitations-2024",
            "published_date": "2024-03-05",
            "author": "Williams, J. et al."
        },
        {
            "title": "AI Diagnostic Errors in Emergency Medicine",
            "url": "https://www.thelancet.com/ai-errors",
            "published_date": "2024-02-20"
        }
    ]
    
    challenge = "While AI shows promise, real-world implementation faces significant accuracy challenges in clinical settings"
    
    challenge_result = manager.challenge_claim_evidence(
        "Ken",
        verification['claim_id'],
        challenge,
        ken_counter_sources
    )
    
    print(f"Challenge: {challenge}")
    print(f"Counter-evidence provided: {challenge_result['has_counter_evidence']}")
    print(f"Counter credibility: {challenge_result.get('counter_credibility', 0):.2f}")
    
    if 'evidence_comparison' in challenge_result:
        comparison = challenge_result['evidence_comparison']
        print(f"Original evidence strength: {comparison['original_credibility']:.2f}")
        print(f"Counter evidence strength: {comparison['counter_credibility']:.2f}")
        print(f"Counter evidence stronger: {comparison['counter_stronger']}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Add another claim with weaker evidence
    print("3. Testing weak evidence detection:")
    print("-" * 50)
    
    weak_sources = [
        {
            "title": "AI Will Save Healthcare (Opinion)",
            "url": "https://medium.com/@healthblogger/ai-saves-all",
            "published_date": "2024-03-01"
        },
        {
            "title": "Revolutionary AI Breakthrough",
            "url": "https://www.healthnews-blog.com/ai-revolution",
            "date": "2024-02-28"
        }
    ]
    
    weak_claim = "AI will completely replace doctors within 5 years"
    
    weak_verification = manager.verify_agent_claim(
        "Barbie",
        weak_claim,
        weak_sources
    )
    
    print(f"Weak Claim: {weak_claim}")
    print(f"Verification Status: {weak_verification['verification_status']}")
    print(f"Credibility Score: {weak_verification['credibility_score']:.2f}")
    print(f"Requires Better Evidence: {weak_verification['requires_better_evidence']}")
    print(f"Verified Sources: {weak_verification['verified_sources']} (many filtered out)")
    
    print("\n" + "=" * 60 + "\n")
    
    # Evaluate overall debate quality
    print("4. Overall Debate Quality Assessment:")
    print("-" * 50)
    
    quality_assessment = manager.evaluate_debate_quality()
    
    print(f"Overall Quality Score: {quality_assessment['overall_quality_score']:.2f}")
    print(f"Quality Level: {quality_assessment['quality_assessment']}")
    print(f"Average Source Credibility: {quality_assessment['average_source_credibility']:.2f}")
    print(f"Evidence Verification Rate: {quality_assessment['evidence_verification_rate']:.1%}")
    print(f"Claims with Verified Sources: {quality_assessment['claims_with_verified_sources']}/{quality_assessment['total_claims']}")
    
    print("\nImprovement Suggestions:")
    for suggestion in quality_assessment['improvement_suggestions']:
        print(f"  • {suggestion}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Test fact-check query generation
    print("5. Smart Fact-Check Query Generation:")
    print("-" * 50)
    
    test_claims = [
        "AI increases diagnostic accuracy by 25%",
        "Climate change causes sea level rise",
        "COVID-19 vaccines are 95% effective",
        "Electric cars have lower emissions than gas cars"
    ]
    
    for claim in test_claims:
        query = manager.suggest_fact_check_query(claim, "technology")
        print(f"Claim: {claim}")
        print(f"Suggested Query: {query}")
        print()
    
    print("\n" + "=" * 60 + "\n")
    
    # Test source requirements by claim type
    print("6. Source Requirements by Claim Type:")
    print("-" * 50)
    
    claim_types = ["medical", "statistical", "technological", "economic", "social"]
    
    for claim_type in claim_types:
        requirements = manager.generate_source_requirements(claim_type)
        print(f"{claim_type.title()} Claims:")
        print(f"  Min Tier: {requirements.get('min_tier', 'N/A')}")
        print(f"  Min Sources: {requirements.get('min_sources', 1)}")
        print(f"  Preferred Types: {', '.join(requirements.get('preferred_types', ['Any']))}")
        print()


def test_smart_fact_checker():
    """Test the smart fact checker"""
    
    print("\n\n=== Smart Fact Checker Demo ===\n")
    
    fact_checker = SmartFactChecker()
    
    # Test quick verification
    print("Quick Fact Verification:")
    print("-" * 50)
    
    test_claims = [
        "AI market is growing rapidly",
        "Global temperature has increased since 1850",
        "Solar panels are becoming more efficient",
        "Bitcoin price is volatile"
    ]
    
    for claim in test_claims:
        result = fact_checker.quick_verify(claim)
        print(f"Claim: {claim}")
        if result:
            print(f"  Status: {result['status']}")
            print(f"  Sources: {', '.join(result['sources'][:2])}")
        else:
            print("  Status: Not in known facts database - requires search")
        print()
    
    print("\n" + "=" * 60 + "\n")
    
    # Test verification approach suggestions
    print("Verification Approach Suggestions:")
    print("-" * 50)
    
    approach_test_claims = [
        "A study shows that meditation reduces stress",
        "GDP growth increased by 3.2% last quarter",
        "Tesla's market cap exceeded $800 billion",
        "Social media usage affects mental health"
    ]
    
    for claim in approach_test_claims:
        approach = fact_checker.suggest_verification_approach(claim)
        print(f"Claim: {claim}")
        print(f"  Approach: {approach['approach']}")
        print(f"  Keywords: {', '.join(approach['keywords'])}")
        print(f"  Preferred Sources: {', '.join(approach['preferred_sources'][:2])}")
        print(f"  Min Tier: {approach['min_tier'].value}")
        print()


def demonstrate_integration_benefits():
    """Demonstrate the benefits of the integrated system"""
    
    print("\n\n=== Integration Benefits Demo ===\n")
    
    print("Benefits of Verified Conversation System:")
    print("-" * 60)
    print("""
    1. AUTOMATIC SOURCE FILTERING
       ✓ Filters out unreliable sources automatically
       ✓ Prioritizes peer-reviewed studies and reputable news
       ✓ Warns about opinion pieces and blogs
    
    2. CREDIBILITY SCORING
       ✓ Each source gets a credibility score 0-1
       ✓ Claims are rated based on evidence quality
       ✓ Agents know which claims need better support
    
    3. DOMAIN-SPECIFIC PREFERENCES
       ✓ Medical claims prefer medical journals
       ✓ Climate claims prefer scientific institutions
       ✓ Tech claims prefer technical publications
    
    4. FACT-CHECK INTEGRATION
       ✓ Claims are automatically fact-checked
       ✓ Counter-evidence is evaluated for strength
       ✓ Debates can be resolved based on evidence quality
    
    5. CONVERSATION QUALITY METRICS
       ✓ Overall debate quality is measured
       ✓ Improvement suggestions are provided
       ✓ Source verification rates are tracked
    
    6. CITATION FORMATTING
       ✓ Proper academic citations are generated
       ✓ Different formats for different source types
       ✓ Makes debates more scholarly and credible
    
    7. MEMORY INTEGRATION
       ✓ Verified claims are stored in conversation memory
       ✓ No repetition of verification process
       ✓ Builds on established facts
    """)
    
    print("\nBefore vs After:")
    print("-" * 60)
    print("""
    BEFORE (Without Verification):
    - Agents cite random blogs and opinion pieces
    - No way to verify claim accuracy
    - Debates based on unreliable information
    - No progression toward truth
    
    AFTER (With Verification):
    - Only reputable sources are accepted
    - Claims are fact-checked against evidence
    - Debates grounded in reliable information
    - Progress toward evidence-based conclusions
    """)


if __name__ == "__main__":
    test_verified_conversation()
    test_smart_fact_checker()
    demonstrate_integration_benefits()
    
    print("\n" + "=" * 60)
    print("Verified Conversation System Test Complete!")
    print("Ready to integrate with Barbie and Ken for fact-based debates!")
    print("=" * 60)