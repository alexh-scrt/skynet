"""
Verified Conversation Module
Integrates source verification with conversation memory for fact-based debates
"""
from typing import Dict, List, Optional
from src.memory.conversation_memory import ConversationMemory
from src.utils.source_verification import SourceVerifier, SourceTier, FactChecker
import json


class VerifiedConversationManager:
    """Manages conversations with automatic source verification"""
    
    def __init__(self):
        self.memory = ConversationMemory()
        self.verifier = SourceVerifier()
        self.fact_checker = FactChecker(self.verifier)
        self.verified_sources = {}  # Cache of verified sources
        
    def verify_agent_claim(self, speaker: str, claim: str, 
                          sources: List[Dict], topic: str = None) -> Dict:
        """
        Verify an agent's claim against provided sources
        
        Args:
            speaker: Agent making the claim
            claim: The claim being made
            sources: List of source dictionaries with url, title, etc.
            topic: Topic area for context
            
        Returns:
            Verification result with credibility assessment
        """
        
        # Filter sources by credibility
        verified_sources = []
        for source in sources:
            url = source.get("url", "")
            if self.verifier.is_reputable(url, SourceTier.TIER_3):
                # Add quality assessment
                source["quality"] = self.verifier.evaluate_source_quality(source)
                source["citation"] = self.verifier.format_citation(
                    source, 
                    self.verifier.get_domain_tier(url)
                )
                verified_sources.append(source)
        
        # Perform fact check
        verification = self.fact_checker.verify_claim(claim, verified_sources)
        
        # Add to conversation memory
        evidence_list = [s.get("citation", s.get("title", "")) for s in verified_sources]
        memory_claim = self.memory.add_claim(speaker, claim, evidence_list)
        
        # Cache verified sources
        claim_id = memory_claim.id
        self.verified_sources[claim_id] = {
            "sources": verified_sources,
            "verification": verification
        }
        
        return {
            "claim_id": claim_id,
            "verification_status": verification["status"],
            "credibility_score": verification["average_credibility"],
            "verified_sources": len(verified_sources),
            "filtered_out": len(sources) - len(verified_sources),
            "requires_better_evidence": verification["requires_additional_verification"],
            "supporting_sources": verified_sources
        }
    
    def challenge_claim_evidence(self, challenger: str, claim_id: str, 
                                challenge: str, counter_sources: List[Dict] = None) -> Dict:
        """
        Challenge a claim with counter-evidence
        
        Args:
            challenger: Agent making the challenge
            claim_id: ID of claim being challenged
            challenge: The challenge text
            counter_sources: Optional counter-evidence
            
        Returns:
            Challenge assessment
        """
        
        # Add counter-argument to memory
        self.memory.add_counter_argument(claim_id, challenge)
        
        result = {
            "challenge_accepted": True,
            "claim_id": claim_id,
            "challenger": challenger,
            "has_counter_evidence": bool(counter_sources)
        }
        
        if counter_sources:
            # Verify counter-evidence
            verified_counter = []
            for source in counter_sources:
                url = source.get("url", "")
                if self.verifier.is_reputable(url, SourceTier.TIER_3):
                    source["quality"] = self.verifier.evaluate_source_quality(source)
                    verified_counter.append(source)
            
            result["counter_evidence"] = verified_counter
            result["counter_credibility"] = sum(
                s["quality"]["credibility_score"] for s in verified_counter
            ) / len(verified_counter) if verified_counter else 0
            
            # Compare evidence strength
            original_verification = self.verified_sources.get(claim_id, {})
            original_credibility = original_verification.get("verification", {}).get("average_credibility", 0)
            
            result["evidence_comparison"] = {
                "original_credibility": original_credibility,
                "counter_credibility": result["counter_credibility"],
                "counter_stronger": result["counter_credibility"] > original_credibility
            }
        
        return result
    
    def suggest_fact_check_query(self, claim: str, topic: str = None) -> str:
        """Generate a good fact-checking query for a claim"""
        
        # Extract key terms from claim
        key_terms = []
        
        # Look for numbers/statistics
        import re
        numbers = re.findall(r'\d+(?:\.\d+)?%?', claim)
        key_terms.extend(numbers)
        
        # Look for specific claims
        if "better than" in claim.lower() or "worse than" in claim.lower():
            key_terms.append("comparison study")
        
        if "increase" in claim.lower() or "decrease" in claim.lower():
            key_terms.append("longitudinal study")
        
        if "cause" in claim.lower():
            key_terms.append("causal relationship")
        
        # Build query
        base_query = f"evidence research study: {claim}"
        
        if key_terms:
            base_query += f" {' '.join(key_terms[:3])}"
        
        if topic:
            base_query += f" {topic}"
        
        return base_query
    
    def generate_source_requirements(self, claim_type: str) -> Dict:
        """Generate source requirements based on claim type"""
        
        requirements = {
            "statistical": {
                "min_tier": SourceTier.TIER_2,
                "preferred_types": ["peer-reviewed study", "government statistics"],
                "min_sources": 2,
                "require_methodology": True
            },
            "medical": {
                "min_tier": SourceTier.TIER_1,
                "preferred_types": ["clinical trial", "systematic review"],
                "min_sources": 2,
                "require_peer_review": True
            },
            "technological": {
                "min_tier": SourceTier.TIER_2,
                "preferred_types": ["technical paper", "industry report"],
                "min_sources": 1,
                "allow_preprints": True
            },
            "social": {
                "min_tier": SourceTier.TIER_2,
                "preferred_types": ["survey", "social science study"],
                "min_sources": 2,
                "require_sample_size": True
            },
            "economic": {
                "min_tier": SourceTier.TIER_2,
                "preferred_types": ["economic analysis", "institutional report"],
                "min_sources": 1,
                "prefer_institutions": ["IMF", "World Bank", "OECD"]
            }
        }
        
        return requirements.get(claim_type, {
            "min_tier": SourceTier.TIER_3,
            "min_sources": 1
        })
    
    def evaluate_debate_quality(self) -> Dict:
        """Evaluate the overall quality of the debate based on sources used"""
        
        all_claims = []
        for topic in self.memory.topics:
            all_claims.extend(topic.claims)
        
        if not all_claims:
            return {"error": "No claims to evaluate"}
        
        # Analyze source quality across all claims
        total_evidence_items = 0
        verified_evidence = 0
        credibility_scores = []
        
        for claim in all_claims:
            total_evidence_items += len(claim.supporting_evidence)
            
            if claim.id in self.verified_sources:
                verification = self.verified_sources[claim.id]["verification"]
                verified_evidence += len(verification.get("evidence_quality", []))
                credibility_scores.append(verification.get("average_credibility", 0))
        
        avg_credibility = sum(credibility_scores) / len(credibility_scores) if credibility_scores else 0
        
        # Calculate quality metrics
        evidence_verification_rate = verified_evidence / total_evidence_items if total_evidence_items > 0 else 0
        
        quality_score = (avg_credibility * 0.6) + (evidence_verification_rate * 0.4)
        
        return {
            "overall_quality_score": quality_score,
            "average_source_credibility": avg_credibility,
            "evidence_verification_rate": evidence_verification_rate,
            "total_claims": len(all_claims),
            "claims_with_verified_sources": len(credibility_scores),
            "quality_assessment": self._get_quality_level(quality_score),
            "improvement_suggestions": self._get_improvement_suggestions(
                quality_score, avg_credibility, evidence_verification_rate
            )
        }
    
    def _get_quality_level(self, score: float) -> str:
        """Convert quality score to descriptive level"""
        if score >= 0.8:
            return "Excellent - Well-sourced, rigorous debate"
        elif score >= 0.6:
            return "Good - Most claims properly supported"
        elif score >= 0.4:
            return "Fair - Some evidence gaps exist"
        else:
            return "Poor - Insufficient evidence for most claims"
    
    def _get_improvement_suggestions(self, quality_score: float, 
                                   credibility: float, verification_rate: float) -> List[str]:
        """Generate suggestions for improving debate quality"""
        suggestions = []
        
        if credibility < 0.6:
            suggestions.append("Use more reputable sources (aim for peer-reviewed studies)")
        
        if verification_rate < 0.5:
            suggestions.append("Provide sources for more of your claims")
        
        if quality_score < 0.6:
            suggestions.append("Fact-check claims before making them")
            suggestions.append("Challenge unsupported claims from your opponent")
        
        if not suggestions:
            suggestions.append("Maintain high standards of evidence")
        
        return suggestions
    
    def export_source_analysis(self) -> str:
        """Export detailed source analysis"""
        
        analysis = {
            "conversation_summary": self.memory.get_conversation_summary(),
            "source_verification": {},
            "quality_assessment": self.evaluate_debate_quality(),
            "verified_sources_by_claim": {}
        }
        
        # Add detailed source info
        for claim_id, source_info in self.verified_sources.items():
            analysis["verified_sources_by_claim"][claim_id] = {
                "verification_status": source_info["verification"]["status"],
                "credibility": source_info["verification"]["average_credibility"],
                "sources": [
                    {
                        "title": s.get("title", ""),
                        "url": s.get("url", ""),
                        "tier": s.get("quality", {}).get("tier", "unknown"),
                        "credibility": s.get("quality", {}).get("credibility_score", 0)
                    }
                    for s in source_info["sources"]
                ]
            }
        
        return json.dumps(analysis, indent=2)


