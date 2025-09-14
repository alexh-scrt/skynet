"""
Test source verification and enhanced Tavily integration
"""
import sys
from pathlib import Path

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.source_verification import SourceVerifier, SourceTier, FactChecker
# Note: enhanced_tavily requires tavily package - testing core functionality only
import asyncio


def test_source_verification():
    """Test the source verification system"""
    
    print("=== Source Verification System Test ===\n")
    
    verifier = SourceVerifier()
    
    # Test URLs with different credibility levels
    test_urls = [
        ("https://www.nature.com/articles/ai-research", "Nature - Top tier academic"),
        ("https://arxiv.org/abs/2024.01234", "arXiv - Academic preprint"),
        ("https://www.reuters.com/technology/ai-news", "Reuters - Reputable news"),
        ("https://www.bbc.com/news/science", "BBC - Reputable news"),
        ("https://en.wikipedia.org/wiki/Artificial_intelligence", "Wikipedia - Needs verification"),
        ("https://medium.com/@user/ai-thoughts", "Medium - Blog/opinion"),
        ("https://www.infowars.com/conspiracy", "InfoWars - Unreliable"),
        ("https://www.nih.gov/research/ai-health", "NIH - Government source"),
        ("https://stanford.edu/research/ai", "Stanford - University source")
    ]
    
    print("URL Credibility Assessment:")
    print("-" * 60)
    
    for url, description in test_urls:
        tier = verifier.get_domain_tier(url)
        is_reputable = verifier.is_reputable(url, SourceTier.TIER_3)
        print(f"{description:40} | Tier: {tier.value:8} | Reputable: {is_reputable}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Test topic-based domain preferences
    print("Preferred Domains by Topic:")
    print("-" * 60)
    
    topics = ["ai", "medicine", "climate", "economics", "quantum physics"]
    
    for topic in topics:
        preferred = verifier.get_preferred_domains(topic)
        print(f"{topic:15} | {', '.join(preferred[:3])}...")
    
    print("\n" + "=" * 60 + "\n")
    
    # Test search result filtering
    print("Search Result Filtering Demo:")
    print("-" * 60)
    
    # Simulate search results
    mock_results = [
        {
            "title": "AI Breakthrough in Cancer Detection",
            "url": "https://www.nature.com/articles/ai-cancer",
            "published_date": "2024-01-15",
            "content": "New AI system achieves 95% accuracy..."
        },
        {
            "title": "Opinion: Why AI Will Save Us All",
            "url": "https://medium.com/@blogger/ai-salvation",
            "published_date": "2024-02-01",
            "content": "I believe AI is the answer to everything..."
        },
        {
            "title": "SHOCKING: AI Mind Control Revealed",
            "url": "https://www.infowars.com/ai-conspiracy",
            "published_date": "2024-01-01",
            "content": "The government is using AI to..."
        },
        {
            "title": "Reuters: AI Regulation Update",
            "url": "https://www.reuters.com/technology/ai-regulation",
            "published_date": "2024-03-01",
            "content": "European Union announces new AI regulations..."
        },
        {
            "title": "Wikipedia: Artificial General Intelligence",
            "url": "https://en.wikipedia.org/wiki/AGI",
            "date": "2024-03-10",
            "content": "AGI refers to machine intelligence that..."
        }
    ]
    
    # Filter with different tier requirements
    for min_tier in [SourceTier.TIER_1, SourceTier.TIER_2, SourceTier.TIER_3]:
        filtered = verifier.filter_search_results(mock_results, min_tier=min_tier)
        print(f"\nMin Tier: {min_tier.value} - {len(filtered)} results pass filter")
        for result in filtered:
            print(f"  ✓ {result['title'][:50]}... [{result['source_tier']}]")
    
    print("\n" + "=" * 60 + "\n")
    
    # Test fact checking
    print("Fact Checking Demo:")
    print("-" * 60)
    
    fact_checker = FactChecker(verifier)
    
    # Test claim with varying evidence quality
    claim = "AI can improve medical diagnosis accuracy by 20%"
    
    evidence_sets = [
        {
            "name": "Strong Evidence",
            "evidence": [
                {"url": "https://www.nature.com/study1", "title": "AI in Medicine", 
                 "published_date": "2024-01"},
                {"url": "https://www.nejm.org/study2", "title": "Clinical AI Trial",
                 "published_date": "2024-02"}
            ]
        },
        {
            "name": "Weak Evidence",
            "evidence": [
                {"url": "https://medium.com/blog1", "title": "My thoughts on AI",
                 "published_date": "2024-01"},
                {"url": "https://www.reddit.com/post", "title": "AI is amazing!",
                 "date": "2024-03"}
            ]
        },
        {
            "name": "Mixed Evidence",
            "evidence": [
                {"url": "https://www.nature.com/study", "title": "Peer-reviewed study",
                 "published_date": "2024-01"},
                {"url": "https://www.wikipedia.org/ai", "title": "Wikipedia article",
                 "date": "2024-02"},
                {"url": "https://medium.com/opinion", "title": "Opinion piece",
                 "published_date": "2024-03"}
            ]
        }
    ]
    
    for evidence_set in evidence_sets:
        verification = fact_checker.verify_claim(claim, evidence_set["evidence"])
        print(f"\n{evidence_set['name']}:")
        print(f"  Status: {verification['status']}")
        print(f"  Average Credibility: {verification['average_credibility']:.2f}")
        print(f"  Requires Additional Verification: {verification['requires_additional_verification']}")
    
    print("\n" + "=" * 60 + "\n")
    
    # Test citation formatting
    print("Citation Formatting:")
    print("-" * 60)
    
    test_results = [
        {
            "title": "Artificial Intelligence in Healthcare",
            "url": "https://www.nature.com/articles/s41591-024-1234",
            "published_date": "2024-03-15",
            "author": "Smith, J. et al."
        },
        {
            "title": "AI News Update",
            "url": "https://www.reuters.com/technology/ai-2024",
            "date": "March 15, 2024"
        }
    ]
    
    for result in test_results:
        tier = verifier.get_domain_tier(result["url"])
        citation = verifier.format_citation(result, tier)
        print(f"\n[{tier.value}] Citation:")
        print(f"  {citation}")


def test_tavily_query_building():
    """Test building Tavily queries with domain preferences"""
    
    print("\n\n=== Tavily Query Building Test ===\n")
    
    verifier = SourceVerifier()
    
    test_queries = [
        {
            "query": "latest AI breakthrough in cancer detection",
            "topic": "medicine",
            "description": "Medical AI research"
        },
        {
            "query": "climate change impact 2024",
            "topic": "climate",
            "description": "Climate science"
        },
        {
            "query": "quantum computing advances",
            "topic": "physics",
            "description": "Physics research"
        }
    ]
    
    for test in test_queries:
        print(f"\n{test['description']}:")
        print(f"Query: '{test['query']}'")
        
        params = verifier.build_tavily_query(
            test["query"],
            topic=test["topic"],
            exclude_tier_5=True
        )
        
        print(f"Tavily Parameters:")
        print(f"  - Search depth: {params.get('search_depth', 'basic')}")
        print(f"  - Max results: {params.get('max_results', 5)}")
        if "include_domains" in params:
            print(f"  - Preferred domains: {', '.join(params['include_domains'][:3])}...")
        if "exclude_domains" in params:
            print(f"  - Excluded: {len(params['exclude_domains'])} unreliable domains")


def demonstrate_enhanced_search():
    """Demonstrate the enhanced search capabilities"""
    
    print("\n\n=== Enhanced Search Capabilities Demo ===\n")
    
    # Note: This would require an actual Tavily API key
    # For demo purposes, we'll show the structure
    
    print("Enhanced Search Features:")
    print("-" * 60)
    print("1. Automatic source filtering by credibility tier")
    print("2. Topic-based domain preferences")
    print("3. Fact-checking mode with evidence verification")
    print("4. Diverse perspective gathering")
    print("5. Proper academic citations")
    print("6. Quality assessment for each result")
    print("7. Automatic exclusion of known misinformation sources")
    
    print("\n" + "=" * 60 + "\n")
    
    print("Example Search Flow:")
    print("-" * 60)
    print("""
    1. Agent makes claim: "AI can diagnose cancer better than doctors"
    
    2. Enhanced Tavily search:
       - Query: "AI cancer diagnosis accuracy compared to doctors"
       - Topic: "medicine"
       - Preferred domains: nejm.org, lancet.com, pubmed.ncbi.nlm.nih.gov
       - Excluded: All Tier 5 (unreliable) sources
       - Min tier: TIER_2 (reputable sources only)
    
    3. Results filtered and verified:
       - Only peer-reviewed studies and reputable news
       - Each result gets credibility score
       - Proper citations generated
    
    4. Fact-check verdict:
       - Status: "supported" (if high-quality evidence found)
       - Average credibility: 0.85
       - Evidence: 3 peer-reviewed studies from Nature, NEJM
    
    5. Agent uses verified information:
       - Cites specific studies with proper attribution
       - Acknowledges confidence level based on source quality
       - Avoids spreading misinformation
    """)


if __name__ == "__main__":
    test_source_verification()
    test_tavily_query_building()
    demonstrate_enhanced_search()
    
    print("\n" + "=" * 60)
    print("Source Verification System Test Complete!")
    print("=" * 60)