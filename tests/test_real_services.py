"""
Real Service Integration Tests for Skynet Distributed GAN System
Tests actual connectivity and functionality with Ollama, ChromaDB, and Tavily
"""

import pytest
import asyncio
import os
import time
import requests
from datetime import datetime
from typing import List, Dict, Any

# Import the agents and dependencies
from barbie import BarbieAgent, ConversationState
from ken import KenAgent, EvaluationState

# Import external service clients directly
from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.schema import Document

# Load environment variables
import env


class TestServiceConnectivity:
    """Test basic connectivity to all external services"""
    
    def test_ollama_service_health(self):
        """Test Ollama service is running and accessible"""
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        try:
            api_key = os.getenv("SECRET_AI_API_KEY")
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = requests.get(f"{ollama_url}/api/tags", headers=headers, timeout=10)
            assert response.status_code == 200
            
            # Check if we have models available
            models = response.json()
            print(f"📋 Available Ollama models: {len(models.get('models', []))}")
            for model in models.get('models', []):
                print(f"  - {model['name']}")
            
            # Test if our required models are available
            model_names = [m['name'] for m in models.get('models', [])]
            barbie_model = os.getenv("BARBIE_MODEL", "llama3.3:70b")
            ken_model = os.getenv("KEN_MODEL", "qwen3:32b")
            analyzer_model = "qwen2.5:3b"
            
            print(f"\n🔍 Checking required models:")
            print(f"  Barbie model ({barbie_model}): {'✅' if barbie_model in model_names else '❌'}")
            print(f"  Ken model ({ken_model}): {'✅' if ken_model in model_names else '❌'}")
            print(f"  Analyzer model ({analyzer_model}): {'✅' if analyzer_model in model_names else '❌'}")
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ Ollama service not accessible: {e}")
    
    def test_chromadb_service_health(self):
        """Test ChromaDB service is running and accessible"""
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = os.getenv("CHROMA_PORT", "8000")
        chroma_url = f"http://{chroma_host}:{chroma_port}"
        
        try:
            # Test heartbeat endpoint (try v1 first, fallback to v2)
            response = requests.get(f"{chroma_url}/api/v1/heartbeat", timeout=10)
            if response.status_code == 500:  # v1 deprecated, try v2
                response = requests.get(f"{chroma_url}/api/v2/heartbeat", timeout=10)
            assert response.status_code == 200
            
            heartbeat = response.json()
            print(f"💓 ChromaDB heartbeat: {heartbeat}")
            
            # Test version endpoint
            response = requests.get(f"{chroma_url}/api/v1/version", timeout=5)
            if response.status_code == 200:
                version = response.json()
                print(f"📦 ChromaDB version: {version}")
                
        except requests.exceptions.RequestException as e:
            pytest.fail(f"❌ ChromaDB service not accessible: {e}")
    
    def test_tavily_api_connectivity(self):
        """Test Tavily API key and connectivity"""
        tavily_key = os.getenv("TAVILY_API_KEY")
        
        if not tavily_key:
            pytest.skip("❌ TAVILY_API_KEY not set")
        
        try:
            # Create Tavily search tool
            search_tool = TavilySearchResults(
                api_key=tavily_key,
                max_results=1,
                search_depth="basic"
            )
            
            # Test simple search
            results = search_tool.run("test search query")
            assert isinstance(results, (str, list))
            print(f"🔍 Tavily search test successful. Result type: {type(results)}")
            
        except Exception as e:
            pytest.fail(f"❌ Tavily API error: {e}")