class SmartFactChecker:
    """AI-enhanced fact checker that can work without live search"""
    
    def __init__(self):
        # Common facts database for quick verification
        self.known_facts = {
            "ai_market_growth": {
                "claim": "AI market growing at 40% annually",
                "status": "supported",
                "sources": [
                    "McKinsey Global AI Survey 2024",
                    "Statista AI Market Report 2024"
                ],
                "last_updated": "2024-01"
            },
            "climate_temperature": {
                "claim": "Global average temperature increased 1.1°C since 1850-1900",
                "status": "well_supported",
                "sources": [
                    "IPCC Sixth Assessment Report",
                    "NASA GISS Temperature Data"
                ],
                "last_updated": "2023"
            },
            # Add more common facts as needed
        }
    
    def quick_verify(self, claim: str) -> Optional[Dict]:
        """Quick verification against known facts database"""
        
        claim_lower = claim.lower()
        
        for fact_key, fact_data in self.known_facts.items():
            if any(keyword in claim_lower for keyword in fact_key.split("_")):
                return fact_data
        
        return None
    
    def suggest_verification_approach(self, claim: str) -> Dict:
        """Suggest how to verify a specific type of claim"""
        
        claim_lower = claim.lower()
        
        if any(word in claim_lower for word in ["study", "research", "shows"]):
            return {
                "approach": "academic_search",
                "keywords": ["study", "research", "peer review"],
                "preferred_sources": ["pubmed", "scholar.google.com", "arxiv.org"],
                "min_tier": SourceTier.TIER_1
            }
        
        elif any(word in claim_lower for word in ["increase", "decrease", "%", "statistics"]):
            return {
                "approach": "statistical_verification",
                "keywords": ["statistics", "data", "report"],
                "preferred_sources": ["government agencies", "institutional reports"],
                "min_tier": SourceTier.TIER_2
            }
        
        elif any(word in claim_lower for word in ["company", "business", "market"]):
            return {
                "approach": "business_verification",
                "keywords": ["financial report", "market analysis"],
                "preferred_sources": ["bloomberg.com", "reuters.com", "company reports"],
                "min_tier": SourceTier.TIER_2
            }
        
        else:
            return {
                "approach": "general_verification",
                "keywords": ["fact check", "evidence"],
                "preferred_sources": ["reputable news", "academic sources"],
                "min_tier": SourceTier.TIER_3
            }