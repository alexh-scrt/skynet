"""
Test enhanced agent personalities with domain expertise and rhetorical styles
"""
import sys
from pathlib import Path

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.personality.agent_personalities import (
    PersonalityManager, BarbiePersonality, KenPersonality, DomainExpertise
)
from src.personality.personality_integration import (
    PersonalizedConversationManager, create_personality_enhanced_prompt
)


def test_domain_expertise():
    """Test the comprehensive domain knowledge system"""
    
    print("=== Domain Expertise System Test ===\n")
    
    domains = DomainExpertise.DOMAINS
    
    print(f"Available domains: {len(domains)}")
    print("-" * 60)
    
    for domain_name, domain_info in list(domains.items())[:4]:  # Show first 4
        print(f"\n{domain_name.replace('_', ' ').title()}:")
        print(f"  Key Concepts: {', '.join(domain_info['key_concepts'][:5])}...")
        print(f"  Recent Developments: {', '.join(domain_info['recent_developments'][:3])}...")
        print(f"  Key Figures: {', '.join(domain_info['key_figures'][:4])}...")
        
        if 'applications' in domain_info:
            print(f"  Applications: {', '.join(domain_info['applications'][:3])}...")
        elif 'impacts' in domain_info:
            print(f"  Impacts: {', '.join(domain_info['impacts'][:3])}...")


def test_barbie_personality():
    """Test Barbie's synthesist-analogical reasoning style"""
    
    print("\n\n=== Barbie's Synthesist-Analogical Style ===\n")
    
    barbie = BarbiePersonality()
    
    # Test rhetorical approaches for different phases
    phases = ["opening", "exploration", "challenge", "synthesis"]
    topic = "artificial_intelligence"
    
    for phase in phases:
        approach = barbie.get_rhetorical_approach(topic, phase)
        print(f"{phase.title()} Phase:")
        print(f"  Primary approach: {approach['primary_approaches'][0]}")
        print(f"  Analogical sources: {', '.join(approach['analogical_sources'][:3])}...")
        print(f"  Synthesis technique: {approach['synthesis_techniques'][0]}")
        print()
    
    print("Signature Phrases:")
    signatures = barbie.get_signature_phrases()
    for i, phrase in enumerate(signatures[:6], 1):
        print(f"  {i}. {phrase}")
    
    print("\nCross-Domain Connection Example:")
    connection = barbie.generate_domain_connection(
        "artificial_intelligence", "neuroscience", "learning algorithms"
    )
    print(f"  {connection}")


def test_ken_personality():
    """Test Ken's systems-dialectical reasoning style"""
    
    print("\n\n=== Ken's Systems-Dialectical Style ===\n")
    
    ken = KenPersonality()
    
    # Test rhetorical approaches for different phases
    phases = ["opening", "exploration", "challenge", "synthesis"]
    topic = "climate_science"
    
    for phase in phases:
        approach = ken.get_rhetorical_approach(topic, phase)
        print(f"{phase.title()} Phase:")
        print(f"  Primary approach: {approach['primary_approaches'][0]}")
        print(f"  Analytical framework: {approach['analytical_frameworks'][0]}")
        print(f"  Dialectical technique: {approach['dialectical_techniques'][0]}")
        print()
    
    print("Signature Phrases:")
    signatures = ken.get_signature_phrases()
    for i, phrase in enumerate(signatures[:6], 1):
        print(f"  {i}. {phrase}")
    
    print("\nDialectical Probe Example:")
    probe = ken.generate_dialectical_probe(
        "AI will solve climate change", "economics"
    )
    print(f"  {probe}")
    
    print("\nArgument Structure Analysis:")
    analysis = ken.analyze_argument_structure(
        "Since AI can process vast amounts of climate data, it will solve global warming"
    )
    print(f"  Structure type: {analysis['structure_type']}")
    print(f"  Dialectical probes: {analysis['dialectical_probes'][0]}")


