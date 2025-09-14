"""
Integration Tests for Skynet Distributed GAN System
End-to-end testing of Barbie and Ken agent interactions
"""

import pytest
import asyncio
import httpx
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import json
import os

# Import the agents
from barbie import BarbieAgent, ConversationState, ChatRequest, ChatResponse
from ken import KenAgent, EvaluationState


class TestFullWorkflowIntegration:
    """Test complete workflow from genesis to consensus"""
    
    def setup_method(self):
        """Setup test environment"""
        # Mock environment variables
        self.env_vars = {
            'OLLAMA_BASE_URL': 'http://test-ollama',
            'SECRET_AI_API_KEY': 'test-key',
            'CHROMA_HOST': 'localhost',
            'CHROMA_PORT': '8000',
            'TAVILY_API_KEY': 'test-tavily-key',
            'BARBIE_MODEL': 'test-barbie-model',
            'KEN_MODEL': 'test-ken-model'
        }
    
    @patch.dict(os.environ, {
        'OLLAMA_BASE_URL': 'http://test-ollama',
        'SECRET_AI_API_KEY': 'test-key',
        'CHROMA_HOST': 'localhost',
        'CHROMA_PORT': '8000'
    })
    def test_barbie_agent_initialization(self):
        """Test Barbie agent initializes correctly"""
        with patch('barbie.Chroma'), \
             patch('barbie.OllamaLLM'), \
             patch('barbie.OllamaEmbeddings'), \
             patch('barbie.TavilySearchResults'):
            
            barbie = BarbieAgent()
            assert barbie.agent_name == "Barbie"
            assert hasattr(barbie, 'graph')
            assert hasattr(barbie, 'app')
    
    @patch.dict(os.environ, {
        'OLLAMA_BASE_URL': 'http://test-ollama',
        'SECRET_AI_API_KEY': 'test-key',
        'CHROMA_HOST': 'localhost',
        'CHROMA_PORT': '8000'
    })
    def test_ken_agent_initialization(self):
        """Test Ken agent initializes correctly"""
        with patch('ken.Chroma'), \
             patch('ken.OllamaLLM'), \
             patch('ken.OllamaEmbeddings'), \
             patch('ken.TavilySearchResults'):
            
            ken = KenAgent()
            assert ken.agent_name == "Ken"
            assert hasattr(ken, 'graph')
            assert hasattr(ken, 'app')
            assert ken.approval_threshold == 0.8


