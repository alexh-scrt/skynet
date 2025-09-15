"""
Skynet AI Agent Tuning Parameters
=================================

This module contains all the fine-tuning parameters for the Barbie and Ken AI agents.
These parameters control the behavior, personality, and interaction dynamics between agents.

The goal is to achieve:
- Healthy intellectual discourse with appropriate challenge/skepticism
- Natural convergence to consensus when sufficient evidence is presented
- Balanced conversations that are neither too aggressive nor too passive
- Quality discussions that cover topics thoroughly without endless loops

Modify these values to adjust agent behavior. Higher values generally increase
the effect of the parameter, while lower values decrease it.
"""

# =============================================================================
# CORE DEBATE DYNAMICS
# =============================================================================

class DebateParameters:
    """Parameters controlling overall debate behavior and convergence"""
    
    # Ken's approval threshold - how confident he needs to be to approve Barbie's arguments
    # 0.60-0.70: Very agreeable (too soft, may approve weak arguments)
    # 0.75-0.80: Balanced (healthy skepticism, reasonable convergence)  
    # 0.85-0.90: Critical (demanding but achievable)
    # 0.95+: Near-impossible to satisfy (endless debates)
    KEN_APPROVAL_THRESHOLD = 0.89  # Adjusted to realistic range
    
    # Discussion completeness boost threshold - when to help push toward conclusion
    # If discussion completeness score > this value, boost confidence slightly
    DISCUSSION_COMPLETENESS_THRESHOLD = 0.5
    
    # Confidence boost amount when discussion is deemed complete
    # 0.10 = gentle nudge toward consensus, 0.20 = strong push
    DISCUSSION_COMPLETENESS_BOOST = 0.175  # Increased for better convergence
    
    # Maximum number of rounds before aggressive conclusion pushing
    # After this many rounds, agents should be very motivated to conclude
    MAX_ROUNDS_BEFORE_CONCLUSION_PUSH = 25
    
    # Topic drift tolerance - how many drift instances before intervention
    # Lower = quicker to refocus, Higher = more tolerant of tangential discussion
    TOPIC_DRIFT_THRESHOLD = 1

# =============================================================================
# CONVERSATION MATURITY AND TEMPERATURE CONTROL
# =============================================================================

class MaturityParameters:
    """Parameters controlling conversation maturity assessment and LLM temperature"""
    
    # LLM Temperature settings for different conversation stages
    # Higher temperature = more creative/diverse responses
    # Lower temperature = more focused/consistent responses
    
    BARBIE_EXPLORATION_TEMP = 1.2      # Initial creative exploration
    BARBIE_REFINEMENT_TEMP = 0.9       # Focused development of ideas
    BARBIE_CONVERGENCE_TEMP = 0.6      # Structured argument building
    BARBIE_CONSENSUS_TEMP = 0.3        # Final consensus confirmation
    
    KEN_EXPLORATION_TEMP = 1.1         # Initial evaluation (slightly more focused than Barbie)
    KEN_REFINEMENT_TEMP = 0.8          # Targeted criticism and questions
    KEN_CONVERGENCE_TEMP = 0.5         # Precise evaluation of final arguments
    KEN_CONSENSUS_TEMP = 0.3           # Final approval/consensus
    
    # Top-p values for nucleus sampling (probability mass cutoff)
    # Higher = more diverse word choices, Lower = more predictable
    BARBIE_EXPLORATION_TOP_P = 0.95
    BARBIE_REFINEMENT_TOP_P = 0.85
    BARBIE_CONVERGENCE_TOP_P = 0.7
    BARBIE_CONSENSUS_TOP_P = 0.5
    
    KEN_EXPLORATION_TOP_P = 0.925
    KEN_REFINEMENT_TOP_P = 0.825
    KEN_CONVERGENCE_TOP_P = 0.65
    KEN_CONSENSUS_TOP_P = 0.45
    
    # Maturity stage thresholds (0.0 to 1.0)
    # These determine when conversation transitions between stages
    EXPLORATION_TO_REFINEMENT = 0.25   # Broad questions → focused discussion
    REFINEMENT_TO_CONVERGENCE = 0.50   # Focused discussion → argument building
    CONVERGENCE_TO_CONSENSUS = 0.75    # Argument building → final agreement