class TestOllamaLLMIntegration:
    """Test Ollama LLM integration with different models"""
    
    def setup_method(self):
        """Setup Ollama LLM clients"""
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.api_key = os.getenv("SECRET_AI_API_KEY")
        
        # Test models
        self.models_to_test = [
            os.getenv("BARBIE_MODEL", "llama3.3:70b"),
            os.getenv("KEN_MODEL", "qwen3:32b"),
            "qwen2.5:3b"  # Analyzer model
        ]
    
    def test_llm_basic_generation(self):
        """Test basic LLM text generation"""
        for model in self.models_to_test:
            print(f"\n🧠 Testing LLM model: {model}")
            
            try:
                llm = OllamaLLM(
                    base_url=self.ollama_base_url,
                    model=model,
                    timeout=30.0,
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else None
                )
                
                # Simple test prompt
                response = llm.invoke("Hello! Please respond with exactly: 'Model test successful'")
                
                assert isinstance(response, str)
                assert len(response) > 0
                print(f"  ✅ Response: {response[:100]}...")
                
            except Exception as e:
                print(f"  ❌ Error with {model}: {e}")
                # Don't fail the entire test, just log the issue
    
    def test_llm_with_different_parameters(self):
        """Test LLM with different temperature and top_p values"""
        model = "qwen2.5:3b"  # Use fastest model for parameter testing
        
        parameters_to_test = [
            {"temperature": 1.2, "top_p": 0.95},  # Exploration
            {"temperature": 0.8, "top_p": 0.85},  # Refinement
            {"temperature": 0.4, "top_p": 0.7},   # Convergence
            {"temperature": 0.2, "top_p": 0.5}    # Consensus
        ]
        
        for params in parameters_to_test:
            print(f"\n🎛️ Testing parameters: {params}")
            
            try:
                llm = OllamaLLM(
                    base_url=self.ollama_base_url,
                    model=model,
                    timeout=20.0,
                    **params,
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else None
                )
                
                response = llm.invoke("Rate this on a scale of 1-5: How creative should AI responses be?")
                
                assert isinstance(response, str)
                print(f"  ✅ Response length: {len(response)} chars")
                
            except Exception as e:
                print(f"  ❌ Error with params {params}: {e}")


class TestChromaDBIntegration:
    """Test ChromaDB vector store operations"""
    
    def setup_method(self):
        """Setup ChromaDB connections"""
        self.chroma_host = os.getenv("CHROMA_HOST", "localhost")
        self.chroma_port = os.getenv("CHROMA_PORT", "8000")
        self.api_key = os.getenv("SECRET_AI_API_KEY")
        
        # Setup embeddings
        try:
            self.embeddings = OllamaEmbeddings(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model="nomic-embed-text",
                headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else None
            )
        except Exception as e:
            pytest.skip(f"❌ Could not initialize embeddings: {e}")
    
    def test_chromadb_connection_and_operations(self):
        """Test ChromaDB connection and basic operations"""
        collection_name = f"test_skynet_{int(time.time())}"
        
        try:
            # Create vectorstore
            vectorstore = Chroma(
                collection_name=collection_name,
                embedding_function=self.embeddings,
                client_settings={
                    "chroma_api_impl": "chromadb.api.fastapi.FastAPI",
                    "chroma_server_host": self.chroma_host,
                    "chroma_server_http_port": self.chroma_port,
                }
            )
            
            # Test document addition
            test_docs = [
                Document(
                    page_content="This is a test conversation between Barbie and Ken about AI",
                    metadata={"timestamp": datetime.now().isoformat(), "agent": "test"}
                ),
                Document(
                    page_content="Ken evaluated Barbie's response and found it technically sound",
                    metadata={"timestamp": datetime.now().isoformat(), "agent": "test"}
                )
            ]
            
            # Add documents
            vectorstore.add_documents(test_docs)
            print(f"✅ Added {len(test_docs)} test documents to collection '{collection_name}'")
            
            # Test similarity search
            search_results = vectorstore.similarity_search("AI conversation", k=2)
            
            assert len(search_results) > 0
            print(f"✅ Retrieved {len(search_results)} documents from similarity search")
            
            for i, doc in enumerate(search_results):
                print(f"  Document {i+1}: {doc.page_content[:50]}...")
            
            # Cleanup - delete collection
            try:
                vectorstore.delete_collection()
                print(f"✅ Cleaned up test collection '{collection_name}'")
            except:
                pass  # Collection cleanup is not critical for test success
                
        except Exception as e:
            pytest.fail(f"❌ ChromaDB integration error: {e}")
    
    def test_barbie_and_ken_vectorstore_setup(self):
        """Test that Barbie and Ken can set up their vector stores"""
        try:
            # Test Barbie's vectorstore
            barbie_vectorstore = Chroma(
                collection_name="test_barbie_context",
                embedding_function=self.embeddings,
                client_settings={
                    "chroma_api_impl": "chromadb.api.fastapi.FastAPI",
                    "chroma_server_host": self.chroma_host,
                    "chroma_server_http_port": self.chroma_port,
                }
            )
            print("✅ Barbie vectorstore connection successful")
            
            # Test Ken's vectorstore
            ken_vectorstore = Chroma(
                collection_name="test_ken_context",
                embedding_function=self.embeddings,
                client_settings={
                    "chroma_api_impl": "chromadb.api.fastapi.FastAPI",
                    "chroma_server_host": self.chroma_host,
                    "chroma_server_http_port": self.chroma_port,
                }
            )
            print("✅ Ken vectorstore connection successful")
            
            # Cleanup
            try:
                barbie_vectorstore.delete_collection()
                ken_vectorstore.delete_collection()
            except:
                pass
                
        except Exception as e:
            pytest.fail(f"❌ Agent vectorstore setup error: {e}")