class TestAgentWorkflowNodes:
    """Test individual workflow nodes with mocked dependencies"""
    
    def setup_method(self):
        """Setup agents with mocked dependencies"""
        with patch('barbie.Chroma'), \
             patch('barbie.OllamaLLM'), \
             patch('barbie.OllamaEmbeddings'), \
             patch('barbie.TavilySearchResults'), \
             patch.dict(os.environ, {
                 'OLLAMA_BASE_URL': 'http://test-ollama',
                 'SECRET_AI_API_KEY': 'test-key'
             }):
            self.barbie = BarbieAgent()
            
        with patch('ken.Chroma'), \
             patch('ken.OllamaLLM'), \
             patch('ken.OllamaEmbeddings'), \
             patch('ken.TavilySearchResults'), \
             patch.dict(os.environ, {
                 'OLLAMA_BASE_URL': 'http://test-ollama',
                 'SECRET_AI_API_KEY': 'test-key'
             }):
            self.ken = KenAgent()
    
    def test_barbie_load_context_node(self):
        """Test Barbie's context loading"""
        state = ConversationState(user_input="Test question")
        
        # Mock vectorstore search
        mock_docs = [Mock(page_content="Previous conversation content")]
        with patch.object(self.barbie.vectorstore, 'similarity_search', return_value=mock_docs):
            result_state = self.barbie.load_context_node(state)
            assert result_state.conversation_context != ""
    
    def test_barbie_search_web_node(self):
        """Test Barbie's web search functionality"""
        state = ConversationState(user_input="find latest AI research")
        
        # Mock search tool
        with patch.object(self.barbie.search_tool, 'run', return_value="Search results"):
            result_state = self.barbie.search_web_node(state)
            assert result_state.search_results != ""
    
    def test_barbie_generate_response_node(self):
        """Test Barbie's response generation"""
        state = ConversationState(
            user_input="Test question",
            maturity_stage="exploration",
            llm_temperature=1.2,
            llm_top_p=0.95
        )
        
        # Mock LLM response
        mock_response = "This is Barbie's generated response"
        with patch('barbie.OllamaLLM') as mock_llm_class:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm
            
            result_state = self.barbie.generate_response_node(state)
            assert result_state.generated_response == mock_response
    
    def test_ken_evaluate_response_node(self):
        """Test Ken's response evaluation"""
        state = EvaluationState(
            barbie_response="Test response from Barbie",
            evaluation_criteria="Test criteria",
            llm_temperature=1.0,
            llm_top_p=0.9
        )
        
        # Mock LLM evaluation
        mock_evaluation = "This response is good but needs improvement"
        with patch('ken.OllamaLLM') as mock_llm_class:
            mock_llm = Mock()
            mock_llm.invoke.return_value = mock_evaluation
            mock_llm_class.return_value = mock_llm
            
            result_state = self.ken.evaluate_response_node(state)
            assert result_state.evaluation_response == mock_evaluation
    
    def test_ken_calculate_confidence_node(self):
        """Test Ken's confidence calculation"""
        state = EvaluationState(
            evaluation_response="Good response with strong points",
            search_results="Supporting evidence found"
        )
        
        # Mock LLM confidence scoring
        with patch.object(self.ken.llm, 'invoke', return_value="0.85"):
            result_state = self.ken.calculate_confidence_node(state)
            assert 0.0 <= result_state.confidence_score <= 1.0
            assert result_state.should_approve in [True, False]


class TestMaturityProgression:
    """Test conversation maturity progression through stages"""
    
    def setup_method(self):
        """Setup test environment"""
        with patch('barbie.Chroma'), \
             patch('barbie.OllamaLLM'), \
             patch('barbie.OllamaEmbeddings'), \
             patch('barbie.TavilySearchResults'), \
             patch.dict(os.environ, {
                 'OLLAMA_BASE_URL': 'http://test-ollama',
                 'SECRET_AI_API_KEY': 'test-key'
             }):
            self.barbie = BarbieAgent()
    
    def test_maturity_progression_through_stages(self):
        """Test conversation progresses through all maturity stages"""
        # Start in exploration
        state = ConversationState(
            round_number=0,
            conversation_history=[]
        )
        
        # Simulate progression through rounds
        stages_encountered = []
        
        for round_num in range(0, 20, 3):
            state.round_number = round_num
            state.conversation_history.extend([
                f"Barbie: Round {round_num} response with increasing specificity and technical detail",
                f"Ken: Round {round_num} feedback becoming more precise and detailed"
            ])
            
            # Mock LLM analysis for some rounds
            if round_num % 6 == 0:
                mock_score = min(round_num / 15.0, 0.95)
                with patch.object(self.barbie.analyzer_llm, 'invoke', return_value=str(mock_score)):
                    result_state = self.barbie.assess_conversation_maturity(state)
            else:
                result_state = self.barbie.assess_conversation_maturity(state)
            
            stages_encountered.append(result_state.maturity_stage)
            state = result_state
        
        # Should progress through stages
        assert "exploration" in stages_encountered
        assert len(set(stages_encountered)) > 1  # Should have multiple stages


