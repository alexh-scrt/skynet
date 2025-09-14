# Centralized Tuning System for Skynet AI Agents

## Problem Analysis: Latest Conversation Issues

After analyzing `conversation_20250913_231837.md`, Ken was **too agreeable**:
- ✅ Round 1: Ken immediately said "I'm convinced! STOP" after just one exchange
- ✅ Round 2: Ken agreed again with "<STOP>" after Barbie continued  
- 🚨 **Total rounds: Only 2-3 exchanges** - too short for meaningful debate

**Root cause**: Ken's approval threshold was set to **0.95** (too soft) after being lowered from 0.99 (too demanding). This swing from one extreme to another shows the need for fine-tuned balance.

## Solution: Centralized Tuning System

Created `src/config/tune.py` - a comprehensive parameter configuration system that controls all aspects of agent behavior with detailed documentation.

### Key Components

#### 1. Core Debate Dynamics (`DebateParameters`)
```python
KEN_APPROVAL_THRESHOLD = 0.85  # Balanced: 0.75-0.85 healthy, 0.90+ too demanding, 0.70- too soft
DISCUSSION_COMPLETENESS_THRESHOLD = 0.5  # When to boost confidence toward conclusion
DISCUSSION_COMPLETENESS_BOOST = 0.12     # How much to boost (gentle nudge)
MAX_ROUNDS_BEFORE_CONCLUSION_PUSH = 25   # Prevent endless debates
TOPIC_DRIFT_THRESHOLD = 2                # Tolerance for tangential discussion
```

#### 2. Temperature Control (`MaturityParameters`)
Dynamic LLM temperature based on conversation maturity:

**Barbie (Generator)**: More creative, starts high and reduces
- Exploration: 1.2 temp, 0.95 top_p (very creative)
- Refinement: 0.9 temp, 0.85 top_p (focused development)  
- Convergence: 0.6 temp, 0.7 top_p (structured arguments)
- Consensus: 0.3 temp, 0.5 top_p (final confirmation)

**Ken (Evaluator)**: More focused, consistently lower than Barbie
- Exploration: 1.0 temp, 0.9 top_p (focused evaluation)
- Refinement: 0.7 temp, 0.8 top_p (targeted criticism)
- Convergence: 0.3 temp, 0.6 top_p (precise evaluation)
- Consensus: 0.1 temp, 0.4 top_p (final approval)

#### 3. Conversation Stage Transitions
- **Exploration → Refinement**: 0.25 (broad questions → focused discussion)
- **Refinement → Convergence**: 0.50 (focused discussion → argument building)
- **Convergence → Consensus**: 0.75 (argument building → final agreement)

### Agent Integration

#### Updated Ken (`ken.py`)
```python
# Import centralized parameters
from src.config.tune import get_ken_approval_threshold, get_temperature_for_stage

# Use centralized threshold
self.approval_threshold = get_ken_approval_threshold()

# Use centralized temperature control
def adjust_llm_parameters(self, state: EvaluationState) -> EvaluationState:
    state.llm_temperature, state.llm_top_p = get_temperature_for_stage("ken", state.maturity_stage)
    return state
```

#### Updated Barbie (`barbie.py`)
```python
# Import centralized parameters  
from src.config.tune import get_temperature_for_stage

# Use centralized temperature control
def adjust_llm_parameters(self, state: ConversationState) -> ConversationState:
    state.llm_temperature, state.llm_top_p = get_temperature_for_stage("barbie", state.maturity_stage)
    return state
```

## Balanced Configuration Analysis

### Ken's Approval Threshold: **0.85**
- **Previous 0.99**: Endless debates (82 rounds)
- **Previous 0.95**: Too agreeable (2-3 rounds) 
- **Current 0.85**: **Balanced** - healthy skepticism with reasonable convergence

### Expected Debate Dynamics
Based on the 0.85 threshold:
1. **Rounds 1-5**: Exploration phase - Ken asks broad questions, challenges assumptions
2. **Rounds 6-12**: Refinement phase - Ken focuses on specific evidence, requests clarification
3. **Rounds 13-18**: Convergence phase - Ken evaluates final arguments, builds toward consensus
4. **Rounds 19-25**: Consensus phase - Ken approves when sufficiently convinced

**Target**: **10-20 round conversations** with natural conclusion when evidence is solid

## Parameter Categories Covered

### 🎯 **Core Behavior**
- Approval thresholds, discussion completeness detection, conclusion logic

### 🌡️ **Temperature Control** 
- Dynamic LLM settings based on conversation maturity

### 🔍 **Quality Control**
- Repetition detection, evidence validation, topic coherence monitoring

### 🎭 **Personality**
- Agent-specific traits, communication styles, collaboration focus

### 🔬 **Research & Sources**
- Fact-checking behavior, source acceptance criteria, research query generation

## Testing Results

✅ **All tests pass** with current configuration:
- Ken threshold 0.85 is in healthy range (0.75-0.90)
- Temperature settings follow expected patterns
- Maturity thresholds properly ordered
- Parameter validation successful
- Debate balance analysis shows good configuration

## Usage

### Adjusting Parameters
Simply modify values in `src/config/tune.py`:

```python
# Make Ken more demanding (longer debates)
KEN_APPROVAL_THRESHOLD = 0.88

# Make Ken more agreeable (shorter debates) 
KEN_APPROVAL_THRESHOLD = 0.82

# Increase Barbie's creativity
BARBIE_EXPLORATION_TEMP = 1.4

# Make Ken more focused
KEN_EXPLORATION_TEMP = 0.8
```

### Parameter Guidelines

**For Longer, More Thorough Debates:**
- Increase `KEN_APPROVAL_THRESHOLD` (0.85 → 0.88)
- Increase `MAX_ROUNDS_BEFORE_CONCLUSION_PUSH` (25 → 30)
- Decrease `DISCUSSION_COMPLETENESS_BOOST` (0.12 → 0.08)

**For Quicker Convergence:**
- Decrease `KEN_APPROVAL_THRESHOLD` (0.85 → 0.82) 
- Increase `DISCUSSION_COMPLETENESS_BOOST` (0.12 → 0.15)
- Lower `MAX_ROUNDS_BEFORE_CONCLUSION_PUSH` (25 → 20)

**For More Creative Discussions:**
- Increase both agents' exploration temperatures
- Raise `BARBIE_EXPLORATION_TEMP` (1.2 → 1.4)
- Raise `KEN_EXPLORATION_TEMP` (1.0 → 1.1)

## Impact

### 🎯 **Achieved**
- **Centralized control** over all agent behavior parameters
- **Balanced debate dynamics** - neither too soft nor too demanding
- **Fine-grained control** over conversation flow and quality
- **Easy experimentation** - change one file to adjust all behavior
- **Comprehensive documentation** for each parameter's purpose and effect

### 🔮 **Expected Results**
- **10-20 round conversations** (vs 2-3 too short or 82 too long)
- **Healthy intellectual discourse** with appropriate challenge
- **Natural convergence** when sufficient evidence is presented
- **Quality discussions** that cover topics thoroughly without endless loops
- **Consistent behavior** across different conversation topics

The tuning system provides the foundation for fine-tuned, balanced AI agent interactions that can be easily adjusted for different use cases and requirements.