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
            
            # Ultra-detailed anime/manga prompt with precise positioning
            prompt = """Create an anime/manga image prompt with comma-separated tags. Be extremely detailed and precise:
1. Subject count: 1girl, 1boy, etc.
2. Character name if anime character (like kanroji_mitsuri, nezuko_kamado, etc.)
3. Group status: solo, group
4. Clothing: exact type (bikini, swimsuit, school_uniform, dress), colors (green_bikini, red_dress)
5. Hair: color (pink_hair, black_hair), length (long_hair, short_hair), style (twin_braids, ponytail, twin_tails)
6. Eyes: color (green_eyes, red_eyes, blue_eyes)
7. Body features: mole_under_eye, navel, upper_body, full_body
8. Expression: looking_at_viewer, closed_mouth, open_mouth, smile
9. Pose: arms_behind_back, arms_up, hand_on_hip
10. Setting: beach, outdoors, indoors, day, night
11. Background: blue_sky, ocean, clouds, water, trees
Be very specific about positioning and details like "mole under eye" not just "mole"."""
            
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
                    "temperature": 0.01,
                    "topK": 3,
                    "topP": 0.3,
                    "maxOutputTokens": 250
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean anime/manga prompt format - preserve underscores in tags
                prefixes = [
                    "Create an anime/manga image prompt with comma-separated tags.",
                    "Here's an anime/manga image prompt:",
                    "Here's an image prompt:",
                    "Here's a description:",
                    "Image prompt:",
                    "Prompt:",
                    "Tags:",
                    "**",
                    "*",
                    "Here is the prompt:",
                    "The prompt is:",
                    "Be extremely detailed and precise:",
                ]
                
                for prefix in prefixes:
                    if text.lower().startswith(prefix.lower()):
                        text = text[len(prefix):].strip()
                        break
                
                # Clean but preserve anime tag structure
                text = text.replace('**', '').replace('*', '').replace('##', '')
                text = text.replace(' and ', ', ').replace('; ', ', ')
                
                # Fix common spacing issues in anime tags
                text = text.replace(' _', '_').replace('_ ', '_')  # Fix underscores
                text = text.replace(' hair', '_hair').replace(' eyes', '_eyes')
                text = text.replace(' body', '_body').replace(' mouth', '_mouth')
                text = text.replace(' viewer', '_viewer').replace(' back', '_back')
                text = text.replace(' sky', '_sky').replace(' under eye', '_under_eye')
                
                # Normalize spacing
                text = ' '.join(text.split())
                
                # Remove trailing punctuation
                text = text.rstrip('.,;:')
                
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