# =============================================================================
# HELPER FUNCTIONS FOR PARAMETER ACCESS
# =============================================================================

def get_ken_approval_threshold() -> float:
    """Get Ken's current approval threshold"""
    return DebateParameters.KEN_APPROVAL_THRESHOLD

def get_temperature_for_stage(agent: str, stage: str) -> tuple:
    """Get temperature and top_p for agent and conversation stage"""
    if agent.lower() == "barbie":
        temp_map = {
            "exploration": (MaturityParameters.BARBIE_EXPLORATION_TEMP, MaturityParameters.BARBIE_EXPLORATION_TOP_P),
            "refinement": (MaturityParameters.BARBIE_REFINEMENT_TEMP, MaturityParameters.BARBIE_REFINEMENT_TOP_P),
            "convergence": (MaturityParameters.BARBIE_CONVERGENCE_TEMP, MaturityParameters.BARBIE_CONVERGENCE_TOP_P),
            "consensus": (MaturityParameters.BARBIE_CONSENSUS_TEMP, MaturityParameters.BARBIE_CONSENSUS_TOP_P)
        }
    else:  # Ken
        temp_map = {
            "exploration": (MaturityParameters.KEN_EXPLORATION_TEMP, MaturityParameters.KEN_EXPLORATION_TOP_P),
            "refinement": (MaturityParameters.KEN_REFINEMENT_TEMP, MaturityParameters.KEN_REFINEMENT_TOP_P),
            "convergence": (MaturityParameters.KEN_CONVERGENCE_TEMP, MaturityParameters.KEN_CONVERGENCE_TOP_P),
            "consensus": (MaturityParameters.KEN_CONSENSUS_TEMP, MaturityParameters.KEN_CONSENSUS_TOP_P)
        }
    
    return temp_map.get(stage, (0.7, 0.8))  # Default values

def validate_parameters():
    """Validate that all parameters are within reasonable ranges"""
    issues = []
    
    # Check approval threshold
    if not 0.5 <= DebateParameters.KEN_APPROVAL_THRESHOLD <= 0.98:
        issues.append(f"KEN_APPROVAL_THRESHOLD ({DebateParameters.KEN_APPROVAL_THRESHOLD}) should be between 0.5 and 0.98")
    
    # Check temperature values
    temps = [
        MaturityParameters.BARBIE_EXPLORATION_TEMP, MaturityParameters.BARBIE_REFINEMENT_TEMP,
        MaturityParameters.BARBIE_CONVERGENCE_TEMP, MaturityParameters.BARBIE_CONSENSUS_TEMP,
        MaturityParameters.KEN_EXPLORATION_TEMP, MaturityParameters.KEN_REFINEMENT_TEMP,
        MaturityParameters.KEN_CONVERGENCE_TEMP, MaturityParameters.KEN_CONSENSUS_TEMP
    ]
    
    for temp in temps:
        if not 0.1 <= temp <= 2.0:
            issues.append(f"Temperature value {temp} should be between 0.1 and 2.0")
    
    # Check maturity thresholds are in ascending order
    thresholds = [
        MaturityParameters.EXPLORATION_TO_REFINEMENT,
        MaturityParameters.REFINEMENT_TO_CONVERGENCE, 
        MaturityParameters.CONVERGENCE_TO_CONSENSUS
    ]
    
    for i in range(len(thresholds) - 1):
        if thresholds[i] >= thresholds[i + 1]:
            issues.append("Maturity stage thresholds should be in ascending order")
            break
    
    if issues:
        raise ValueError("Parameter validation failed:\n" + "\n".join(issues))
    
    return True

# Validate parameters on import
if __name__ == "__main__":
    validate_parameters()
    print("✅ All tuning parameters are valid!")