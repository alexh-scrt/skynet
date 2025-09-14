"""
Source Verification and Credibility System
Ensures only reputable sources are used in debates
"""
from typing import List, Dict, Optional, Tuple
from enum import Enum
from urllib.parse import urlparse
import re
from datetime import datetime


class SourceTier(Enum):
    """Credibility tiers for sources"""
    TIER_1 = "tier_1"  # Highly reputable academic/official sources
    TIER_2 = "tier_2"  # Reputable mainstream sources
    TIER_3 = "tier_3"  # Generally reliable but requires verification
    TIER_4 = "tier_4"  # Opinion/blog sites, use with caution
    TIER_5 = "tier_5"  # Unreliable or known misinformation sources


class SourceVerifier:
    """Verifies and filters sources based on credibility"""
    
    def __init__(self):
        # Define reputable domains by tier
        self.source_tiers = {
            SourceTier.TIER_1: {
                # Academic journals and repositories
                "nature.com", "science.org", "sciencemag.org", "cell.com",
                "nejm.org", "thelancet.com", "bmj.com", "jamanetwork.com",
                "pnas.org", "journals.plos.org", "arxiv.org", "pubmed.ncbi.nlm.nih.gov",
                "scholar.google.com", "jstor.org", "sciencedirect.com",
                "ieeexplore.ieee.org", "acm.org", "springer.com",
                
                # Government and international organizations
                "who.int", "cdc.gov", "nih.gov", "fda.gov", "europa.eu",
                "un.org", "worldbank.org", "imf.org", "oecd.org",
                ".gov", ".edu",  # General government and education domains
                
                # Top universities
                "mit.edu", "stanford.edu", "harvard.edu", "oxford.ac.uk",
                "cambridge.org", "yale.edu", "princeton.edu", "caltech.edu"
            },
            
            SourceTier.TIER_2: {
                # Reputable news organizations
                "reuters.com", "apnews.com", "bbc.com", "bbc.co.uk",
                "npr.org", "pbs.org", "economist.com", "ft.com",
                "wsj.com", "nytimes.com", "washingtonpost.com",
                "theguardian.com", "bloomberg.com", "scientificamerican.com",
                "nationalgeographic.com", "smithsonianmag.com",
                
                # Reputable tech and science news
                "arstechnica.com", "technologyreview.com", "quantamagazine.org",
                "phys.org", "eurekalert.org", "sciencenews.org",
                
                # Professional organizations
                "ama-assn.org", "apa.org", "acm.org", "ieee.org"
            },
            
            SourceTier.TIER_3: {
                # Generally reliable but needs verification
                "wikipedia.org", "britannica.com", "howstuffworks.com",
                "mayoclinic.org", "webmd.com", "healthline.com",
                "investopedia.com", "techcrunch.com", "wired.com",
                "verge.com", "engadget.com", "vice.com", "vox.com",
                "theatlantic.com", "newyorker.com", "slate.com",
                "foreignaffairs.com", "cfr.org", "brookings.edu"
            },
            
            SourceTier.TIER_4: {
                # Opinion sites, blogs, requires careful evaluation
                "medium.com", "substack.com", "blogger.com", "wordpress.com",
                "tumblr.com", "quora.com", "reddit.com", "hackernews.com",
                "dev.to", "towards datascience.com", "analyticsvidhya.com"
            },
            
            SourceTier.TIER_5: {
                # Known unreliable or conspiracy sources
                "infowars.com", "naturalnews.com", "mercola.com",
                "globalresearch.ca", "zerohedge.com", "beforeitsnews.com",
                "rt.com", "sputniknews.com", "breitbart.com",
                # Add more known misinformation sources as needed
            }
        }
        
        # Preferred domains for specific topics
        self.topic_preferred_sources = {
            "ai": ["arxiv.org", "nature.com", "science.org", "mit.edu", "stanford.edu", 
                   "openai.com", "deepmind.com", "ai.google"],
            "medicine": ["nejm.org", "thelancet.com", "bmj.com", "jamanetwork.com", 
                        "pubmed.ncbi.nlm.nih.gov", "cdc.gov", "who.int"],
            "climate": ["ipcc.ch", "noaa.gov", "nasa.gov", "nature.com", 
                       "realclimate.org", "carbonbrief.org"],
            "economics": ["imf.org", "worldbank.org", "oecd.org", "federalreserve.gov",
                         "ecb.europa.eu", "bis.org", "nber.org"],
            "technology": ["ieee.org", "acm.org", "arxiv.org", "github.com",
                          "stackoverflow.com", "technologyreview.com"],
            "physics": ["arxiv.org", "aps.org", "iop.org", "nature.com", "science.org"],
            "psychology": ["apa.org", "psychologicalscience.org", "pubmed.ncbi.nlm.nih.gov"],
            "general": ["nature.com", "science.org", "reuters.com", "apnews.com", "bbc.com"]
        }
        
    def get_domain_tier(self, url: str) -> SourceTier:
        """Determine the credibility tier of a URL"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        
        # Check each tier
        for tier, domains in self.source_tiers.items():
            if domain in domains:
                return tier
            # Check for subdomain matches (e.g., "blog.nature.com")
            for trusted_domain in domains:
                if domain.endswith(f".{trusted_domain}") or domain == trusted_domain:
                    return tier
        
        # Special handling for .gov and .edu domains
        if domain.endswith(".gov") or domain.endswith(".edu"):
            return SourceTier.TIER_1
        
        # Default to TIER_4 for unknown sources
        return SourceTier.TIER_4
    
    def is_reputable(self, url: str, min_tier: SourceTier = SourceTier.TIER_3) -> bool:
        """Check if a source meets minimum credibility standards"""
        tier = self.get_domain_tier(url)
        # Compare enum values (TIER_1 < TIER_2 < TIER_3 etc.)
        tier_values = {
            SourceTier.TIER_1: 1,
            SourceTier.TIER_2: 2,
            SourceTier.TIER_3: 3,
            SourceTier.TIER_4: 4,
            SourceTier.TIER_5: 5
        }
        return tier_values[tier] <= tier_values[min_tier]
    
    def filter_search_results(self, results: List[Dict], 
                            min_tier: SourceTier = SourceTier.TIER_3,
                            require_date: bool = True) -> List[Dict]:
        """Filter search results based on credibility"""
        filtered = []
        
        for result in results:
            url = result.get("url", "")
            
            # Check credibility
            if not self.is_reputable(url, min_tier):
                continue
            
            # Check for publication date if required
            if require_date:
                date_str = result.get("published_date") or result.get("date")
                if date_str and not self._is_recent(date_str):
                    continue
            
            # Add tier information to result
            result["source_tier"] = self.get_domain_tier(url).value
            filtered.append(result)
        
        # Sort by tier (best sources first)
        filtered.sort(key=lambda x: x["source_tier"])
        
        return filtered
    
    def _is_recent(self, date_str: str, max_years: int = 5) -> bool:
        """Check if a date string indicates recent publication"""
        try:
            # Try to parse various date formats
            year_match = re.search(r"20\d{2}", date_str)
            if year_match:
                year = int(year_match.group())
                current_year = datetime.now().year
                return (current_year - year) <= max_years
        except:
            pass
        return True  # If we can't parse, assume it's okay
    
    def get_preferred_domains(self, topic: str) -> List[str]:
        """Get preferred domains for a specific topic"""
        topic_lower = topic.lower()
        
        # Check for exact match
        if topic_lower in self.topic_preferred_sources:
            return self.topic_preferred_sources[topic_lower]
        
        # Check for partial matches
        for key, domains in self.topic_preferred_sources.items():
            if key in topic_lower or topic_lower in key:
                return domains
        
        # Default to general sources
        return self.topic_preferred_sources["general"]
    
    def build_tavily_query(self, query: str, topic: str = None,
                          include_domains: List[str] = None,
                          exclude_tier_5: bool = True) -> Dict:
        """Build a Tavily search query with domain preferences"""
        
        # Get preferred domains for topic
        if topic and not include_domains:
            include_domains = self.get_preferred_domains(topic)
        
        # Build exclude list (always exclude tier 5 unless specified)
        exclude_domains = []
        if exclude_tier_5:
            exclude_domains = list(self.source_tiers[SourceTier.TIER_5])
        
        # Build the query parameters
        tavily_params = {
            "query": query,
            "search_depth": "advanced",  # Use advanced search for better results
            "max_results": 10,  # Get more results to filter from
        }
        
        # Add domain preferences if specified
        if include_domains:
            # Tavily uses include_domains parameter
            tavily_params["include_domains"] = include_domains[:5]  # Limit to 5 domains
        
        if exclude_domains:
            # Tavily uses exclude_domains parameter
            tavily_params["exclude_domains"] = exclude_domains[:5]  # Limit to 5 domains
        
        return tavily_params
    
    def evaluate_source_quality(self, result: Dict) -> Dict:
        """Evaluate the quality of a search result"""
        url = result.get("url", "")
        tier = self.get_domain_tier(url)
        
        quality_assessment = {
            "url": url,
            "tier": tier.value,
            "is_academic": tier == SourceTier.TIER_1,
            "is_reputable": tier in [SourceTier.TIER_1, SourceTier.TIER_2],
            "requires_verification": tier in [SourceTier.TIER_3, SourceTier.TIER_4],
            "credibility_score": self._calculate_credibility_score(result, tier)
        }
        
        # Add warnings if needed
        warnings = []
        if tier == SourceTier.TIER_4:
            warnings.append("Opinion/blog content - verify claims independently")
        if tier == SourceTier.TIER_5:
            warnings.append("Known unreliable source - do not use")
        
        if not result.get("published_date") and not result.get("date"):
            warnings.append("No publication date available")
        
        quality_assessment["warnings"] = warnings
        
        return quality_assessment
    
    def _calculate_credibility_score(self, result: Dict, tier: SourceTier) -> float:
        """Calculate a credibility score from 0-1"""
        # Base score from tier
        tier_scores = {
            SourceTier.TIER_1: 1.0,
            SourceTier.TIER_2: 0.8,
            SourceTier.TIER_3: 0.6,
            SourceTier.TIER_4: 0.4,
            SourceTier.TIER_5: 0.0
        }
        
        score = tier_scores[tier]
        
        # Bonus for having a date
        if result.get("published_date") or result.get("date"):
            score += 0.05
        
        # Bonus for having an author
        if result.get("author"):
            score += 0.05
        
        # Cap at 1.0
        return min(score, 1.0)
    
    def format_citation(self, result: Dict, tier: SourceTier) -> str:
        """Format a search result as a proper citation"""
        title = result.get("title", "Untitled")
        url = result.get("url", "")
        date = result.get("published_date") or result.get("date", "n.d.")
        author = result.get("author", "")
        domain = urlparse(url).netloc.replace("www.", "")
        
        # Different citation formats based on tier
        if tier == SourceTier.TIER_1:
            # Academic format
            if author:
                citation = f"{author} ({date}). {title}. {domain}. {url}"
            else:
                citation = f"{title} ({date}). {domain}. {url}"
        else:
            # Standard web format
            citation = f"{title}. {domain}, {date}. {url}"
        
        return citation


class FactChecker:
    """Fact-checking utilities for verifying claims"""
    
    def __init__(self, verifier: SourceVerifier):
        self.verifier = verifier
        
    def verify_claim(self, claim: str, evidence: List[Dict]) -> Dict:
        """Verify a claim against provided evidence"""
        
        # Assess evidence quality
        evidence_quality = []
        for item in evidence:
            quality = self.verifier.evaluate_source_quality(item)
            evidence_quality.append(quality)
        
        # Calculate overall support
        credibility_scores = [eq["credibility_score"] for eq in evidence_quality]
        avg_credibility = sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0
        
        # Determine verification status
        if avg_credibility >= 0.8 and len(evidence_quality) >= 2:
            status = "well_supported"
        elif avg_credibility >= 0.6 and len(evidence_quality) >= 1:
            status = "supported"
        elif avg_credibility >= 0.4:
            status = "weakly_supported"
        else:
            status = "unsupported"
        
        return {
            "claim": claim,
            "status": status,
            "evidence_count": len(evidence),
            "average_credibility": avg_credibility,
            "evidence_quality": evidence_quality,
            "requires_additional_verification": avg_credibility < 0.6
        }
    
    def check_date_relevance(self, claim: str, date_str: str) -> bool:
        """Check if evidence date is relevant for the claim"""
        # For claims about current events, require recent sources
        current_terms = ["now", "today", "current", "recent", "latest", "2024", "2025"]
        if any(term in claim.lower() for term in current_terms):
            return self.verifier._is_recent(date_str, max_years=2)
        
        # For historical claims, older sources are fine
        return True