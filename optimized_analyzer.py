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
        self.api_key = "AIzaSyCfdO3Mp0rwzgmtQFWMyxyCO6M6wFQMGIY"
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
            
            # Anime/manga style prompt generation
            prompt = """Generate an image prompt in this exact format: number+gender, character_name (if recognizable), solo/group, main_clothing, distinctive_features, hair_details, pose/action, setting, background_elements. Use comma-separated tags like: 1girl, character_name, solo, outfit_type, eye_color, hair_color, hair_style, pose, location, background. Be precise and detailed but concise."""
            
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
                    "temperature": 0.05,
                    "topK": 8,
                    "topP": 0.5,
                    "maxOutputTokens": 150
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean anime/manga prompt format
                prefixes = [
                    "Here's an image prompt:",
                    "Here's a description:",
                    "Image prompt:",
                    "Prompt:",
                    "Tags:",
                    "Generate an image prompt in this exact format:",
                    "**",
                    "*",
                    "Here is the prompt:",
                    "The prompt is:",
                ]
                
                for prefix in prefixes:
                    if text.lower().startswith(prefix.lower()):
                        text = text[len(prefix):].strip()
                        break
                
                # Clean markdown and normalize for tag format
                text = text.replace('**', '').replace('*', '').replace('##', '')
                text = text.replace(', and ', ', ').replace(' and ', ', ')
                text = text.replace('with ', '').replace(' with', '')
                text = text.replace(' in ', ', ').replace(' on ', ', ')
                
                # Ensure comma-separated format
                text = text.replace('; ', ', ').replace(': ', ', ')
                text = ' '.join(text.split())
                
                # Remove trailing punctuation
                text = text.rstrip('.,;:')
                
                # Strict truncation for anime tag format - cut at comma boundaries
                if len(text) > 650:
                    # Split by commas to preserve tag structure
                    tags = text.split(', ')
                    truncated_tags = []
                    char_count = 0
                    
                    for tag in tags:
                        tag = tag.strip()
                        # Calculate length including comma separator
                        tag_length = len(tag) + (2 if truncated_tags else 0)  # +2 for ", "
                        
                        if char_count + tag_length <= 645:
                            truncated_tags.append(tag)
                            char_count += tag_length
                        else:
                            break
                    
                    text = ', '.join(truncated_tags)
                
                # Final character count check
                logger.info(f"Final prompt length: {len(text)} characters")
                
                logger.info(f"Generated optimized prompt: {text[:100]}...")
                return text
            else:
                logger.error("No valid response from Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            return None