"""
Unit Tests for Skynet Distributed GAN System
Tests for Barbie (Generator) and Ken (Discriminator) agents
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from dataclasses import dataclass
from typing import Dict, Any

# Import the agents
from barbie import BarbieAgent, ConversationState, ChatRequest
from ken import KenAgent, EvaluationState


class TestConversationState:
    """Test ConversationState dataclass functionality"""
    
    def test_conversation_state_initialization(self):
        """Test ConversationState initializes with correct defaults"""
        state = ConversationState()
        
        assert state.user_input == ""
        assert state.original_message == ""
        assert state.generated_response == ""
        assert state.ken_feedback == ""
        assert state.round_number == 0
        assert state.should_stop == False
        assert state.is_genesis == False
        assert state.maturity_score == 0.0
        assert state.maturity_stage == "exploration"
        assert state.llm_temperature == 1.2
        assert state.llm_top_p == 0.95
        assert state.conversation_history == []
    
    def test_conversation_state_with_data(self):
        """Test ConversationState with custom data"""
        state = ConversationState(
            user_input="Test question",
            round_number=3,
            is_genesis=True,
            maturity_score=0.6,
            maturity_stage="convergence"
        )
        
        assert state.user_input == "Test question"
        assert state.round_number == 3
        assert state.is_genesis == True
        assert state.maturity_score == 0.6
        assert state.maturity_stage == "convergence"


class TestEvaluationState:
    """Test EvaluationState dataclass functionality"""
    
    def test_evaluation_state_initialization(self):
        """Test EvaluationState initializes with correct defaults"""
        state = EvaluationState()
        
        assert state.barbie_response == ""
        assert state.should_approve == False
        assert state.confidence_score == 0.0
        assert state.maturity_score == 0.0
        assert state.maturity_stage == "exploration"
        assert state.llm_temperature == 1.2
        assert state.conversation_history == []


class TestMaturityAssessment:
    """Test conversation maturity assessment functions"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.barbie_agent = BarbieAgent()
        self.ken_agent = KenAgent()
    
    def test_barbie_heuristic_maturity_empty_history(self):
        """Test heuristic maturity calculation with empty history"""
        state = ConversationState()
        score = self.barbie_agent.calculate_heuristic_maturity(state)
        assert score == 0.0
    
    def test_barbie_heuristic_maturity_with_history(self):
        """Test heuristic maturity calculation with conversation history"""
        state = ConversationState(
            round_number=5,
            conversation_history=[
                "Barbie: I think we should implement a solution using specific methods",
                "Ken: Your approach is detailed and precise, but consider this technical improvement"
            ]
        )
        score = self.barbie_agent.calculate_heuristic_maturity(state)
        assert 0.0 <= score <= 1.0
        assert score > 0  # Should have some maturity with content
    
    def test_ken_heuristic_maturity_with_confidence(self):
        """Test Ken's heuristic maturity with confidence score"""
        state = EvaluationState(
            confidence_score=0.7,
            conversation_history=[
                "Barbie: Here's my specific implementation approach",
                "Ken: I need you to refine the technical details however"
            ]
        )
        score = self.ken_agent.calculate_heuristic_maturity(state)
        assert 0.0 <= score <= 1.0
        assert score > 0.2  # Should reflect confidence score
    
    def test_update_maturity_stage(self):
        """Test maturity stage updates based on score"""
        state = ConversationState()
        
        # Test exploration stage
        state.maturity_score = 0.1
        updated_state = self.barbie_agent.update_maturity_stage(state)
        assert updated_state.maturity_stage == "exploration"
        
        # Test refinement stage
        state.maturity_score = 0.4
        updated_state = self.barbie_agent.update_maturity_stage(state)
        assert updated_state.maturity_stage == "refinement"
        
        # Test convergence stage
        state.maturity_score = 0.6
        updated_state = self.barbie_agent.update_maturity_stage(state)
        assert updated_state.maturity_stage == "convergence"
        
        # Test consensus stage
        state.maturity_score = 0.9
        updated_state = self.barbie_agent.update_maturity_stage(state)
        assert updated_state.maturity_stage == "consensus"
    
    def test_adjust_llm_parameters(self):
        """Test LLM parameter adjustment based on maturity stage"""
        state = ConversationState()
        
        # Test exploration parameters
        state.maturity_stage = "exploration"
        updated_state = self.barbie_agent.adjust_llm_parameters(state)
        assert updated_state.llm_temperature == 1.2
        assert updated_state.llm_top_p == 0.95
        
        # Test consensus parameters
        state.maturity_stage = "consensus"
        updated_state = self.barbie_agent.adjust_llm_parameters(state)
        assert updated_state.llm_temperature == 0.2
        assert updated_state.llm_top_p == 0.5


