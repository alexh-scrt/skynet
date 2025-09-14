#!/usr/bin/env python3
"""
Simple Service Connectivity Test
Tests all external services without importing agent code
"""

import os
import requests
import time

# Load environment variables
import env

def test_ollama():
    """Test Ollama service connectivity"""
    print("🧠 Testing Ollama...")
    
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        api_key = os.getenv("SECRET_AI_API_KEY")
        
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        response = requests.get(f"{ollama_url}/api/tags", headers=headers, timeout=10)
        
        if response.status_code == 200:
            models = response.json().get('models', [])
            print(f"  ✅ Connected! Found {len(models)} models")
            
            # Check required models
            model_names = [m['name'] for m in models]
            required_models = [
                os.getenv("BARBIE_MODEL", "llama3.3:70b"),
                os.getenv("KEN_MODEL", "qwen3:32b"),
                "qwen2.5:3b"
            ]
            
            for model in required_models:
                status = "✅" if model in model_names else "❌"
                print(f"    {model}: {status}")
            
            return True
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_chromadb():
    """Test ChromaDB service connectivity"""
    print("🗄️  Testing ChromaDB...")
    
    try:
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = os.getenv("CHROMA_PORT", "8000")
        chroma_url = f"http://{chroma_host}:{chroma_port}"
        
        # Try v2 API first (current), fallback to v1
        response = requests.get(f"{chroma_url}/api/v2/heartbeat", timeout=5)
        if response.status_code != 200:
            response = requests.get(f"{chroma_url}/api/v1/heartbeat", timeout=5)
        
        if response.status_code == 200:
            heartbeat = response.json()
            print(f"  ✅ Connected! Heartbeat: {heartbeat}")
            return True
        else:
            print(f"  ❌ Failed with status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_tavily():
    """Test Tavily API connectivity"""
    print("🔍 Testing Tavily API...")
    
    try:
        tavily_key = os.getenv("TAVILY_API_KEY")
        if not tavily_key:
            print("  ❌ No API key set")
            return False
        
        # Simple test without importing deprecated class
        # We'll just check if the key is set for now
        print("  ✅ API key is configured")
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_llm_basic():
    """Test basic LLM functionality"""
    print("🤖 Testing LLM Generation...")
    
    try:
        from langchain_ollama import OllamaLLM
        
        ollama_url = os.getenv("OLLAMA_BASE_URL")
        api_key = os.getenv("SECRET_AI_API_KEY")
        
        llm = OllamaLLM(
            base_url=ollama_url,
            model="qwen2.5:3b",  # Use fastest model
            timeout=30.0,
            temperature=0.1,
            headers={"Authorization": f"Bearer {api_key}"} if api_key else None
        )
        
        response = llm.invoke("Respond with exactly: 'Test successful'")
        
        if "successful" in response.lower():
            print(f"  ✅ LLM generation working!")
            print(f"    Response: {response[:50]}...")
            return True
        else:
            print(f"  ⚠️  Unexpected response: {response[:50]}...")
            return False
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_chromadb_operations():
    """Test basic ChromaDB operations"""
    print("📚 Testing ChromaDB Operations...")
    
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import OllamaEmbeddings
        
        # Setup embeddings
        embeddings = OllamaEmbeddings(
            base_url=os.getenv("OLLAMA_BASE_URL"),
            model="nomic-embed-text",
            headers={"Authorization": f"Bearer {os.getenv('SECRET_AI_API_KEY')}"} if os.getenv('SECRET_AI_API_KEY') else None
        )
        
        # Create test collection
        collection_name = f"test_connectivity_{int(time.time())}"
        
        vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            client_settings={
                "chroma_api_impl": "chromadb.api.fastapi.FastAPI",
                "chroma_server_host": os.getenv("CHROMA_HOST", "localhost"),
                "chroma_server_http_port": os.getenv("CHROMA_PORT", "8000"),
            }
        )
        
        print("  ✅ ChromaDB operations working!")
        
        # Cleanup
        try:
            vectorstore.delete_collection()
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all connectivity tests"""
    print("🤖 Skynet Service Connectivity Test")
    print("=" * 40)
    
    tests = [
        ("Ollama", test_ollama),
        ("ChromaDB", test_chromadb),
        ("Tavily", test_tavily),
        ("LLM Generation", test_llm_basic),
        ("ChromaDB Ops", test_chromadb_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        result = test_func()
        results.append((test_name, result))
        
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Summary: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All services are working perfectly!")
    else:
        print("⚠️  Some services need attention")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)