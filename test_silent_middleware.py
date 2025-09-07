#!/usr/bin/env python3
"""Quick test for silent middleware behavior."""

import requests
import time
import json

def test_silent_middleware():
    """Test the silent middleware with a calculation."""
    
    # Test calculation request
    payload = {
        "model": "gemma3:4b",
        "prompt": "What is 25 * 4?",
        "stream": False
    }
    
    print("🧪 Testing silent middleware with calculation...")
    
    try:
        response = requests.post(
            "http://localhost:11435/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get('response', '')
            
            print(f"✅ Response received:")
            print(f"📝 Response: {response_text}")
            print(f"📏 Length: {len(response_text)} characters")
            
            # Check if response contains any tool-call patterns
            tool_patterns = ['🔍', '✓', '✗', '🎯', '[', 'Selected', 'Analyzing', 'Executing']
            found_patterns = [p for p in tool_patterns if p in response_text]
            
            if found_patterns:
                print(f"⚠️  Found potential tool patterns: {found_patterns}")
                return False
            else:
                print("✅ Response appears clean - no tool-call patterns detected!")
                return True
                
        else:
            print(f"❌ Request failed with status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint as well."""
    
    payload = {
        "model": "gemma3:4b", 
        "messages": [
            {"role": "user", "content": "Calculate 12 + 8 for me"}
        ],
        "stream": False
    }
    
    print("\n🧪 Testing chat endpoint...")
    
    try:
        response = requests.post(
            "http://localhost:11435/api/chat",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            message = data.get('message', {})
            response_text = message.get('content', '')
            
            print(f"✅ Chat response received:")
            print(f"📝 Response: {response_text}")
            
            # Check for tool patterns
            tool_patterns = ['🔍', '✓', '✗', '🎯', '[', 'Selected', 'Analyzing', 'Executing']
            found_patterns = [p for p in tool_patterns if p in response_text]
            
            if found_patterns:
                print(f"⚠️  Found potential tool patterns: {found_patterns}")
                return False
            else:
                print("✅ Chat response appears clean!")
                return True
                
        else:
            print(f"❌ Chat request failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Starting silent middleware test...")
    
    # Check if middleware is running
    try:
        health_response = requests.get("http://localhost:11435/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ Middleware not running. Start it with: ollamapy --middleware")
            exit(1)
    except:
        print("❌ Middleware not running. Start it with: ollamapy --middleware")
        exit(1)
    
    print("✅ Middleware is running!")
    
    # Run tests
    test1_passed = test_silent_middleware()
    test2_passed = test_chat_endpoint()
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! The middleware appears to be working silently.")
    else:
        print("\n💥 Some tests failed. Check the output above.")