def test_personality_manager():
    """Test the personality management system"""
    
    print("\n\n=== Personality Management System ===\n")
    
    manager = PersonalityManager()
    
    # Test domain expertise prompts
    topics = ["artificial_intelligence", "climate_science", "economics"]
    
    for topic in topics:
        print(f"{topic.replace('_', ' ').title()} Expertise:")
        print("-" * 40)
        
        barbie_context = manager.generate_domain_expertise_prompt("Barbie", topic)
        ken_context = manager.generate_domain_expertise_prompt("Ken", topic)
        
        print("Barbie's context (first 200 chars):")
        print(f"  {barbie_context[:200]}...")
        
        print("Ken's context (first 200 chars):")
        print(f"  {ken_context[:200]}...")
        print()
    
    # Test complementary response suggestions
    print("Complementary Response Suggestions:")
    print("-" * 40)
    
    barbie_suggestions = manager.get_complementary_response_suggestions(
        "Barbie", "systems_dialectical", "artificial_intelligence"
    )
    ken_suggestions = manager.get_complementary_response_suggestions(
        "Ken", "synthesist_analogical", "artificial_intelligence"
    )
    
    print("Barbie responding to Ken's systems approach:")
    for suggestion in barbie_suggestions:
        print(f"  • {suggestion}")
    
    print("\nKen responding to Barbie's analogical approach:")
    for suggestion in ken_suggestions:
        print(f"  • {suggestion}")
    
    # Test cross-domain connections
    print("\nCross-Domain Connection Suggestions:")
    print("-" * 40)
    
    barbie_connections = manager.suggest_cross_domain_connections("artificial_intelligence", "Barbie")
    ken_connections = manager.suggest_cross_domain_connections("artificial_intelligence", "Ken")
    
    print("Barbie's connections:")
    for connection in barbie_connections[:2]:
        print(f"  • {connection}")
    
    print("\nKen's connections:")
    for connection in ken_connections[:2]:
        print(f"  • {connection}")


def test_personality_integration():
    """Test the integrated personality conversation system"""
    
    print("\n\n=== Personality Integration Test ===\n")
    
    manager = PersonalizedConversationManager()
    
    # Simulate conversation context
    conversation_context = {
        "phase": "exploration",
        "agreement_level": 0.4,
        "disputed_claims": ["claim_1", "claim_2"],
        "unresolved_questions": ["How to ensure AI safety?"]
    }
    
    memory_context = {
        "shared_facts": {"fact_1": "AI market growing 40% annually"},
        "unaddressed_claims": [],
        "quality_score": 0.75
    }
    
    topic = "artificial_intelligence"
    
    # Generate personality prompts
    print("Personality-Enhanced Prompts:")
    print("-" * 40)
    
    barbie_prompt = manager.generate_personality_prompt("Barbie", topic, conversation_context)
    ken_prompt = manager.generate_personality_prompt("Ken", topic, conversation_context)
    
    print("Barbie's prompt (first 300 chars):")
    print(f"{barbie_prompt[:300]}...")
    
    print("\nKen's prompt (first 300 chars):")
    print(f"{ken_prompt[:300]}...")
    
    # Test conversation analysis (with mock data)
    print("\n\nConversation Analysis:")
    print("-" * 40)
    
    mock_conversation = [
        {
            "speaker": "Barbie",
            "content": "What if we imagine AI development like the evolution of language - starting with simple symbols and growing into rich, nuanced communication systems?"
        },
        {
            "speaker": "Ken", 
            "content": "Let's examine the logical structure of that analogy. Language evolution operates through different mechanisms than technological development - what specific causal pathways are you proposing?"
        },
        {
            "speaker": "Barbie",
            "content": "The underlying pattern I see is emergence through iteration and selection pressure. Just as words that communicate effectively survive and spread..."
        },
        {
            "speaker": "Ken",
            "content": "But this creates a fundamental tension - technological development is intentional and goal-directed, while language evolution is largely unconscious. How do we reconcile this?"
        }
    ]
    
    analysis = manager.analyze_personality_dynamics(mock_conversation)
    
    print(f"Barbie's style consistency: {analysis['barbie_style_analysis']['style_consistency']:.2f}")
    print(f"Ken's style consistency: {analysis['ken_style_analysis']['style_consistency']:.2f}")
    print(f"Overall balance: {analysis['personality_balance']['balance_quality']}")
    
    print("\nImprovement suggestions:")
    for suggestion in analysis['improvement_suggestions']:
        print(f"  • {suggestion}")


