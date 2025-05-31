#!/usr/bin/env python3
"""
Deployment test script for Image Prompt Extractor
Tests health endpoints and basic functionality
"""

import requests
import sys
import json
import time

def test_health_endpoint(base_url):
    """Test the health endpoint"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"Health check status: {response.status_code}")
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"Service: {health_data.get('service')}")
            print(f"Gemini configured: {health_data.get('gemini_configured')}")
            return True
        else:
            print(f"Health check failed: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"Health check error: {e}")
        return False

def test_api_endpoint(base_url):
    """Test the API endpoint with a sample image"""
    try:
        test_url = "https://i.ibb.co/MkVH92j3/image.jpg"
        payload = {"image_url": test_url}
        
        print(f"Testing API with image: {test_url}")
        response = requests.post(
            f"{base_url}/api/analyze", 
            json=payload, 
            timeout=30,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"API response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                prompt = result.get('prompt', '')
                print(f"Generated prompt length: {len(prompt)} characters")
                print(f"Prompt preview: {prompt[:100]}...")
                return True
            else:
                print(f"API returned error: {result.get('error')}")
                return False
        else:
            print(f"API request failed: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"API test error: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) != 2:
        print("Usage: python test-deployment.py <base_url>")
        print("Example: python test-deployment.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    print(f"Testing deployment at: {base_url}")
    print("=" * 50)
    
    # Test health endpoint
    print("1. Testing health endpoint...")
    health_ok = test_health_endpoint(base_url)
    
    # Test API endpoint
    print("\n2. Testing API endpoint...")
    api_ok = test_api_endpoint(base_url)
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Health endpoint: {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"API endpoint: {'✓ PASS' if api_ok else '✗ FAIL'}")
    
    if health_ok and api_ok:
        print("\n🎉 All tests passed! Deployment is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()