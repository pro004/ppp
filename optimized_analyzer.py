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
            
            # Universal image analysis prompt
            prompt = """Analyze this image comprehensively and generate a detailed description covering:

1. Image Type & Style: Specify if human/anime/object/landscape/abstract, art style (realistic/stylized/cartoonish)
2. Subject Details: For humans/anime - age, gender, hair (color/length/style), clothing (type/colors), facial features, pose, expression, body position
3. Spatial Positioning: Exact placement (left/right/center, foreground/background), relative positions between subjects/objects
4. Composition: Camera angle, framing, lighting conditions, depth of field
5. Environment: Setting, background elements, time of day, atmosphere
6. Colors & Materials: Dominant colors, textures, materials visible
7. Emotions & Interactions: Expressions, body language, subject interactions

Generate as comma-separated tags with precise positional details. Be accurate about what's actually visible."""
            
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
                    "topK": 15,
                    "topP": 0.6,
                    "maxOutputTokens": 350
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean comprehensive analysis format
                prefixes = [
                    "Analyze this image comprehensively and generate a detailed description covering:",
                    "1. Image Type & Style:",
                    "2. Subject Details:",
                    "3. Spatial Positioning:",
                    "4. Composition:",
                    "5. Environment:",
                    "6. Colors & Materials:",
                    "7. Emotions & Interactions:",
                    "Generate as comma-separated tags with precise positional details.",
                    "Be accurate about what's actually visible.",
                    "Here's the comprehensive analysis:",
                    "Analysis:",
                    "Tags:",
                ]
                
                for prefix in prefixes:
                    if text.lower().startswith(prefix.lower()):
                        text = text[len(prefix):].strip()
                        break
                
                # Remove numbered list format and extract actual content
                lines = text.split('\n')
                content_lines = []
                
                for line in lines:
                    line = line.strip()
                    # Skip numbered categories and instruction lines
                    if any(skip in line.lower() for skip in [
                        '1.', '2.', '3.', '4.', '5.', '6.', '7.',
                        'image type', 'subject details', 'spatial positioning',
                        'composition', 'environment', 'colors & materials', 'emotions'
                    ]):
                        continue
                    
                    # Keep actual descriptive content
                    if line and (',' in line or len(line.split()) > 3):
                        content_lines.append(line)
                
                if content_lines:
                    text = ' '.join(content_lines)
                
                # Convert structured format to tags
                text = text.replace(':', ',').replace(';', ',')
                text = text.replace(' - ', ', ').replace(' / ', ', ')
                
                # Clean and format
                text = text.replace('**', '').replace('*', '').replace('##', '')
                text = text.replace('- ', '').replace(': ', ', ')
                text = text.replace('; ', ', ').replace(' and ', ', ')
                
                # Fix anime tag formatting
                text = text.replace(' hair', '_hair').replace(' eyes', '_eyes')
                text = text.replace(' body', '_body').replace(' mouth', '_mouth')
                text = text.replace(' viewer', '_viewer').replace(' back', '_back')
                text = text.replace(' sky', '_sky').replace(' under eye', '_under_eye')
                text = text.replace('looking at', 'looking_at')
                text = text.replace('arms behind', 'arms_behind')
                
                # Clean spacing and punctuation
                text = ' '.join(text.split())
                text = text.replace(' ,', ',').replace(',,', ',')
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