def demonstrate_personality_contrast():
    """Demonstrate the stark contrast between personality styles"""
    
    print("\n\n=== Personality Style Contrast Demo ===\n")
    
    # Same topic, different approaches
    topic = "The Future of Work in an AI-Dominated World"
    
    print(f"Topic: {topic}")
    print("=" * 60)
    
    barbie = BarbiePersonality()
    ken = KenPersonality()
    
    print("\nBarbie's Synthesist-Analogical Approach:")
    print("-" * 40)
    barbie_approach = barbie.get_rhetorical_approach("economics", "opening")
    print("Opening strategy:", barbie_approach['primary_approaches'][0])
    print("Analogical sources:", ", ".join(barbie_approach['analogical_sources'][:3]))
    print("Synthesis focus:", barbie_approach['synthesis_techniques'][0])
    
    barbie_example = """
    'Imagine the future of work like a jazz ensemble - instead of replacing musicians, 
    AI becomes a new instrument that transforms the entire composition. Just as the 
    electric guitar didn't eliminate orchestras but created rock music, AI won't 
    eliminate human work but will compose entirely new forms of human-AI collaboration.'
    """
    print("Example response:", barbie_example.strip())
    
    print("\nKen's Systems-Dialectical Approach:")
    print("-" * 40)
    ken_approach = ken.get_rhetorical_approach("economics", "opening")
    print("Opening strategy:", ken_approach['primary_approaches'][0])
    print("Analytical framework:", ken_approach['analytical_frameworks'][0])
    print("Dialectical technique:", ken_approach['dialectical_techniques'][0])
    
    ken_example = """
    'Let's examine the logical structure of "AI-dominated work." This assumes a 
    zero-sum relationship between AI capability and human employment. But if we 
    trace the causal mechanisms, we need to distinguish between task automation 
    and job elimination. The boundary conditions matter: at what point does AI 
    capability actually translate to workforce displacement?'
    """
    print("Example response:", ken_example.strip())
    
    print("\n\nKey Differences:")
    print("-" * 40)
    print("Barbie:")
    print("  ✓ Uses creative analogies (jazz ensemble)")
    print("  ✓ Focuses on synthesis and new possibilities")
    print("  ✓ Emotional and aesthetic framing")
    print("  ✓ Narrative structure")
    
    print("\nKen:")
    print("  ✓ Analytical deconstruction of terms")
    print("  ✓ Focus on mechanisms and causality")
    print("  ✓ Logical structure examination")
    print("  ✓ Boundary condition analysis")


def test_comprehensive_prompt_generation():
    """Test the comprehensive prompt generation system"""
    
    print("\n\n=== Comprehensive Prompt Generation ===\n")
    
    conversation_context = {
        "phase": "challenge",
        "agreement_level": 0.3,
        "turn_number": 6
    }
    
    memory_context = {
        "shared_facts": {"ai_growth": "40% annually", "energy_usage": "increasing"},
        "unaddressed_claims": ["claim_1"],
        "unresolved_questions": ["How to balance innovation with regulation?"],
        "quality_score": 0.8
    }
    
    # Generate comprehensive prompts
    barbie_prompt = create_personality_enhanced_prompt(
        "Barbie", "artificial_intelligence", conversation_context, memory_context
    )
    
    ken_prompt = create_personality_enhanced_prompt(
        "Ken", "artificial_intelligence", conversation_context, memory_context
    )
    
    print("Comprehensive Barbie Prompt Structure:")
    print("-" * 50)
    sections = barbie_prompt.split("\n\n")
    for i, section in enumerate(sections[:5], 1):
        print(f"{i}. {section.split(':')[0] if ':' in section else section[:50]}...")
    
    print("\nComprehensive Ken Prompt Structure:")
    print("-" * 50)
    sections = ken_prompt.split("\n\n")
    for i, section in enumerate(sections[:5], 1):
        print(f"{i}. {section.split(':')[0] if ':' in section else section[:50]}...")
    
    print(f"\nBarbie prompt length: {len(barbie_prompt)} characters")
    print(f"Ken prompt length: {len(ken_prompt)} characters")


if __name__ == "__main__":
    test_domain_expertise()
    test_barbie_personality()
    test_ken_personality()
    test_personality_manager()
    test_personality_integration()
    demonstrate_personality_contrast()
    test_comprehensive_prompt_generation()
    
    print("\n" + "=" * 60)
    print("Enhanced Agent Personalities Test Complete!")
    print("Barbie: Synthesist-Analogical • Ken: Systems-Dialectical")
    print("Both agents now have comprehensive domain expertise!")
    print("=" * 60)