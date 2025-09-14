"""
Test enhanced prompting system
"""
import sys
from pathlib import Path

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.prompts.enhanced_prompts import (
    generate_contextual_prompt,
    get_debate_instruction,
    DEBATE_TOPICS_PROGRESSIVE
)
from src.prompts.prompt_optimizer import (
    PromptOptimizer,
    DebatePhase,
    DebateTone,
    ResponseEvaluator,
    create_dynamic_prompt
)


def test_prompt_optimization():
    """Test the prompt optimization system"""
    
    print("=== Enhanced Prompting System Demo ===\n")
    
    # Initialize optimizer
    optimizer = PromptOptimizer()
    evaluator = ResponseEvaluator()
    
    # Simulate conversation states
    conversation_states = [
        {
            "turn_number": 1,
            "resolution_rate": 0.0,
            "dispute_rate": 0.0,
            "agreement_level": 0.5,
            "description": "Opening"
        },
        {
            "turn_number": 5,
            "resolution_rate": 0.2,
            "dispute_rate": 0.6,
            "agreement_level": 0.3,
            "description": "Heated challenge"
        },
        {
            "turn_number": 8,
            "resolution_rate": 0.5,
            "dispute_rate": 0.3,
            "agreement_level": 0.6,
            "description": "Finding synthesis"
        },
        {
            "turn_number": 12,
            "resolution_rate": 0.7,
            "dispute_rate": 0.1,
            "agreement_level": 0.8,
            "description": "Approaching conclusion"
        }
    ]
    
    for state in conversation_states:
        print(f"\n--- {state['description']} (Turn {state['turn_number']}) ---")
        
        # Determine phase
        phase = optimizer.determine_phase(
            state["turn_number"],
            state["resolution_rate"],
            state["dispute_rate"]
        )
        print(f"Phase: {phase.value}")
        
        # Get tones for both agents
        barbie_tone = optimizer.select_tone("Barbie", phase, state["agreement_level"])
        ken_tone = optimizer.select_tone("Ken", phase, state["agreement_level"])
        print(f"Barbie's tone: {barbie_tone.value}")
        print(f"Ken's tone: {ken_tone.value}")
        
        # Get phase instructions
        barbie_instruction = optimizer.generate_phase_instruction(phase, barbie_tone)
        print(f"\nBarbie's instruction: {barbie_instruction}")
        
        ken_instruction = optimizer.generate_phase_instruction(phase, ken_tone)
        print(f"Ken's instruction: {ken_instruction}")
        
        # Get rhetorical devices
        barbie_device = optimizer.suggest_rhetorical_device("Barbie", phase)
        print(f"\nBarbie's rhetorical device: {barbie_device}")
        
        ken_device = optimizer.suggest_rhetorical_device("Ken", phase)
        print(f"Ken's rhetorical device: {ken_device}")
    
    print("\n\n=== Testing Response Evaluation ===\n")
    
    # Test response evaluation
    test_responses = [
        {
            "response": "AI is good for society.",
            "expected_score": "Low",
            "reason": "Too generic, no evidence"
        },
        {
            "response": "As you mentioned, AI has risks. However, studies from MIT (2023) show that AI-assisted diagnosis improved accuracy by 23% in radiology. For example, detecting early-stage cancers that human radiologists missed.",
            "expected_score": "High",
            "reason": "Engages with opponent, provides evidence, specific example"
        },
        {
            "response": "I think AI is problematic. AI causes issues. AI needs regulation. AI is concerning.",
            "expected_score": "Low",
            "reason": "Repetitive, no specifics, no structure"
        }
    ]
    
    criteria = {
        "specificity": 1.0,
        "evidence": 1.0,
        "engagement": 1.0,
        "novelty": 1.0,
        "structure": 1.0
    }
    
    for test in test_responses:
        score, feedback = evaluator.score_response(test["response"], criteria)
        print(f"Response: \"{test['response'][:50]}...\"")
        print(f"Expected: {test['expected_score']} ({test['reason']})")
        print(f"Score: {score:.2f}")
        print(f"Feedback: {', '.join(feedback) if feedback else 'Good response!'}")
        print()
    
    print("\n=== Testing Dynamic Prompt Generation ===\n")
    
    # Test dynamic prompt generation
    for agent in ["Barbie", "Ken"]:
        print(f"\n--- Dynamic Prompt for {agent} ---")
        
        conversation_state = {
            "turn_number": 6,
            "resolution_rate": 0.3,
            "dispute_rate": 0.5,
            "agreement_level": 0.4,
            "previous_responses": [
                "However, this point is questionable...",
                "However, we must consider...",
                "However, the evidence suggests..."
            ]
        }
        
        dynamic_prompt = create_dynamic_prompt(agent, conversation_state)
        print(dynamic_prompt)
    
    print("\n=== Sample Enhanced Topics ===\n")
    
    # Show enhanced debate topics
    for i, topic_info in enumerate(DEBATE_TOPICS_PROGRESSIVE[:3], 1):
        print(f"\n{i}. {topic_info['topic']}")
        print(f"   Opening: {topic_info['opening_question']}")
        print(f"   Subtopics: {', '.join(topic_info['subtopics'][:2])}...")


def test_contextual_prompt_generation():
    """Test contextual prompt generation with memory"""
    
    print("\n\n=== Testing Contextual Prompt with Memory ===\n")
    
    memory_context = {
        "unaddressed_claims": ["claim_1", "claim_2"],
        "disputed_claims": ["claim_3"],
        "shared_facts": {"fact_1": "AI growing 40% annually"},
        "strong_arguments": [
            {"id": "arg_1", "speaker": "Barbie", "conclusion": "AI benefits outweigh risks"},
            {"id": "arg_2", "speaker": "Ken", "conclusion": "Regulation is essential"}
        ],
        "should_change_topic": False,
        "unresolved_questions": ["How to ensure AI safety?", "What about job displacement?"]
    }
    
    goals = [
        "Explore AI's impact on society",
        "Find balanced perspective",
        "Identify actionable solutions"
    ]
    
    # Generate contextual prompt for Barbie
    barbie_prompt = generate_contextual_prompt("Barbie", memory_context, goals)
    
    # Show just the memory integration part
    print("Memory Integration in Barbie's Prompt:")
    print("-" * 40)
    memory_section = barbie_prompt.split("MEMORY INTEGRATION:")[1].split("CURRENT GOALS:")[0]
    print(memory_section[:500])  # First 500 chars
    
    print("\n" + "=" * 50)
    
    # Get debate instruction based on turn
    for turn in [1, 5, 9, 12]:
        instruction = get_debate_instruction(turn, "Previous discussion summary...")
        print(f"Turn {turn}: {instruction}")


if __name__ == "__main__":
    test_prompt_optimization()
    test_contextual_prompt_generation()