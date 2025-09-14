"""
Tests for conversation logging system
"""
import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path
import sys

# Add src to path
prj_root = Path(__file__).parent.parent
sys.path.insert(0, str(prj_root))

from src.utils.conversation_logger import ConversationLogger, BarbieConversationManager


class TestConversationLogger:
    
    def test_start_conversation(self):
        """Test starting a new conversation creates proper file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = ConversationLogger(temp_dir)
            
            original_question = "What is the meaning of consciousness?"
            log_file = logger.start_conversation(original_question)
            
            # Check file was created
            assert os.path.exists(log_file)
            assert "conversation_" in os.path.basename(log_file)
            assert log_file.endswith(".md")
            
            # Check content
            with open(log_file, 'r') as f:
                content = f.read()
            
            assert "# Conversation Log" in content
            assert original_question in content
            assert "Started:" in content
    
    def test_log_messages(self):
        """Test logging messages from both agents"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = ConversationLogger(temp_dir)
            
            # Start conversation
            logger.start_conversation("Test question")
            
            # Log messages
            barbie_msg = "This is Barbie's message"
            ken_msg = "This is Ken's response"
            
            logger.log_barbie_message(barbie_msg)
            logger.log_ken_message(ken_msg)
            
            # Check content
            with open(logger.current_conversation_file, 'r') as f:
                content = f.read()
            
            assert f"<Barbie>\n{barbie_msg}\n</Barbie>" in content
            assert f"<Ken>\n{ken_msg}\n</Ken>" in content
            assert "--" in content  # Separator
    
    def test_end_conversation(self):
        """Test ending conversation adds proper footer"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = ConversationLogger(temp_dir)
            
            logger.start_conversation("Test question")
            summary = "Great discussion about consciousness"
            logger.end_conversation(summary)
            
            with open(logger.current_conversation_file, 'r') as f:
                content = f.read()
            
            assert "Ended:" in content
            assert summary in content
            
            # Should reset state
            assert not logger.conversation_started
            assert logger.current_conversation_file is None
    
    def test_conversation_without_start_fails(self):
        """Test that logging without starting conversation raises error"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = ConversationLogger(temp_dir)
            
            with pytest.raises(ValueError, match="Conversation not started"):
                logger.log_barbie_message("Should fail")
            
            with pytest.raises(ValueError, match="Conversation not started"):
                logger.log_ken_message("Should also fail")
    
    def test_list_conversation_files(self):
        """Test listing conversation files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            logger = ConversationLogger(temp_dir)
            
            # Start two conversations
            logger.start_conversation("Question 1")
            logger.end_conversation()
            
            logger.start_conversation("Question 2")
            logger.end_conversation()
            
            files = logger.list_conversation_files()
            assert len(files) == 2
            assert all("conversation_" in f for f in files)
            assert all(f.endswith(".md") for f in files)


class TestBarbieConversationManager:
    
    def test_full_conversation_flow(self):
        """Test complete conversation flow through Barbie's manager"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = BarbieConversationManager(temp_dir)
            
            # Begin debate
            question = "Should AI have rights?"
            log_file = manager.begin_debate(question)
            
            assert manager.conversation_active
            assert os.path.exists(log_file)
            
            # Exchange messages
            manager.send_to_ken("What if AI consciousness is like...")
            manager.receive_from_ken("Let's examine the logical structure...")
            manager.send_to_ken("This connects to a deeper pattern...")
            
            # End debate
            manager.conclude_debate("Explored AI rights through consciousness framework")
            
            assert not manager.conversation_active
            
            # Verify logged conversation
            with open(log_file, 'r') as f:
                content = f.read()
            
            assert question in content
            assert "<Barbie>" in content
            assert "<Ken>" in content
            assert "consciousness framework" in content
    
    def test_get_conversation_history(self):
        """Test retrieving conversation history"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = BarbieConversationManager(temp_dir)
            
            # Create multiple conversations
            manager.begin_debate("Question 1")
            manager.send_to_ken("Message 1")
            manager.conclude_debate()
            
            manager.begin_debate("Question 2") 
            manager.send_to_ken("Message 2")
            manager.conclude_debate()
            
            history = manager.get_conversation_history()
            assert len(history) == 2
    
    def test_current_conversation_path(self):
        """Test getting current conversation path"""
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = BarbieConversationManager(temp_dir)
            
            # No active conversation
            assert manager.get_current_conversation_path() is None
            
            # Active conversation
            log_file = manager.begin_debate("Test question")
            current_path = manager.get_current_conversation_path()
            
            assert current_path == log_file
            assert os.path.exists(current_path)
            
            # After ending
            manager.conclude_debate()
            assert manager.get_current_conversation_path() is None


def test_conversation_format_demo():
    """Test the conversation format matches requirements"""
    with tempfile.TemporaryDirectory() as temp_dir:
        manager = BarbieConversationManager(temp_dir)
        
        # Create a sample conversation
        original_question = "Can AI systems exhibit true creativity?"
        log_file = manager.begin_debate(original_question)
        
        manager.send_to_ken(
            "What if we imagine creativity like jazz improvisation? AI might follow "
            "harmonic rules but still surprise us with novel combinations and unexpected "
            "beauty that emerges from constraint and freedom dancing together."
        )
        
        manager.receive_from_ken(
            "But this assumes creativity requires conscious intention. Let's examine "
            "the boundary conditions: if an AI generates novel artistic output through "
            "statistical patterns, how do we distinguish between mimicry and genuine "
            "creative expression? What would falsify the claim of AI creativity?"
        )
        
        manager.send_to_ken(
            "That's the beautiful paradox - maybe creativity isn't about intention but "
            "about the elegant emergence of meaning from complexity. When we humans "
            "create, aren't we also following patterns, just biological ones?"
        )
        
        manager.conclude_debate("Explored creativity through improvisation vs intention framework")
        
        # Verify format
        with open(log_file, 'r') as f:
            content = f.read()
        
        print("\n" + "="*60)
        print("SAMPLE CONVERSATION FORMAT:")
        print("="*60)
        print(content)
        print("="*60)
        
        # Check format requirements
        assert content.startswith("# Conversation Log")
        assert original_question in content
        assert "<Barbie>\n" in content and "\n</Barbie>" in content
        assert "<Ken>\n" in content and "\n</Ken>" in content
        assert "\n--\n" in content  # Separators
        assert "Started:" in content
        assert "Ended:" in content


if __name__ == "__main__":
    # Run demo test
    test_conversation_format_demo()
    print("\nConversation logging system working perfectly!")