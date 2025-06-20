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
            
            # Comprehensive anime/manga tag prompt
            prompt = """Analyze this image and create a detailed anime/manga booru-style tag list. Include ALL visible elements in comma-separated format:

MANDATORY TAGS (in order):
- Character count (1girl, 2girls, 1boy, etc.)
- Character name if recognizable from anime/manga
- Group status (solo, duo, group)
- Clothing items with colors (green_bikini, white_shirt, school_uniform, etc.)
- Hair details (pink_hair, long_hair, twin_braids, gradient_hair, multicolored_hair)
- Eye details (green_eyes, blue_eyes, red_eyes)
- Facial features (mole_under_eye, smile, closed_mouth, open_mouth)
- Body visibility (upper_body, full_body, navel)
- Pose/action (looking_at_viewer, arms_behind_back, hand_on_hip, sitting, standing)
- Camera angle (from_above, from_side, close-up)
- Setting/location (beach, outdoors, indoors, classroom, bedroom)
- Time/lighting (day, night, sunlight, sunset)
- Background elements (blue_sky, ocean, clouds, trees, water)
- Art style if applicable (anime_style, realistic, etc.)

Generate at least 20-30 detailed tags covering everything visible. Be extremely specific."""
            
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
                    "temperature": 0.1,
                    "topK": 10,
                    "topP": 0.5,
                    "maxOutputTokens": 300
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean booru-style tag formatting
                prefixes = [
                    "Analyze this image and create a detailed anime/manga booru-style tag list.",
                    "Include ALL visible elements in comma-separated format:",
                    "MANDATORY TAGS (in order):",
                    "Generate at least 20-30 detailed tags covering everything visible.",
                    "Here's an anime/manga booru-style tag list:",
                    "Here's a detailed tag list:",
                    "Tags:",
                    "**",
                    "*",
                    "Be extremely specific.",
                ]
                
                # Remove prefixes and clean text
                for prefix in prefixes:
                    if text.lower().startswith(prefix.lower()):
                        text = text[len(prefix):].strip()
                        break
                
                # Clean markdown and format for proper tag structure
                text = text.replace('**', '').replace('*', '').replace('##', '')
                text = text.replace('- ', '').replace('\n', ', ')  # Convert bullet points to commas
                text = text.replace('; ', ', ').replace(': ', ', ')
                
                # Ensure proper anime tag formatting
                text = text.replace(' hair', '_hair').replace(' eyes', '_eyes')
                text = text.replace(' body', '_body').replace(' mouth', '_mouth')
                text = text.replace(' viewer', '_viewer').replace(' back', '_back')
                text = text.replace(' sky', '_sky').replace(' under eye', '_under_eye')
                text = text.replace(' behind back', '_behind_back')
                text = text.replace(' at viewer', '_at_viewer')
                
                # Clean extra spaces and normalize
                text = ' '.join(text.split())
                text = text.replace(' ,', ',').replace(',,', ',')
                
                # Remove trailing punctuation
                text = text.strip().rstrip('.,;:')
                
                # Strict truncation for anime tag format - cut at comma boundaries
                if len(text) > 680:
                    # Split by commas to preserve tag structure
                    tags = text.split(', ')
                    truncated_tags = []
                    char_count = 0
                    
                    for tag in tags:
                        tag = tag.strip()
                        # Calculate length including comma separator
                        tag_length = len(tag) + (2 if truncated_tags else 0)  # +2 for ", "
                        
                        if char_count + tag_length <= 675:
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