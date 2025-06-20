import os
import requests
import logging
import base64
import json
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)

class OptimizedImageAnalyzer:
    """Optimized image analyzer with consistent prompts for web and API."""
    
    def __init__(self):
        """Initialize with API key."""
        self.api_key = os.environ.get("GEMINI_API_KEY") or "AIzaSyCfdO3Mp0rwzgmtQFWMyxyCO6M6wFQMGIY"
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("GEMINI_API_KEY not configured - image analysis will not work")
        else:
            logger.info("Optimized analyzer initialized successfully with API key")
    
    def is_configured(self):
        """Check if API key is available."""
        return bool(self.api_key)
    
    def analyze_from_url(self, image_url):
        """Analyze image from URL."""
        try:
            # Download image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Convert to base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            mime_type = response.headers.get('content-type', 'image/jpeg')
            
            return self._analyze_with_api(image_data, mime_type)
            
        except Exception as e:
            logger.error(f"Error analyzing image from URL: {str(e)}")
            return None
    
    def analyze_from_file(self, file_path):
        """Analyze image from file."""
        try:
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Detect mime type
            ext = os.path.splitext(file_path)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.png': 'image/png', '.gif': 'image/gif',
                '.webp': 'image/webp', '.bmp': 'image/bmp'
            }.get(ext, 'image/jpeg')
            
            return self._analyze_with_api(image_data, mime_type)
            
        except Exception as e:
            logger.error(f"Error analyzing image from file: {str(e)}")
            return None
    
    def _analyze_with_api(self, image_data, mime_type):
        """Direct API call to Gemini with optimized prompt."""
        try:
            if not self.api_key:
                raise RuntimeError("API key not configured")
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            # Balanced prompt for detailed accuracy within character limits
            prompt = """Describe precisely: subjects (exact age, gender, hair color/style, facial expression, pose, clothing details, accessories), objects (precise position using left/right/center/foreground/background, exact colors, materials), environment (lighting direction, setting details), art style (realistic/anime/digital), specific color names, composition (camera angle, depth). Include spatial relationships and fine details. Be detailed but concise."""
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_data
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.15,
                    "topK": 15,
                    "topP": 0.7,
                    "maxOutputTokens": 180
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Aggressive cleaning to ensure under 700 characters
                prefixes = [
                    "Here's a description of the image:",
                    "Here's a detailed description of the image:",
                    "Here's a detailed description:",
                    "Here's a description:",
                    "This image shows:",
                    "This image depicts:",
                    "The image shows:",
                    "The image depicts:",
                    "I can see:",
                    "Looking at this image:",
                    "In this image:",
                    "The scene shows:",
                    "This shows:",
                    "**Description:**",
                    "Description:",
                    "Subjects:",
                ]
                
                for prefix in prefixes:
                    if text.lower().startswith(prefix.lower()):
                        text = text[len(prefix):].strip()
                        break
                
                # Remove markdown and normalize
                text = text.replace('**', '').replace('*', '').replace('##', '')
                text = ' '.join(text.split())
                
                # Remove trailing period if present
                if text.endswith('.'):
                    text = text[:-1]
                
                # Smart truncation to stay under 700 characters while preserving meaning
                if len(text) > 700:
                    # Try to cut at sentence boundary
                    sentences = text.split('. ')
                    if len(sentences) > 1:
                        truncated = sentences[0]
                        for sentence in sentences[1:]:
                            if len(truncated + '. ' + sentence) <= 697:
                                truncated += '. ' + sentence
                            else:
                                break
                        text = truncated
                    else:
                        # Cut at word boundary if no sentences
                        words = text.split()
                        truncated = []
                        char_count = 0
                        for word in words:
                            if char_count + len(word) + 1 <= 697:
                                truncated.append(word)
                                char_count += len(word) + 1
                            else:
                                break
                        text = ' '.join(truncated) + "..."
                
                logger.info(f"Generated optimized prompt: {text[:100]}...")
                return text
            else:
                logger.error("No valid response from Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            return None