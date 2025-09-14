# Thinking Tag Stripping Implementation

## Problem
When Barbie receives messages from Ken or Ken receives messages from Barbie, the messages may contain internal reasoning between `<think>` and `</think>` tags. These thinking sections should not be visible to the other agent to prevent:
- One agent being influenced by the other's reasoning process
- Confusion from seeing internal thoughts that weren't meant to be part of the conversation
- Potential biases from understanding the other agent's strategy

## Solution
Added functionality to strip thinking tags from received messages before processing them.

## Implementation Details

### 1. Added `strip_thinking_tags()` Method
Both Barbie and Ken now have a method to remove thinking content:

```python
def strip_thinking_tags(self, message: str) -> str:
    """Remove content between <think> and </think> tags from a message"""
    import re
    # Remove everything between <think> and </think> tags (including the tags)
    cleaned = re.sub(r'<think>.*?</think>', '', message, flags=re.DOTALL)
    # Clean up any extra whitespace that might be left
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    return cleaned.strip()
```

### 2. Applied in Message Reception

#### In Barbie (`barbie.py` line 326-344):
```python
def _process_chat_task(self, task):
    """Process a chat task (response from Ken) in the background"""
    try:
        ken_message = task['ken_message']
        conversation_id = task['conversation_id']
        
        # Strip thinking tags from Ken's message before processing
        ken_message = self.strip_thinking_tags(ken_message)
        
        logger.info(f"Processing chat from Ken: {conversation_id}")
        
        # Initialize state with Ken's feedback (thinking tags already stripped)
        state = ConversationState(
            user_input=ken_message,
            ken_feedback=ken_message,
            round_number=task.get('round_number', 1)
        )
```

#### In Ken (`ken.py` line 119-135):
```python
def _process_evaluation_task(self, task):
    """Process an evaluation task in the background"""
    try:
        barbie_message = task['barbie_message']
        conversation_id = task['conversation_id']
        round_number = task.get('round_number', 0)
        
        # Strip thinking tags from Barbie's message before processing
        barbie_message = self.strip_thinking_tags(barbie_message)
        
        logger.info(f"Ken processing evaluation: {conversation_id}, round {round_number}")
        
        # Initialize evaluation state (thinking tags already stripped)
        state = EvaluationState(
            barbie_response=barbie_message
        )
```

## Features
- **Complete removal**: All content between `<think>` and `</think>` tags is removed
- **Multi-line support**: Handles thinking blocks that span multiple lines
- **Multiple blocks**: Can handle multiple thinking sections in one message
- **Whitespace cleanup**: Removes excessive blank lines left after tag removal
- **Edge case handling**: Works with empty tags, special characters, and messages without tags

## Testing
Created comprehensive tests in `tests/test_thinking_tag_stripping.py` that verify:
- ✅ Barbie strips thinking tags from Ken's messages
- ✅ Ken strips thinking tags from Barbie's messages
- ✅ Multiple thinking blocks are handled correctly
- ✅ Edge cases (empty tags, special characters, no tags) work properly

## Example

### Before (Message with thinking tags):
```
Hi Barbie,

<think>
I need to be very critical here and find flaws in her argument.
Let me think about what questions to ask...
Maybe I should challenge her sources?
</think>

I appreciate your response, but I have some concerns about your sources.
Could you provide more evidence for your claims?

<think>
Actually, I'm not convinced at all. This seems weak.
I should demand more proof.
</think>

What specific studies support your hypothesis?
```

### After (Cleaned message):
```
Hi Barbie,

I appreciate your response, but I have some concerns about your sources.
Could you provide more evidence for your claims?

What specific studies support your hypothesis?
```

## Impact
- Agents only see the intended conversation content
- Internal reasoning processes remain private
- Prevents cross-contamination of thinking strategies
- Ensures cleaner, more focused dialogue between agents