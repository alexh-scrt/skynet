#!/usr/bin/env python3
"""
Test the centralized tuning system to ensure parameters are properly loaded and used
"""

import sys
from pathlib import Path

# Add project root to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.config.tune import (
    get_ken_approval_threshold, 
    get_temperature_for_stage,
    validate_parameters,
    DebateParameters,
    MaturityParameters
)

def test_parameter_validation():
    """Test that parameter validation works correctly"""
    print("🔍 TEST 1: PARAMETER VALIDATION")
    print("-" * 50)
    
    # Should pass with current parameters
    try:
        validate_parameters()
        print("✅ PASSED: Parameter validation successful")
    except ValueError as e:
        print(f"❌ FAILED: Parameter validation error: {e}")
        raise
    
    print()

def test_ken_approval_threshold():
    """Test that Ken's approval threshold is properly configured"""
    print("🔍 TEST 2: KEN APPROVAL THRESHOLD")
    print("-" * 50)
    
    threshold = get_ken_approval_threshold()
    print(f"Ken's approval threshold: {threshold}")
    
    # Should be in a reasonable range for healthy debate
    assert 0.75 <= threshold <= 0.90, f"Ken threshold {threshold} should be between 0.75-0.90 for balanced debate"
    
    # Should not be the problematic 0.95 that made him too soft
    assert threshold != 0.95, "Threshold should not be 0.95 (too soft)"
    
    # Should not be the problematic 0.99 that caused endless debates
    assert threshold != 0.99, "Threshold should not be 0.99 (too demanding)"
    
    print(f"✅ PASSED: Threshold {threshold} is in healthy range (0.75-0.90)")
    print()

def test_temperature_settings():
    """Test that temperature settings are properly configured for both agents"""
    print("🔍 TEST 3: TEMPERATURE SETTINGS")
    print("-" * 50)
    
    stages = ["exploration", "refinement", "convergence", "consensus"]
    
    for agent in ["barbie", "ken"]:
        print(f"\n{agent.upper()} temperature settings:")
        for stage in stages:
            temp, top_p = get_temperature_for_stage(agent, stage)
            print(f"  {stage}: temp={temp}, top_p={top_p}")
            
            # Validate temperature range
            assert 0.1 <= temp <= 2.0, f"{agent} {stage} temperature {temp} out of range"
            assert 0.1 <= top_p <= 1.0, f"{agent} {stage} top_p {top_p} out of range"
        
        # Test that temperatures generally decrease as conversation matures
        temps = [get_temperature_for_stage(agent, stage)[0] for stage in stages]
        
        # Should have general downward trend (with some flexibility)
        exploration_temp = temps[0]
        consensus_temp = temps[3]
        assert exploration_temp > consensus_temp, f"{agent} temperature should decrease from exploration to consensus"
    
    print("✅ PASSED: All temperature settings are valid and follow expected patterns")
    print()

def test_maturity_thresholds():
    """Test that conversation maturity thresholds are properly ordered"""
    print("🔍 TEST 4: MATURITY STAGE THRESHOLDS")
    print("-" * 50)
    
    exploration_to_refinement = MaturityParameters.EXPLORATION_TO_REFINEMENT
    refinement_to_convergence = MaturityParameters.REFINEMENT_TO_CONVERGENCE
    convergence_to_consensus = MaturityParameters.CONVERGENCE_TO_CONSENSUS
    
    print(f"Stage transitions:")
    print(f"  Exploration → Refinement: {exploration_to_refinement}")
    print(f"  Refinement → Convergence: {refinement_to_convergence}")
    print(f"  Convergence → Consensus: {convergence_to_consensus}")
    
    # Should be in ascending order
    assert exploration_to_refinement < refinement_to_convergence, "Exploration threshold should be less than refinement"
    assert refinement_to_convergence < convergence_to_consensus, "Refinement threshold should be less than convergence"
    
    # Should be reasonable values
    assert 0.0 <= exploration_to_refinement <= 0.5, "Exploration threshold should be in reasonable range"
    assert 0.3 <= refinement_to_convergence <= 0.7, "Refinement threshold should be in reasonable range"
    assert 0.6 <= convergence_to_consensus <= 1.0, "Convergence threshold should be in reasonable range"
    
    print("✅ PASSED: Maturity thresholds are properly ordered and in reasonable ranges")
    print()

