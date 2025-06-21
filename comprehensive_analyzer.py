import os
import requests
import logging
import base64
import json
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class ComprehensiveImageAnalyzer:
    """
    Advanced image analyzer that provides detailed, comprehensive analysis of all visual elements,
    including composition, artistic style, emotional impact, and contextual elements.
    """
    
    def __init__(self):
        """Initialize with API key."""
        self.api_key = "AIzaSyCfdO3Mp0rwzgmtQFWMyxyCO6M6wFQMGIY"
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("GEMINI_API_KEY not configured - comprehensive analysis will not work")
        else:
            logger.info("Comprehensive analyzer initialized successfully with API key")
    
    def is_configured(self):
        """Check if API key is available."""
        return bool(self.api_key)
    
    def analyze_from_url(self, image_url):
        """Analyze image from URL with comprehensive detail."""
        try:
            # Download image with proper headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Convert to base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            mime_type = response.headers.get('content-type', 'image/jpeg')
            
            return self._analyze_with_comprehensive_api(image_data, mime_type)
            
        except Exception as e:
            logger.error(f"Error analyzing image from URL: {str(e)}")
            return {"success": False, "error": f"Failed to analyze image: {str(e)}"}
    
    def analyze_from_file(self, file_path):
        """Analyze image from file with comprehensive detail."""
        try:
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Detect mime type from file extension
            ext = os.path.splitext(file_path)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.png': 'image/png', '.gif': 'image/gif',
                '.webp': 'image/webp', '.bmp': 'image/bmp',
                '.tiff': 'image/tiff', '.tif': 'image/tiff',
                '.svg': 'image/svg+xml', '.ico': 'image/x-icon',
                '.heic': 'image/heic', '.heif': 'image/heif',
                '.avif': 'image/avif'
            }.get(ext, 'image/jpeg')
            
            return self._analyze_with_comprehensive_api(image_data, mime_type)
            
        except Exception as e:
            logger.error(f"Error analyzing image from file: {str(e)}")
            return {"success": False, "error": f"Failed to analyze image: {str(e)}"}
    
    def _analyze_with_comprehensive_api(self, image_data, mime_type):
        """Direct API call to Gemini with comprehensive analysis prompt."""
        try:
            if not self.api_key:
                raise RuntimeError("API key not configured")
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            # Enhanced detailed prompt with spatial positioning and background focus
            comprehensive_prompt = """Analyze this image in detail and provide a comprehensive comma-separated description. Focus particularly on:

Image type and artistic style, medium used.

Characters/subjects: age, gender, facial features, hairstyle, clothing details, exact positioning (where each person/object is located - left/right/center, foreground/background, sitting/standing/lying, body orientation, limb positions), poses, expressions, interactions between subjects.

Background environment: specific location type (indoor/outdoor, room type, furniture, objects), detailed background elements, spatial depth, what's visible behind subjects, environmental context, setting atmosphere.

Composition: framing, angle, perspective, focal points, positioning within frame (top/bottom/center/sides).

Lighting: source direction, quality, shadows, highlights, color temperature.

Colors and textures: palette, materials, surface qualities.

Mood and atmosphere: emotional tone, thematic elements.

Be extremely precise about spatial relationships - specify exact positions like "woman seated center-left, man positioned behind her on the right side, bed visible in background center, window on far left wall, furniture placement" etc. Include detailed background elements and their specific locations.

Provide comprehensive description targeting 700-800 characters, comma-separated phrases only, prioritizing positioning and background details."""
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": comprehensive_prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_data
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.12,
                    "topK": 15,
                    "topP": 0.65,
                    "maxOutputTokens": 650
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean up the comma-separated prompt response
                logger.debug(f"Raw prompt response: {text[:200]}...")
                
                # Remove common prefixes
                prefixes_to_remove = [
                    "Here's the comma-separated description:",
                    "The comma-separated description is:",
                    "Description:",
                    "Here's the description:",
                    "The image shows:",
                ]
                
                for prefix in prefixes_to_remove:
                    if text.lower().startswith(prefix.lower()):
                        text = text[len(prefix):].strip()
                        break
                
                # Clean up formatting
                text = text.replace('**', '').replace('*', '').replace('\n', ' ')
                text = text.replace('- ', '').replace('• ', '')
                
                # Remove numbered list formatting
                import re
                text = re.sub(r'^\d+\.\s*', '', text)
                text = re.sub(r'\n\d+\.\s*', ', ', text)
                
                # Ensure proper comma separation
                text = ', '.join([phrase.strip() for phrase in text.split(',') if phrase.strip()])
                
                # Remove any unwanted phrases
                unwanted = ['as you can see', 'in this image', 'the image shows', 'we can see']
                for phrase in unwanted:
                    text = text.replace(phrase, '')
                
                # Clean up spacing and punctuation
                text = text.replace(' ,', ',').replace(',,', ',')
                text = text.strip().rstrip('.,;:')
                
                # Ensure length is around 700-800 characters
                if len(text) > 820:
                    # Smart truncation while keeping essential elements
                    parts = text.split(', ')
                    essential_parts = []
                    char_count = 0
                    
                    # Prioritize spatial positioning and background info
                    priority_keywords = [
                        'positioned', 'located', 'background', 'foreground', 'center', 'left', 'right',
                        'behind', 'front', 'sitting', 'standing', 'lying', 'room', 'setting'
                    ]
                    
                    # Add high priority parts first
                    for part in parts:
                        if any(keyword in part.lower() for keyword in priority_keywords):
                            if char_count + len(part) + 2 <= 800:
                                essential_parts.append(part)
                                char_count += len(part) + 2
                    
                    # Add remaining parts if space allows
                    for part in parts:
                        if part not in essential_parts and char_count + len(part) + 2 <= 800:
                            essential_parts.append(part)
                            char_count += len(part) + 2
                    
                    text = ', '.join(essential_parts)
                
                logger.info(f"Generated spatial-focused prompt: {len(text)} characters")
                return {"success": True, "prompt": text, "analysis_type": "comprehensive"}
                
            else:
                logger.error("No valid response from Gemini API")
                return {"success": False, "error": "No analysis generated by AI service"}
                
        except Exception as e:
            logger.error(f"Comprehensive API call failed: {str(e)}")
            return {"success": False, "error": f"Analysis failed: {str(e)}"}