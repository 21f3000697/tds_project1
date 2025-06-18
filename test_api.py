#!/usr/bin/env python3
"""
Test script for TDS Virtual TA API
"""

import requests
import json
import time
import psutil
import os

def get_memory_usage():
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def test_api():
    """Test the API with sample questions"""
    
    # API endpoint
    base_url = "http://localhost:8000"
    
    # Sample questions
    test_questions = [
        "What is PromptFoo and how do I use it?",
        "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
        "How do I evaluate my application with promptfoo?",
        "What are the memory requirements for this project?"
    ]
    
    print("Testing TDS Virtual TA API...")
    print(f"Initial memory usage: {get_memory_usage():.2f} MB")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Test {i}: {question[:50]}... ---")
        
        try:
            # Make API request
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/",
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Response time: {response_time:.2f}s")
                print(f"Answer: {data['answer'][:100]}...")
                print(f"Links: {len(data['links'])} found")
                for link in data['links'][:2]:  # Show first 2 links
                    print(f"  - {link['text'][:50]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print(f"Memory usage: {get_memory_usage():.2f} MB")
    
    # Test health endpoint
    try:
        health_response = requests.get(f"{base_url}/health")
        if health_response.status_code == 200:
            print(f"\n✅ Health check passed: {health_response.json()}")
        else:
            print(f"\n❌ Health check failed: {health_response.status_code}")
    except Exception as e:
        print(f"\n❌ Health check exception: {e}")

if __name__ == "__main__":
    test_api() 