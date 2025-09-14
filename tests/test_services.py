#!/usr/bin/env python3
"""
Service Testing Script for Skynet
Checks and tests all external service dependencies
"""

import subprocess
import sys
import os
import time
import requests
from pathlib import Path

# Load environment variables from .env file
import env

def check_service_status():
    """Check status of all required services"""
    print("🔍 Checking Service Status")
    print("=" * 40)
    
    services = {}
    
    # Check Ollama
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        api_key = os.getenv("SECRET_AI_API_KEY")
        
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        response = requests.get(f"{ollama_url}/api/tags", headers=headers, timeout=10)
        services["ollama"] = response.status_code == 200
        
        if services["ollama"]:
            models = response.json().get('models', [])
            print(f"📡 Ollama: ✅ Running ({len(models)} models available)")
            
            # Check required models
            model_names = [m['name'] for m in models]
            required_models = [
                os.getenv("BARBIE_MODEL", "llama3.3:70b"),
                os.getenv("KEN_MODEL", "qwen3:32b"),
                "qwen2.5:3b",
                "nomic-embed-text"
            ]
            
            for model in required_models:
                status = "✅" if model in model_names else "❌"
                print(f"    {model}: {status}")
        else:
            print("📡 Ollama: ❌ Not responding")
            
    except Exception as e:
        services["ollama"] = False
        print(f"📡 Ollama: ❌ Error - {e}")
    
    # Check ChromaDB
    try:
        chroma_host = os.getenv("CHROMA_HOST", "localhost")
        chroma_port = os.getenv("CHROMA_PORT", "8000")
        
        # For local testing, try localhost if chromadb host fails
        chroma_urls = [f"http://{chroma_host}:{chroma_port}"]
        if chroma_host == "chromadb":
            chroma_urls.append(f"http://localhost:{chroma_port}")
        
        chroma_connected = False
        for url in chroma_urls:
            try:
                response = requests.get(f"{url}/api/v1/heartbeat", timeout=5)
                if response.status_code == 500:  # Try v2 API
                    response = requests.get(f"{url}/api/v2/heartbeat", timeout=5)
                if response.status_code == 200:
                    chroma_connected = True
                    print(f"🗄️  ChromaDB: ✅ Running (connected to {url})")
                    break
            except Exception as e:
                print(f"    Failed to connect to {url}: {e}")
                continue
        
        if not chroma_connected:
            response = requests.get(f"http://{chroma_host}:{chroma_port}/api/v1/heartbeat", timeout=5)
        services["chromadb"] = response.status_code == 200
        
        if services["chromadb"]:
            print("🗄️  ChromaDB: ✅ Running")
            # Get version if available
            try:
                version_response = requests.get(f"http://{chroma_host}:{chroma_port}/api/v1/version", timeout=3)
                if version_response.status_code == 200:
                    version = version_response.json()
                    print(f"    Version: {version}")
            except:
                pass
        else:
            print("🗄️  ChromaDB: ❌ Not responding")
            
    except Exception as e:
        services["chromadb"] = False
        print(f"🗄️  ChromaDB: ❌ Error - {e}")
    
    # Check Tavily API
    try:
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key and tavily_key != "":
            from langchain_community.tools.tavily_search import TavilySearchResults
            search_tool = TavilySearchResults(api_key=tavily_key, max_results=1)
            result = search_tool.run("test connectivity")
            services["tavily"] = result is not None
            print("🔍 Tavily API: ✅ Connected")
        else:
            services["tavily"] = False
            print("🔍 Tavily API: ❌ No API key set")
            
    except Exception as e:
        services["tavily"] = False
        print(f"🔍 Tavily API: ❌ Error - {e}")
    
    return services

