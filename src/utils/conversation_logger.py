"""
Conversation Logging System
Handles creating timestamped conversation files with proper formatting
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class ConversationLogger:
    """Handles logging conversations between Barbie and Ken"""
    
    def __init__(self, log_directory: str = "data/conversation"):
        """
        Initialize the conversation logger
        
        Args:
            log_directory: Directory to store conversation logs
        """
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(parents=True, exist_ok=True)
        self.current_conversation_file = None
        self.conversation_started = False
    
    def start_conversation(self, original_question: str) -> str:
        """
        Start a new conversation with a timestamped file
        
        Args:
            original_question: The original question that started the conversation
            
        Returns:
            Path to the created conversation file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.md"
        self.current_conversation_file = self.log_directory / filename
        
        # Create the file with the original question header
        with open(self.current_conversation_file, 'w', encoding='utf-8') as f:
            f.write(f"# Conversation Log\n\n")
            f.write(f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Original Question:** {original_question}\n\n")
            f.write("---\n\n")
        
        self.conversation_started = True
        return str(self.current_conversation_file)
    
    def log_barbie_message(self, message: str) -> None:
        """
        Log a message from Barbie
        
        Args:
            message: Barbie's message content
        """
        if not self.conversation_started or not self.current_conversation_file:
            raise ValueError("Conversation not started. Call start_conversation() first.")
        
        with open(self.current_conversation_file, 'a', encoding='utf-8') as f:
            f.write(f"<Barbie>\n{message}\n</Barbie>\n\n--\n\n")
    
    def log_ken_message(self, message: str) -> None:
        """
        Log a message from Ken
        
        Args:
            message: Ken's message content
        """
        if not self.conversation_started or not self.current_conversation_file:
            raise ValueError("Conversation not started. Call start_conversation() first.")
        
        with open(self.current_conversation_file, 'a', encoding='utf-8') as f:
            f.write(f"<Ken>\n{message}\n</Ken>\n\n--\n\n")
    
    def end_conversation(self, summary: Optional[str] = None) -> None:
        """
        End the current conversation
        
        Args:
            summary: Optional conversation summary
        """
        if not self.conversation_started or not self.current_conversation_file:
            return
        
        with open(self.current_conversation_file, 'a', encoding='utf-8') as f:
            f.write("---\n\n")
            f.write(f"**Ended:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if summary:
                f.write(f"**Summary:** {summary}\n\n")
        
        self.conversation_started = False
        self.current_conversation_file = None
    
    def get_current_file_path(self) -> Optional[str]:
        """Get the path to the current conversation file"""
        return str(self.current_conversation_file) if self.current_conversation_file else None
    
    def list_conversation_files(self) -> list[str]:
        """List all conversation files in the log directory"""
        pattern = "conversation_*.md"
        return [str(f) for f in self.log_directory.glob(pattern)]
    
    def read_conversation(self, filename: str) -> str:
        """
        Read a conversation file
        
        Args:
            filename: Name of the conversation file
            
        Returns:
            Content of the conversation file
        """
        file_path = self.log_directory / filename
        if not file_path.exists():
            raise FileNotFoundError(f"Conversation file not found: {filename}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()


class BarbieConversationManager:
    """
    Enhanced conversation manager specifically for Barbie
    Integrates conversation logging with existing conversation flow
    """
    
    def __init__(self, log_directory: str = "data/conversation"):
        """
        Initialize Barbie's conversation manager
        
        Args:
            log_directory: Directory to store conversation logs
        """
        self.logger = ConversationLogger(log_directory)
        self.conversation_active = False
    
    def begin_debate(self, original_question: str) -> str:
        """
        Begin a new debate conversation
        
        Args:
            original_question: The question from /v1/genesis endpoint
            
        Returns:
            Path to the conversation log file
        """
        log_file = self.logger.start_conversation(original_question)
        self.conversation_active = True
        return log_file
    
    def send_to_ken(self, message: str) -> None:
        """
        Log Barbie's message when sending to Ken
        
        Args:
            message: Barbie's message content
        """
        if self.conversation_active:
            self.logger.log_barbie_message(message)
    
    def receive_from_ken(self, message: str) -> None:
        """
        Log Ken's message when received by Barbie
        
        Args:
            message: Ken's message content
        """
        if self.conversation_active:
            self.logger.log_ken_message(message)
    
    def conclude_debate(self, summary: Optional[str] = None) -> None:
        """
        Conclude the current debate
        
        Args:
            summary: Optional summary of the conversation
        """
        if self.conversation_active:
            self.logger.end_conversation(summary)
            self.conversation_active = False
    
    def get_conversation_history(self) -> list[str]:
        """Get list of all conversation files"""
        return self.logger.list_conversation_files()
    
    def get_current_conversation_path(self) -> Optional[str]:
        """Get path to current conversation file"""
        return self.logger.get_current_file_path()


# Example usage demonstration
if __name__ == "__main__":
    # Demo the conversation logging system
    print("=== Conversation Logging System Demo ===\n")
    
    # Initialize Barbie's conversation manager
    barbie_manager = BarbieConversationManager()
    
    # Start a conversation
    original_question = "Should we trust AI systems with critical decision-making in healthcare?"
    log_file = barbie_manager.begin_debate(original_question)
    print(f"Started conversation: {log_file}")
    
    # Simulate a conversation
    barbie_manager.send_to_ken(
        "What if we imagine AI in healthcare like a sophisticated diagnostic partner? "
        "Just as a second medical opinion strengthens diagnosis, AI could serve as an "
        "tireless analytical companion that never gets fatigued or overlooks patterns."
    )
    
    barbie_manager.receive_from_ken(
        "But this assumes AI systems are infallible pattern detectors. Let's examine "
        "the logical structure: if we trace the causal chain from data to diagnosis, "
        "where do systematic biases enter? How do we distinguish between correlation "
        "and causation in AI medical recommendations?"
    )
    
    barbie_manager.send_to_ken(
        "That's exactly why I love this analogy - it reveals the beautiful tension "
        "between pattern recognition and wisdom. AI might excel at seeing connections "
        "we miss, but human physicians bring contextual understanding and ethical "
        "judgment that transcends data patterns."
    )
    
    # End the conversation
    barbie_manager.conclude_debate(
        "Explored AI in healthcare through partnership vs replacement framework"
    )
    
    print(f"\nConversation logged to: {log_file}")
    print("\nConversation format example:")
    print("-" * 50)
    
    # Show the logged conversation
    with open(log_file, 'r') as f:
        content = f.read()
    print(content)
    
    print("=" * 60)
    print("Conversation Logging System Ready!")
    print("=" * 60)