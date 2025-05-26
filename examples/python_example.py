#!/usr/bin/env python3
"""
Image Prompt Extractor - Python Integration Examples

This file demonstrates various ways to integrate with the Image Prompt Extractor API
using Python and different libraries.
"""

import requests
import json
import asyncio
import aiohttp
from typing import Optional, List, Dict, Any
from pathlib import Path
import time


# =============================================================================
# 1. Basic Synchronous Example
# =============================================================================

def analyze_image_from_url(image_url: str, api_base_url: str = "http://localhost:5000") -> Dict[str, Any]:
    """
    Analyzes an image from URL using the Image Prompt Extractor API
    
    Args:
        image_url: The URL of the image to analyze
        api_base_url: Base URL of the API
        
    Returns:
        API response with prompt or error
    """
    try:
        response = requests.post(
            f"{api_base_url}/api/analyze",
            json={"image_url": image_url},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e)
        }


def analyze_image_from_file(file_path: str, api_base_url: str = "http://localhost:5000") -> Dict[str, Any]:
    """
    Analyzes an image file using the Image Prompt Extractor API
    
    Args:
        file_path: Path to the image file
        api_base_url: Base URL of the API
        
    Returns:
        API response with prompt or error
    """
    try:
        with open(file_path, 'rb') as file:
            files = {'image_file': file}
            response = requests.post(
                f"{api_base_url}/api/analyze",
                files=files,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
    except (requests.RequestException, IOError) as e:
        return {
            "success": False,
            "error": str(e)
        }


# =============================================================================
# 2. Advanced Class with Retry Logic
# =============================================================================

class ImagePromptExtractor:
    """Advanced Image Prompt Extractor client with additional features"""
    
    def __init__(self, api_base_url: str = "http://localhost:5000", max_retries: int = 3):
        self.api_base_url = api_base_url
        self.max_retries = max_retries
        self.session = requests.Session()
        
    def check_health(self) -> bool:
        """Check if the API service is healthy"""
        try:
            response = self.session.get(f"{self.api_base_url}/health", timeout=10)
            health = response.json()
            return health.get("status") == "healthy" and health.get("gemini_configured", False)
        except Exception as e:
            print(f"Health check failed: {e}")
            return False
    
    def analyze_with_retry(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image with retry logic"""
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"Attempt {attempt}/{self.max_retries}: Analyzing image...")
                
                response = self.session.post(
                    f"{self.api_base_url}/api/analyze",
                    json=input_data,
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
                
                if result.get("success"):
                    return result
                else:
                    raise Exception(result.get("error", "Unknown error"))
                    
            except Exception as e:
                last_error = e
                if attempt < self.max_retries:
                    wait_time = attempt * 2  # Exponential backoff
                    print(f"Attempt {attempt} failed: {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
        
        return {
            "success": False,
            "error": f"Failed after {self.max_retries} attempts: {last_error}"
        }
    
    def analyze_batch(self, image_urls: List[str], max_workers: int = 3) -> List[Dict[str, Any]]:
        """Analyze multiple images with controlled concurrency"""
        import concurrent.futures
        
        def analyze_single(url):
            return self.analyze_with_retry({"image_url": url})
        
        results = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_url = {executor.submit(analyze_single, url): url for url in image_urls}
            
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    result = future.result()
                    results.append({"url": url, "result": result})
                except Exception as e:
                    results.append({
                        "url": url, 
                        "result": {"success": False, "error": str(e)}
                    })
        
        return results


# =============================================================================
# 3. Asynchronous Example
# =============================================================================

class AsyncImagePromptExtractor:
    """Asynchronous Image Prompt Extractor client"""
    
    def __init__(self, api_base_url: str = "http://localhost:5000"):
        self.api_base_url = api_base_url
    
    async def analyze_image_async(self, image_url: str) -> Dict[str, Any]:
        """Analyze image asynchronously"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.api_base_url}/api/analyze",
                    json={"image_url": image_url},
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
    
    async def analyze_batch_async(self, image_urls: List[str], semaphore_limit: int = 5) -> List[Dict[str, Any]]:
        """Analyze multiple images asynchronously with rate limiting"""
        semaphore = asyncio.Semaphore(semaphore_limit)
        
        async def analyze_with_semaphore(url):
            async with semaphore:
                result = await self.analyze_image_async(url)
                return {"url": url, "result": result}
        
        tasks = [analyze_with_semaphore(url) for url in image_urls]
        return await asyncio.gather(*tasks)


# =============================================================================
# 4. Usage Examples
# =============================================================================

def example_basic_usage():
    """Basic usage example"""
    print("🔍 Basic Image Analysis Example")
    
    # Test with the provided image
    test_image = "https://i.ibb.co/MkVH92j3/image.jpg"
    result = analyze_image_from_url(test_image)
    
    if result["success"]:
        print("✅ Analysis successful!")
        print(f"📝 Generated prompt: {result['prompt'][:100]}...")
    else:
        print(f"❌ Analysis failed: {result['error']}")


def example_advanced_usage():
    """Advanced usage with retry logic"""
    print("\n🚀 Advanced Usage Example")
    
    extractor = ImagePromptExtractor()
    
    # Check service health
    if not extractor.check_health():
        print("❌ Service is not healthy")
        return
    
    # Analyze single image with retry
    test_image = "https://i.ibb.co/MkVH92j3/image.jpg"
    result = extractor.analyze_with_retry({"image_url": test_image})
    
    if result["success"]:
        print("✅ Advanced analysis successful!")
        print(f"📝 Generated prompt: {result['prompt'][:100]}...")
    else:
        print(f"❌ Advanced analysis failed: {result['error']}")


def example_batch_processing():
    """Batch processing example"""
    print("\n📦 Batch Processing Example")
    
    extractor = ImagePromptExtractor()
    
    # Example URLs (replace with actual image URLs)
    image_urls = [
        "https://i.ibb.co/MkVH92j3/image.jpg",
        # Add more URLs here for testing
    ]
    
    print(f"Processing {len(image_urls)} images...")
    results = extractor.analyze_batch(image_urls, max_workers=2)
    
    for i, item in enumerate(results):
        url = item["url"]
        result = item["result"]
        
        print(f"\nImage {i+1}: {url}")
        if result["success"]:
            print(f"✅ Success: {result['prompt'][:80]}...")
        else:
            print(f"❌ Failed: {result['error']}")


async def example_async_usage():
    """Asynchronous usage example"""
    print("\n⚡ Async Processing Example")
    
    extractor = AsyncImagePromptExtractor()
    
    # Test single image
    test_image = "https://i.ibb.co/MkVH92j3/image.jpg"
    result = await extractor.analyze_image_async(test_image)
    
    if result["success"]:
        print("✅ Async analysis successful!")
        print(f"📝 Generated prompt: {result['prompt'][:100]}...")
    else:
        print(f"❌ Async analysis failed: {result['error']}")


# =============================================================================
# 5. Specialized Use Cases
# =============================================================================

def generate_alt_text(image_url: str, max_length: int = 125) -> str:
    """Generate SEO-optimized alt text from image analysis"""
    result = analyze_image_from_url(image_url)
    
    if not result["success"]:
        raise Exception(f"Failed to analyze image: {result['error']}")
    
    alt_text = result["prompt"]
    
    # Truncate if too long for SEO
    if len(alt_text) > max_length:
        alt_text = alt_text[:max_length-3] + "..."
    
    return alt_text


def content_moderation(image_url: str) -> Dict[str, Any]:
    """Basic content moderation based on image analysis"""
    result = analyze_image_from_url(image_url)
    
    if not result["success"]:
        raise Exception(f"Failed to analyze image: {result['error']}")
    
    prompt = result["prompt"].lower()
    
    # Simple keyword-based filtering (extend as needed)
    inappropriate_keywords = ["explicit", "nude", "violence", "inappropriate"]
    is_appropriate = not any(keyword in prompt for keyword in inappropriate_keywords)
    
    return {
        "is_appropriate": is_appropriate,
        "description": result["prompt"],
        "confidence": "medium"  # Could be enhanced with more sophisticated analysis
    }


def product_catalog_description(image_url: str) -> str:
    """Generate product descriptions for e-commerce"""
    result = analyze_image_from_url(image_url)
    
    if not result["success"]:
        raise Exception(f"Failed to analyze image: {result['error']}")
    
    # The API already provides clean, detailed descriptions perfect for product catalogs
    return result["prompt"]


# =============================================================================
# 6. Error Handling and Validation
# =============================================================================

def validate_image_url(url: str) -> bool:
    """Validate if URL points to a supported image format"""
    try:
        response = requests.head(url, timeout=10)
        content_type = response.headers.get('content-type', '').lower()
        return content_type.startswith('image/')
    except:
        return False


def analyze_with_validation(image_url: str) -> Dict[str, Any]:
    """Analyze image with pre-validation"""
    # Validate URL first
    if not validate_image_url(image_url):
        return {
            "success": False,
            "error": "Invalid image URL or unsupported format"
        }
    
    return analyze_image_from_url(image_url)


# =============================================================================
# 7. Command Line Interface
# =============================================================================

def main():
    """Command line interface for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Image Prompt Extractor CLI")
    parser.add_argument("--url", help="Image URL to analyze")
    parser.add_argument("--file", help="Image file path to analyze")
    parser.add_argument("--batch", nargs="+", help="Multiple image URLs for batch processing")
    parser.add_argument("--api-url", default="http://localhost:5000", help="API base URL")
    
    args = parser.parse_args()
    
    if args.url:
        print(f"Analyzing URL: {args.url}")
        result = analyze_image_from_url(args.url, args.api_url)
        print(json.dumps(result, indent=2))
    
    elif args.file:
        print(f"Analyzing file: {args.file}")
        result = analyze_image_from_file(args.file, args.api_url)
        print(json.dumps(result, indent=2))
    
    elif args.batch:
        print(f"Batch processing {len(args.batch)} images...")
        extractor = ImagePromptExtractor(args.api_url)
        results = extractor.analyze_batch(args.batch)
        print(json.dumps(results, indent=2))
    
    else:
        # Run examples
        example_basic_usage()
        example_advanced_usage()
        example_batch_processing()
        
        # Run async example
        asyncio.run(example_async_usage())


if __name__ == "__main__":
    main()