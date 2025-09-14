"""
Enhanced Tavily Integration with Source Verification
"""
from typing import List, Dict, Optional, Tuple
import asyncio
from tavily import TavilyClient, AsyncTavilyClient
from src.utils.source_verification import SourceVerifier, SourceTier, FactChecker
import json


class EnhancedTavilySearch:
    """Enhanced Tavily search with source verification and filtering"""
    
    def __init__(self, api_key: str):
        self.client = TavilyClient(api_key=api_key)
        self.async_client = AsyncTavilyClient(api_key=api_key)
        self.verifier = SourceVerifier()
        self.fact_checker = FactChecker(self.verifier)
        
    def search_with_verification(self, 
                                query: str,
                                topic: str = None,
                                min_tier: SourceTier = SourceTier.TIER_3,
                                max_results: int = 5,
                                require_date: bool = True) -> Dict:
        """
        Perform a Tavily search with source verification
        
        Args:
            query: Search query
            topic: Topic area for domain preferences (ai, medicine, climate, etc.)
            min_tier: Minimum acceptable source tier
            max_results: Maximum number of results to return
            require_date: Whether to require publication dates
            
        Returns:
            Dictionary with verified results and metadata
        """
        
        # Build query with domain preferences
        preferred_domains = self.verifier.get_preferred_domains(topic) if topic else []
        
        # Perform search with Tavily
        try:
            # Include preferred domains in the search
            search_params = {
                "query": query,
                "search_depth": "advanced",
                "max_results": max_results * 2,  # Get extra to account for filtering
            }
            
            # Add domain preferences if available
            if preferred_domains:
                search_params["include_domains"] = preferred_domains[:5]
            
            # Exclude known unreliable sources
            exclude_domains = list(self.verifier.source_tiers[SourceTier.TIER_5])
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains[:5]
            
            # Perform the search
            raw_results = self.client.search(**search_params)
            
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "metadata": {}
            }
        
        # Extract results
        results = raw_results.get("results", [])
        
        # Filter and verify results
        verified_results = self.verifier.filter_search_results(
            results, 
            min_tier=min_tier,
            require_date=require_date
        )
        
        # Limit to requested number
        verified_results = verified_results[:max_results]
        
        # Add quality assessment to each result
        for result in verified_results:
            result["quality_assessment"] = self.verifier.evaluate_source_quality(result)
            result["citation"] = self.verifier.format_citation(
                result, 
                self.verifier.get_domain_tier(result["url"])
            )
        
        # Calculate metadata
        metadata = {
            "query": query,
            "topic": topic,
            "total_results_found": len(results),
            "results_after_filtering": len(verified_results),
            "min_tier_used": min_tier.value,
            "tier_distribution": self._calculate_tier_distribution(verified_results),
            "average_credibility": self._calculate_avg_credibility(verified_results),
            "preferred_domains_used": preferred_domains[:5] if preferred_domains else []
        }
        
        return {
            "results": verified_results,
            "metadata": metadata,
            "error": None
        }
    
    async def async_search_with_verification(self,
                                            query: str,
                                            topic: str = None,
                                            min_tier: SourceTier = SourceTier.TIER_3,
                                            max_results: int = 5) -> Dict:
        """Async version of search_with_verification"""
        
        preferred_domains = self.verifier.get_preferred_domains(topic) if topic else []
        
        try:
            search_params = {
                "query": query,
                "search_depth": "advanced",
                "max_results": max_results * 2,
            }
            
            if preferred_domains:
                search_params["include_domains"] = preferred_domains[:5]
            
            exclude_domains = list(self.verifier.source_tiers[SourceTier.TIER_5])
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains[:5]
            
            raw_results = await self.async_client.search(**search_params)
            
        except Exception as e:
            return {
                "error": f"Search failed: {str(e)}",
                "results": [],
                "metadata": {}
            }
        
        results = raw_results.get("results", [])
        verified_results = self.verifier.filter_search_results(results, min_tier=min_tier)
        verified_results = verified_results[:max_results]
        
        for result in verified_results:
            result["quality_assessment"] = self.verifier.evaluate_source_quality(result)
            result["citation"] = self.verifier.format_citation(
                result,
                self.verifier.get_domain_tier(result["url"])
            )
        
        metadata = {
            "query": query,
            "topic": topic,
            "total_results_found": len(results),
            "results_after_filtering": len(verified_results),
            "average_credibility": self._calculate_avg_credibility(verified_results)
        }
        
        return {
            "results": verified_results,
            "metadata": metadata,
            "error": None
        }
    
    def search_for_fact_check(self, claim: str, topic: str = None) -> Dict:
        """
        Search specifically for fact-checking a claim
        
        Args:
            claim: The claim to verify
            topic: Topic area for better source selection
            
        Returns:
            Fact-check results with verification status
        """
        
        # Modify query for fact-checking
        fact_check_query = f"evidence for: {claim}"
        
        # Search with high standards for fact-checking
        search_results = self.search_with_verification(
            query=fact_check_query,
            topic=topic,
            min_tier=SourceTier.TIER_2,  # Higher standards for fact-checking
            max_results=5,
            require_date=True
        )
        
        if search_results["error"]:
            return {
                "claim": claim,
                "verification_status": "error",
                "error": search_results["error"]
            }
        
        # Verify the claim against evidence
        verification = self.fact_checker.verify_claim(
            claim,
            search_results["results"]
        )
        
        # Add supporting evidence
        verification["supporting_evidence"] = [
            {
                "title": r["title"],
                "url": r["url"],
                "citation": r["citation"],
                "credibility": r["quality_assessment"]["credibility_score"]
            }
            for r in search_results["results"]
        ]
        
        return verification
    
    def get_diverse_perspectives(self, topic: str, max_sources: int = 3) -> Dict:
        """
        Get diverse perspectives on a topic from different tier sources
        
        Args:
            topic: Topic to research
            max_sources: Max sources per tier
            
        Returns:
            Perspectives from different source tiers
        """
        
        perspectives = {}
        
        # Get academic perspective (Tier 1)
        academic_results = self.search_with_verification(
            query=f"{topic} research academic study",
            topic=topic,
            min_tier=SourceTier.TIER_1,
            max_results=max_sources
        )
        perspectives["academic"] = academic_results["results"]
        
        # Get mainstream perspective (Tier 2)
        mainstream_results = self.search_with_verification(
            query=f"{topic} news analysis",
            topic=topic,
            min_tier=SourceTier.TIER_2,
            max_results=max_sources
        )
        perspectives["mainstream"] = mainstream_results["results"]
        
        # Get general perspective (Tier 3)
        general_results = self.search_with_verification(
            query=f"{topic} explained overview",
            topic=topic,
            min_tier=SourceTier.TIER_3,
            max_results=max_sources
        )
        perspectives["general"] = general_results["results"]
        
        return {
            "topic": topic,
            "perspectives": perspectives,
            "source_diversity": len(perspectives["academic"]) + 
                              len(perspectives["mainstream"]) + 
                              len(perspectives["general"])
        }
    
    def _calculate_tier_distribution(self, results: List[Dict]) -> Dict[str, int]:
        """Calculate distribution of results across tiers"""
        distribution = {}
        for result in results:
            tier = result.get("source_tier", "unknown")
            distribution[tier] = distribution.get(tier, 0) + 1
        return distribution
    
    def _calculate_avg_credibility(self, results: List[Dict]) -> float:
        """Calculate average credibility score"""
        if not results:
            return 0.0
        
        scores = []
        for result in results:
            if "quality_assessment" in result:
                scores.append(result["quality_assessment"]["credibility_score"])
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def format_search_summary(self, search_results: Dict) -> str:
        """Format search results as a summary for agents"""
        
        if search_results.get("error"):
            return f"Search error: {search_results['error']}"
        
        results = search_results["results"]
        metadata = search_results["metadata"]
        
        summary = f"Search: '{metadata['query']}'\n"
        summary += f"Found {len(results)} verified sources "
        summary += f"(filtered from {metadata['total_results_found']} total)\n"
        summary += f"Average credibility: {metadata['average_credibility']:.2f}\n\n"
        
        for i, result in enumerate(results, 1):
            quality = result["quality_assessment"]
            summary += f"{i}. [{quality['tier']}] {result['title']}\n"
            summary += f"   {result['citation']}\n"
            if quality["warnings"]:
                summary += f"   ⚠️  {', '.join(quality['warnings'])}\n"
            summary += f"   Credibility: {quality['credibility_score']:.2f}\n\n"
        
        return summary


class SearchCache:
    """Cache search results to avoid redundant API calls"""
    
    def __init__(self, max_size: int = 100):
        self.cache = {}
        self.max_size = max_size
        
    def get_cache_key(self, query: str, topic: str, min_tier: str) -> str:
        """Generate cache key"""
        return f"{query}|{topic}|{min_tier}"
    
    def get(self, query: str, topic: str, min_tier: str) -> Optional[Dict]:
        """Get cached result if exists"""
        key = self.get_cache_key(query, topic, min_tier)
        return self.cache.get(key)
    
    def set(self, query: str, topic: str, min_tier: str, results: Dict):
        """Cache search results"""
        if len(self.cache) >= self.max_size:
            # Remove oldest entry (simple FIFO)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        key = self.get_cache_key(query, topic, min_tier)
        self.cache[key] = results