def start_chromadb():
    """Start ChromaDB using docker-compose"""
    print("\n🚀 Starting ChromaDB...")
    
    try:
        # Check if docker-compose.yml exists
        if not Path("docker-compose.yml").exists():
            print("❌ docker-compose.yml not found")
            return False
        
        # Start ChromaDB service
        result = subprocess.run([
            "docker-compose", "up", "-d", "chromadb"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ChromaDB started successfully")
            
            # Wait for service to be ready
            print("⏳ Waiting for ChromaDB to be ready...")
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get("http://localhost:8000/api/v1/heartbeat", timeout=2)
                    if response.status_code == 200:
                        print("✅ ChromaDB is ready!")
                        return True
                except:
                    time.sleep(1)
                    
            print("⚠️  ChromaDB started but not responding to heartbeat")
            return False
        else:
            print(f"❌ Failed to start ChromaDB: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting ChromaDB: {e}")
        return False

def run_service_tests():
    """Run the comprehensive service tests"""
    print("\n🧪 Running Service Integration Tests")
    print("=" * 40)
    
    # Change to the skynet directory
    skynet_dir = Path(__file__).parent
    os.chdir(skynet_dir)
    
    try:
        # Run the real service tests
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_real_services.py", 
            "-v", 
            "-s",
            "--tb=short"
        ], capture_output=False, text=True)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running service tests: {e}")
        return False

def run_quick_connectivity_test():
    """Run a quick connectivity test for all services"""
    print("\n⚡ Quick Connectivity Test")
    print("=" * 30)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_real_services.py::TestServiceConnectivity", 
            "-v", 
            "-s"
        ], capture_output=False)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running connectivity test: {e}")
        return False

def show_service_help():
    """Show help for starting services"""
    print("\n📖 Service Setup Help")
    print("=" * 25)
    print("\n🔧 To start required services:")
    print("1. ChromaDB:")
    print("   docker-compose up -d chromadb")
    print("\n2. Ollama (if not running):")
    print("   # Install from https://ollama.ai")
    print("   ollama serve")
    print("   # Pull required models:")
    print("   ollama pull llama3.3:70b")
    print("   ollama pull qwen3:32b") 
    print("   ollama pull qwen2.5:3b")
    print("   ollama pull nomic-embed-text")
    print("\n3. Environment variables:")
    print("   Check your .env file has:")
    print("   - OLLAMA_BASE_URL")
    print("   - SECRET_AI_API_KEY")
    print("   - TAVILY_API_KEY")
    print("   - CHROMA_HOST/CHROMA_PORT")

def main():
    """Main service testing workflow"""
    print("🤖 Skynet Service Testing")
    print("=" * 30)
    
    # Check current service status
    services = check_service_status()
    
    # Count healthy services
    healthy_services = sum(services.values())
    total_services = len(services)
    
    print(f"\n📊 Service Health: {healthy_services}/{total_services} services healthy")
    
    if healthy_services == total_services:
        print("🎉 All services are healthy!")
        
        # Ask if user wants to run full tests
        print("\nWould you like to run comprehensive service tests? [y/N]: ", end="")
        if input().lower().startswith('y'):
            success = run_service_tests()
            if success:
                print("\n✅ All service tests passed!")
            else:
                print("\n❌ Some service tests failed")
        else:
            print("✅ Service health check complete")
            
    else:
        print("\n⚠️  Some services need attention")
        
        # Offer to start ChromaDB if it's down
        if not services.get("chromadb", False):
            print("\nWould you like to start ChromaDB? [y/N]: ", end="")
            if input().lower().startswith('y'):
                start_chromadb()
        
        # Offer to run quick connectivity test
        print("\nWould you like to run a quick connectivity test? [y/N]: ", end="")
        if input().lower().startswith('y'):
            run_quick_connectivity_test()
        
        # Show help for fixing issues
        show_service_help()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            check_service_status()
        elif command == "start-chroma":
            start_chromadb()
        elif command == "test":
            run_service_tests()
        elif command == "quick":
            run_quick_connectivity_test()
        elif command == "help":
            show_service_help()
        else:
            print("Usage: python test_services.py [status|start-chroma|test|quick|help]")
    else:
        main()