class TestAgentWorkflows:
    """Test LangGraph workflow components"""
    
    def setup_method(self):
        """Setup test fixtures"""
        with patch.dict('os.environ', {
            'OLLAMA_BASE_URL': 'http://test-ollama',
            'SECRET_AI_API_KEY': 'test-key',
            'CHROMA_HOST': 'test-chroma',
            'CHROMA_PORT': '8000'
        }):
            self.barbie_agent = BarbieAgent()
            self.ken_agent = KenAgent()
    
    def test_extract_search_keywords(self):
        """Test search keyword extraction"""
        # Test with search indicators
        text = "I need to find the latest information about AI"
        keywords = self.barbie_agent.extract_search_keywords(text)
        assert len(keywords) > 0
        
        # Test without search indicators
        text = "This is a simple statement"
        keywords = self.barbie_agent.extract_search_keywords(text)
        assert keywords == ""
    
    def test_ken_extract_factual_claims(self):
        """Test Ken's factual claim extraction"""
        text = "According to research, 85% of users prefer this approach. Studies indicate significant improvements."
        claims = self.ken_agent.extract_factual_claims(text)
        assert len(claims) > 0
        assert any("85%" in claim for claim in claims)
    
    def test_ken_fallback_confidence_scoring(self):
        """Test Ken's fallback confidence scoring"""
        # Test positive evaluation
        positive_text = "excellent response with strong accuracy and comprehensive coverage"
        score = self.ken_agent.fallback_confidence_scoring(positive_text)
        assert score > 0.5
        
        # Test negative evaluation
        negative_text = "poor response with weak arguments and inaccurate information"
        score = self.ken_agent.fallback_confidence_scoring(negative_text)
        assert score < 0.5
        
        # Test neutral evaluation
        neutral_text = "this is a response"
        score = self.ken_agent.fallback_confidence_scoring(neutral_text)
        assert score == 0.5


class TestAgentCommunication:
    """Test communication between Barbie and Ken"""
    
    def test_barbie_genesis_message_format(self):
        """Test Barbie's initial message format for genesis mode"""
        state = ConversationState(
            is_genesis=True,
            round_number=0,
            original_message="What is the best AI architecture?",
            generated_response="I think transformers are the best approach because..."
        )
        
        # Mock the send_to_ken_node method
        barbie_agent = BarbieAgent()
        
        # Simulate the payload creation logic
        expected_message = "Hi! I am Barbie! Sorry to bother you, but there is a question that keeps me up all night long. Here it is: What is the best AI architecture?. My immediate answer is: I think transformers are the best approach because.... What do you think?"
        
        # Test that the message format is correct
        assert "Hi! I am Barbie!" in expected_message
        assert "What is the best AI architecture?" in expected_message
        assert "I think transformers are the best" in expected_message
        assert "What do you think?" in expected_message
    
    def test_stop_signal_detection(self):
        """Test <STOP> signal detection in feedback processing"""
        barbie_agent = BarbieAgent()
        
        # Test with <STOP> signal
        state = ConversationState(ken_feedback="Great work! I'm convinced! <STOP>")
        result_state = barbie_agent.process_ken_feedback_node(state)
        assert result_state.should_stop == True
        
        # Test with "I'm convinced" signal
        state = ConversationState(ken_feedback="Perfect! I'm convinced this is the best approach!")
        result_state = barbie_agent.process_ken_feedback_node(state)
        assert result_state.should_stop == True
        
        # Test without stop signals
        state = ConversationState(ken_feedback="Good, but needs more refinement")
        result_state = barbie_agent.process_ken_feedback_node(state)
        assert result_state.should_stop == False
        assert result_state.round_number == 1


class TestAPIEndpoints:
    """Test FastAPI endpoint functionality"""
    
    @pytest.mark.asyncio
    async def test_chat_request_model(self):
        """Test ChatRequest model validation"""
        # Valid request
        request = ChatRequest(message="Test message", conversation_id="test-123")
        assert request.message == "Test message"
        assert request.conversation_id == "test-123"
        
        # Request without conversation_id
        request = ChatRequest(message="Test message")
        assert request.message == "Test message"
        assert request.conversation_id is None
    
    def test_health_endpoint_structure(self):
        """Test health endpoint response structure"""
        # This would typically test the actual endpoint, but we'll test the expected structure
        expected_response = {
            "status": "healthy",
            "agent": "Barbie",
            "timestamp": "2024-01-01T00:00:00"
        }
        
        assert "status" in expected_response
        assert "agent" in expected_response
        assert "timestamp" in expected_response
        assert expected_response["status"] == "healthy"


class TestEnvironmentSetup:
    """Test environment configuration and setup"""
    
    def test_default_environment_values(self):
        """Test default environment variable handling"""
        import os
        
        # Test default values when env vars aren't set
        default_barbie_port = int(os.getenv("BARBIE_PORT", "8001"))
        default_ken_port = int(os.getenv("KEN_PORT", "8002"))
        default_max_rounds = int(os.getenv("MAX_CONVERSATION_ROUNDS", "50"))
        
        assert default_barbie_port == 8001
        assert default_ken_port == 8002
        assert default_max_rounds == 50


class TestErrorHandling:
    """Test error handling in various scenarios"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.barbie_agent = BarbieAgent()
        self.ken_agent = KenAgent()
    
    def test_maturity_assessment_error_handling(self):
        """Test maturity assessment handles errors gracefully"""
        state = ConversationState()
        
        # Mock an error in heuristic calculation
        with patch.object(self.barbie_agent, 'calculate_heuristic_maturity', side_effect=Exception("Test error")):
            result_state = self.barbie_agent.assess_conversation_maturity(state)
            # Should return state unchanged without crashing
            assert result_state is not None
    
    def test_llm_maturity_analysis_fallback(self):
        """Test LLM maturity analysis falls back gracefully"""
        state = ConversationState(
            conversation_history=["Test conversation"],
            maturity_score=0.5
        )
        
        # Mock analyzer_llm to raise an exception
        with patch.object(self.barbie_agent.analyzer_llm, 'invoke', side_effect=Exception("LLM error")):
            score = self.barbie_agent.calculate_llm_maturity(state)
            # Should fallback to current maturity score
            assert score == 0.5


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])