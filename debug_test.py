#!/usr/bin/env python3
"""
Debug test for the graph workflow
"""

import env
from barbie import BarbieAgent, ConversationState

def test_barbie_graph():
    print("🔍 Testing Barbie LangGraph workflow...")
    
    try:
        # Initialize Barbie
        barbie = BarbieAgent()
        print("✅ Barbie initialized")
        
        # Create test state
        state = ConversationState(
            user_input="What is machine learning?",
            original_message="What is machine learning?",
            round_number=0,
            is_genesis=True
        )
        print("✅ State created")
        
        # Test individual nodes
        print("\n🧪 Testing individual nodes:")
        
        # 1. Load context
        state = barbie.load_context_node(state)
        print(f"  Load context: ✅ (context length: {len(state.conversation_context)})")
        
        # 2. Assess maturity
        state = barbie.assess_conversation_maturity(state)
        print(f"  Assess maturity: ✅ (score: {state.maturity_score}, stage: {state.maturity_stage})")
        
        # 3. Search web
        state = barbie.search_web_node(state)
        print(f"  Search web: ✅ (results length: {len(state.search_results)})")
        
        print(f"\n📊 State after nodes:")
        print(f"  user_input: {bool(state.user_input)}")
        print(f"  generated_response: {bool(state.generated_response)}")
        print(f"  maturity_stage: {state.maturity_stage}")
        print(f"  round_number: {state.round_number}")
        
        # Test the full graph
        print(f"\n🚀 Testing full graph execution:")
        try:
            final_state = barbie.graph.invoke(state)
            print(f"  Graph execution: ✅")
            print(f"  Final state type: {type(final_state)}")
            print(f"  Final state attributes: {list(final_state.__dict__.keys()) if hasattr(final_state, '__dict__') else 'No __dict__'}")
            
            if hasattr(final_state, 'generated_response'):
                print(f"  Has generated_response: ✅")
            else:
                print(f"  Has generated_response: ❌")
                
        except Exception as e:
            print(f"  Graph execution: ❌ {e}")
            import traceback
            traceback.print_exc()
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_barbie_graph()