def test_parameter_access():
    """Test that parameter access functions work correctly"""
    print("🔍 TEST 5: PARAMETER ACCESS FUNCTIONS")
    print("-" * 50)
    
    # Test that all key parameters can be accessed
    threshold = get_ken_approval_threshold()
    assert isinstance(threshold, float), "Approval threshold should be a float"
    
    # Test temperature function with various inputs
    temp, top_p = get_temperature_for_stage("barbie", "exploration")
    assert isinstance(temp, (int, float)), "Temperature should be numeric"
    assert isinstance(top_p, (int, float)), "Top_p should be numeric"
    
    # Test with invalid stage (should return defaults)
    temp, top_p = get_temperature_for_stage("ken", "invalid_stage")
    assert temp == 0.7 and top_p == 0.8, "Should return default values for invalid stage"
    
    print("✅ PASSED: All parameter access functions work correctly")
    print()

def test_debate_balance():
    """Test that parameters are balanced for good debate dynamics"""
    print("🔍 TEST 6: DEBATE BALANCE ANALYSIS")
    print("-" * 50)
    
    ken_threshold = get_ken_approval_threshold()
    
    # Analyze the balance
    if ken_threshold < 0.75:
        print(f"⚠️  WARNING: Ken threshold {ken_threshold} may be too low (too agreeable)")
    elif ken_threshold > 0.90:
        print(f"⚠️  WARNING: Ken threshold {ken_threshold} may be too high (too demanding)")
    else:
        print(f"✅ GOOD: Ken threshold {ken_threshold} is balanced for healthy debate")
    
    # Check temperature differences between agents
    barbie_exploration = get_temperature_for_stage("barbie", "exploration")[0]
    ken_exploration = get_temperature_for_stage("ken", "exploration")[0]
    
    print(f"Temperature comparison (exploration stage):")
    print(f"  Barbie: {barbie_exploration}")
    print(f"  Ken: {ken_exploration}")
    
    if barbie_exploration > ken_exploration:
        print("✅ GOOD: Barbie is more creative than Ken (as expected)")
    else:
        print("⚠️  Note: Ken and Barbie have similar creativity levels")
    
    print()

def main():
    """Run all tuning system tests"""
    print("🚀 TESTING CENTRALIZED TUNING SYSTEM")
    print("Verifying that parameters are properly configured for balanced debates")
    print("=" * 70)
    print()
    
    try:
        test_parameter_validation()
        test_ken_approval_threshold()
        test_temperature_settings()
        test_maturity_thresholds()
        test_parameter_access()
        test_debate_balance()
        
        print("=" * 70)
        print("📊 TUNING SYSTEM SUMMARY")
        print("=" * 70)
        
        ken_threshold = get_ken_approval_threshold()
        barbie_temp = get_temperature_for_stage("barbie", "exploration")[0]
        ken_temp = get_temperature_for_stage("ken", "exploration")[0]
        
        print("✅ All tuning system tests passed!")
        print()
        print("Current configuration:")
        print(f"- Ken approval threshold: {ken_threshold} (should prevent both endless debates and premature agreement)")
        print(f"- Barbie exploration temperature: {barbie_temp} (creative idea generation)")
        print(f"- Ken exploration temperature: {ken_temp} (focused evaluation)")
        print()
        print("Expected behavior:")
        print("- Healthy intellectual discourse with appropriate challenge")
        print("- Natural convergence when sufficient evidence is presented")
        print("- Balanced conversations (10-20 rounds, not 2-3 or 80+)")
        print("- Quality discussions without endless loops")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        raise

if __name__ == "__main__":
    main()