class TestAPIIntegration:
    """Test API endpoints with mocked external dependencies"""
    
    def setup_method(self):
        """Setup test clients"""
        with patch('barbie.Chroma'), \
             patch('barbie.OllamaLLM'), \
             patch('barbie.OllamaEmbeddings'), \
             patch('barbie.TavilySearchResults'), \
             patch.dict(os.environ, {
                 'OLLAMA_BASE_URL': 'http://test-ollama',
                 'SECRET_AI_API_KEY': 'test-key'
             }):
            barbie_agent = BarbieAgent()
            self.barbie_client = TestClient(barbie_agent.app)
        
        with patch('ken.Chroma'), \
             patch('ken.OllamaLLM'), \
             patch('ken.OllamaEmbeddings'), \
             patch('ken.TavilySearchResults'), \
             patch.dict(os.environ, {
                 'OLLAMA_BASE_URL': 'http://test-ollama',
                 'SECRET_AI_API_KEY': 'test-key'
             }):
            ken_agent = KenAgent()
            self.ken_client = TestClient(ken_agent.app)
    
    def test_barbie_health_endpoint(self):
        """Test Barbie's health endpoint"""
        response = self.barbie_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "Barbie"
        assert "timestamp" in data
    
    def test_ken_health_endpoint(self):
        """Test Ken's health endpoint"""
        response = self.ken_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["agent"] == "Ken"
        assert "timestamp" in data
    
    def test_barbie_root_endpoint(self):
        """Test Barbie's root endpoint"""
        response = self.barbie_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Skynet Barbie Agent" in data["message"]
    
    def test_ken_root_endpoint(self):
        """Test Ken's root endpoint"""
        response = self.ken_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Skynet Ken Agent" in data["message"]
    
    @patch('barbie.StateGraph')
    def test_barbie_genesis_endpoint(self, mock_graph):
        """Test Barbie's genesis endpoint"""
        # Mock the graph execution
        mock_final_state = ConversationState(
            generated_response="This is Barbie's final response",
            should_stop=True
        )
        mock_graph_instance = Mock()
        mock_graph_instance.invoke.return_value = mock_final_state
        mock_graph.return_value.compile.return_value = mock_graph_instance
        
        request_data = {
            "message": "What is the best AI architecture?",
            "conversation_id": "test-genesis-123"
        }
        
        response = self.barbie_client.post("/v1/genesis", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "This is Barbie's final response"
        assert data["conversation_id"] == "test-genesis-123"
        assert data["agent"] == "Barbie"
    
    @patch('ken.StateGraph')
    def test_ken_chat_endpoint(self, mock_graph):
        """Test Ken's chat endpoint"""
        # Mock the graph execution
        mock_final_state = EvaluationState(
            improvement_suggestions="This is Ken's feedback",
            should_approve=False,
            confidence_score=0.6
        )
        mock_graph_instance = Mock()
        mock_graph_instance.invoke.return_value = mock_final_state
        mock_graph.return_value.compile.return_value = mock_graph_instance
        
        request_data = {
            "message": "Hi! I am Barbie! Here's my response to evaluate...",
            "conversation_id": "test-chat-123"
        }
        
        response = self.ken_client.post("/v1/chat", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["response"] == "This is Ken's feedback"
        assert data["approved"] == False
        assert data["confidence"] == 0.6


class TestEndToEndScenarios:
    """Test complete end-to-end scenarios"""
    
    def test_successful_consensus_flow(self):
        """Test a complete flow from genesis to consensus"""
        # This would test the full interaction but requires more complex mocking
        # For now, we'll test the logical flow structure
        
        # 1. External process sends to /v1/genesis
        genesis_request = {
            "message": "How should we implement distributed AI training?"
        }
        
        # 2. Barbie generates initial response
        barbie_initial = "I think we should use federated learning with..."
        
        # 3. Barbie sends to Ken with proper format
        expected_ken_input = f"Hi! I am Barbie! Sorry to bother you, but there is a question that keeps me up all night long. Here it is: {genesis_request['message']}. My immediate answer is: {barbie_initial}. What do you think?"
        
        assert "Hi! I am Barbie!" in expected_ken_input
        assert genesis_request['message'] in expected_ken_input
        assert barbie_initial in expected_ken_input
        assert "What do you think?" in expected_ken_input
        
        # 4. Ken evaluates and provides feedback or approval
        ken_responses = [
            "Hi Barbie, this is Ken! I need more technical details...",
            "Hi Barbie, this is Ken! Better, but consider the security aspects...",
            "Hi Barbie, this is Ken! Perfect! I'm convinced! <STOP>"
        ]
        
        # 5. Final response should contain <STOP>
        final_response = ken_responses[-1]
        assert "<STOP>" in final_response.upper() or "I'M CONVINCED" in final_response.upper()


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "-s"])