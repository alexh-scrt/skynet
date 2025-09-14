"""
Test enhanced conversation with memory integration
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.conversation.enhanced_conversation import (
    EnhancedConversationManager, 
    AgentResponseBuilder
)


def demonstrate_enhanced_conversation():
    """Demonstrate how enhanced conversation improves quality"""
    
    # Initialize conversation manager
    manager = EnhancedConversationManager()
    manager.start_conversation(
        "demo_001",
        "The Future of AI in Society",
        goals=["Explore benefits and risks of AI", "Find common ground", "Identify key challenges"]
    )
    
    print("=== Enhanced Conversation Demo ===\n")
    
    # Barbie makes an initial claim with evidence
    barbie_response = AgentResponseBuilder.build_claim_response(
        speaker="Barbie",
        claim="AI can significantly improve healthcare outcomes",
        evidence=["Study from Nature Medicine 2023 shows 20% improvement in diagnosis accuracy"],
        argument_type="INDUCTIVE",
        premises=["AI can process vast amounts of medical data", "Pattern recognition exceeds human capability"]
    )
    
    result = manager.process_agent_response(
        barbie_response["speaker"],
        barbie_response["response"],
        barbie_response["metadata"]
    )
    print(f"Barbie: {barbie_response['response']}")
    print(f"  -> Tracked as {result['type']} with strength: {result.get('strength', 'N/A')}\n")
    
    # Ken gets context and responds
    ken_context = manager.get_conversation_context("Ken")
    print(f"Ken's context: {len(ken_context['unaddressed_claims'])} claims to address")
    print(f"Suggested action for Ken: {manager.suggest_next_action('Ken')}\n")
    
    # Ken provides a counter-argument
    ken_response = AgentResponseBuilder.build_counter_response(
        speaker="Ken",
        counter="But AI systems can perpetuate biases present in training data",
        target_claim="claim_1",
        target_argument="arg_1",
        premise_index=1
    )
    
    result = manager.process_agent_response(
        ken_response["speaker"],
        ken_response["response"],
        ken_response["metadata"]
    )
    print(f"Ken: {ken_response['response']}")
    print(f"  -> Tracked as {result['type']}\n")
    
    # Check for disputed claims
    disputed = manager.memory.get_disputed_claims()
    print(f"Disputed claims: {len(disputed)}")
    
    # Barbie makes another claim
    barbie_response2 = AgentResponseBuilder.build_claim_response(
        speaker="Barbie",
        claim="Bias mitigation techniques are rapidly improving",
        evidence=["Recent advances in fairness-aware ML", "Audit tools becoming standard"],
        argument_type="DEDUCTIVE",
        premises=["New techniques detect bias", "Regulations require bias testing"]
    )
    
    result = manager.process_agent_response(
        barbie_response2["speaker"],
        barbie_response2["response"],
        barbie_response2["metadata"]
    )
    print(f"\nBarbie: {barbie_response2['response']}")
    print(f"  -> Tracked as {result['type']}\n")
    
    # Add a shared fact
    manager.add_verified_fact(
        "fact_1",
        "AI adoption in healthcare is growing at 40% annually",
        "McKinsey Healthcare Report 2023"
    )
    print("Added shared fact about AI adoption rate\n")
    
    # Ken agrees with the second claim
    ken_agreement = AgentResponseBuilder.build_agreement_response(
        speaker="Ken",
        claim_id="claim_2",
        reason="The evidence for improving bias mitigation is compelling"
    )
    
    result = manager.process_agent_response(
        ken_agreement["speaker"],
        ken_agreement["response"],
        ken_agreement["metadata"]
    )
    print(f"Ken: {ken_agreement['response']}")
    print(f"  -> Tracked as {result['type']}\n")
    
    # Get conversation summary
    summary = manager.get_summary()
    print("\n=== Conversation Summary ===")
    print(f"Topics discussed: {summary['topics_discussed']}")
    print(f"Total claims: {summary['total_claims']}")
    print(f"Resolved points: {summary['resolved_points']}")
    print(f"Shared facts: {summary['shared_facts']}")
    print(f"Strong arguments: {summary['strong_arguments']}")
    print(f"Conversation goals: {summary['conversation_goals']}")
    
    # Show how this prevents repetition
    print("\n=== Benefits of Memory Tracking ===")
    print("1. No repetition - agents know what's been discussed")
    print("2. Claims are tracked with evidence")
    print("3. Arguments build on previous points")
    print("4. Contradictions are detected")
    print("5. Progress toward goals is measurable")
    
    return manager


if __name__ == "__main__":
    manager = demonstrate_enhanced_conversation()
    
    # Export conversation for analysis
    print("\n=== Exported Conversation (truncated) ===")
    export = manager.export_conversation()
    print(export[:500] + "...")  # Show first 500 chars