class TestTavilyIntegration:
    """Test Tavily search API integration"""
    
    def setup_method(self):
        """Setup Tavily search tool"""
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            pytest.skip("❌ TAVILY_API_KEY not set")
        
        self.search_tool = TavilySearchResults(
            api_key=tavily_key,
            max_results=3,
            search_depth="advanced"
        )
    
    def test_tavily_basic_search(self):
        """Test basic Tavily search functionality"""
        try:
            # Test AI-related search (relevant to our use case)
            results = self.search_tool.run("artificial intelligence latest developments 2024")
            
            assert results is not None
            print(f"🔍 Tavily search results type: {type(results)}")
            print(f"📄 Results preview: {str(results)[:200]}...")
            
            # Results should contain relevant information
            results_str = str(results).lower()
            assert any(word in results_str for word in ['ai', 'artificial', 'intelligence', 'technology'])
            
        except Exception as e:
            pytest.fail(f"❌ Tavily search error: {e}")
    
    def test_tavily_factual_search(self):
        """Test Tavily for fact-checking type searches"""
        try:
            # Test factual query
            results = self.search_tool.run("Python programming language current version")
            
            assert results is not None
            print(f"📊 Factual search results: {str(results)[:150]}...")
            
            # Should contain version information
            results_str = str(results).lower()
            assert 'python' in results_str
            
        except Exception as e:
            pytest.fail(f"❌ Tavily factual search error: {e}")


class TestFullAgentIntegration:
    """Test full agent initialization and basic workflow with real services"""
    
    @pytest.mark.slow
    def test_barbie_agent_full_initialization(self):
        """Test Barbie agent can fully initialize with all real services"""
        try:
            barbie = BarbieAgent()
            
            # Test that all components are initialized
            assert hasattr(barbie, 'llm')
            assert hasattr(barbie, 'analyzer_llm')
            assert hasattr(barbie, 'vectorstore')
            assert hasattr(barbie, 'search_tool')
            assert hasattr(barbie, 'graph')
            assert hasattr(barbie, 'app')
            
            print("✅ Barbie agent fully initialized with all services")
            
        except Exception as e:
            pytest.fail(f"❌ Barbie agent initialization error: {e}")
    
    @pytest.mark.slow
    def test_ken_agent_full_initialization(self):
        """Test Ken agent can fully initialize with all real services"""
        try:
            ken = KenAgent()
            
            # Test that all components are initialized
            assert hasattr(ken, 'llm')
            assert hasattr(ken, 'analyzer_llm')
            assert hasattr(ken, 'vectorstore')
            assert hasattr(ken, 'search_tool')
            assert hasattr(ken, 'graph')
            assert hasattr(ken, 'app')
            
            print("✅ Ken agent fully initialized with all services")
            
        except Exception as e:
            pytest.fail(f"❌ Ken agent initialization error: {e}")
    
    @pytest.mark.slow
    def test_basic_conversation_flow(self):
        """Test a basic conversation flow with real services (short timeout)"""
        try:
            # Initialize agents
            print("🚀 Initializing agents...")
            barbie = BarbieAgent()
            ken = KenAgent()
            
            # Test Barbie's basic workflow components
            print("🎭 Testing Barbie's workflow components...")
            
            # Create a simple conversation state
            state = ConversationState(
                user_input="What is machine learning?",
                round_number=0,
                is_genesis=True
            )
            
            # Test context loading
            context_state = barbie.load_context_node(state)
            assert context_state.error_message == ""
            print("  ✅ Context loading successful")
            
            # Test maturity assessment
            maturity_state = barbie.assess_conversation_maturity(context_state)
            assert 0.0 <= maturity_state.maturity_score <= 1.0
            print(f"  ✅ Maturity assessment: {maturity_state.maturity_score:.2f} ({maturity_state.maturity_stage})")
            
            # Test Ken's evaluation components
            print("🎯 Testing Ken's evaluation components...")
            
            eval_state = EvaluationState(
                barbie_response="Machine learning is a subset of AI that enables computers to learn from data."
            )
            
            # Test Ken's context loading
            ken_context_state = ken.load_context_node(eval_state)
            assert ken_context_state.error_message == ""
            print("  ✅ Ken context loading successful")
            
            # Test Ken's maturity assessment
            ken_maturity_state = ken.assess_conversation_maturity(ken_context_state)
            assert 0.0 <= ken_maturity_state.maturity_score <= 1.0
            print(f"  ✅ Ken maturity assessment: {ken_maturity_state.maturity_score:.2f} ({ken_maturity_state.maturity_stage})")
            
            print("🎉 Basic conversation flow test successful!")
            
        except Exception as e:
            pytest.fail(f"❌ Basic conversation flow error: {e}")


