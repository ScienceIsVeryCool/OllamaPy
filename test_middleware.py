#!/usr/bin/env python3
"""Comprehensive test suite for OllamaPy Ollama middleware."""

import json
import time
import requests
import threading
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from ollamapy.ollama_middleware import run_middleware_server


class MiddlewareTestSuite:
    """Test suite for OllamaPy Ollama middleware functionality."""
    
    def __init__(self):
        self.middleware_port = 11435
        self.ollama_port = 11434
        self.middleware_url = f"http://localhost:{self.middleware_port}"
        self.ollama_url = f"http://localhost:{self.ollama_port}"
        self.middleware_server = None
        self.test_model = "gemma3:4b"  # Small model for testing
    
    def check_ollama_available(self) -> bool:
        """Check if Ollama server is running."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def check_test_model_available(self) -> bool:
        """Check if test model is available in Ollama."""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = [model["name"] for model in data.get("models", [])]
                return any(self.test_model in model for model in models)
        except:
            pass
        return False
    
    def start_middleware_server(self) -> bool:
        """Start the middleware server in a separate thread."""
        try:
            print(f"🚀 Starting middleware server on port {self.middleware_port}...")
            
            def run_server():
                run_middleware_server(
                    port=self.middleware_port,
                    upstream_ollama=self.ollama_url,
                    enable_skills=True,
                    enable_analysis=True,
                    analysis_model=self.test_model
                )
            
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            
            # Wait for server to start up
            print("⏳ Waiting for middleware server to start...")
            for _ in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get(f"{self.middleware_url}/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ Middleware server is running!")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(1)
            
            print("❌ Failed to start middleware server")
            return False
            
        except Exception as e:
            print(f"❌ Error starting middleware server: {e}")
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test the health endpoint."""
        print("\n🔍 Testing health endpoint...")
        try:
            response = requests.get(f"{self.middleware_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check passed: {data.get('status')}")
                return True
            else:
                print(f"❌ Health check failed with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    def test_models_endpoint(self) -> bool:
        """Test the models listing endpoint."""
        print("\n🔍 Testing models endpoint...")
        try:
            response = requests.get(f"{self.middleware_url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                print(f"✅ Models endpoint works, found {len(models)} models")
                return True
            else:
                print(f"❌ Models endpoint failed with status: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Models endpoint error: {e}")
            return False
    
    def send_generate_request(self, url: str, model: str, prompt: str) -> Optional[Dict[str, Any]]:
        """Send a generation request to the specified URL."""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False
            }
            response = requests.post(f"{url}/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Request failed with status {response.status_code}: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Request error: {e}")
            return None
    
    def test_core_functionality(self) -> bool:
        """Test the core functionality as requested by the user."""
        print("\n🔍 Testing core functionality (middleware vs direct Ollama)...")
        
        test_prompt = "What is 2 + 2?"
        
        print(f"📝 Test prompt: '{test_prompt}'")
        print(f"🎯 Test model: {self.test_model}")
        
        # Send request to middleware
        print("\n1️⃣ Sending request to OllamaPy middleware...")
        middleware_result = self.send_generate_request(
            self.middleware_url, self.test_model, test_prompt
        )
        
        if not middleware_result:
            print("❌ Middleware request failed")
            return False
        
        print(f"✅ Middleware response received ({len(middleware_result.get('response', ''))} characters)")
        
        # Send request to direct Ollama
        print("\n2️⃣ Sending request to direct Ollama...")
        ollama_result = self.send_generate_request(
            self.ollama_url, self.test_model, test_prompt
        )
        
        if not ollama_result:
            print("❌ Direct Ollama request failed")
            return False
        
        print(f"✅ Direct Ollama response received ({len(ollama_result.get('response', ''))} characters)")
        
        # Compare results
        print("\n🔍 Comparing responses...")
        middleware_response = middleware_result.get("response", "").strip()
        ollama_response = ollama_result.get("response", "").strip()
        
        if middleware_response and ollama_response:
            print("✅ Both responses contain content")
            print(f"📊 Middleware response: {middleware_response[:100]}...")
            print(f"📊 Direct response: {ollama_response[:100]}...")
            return True
        else:
            print("❌ One or both responses are empty")
            return False
    
    def test_chat_endpoint(self) -> bool:
        """Test the chat endpoint."""
        print("\n🔍 Testing chat endpoint...")
        
        try:
            payload = {
                "model": self.test_model,
                "messages": [
                    {"role": "user", "content": "Hello, how are you?"}
                ],
                "stream": False
            }
            response = requests.post(f"{self.middleware_url}/api/chat", json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message", {}).get("content"):
                    print("✅ Chat endpoint works!")
                    return True
                else:
                    print("❌ Chat endpoint returned empty response")
                    return False
            else:
                print(f"❌ Chat endpoint failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Chat endpoint error: {e}")
            return False
    
    def test_streaming_responses(self) -> bool:
        """Test streaming response functionality."""
        print("\n🔍 Testing streaming responses...")
        
        try:
            payload = {
                "model": self.test_model,
                "prompt": "Count from 1 to 5",
                "stream": True
            }
            response = requests.post(
                f"{self.middleware_url}/api/generate", 
                json=payload, 
                stream=True, 
                timeout=30
            )
            
            if response.status_code == 200:
                chunks_received = 0
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            chunks_received += 1
                            if data.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
                
                if chunks_received > 0:
                    print(f"✅ Streaming works! Received {chunks_received} chunks")
                    return True
                else:
                    print("❌ No streaming chunks received")
                    return False
            else:
                print(f"❌ Streaming request failed with status: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Streaming test error: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run the complete test suite."""
        print("🧪 Starting OllamaPy Middleware Test Suite")
        print("=" * 50)
        
        # Check prerequisites
        print("🔍 Checking prerequisites...")
        
        if not self.check_ollama_available():
            print("❌ Ollama server is not running. Please start Ollama first.")
            return False
        
        print("✅ Ollama server is running")
        
        if not self.check_test_model_available():
            print(f"⚠️  Test model '{self.test_model}' not found. Attempting to pull...")
            try:
                pull_payload = {"name": self.test_model}
                response = requests.post(f"{self.ollama_url}/api/pull", json=pull_payload)
                if response.status_code != 200:
                    print(f"❌ Failed to pull model {self.test_model}")
                    return False
            except Exception as e:
                print(f"❌ Error pulling model: {e}")
                return False
        
        print(f"✅ Test model '{self.test_model}' is available")
        
        # Start middleware server
        if not self.start_middleware_server():
            return False
        
        # Run tests
        tests = [
            ("Health endpoint", self.test_health_endpoint),
            ("Models endpoint", self.test_models_endpoint),
            ("Core functionality", self.test_core_functionality),
            ("Chat endpoint", self.test_chat_endpoint),
            ("Streaming responses", self.test_streaming_responses),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed_tests += 1
                else:
                    print(f"❌ {test_name} test failed")
            except Exception as e:
                print(f"❌ {test_name} test crashed: {e}")
        
        # Summary
        print("\n" + "=" * 50)
        print(f"🧪 Test Results: {passed_tests}/{total_tests} passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! OllamaPy middleware is working correctly!")
            return True
        else:
            print("💥 Some tests failed. Check the output above for details.")
            return False


def main():
    """Run the middleware test suite."""
    test_suite = MiddlewareTestSuite()
    success = test_suite.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()