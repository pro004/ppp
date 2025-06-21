#!/usr/bin/env python3
"""
Test script for comprehensive image analysis functionality
"""
import requests
import json

def test_comprehensive_analysis():
    """Test the comprehensive analysis endpoint with a sample image"""
    
    # Test image URL
    test_image_url = "https://i.ibb.co/MkVH92j3/image.jpg"
    
    # API endpoint
    api_url = "http://localhost:5000/api/analyze"
    
    # Request payload
    payload = {
        "image_url": test_image_url
    }
    
    print("Testing comprehensive image analysis...")
    print(f"Image URL: {test_image_url}")
    print(f"API Endpoint: {api_url}")
    print("-" * 60)
    
    try:
        # Make the API request
        response = requests.post(
            api_url,
            json=payload,
            timeout=120  # Allow more time for comprehensive analysis
        )
        
        print(f"HTTP Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                prompt = result.get('prompt', '')
                analysis_type = result.get('analysis_type', 'unknown')
                
                print(f"Analysis Type: {analysis_type}")
                print(f"Analysis Length: {len(prompt)} characters")
                print("-" * 60)
                print("COMPREHENSIVE ANALYSIS RESULT:")
                print("-" * 60)
                print(prompt)
                print("-" * 60)
                
                # Check if it's actually comprehensive
                comprehensive_indicators = [
                    'composition', 'lighting', 'color', 'mood', 'background',
                    'foreground', 'texture', 'style', 'perspective', 'emotional'
                ]
                
                found_indicators = sum(1 for indicator in comprehensive_indicators 
                                     if indicator.lower() in prompt.lower())
                
                print(f"Comprehensive Elements Found: {found_indicators}/{len(comprehensive_indicators)}")
                
                if found_indicators >= 5:
                    print("✅ Analysis appears to be comprehensive!")
                else:
                    print("⚠️  Analysis may not be fully comprehensive")
                    
            else:
                print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out - this is normal for comprehensive analysis")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_comprehensive_analysis()