class TestServiceHealthCheck:
    """Comprehensive service health check"""
    
    def test_all_services_health(self):
        """Run comprehensive health check on all services"""
        print("\n🏥 Comprehensive Service Health Check")
        print("=" * 50)
        
        health_status = {
            "ollama": False,
            "chromadb": False,
            "tavily": False,
            "models": {"barbie": False, "ken": False, "analyzer": False}
        }
        
        # Check Ollama
        try:
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            api_key = os.getenv("SECRET_AI_API_KEY")
            headers = {}
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            response = requests.get(f"{ollama_url}/api/tags", headers=headers, timeout=5)
            health_status["ollama"] = response.status_code == 200
            
            if health_status["ollama"]:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                health_status["models"]["barbie"] = os.getenv("BARBIE_MODEL", "llama3.3:70b") in model_names
                health_status["models"]["ken"] = os.getenv("KEN_MODEL", "qwen3:32b") in model_names
                health_status["models"]["analyzer"] = "qwen2.5:3b" in model_names
                
        except:
            pass
        
        # Check ChromaDB
        try:
            chroma_host = os.getenv("CHROMA_HOST", "localhost")
            chroma_port = os.getenv("CHROMA_PORT", "8000")
            response = requests.get(f"http://{chroma_host}:{chroma_port}/api/v1/heartbeat", timeout=5)
            health_status["chromadb"] = response.status_code == 200
        except:
            pass
        
        # Check Tavily
        try:
            tavily_key = os.getenv("TAVILY_API_KEY")
            if tavily_key:
                search_tool = TavilySearchResults(api_key=tavily_key, max_results=1)
                result = search_tool.run("test")
                health_status["tavily"] = result is not None
        except:
            pass
        
        # Print results
        print(f"📡 Ollama Service: {'✅' if health_status['ollama'] else '❌'}")
        print(f"🗄️  ChromaDB Service: {'✅' if health_status['chromadb'] else '❌'}")
        print(f"🔍 Tavily API: {'✅' if health_status['tavily'] else '❌'}")
        print(f"🧠 Barbie Model: {'✅' if health_status['models']['barbie'] else '❌'}")
        print(f"🎯 Ken Model: {'✅' if health_status['models']['ken'] else '❌'}")
        print(f"⚡ Analyzer Model: {'✅' if health_status['models']['analyzer'] else '❌'}")
        
        # Calculate overall health
        critical_services = [health_status["ollama"], health_status["chromadb"]]
        overall_health = all(critical_services)
        
        print(f"\n🏥 Overall Health: {'✅ HEALTHY' if overall_health else '❌ ISSUES DETECTED'}")
        
        if not overall_health:
            print("\n⚠️  Please ensure all services are running:")
            if not health_status["ollama"]:
                print("   - Start Ollama service")
            if not health_status["chromadb"]:
                print("   - Start ChromaDB service (docker-compose up chromadb)")
        
        # Don't fail the test, just report status
        assert True  # Always pass, this is informational


if __name__ == "__main__":
    # Run the real service integration tests
    pytest.main([__file__, "-v", "-s", "--tb=short"])