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
            
            # Enhanced comprehensive prompt for exact object detection
            comprehensive_prompt = """Look at this image carefully and describe EXACTLY what you observe. Be factual and specific.

MANDATORY SECTIONS:

IMAGE QUALITY: resolution quality, lighting brightness, focus sharpness, any grain or noise

EXACT OBJECTS PRESENT:
- Count and identify each person/animal/object you see
- Describe their precise positioning and what they're doing
- Specify exact clothing items, colors, and accessories visible
- Detail facial features, hair, skin tone, expressions as shown
- List any objects being held, touched, or interacted with

PRECISE POSITIONING:
- Primary posture (sitting/standing/lying - specify exactly how)
- Head direction and tilt, eye gaze direction
- Arm positions, hand placement, finger positions
- Leg positioning, foot placement, weight distribution
- Spatial relationships between objects/people

BACKGROUND DETAILS:
- Exact colors visible, specific objects present
- Architectural elements, furniture, decorations
- Lighting sources, shadows, reflections
- Text, signs, or writing visible

16-POINT ANALYSIS (only include if clearly visible):
1. Color Schemes: dominant colors, color harmony, contrasts
2. Objects: primary subjects, secondary objects, their characteristics
3. Textures: fabric, material, surface qualities you can see
4. Emotions: facial expressions, body language, mood conveyed
5. Composition: balance, rule of thirds, visual structure
6. Lighting: light direction, intensity, shadows, highlights
7. Context: time of day, location type, setting details
8. Action: movements, activities, interactions happening
9. Style: photographic/artistic style, technique used
10. Narrative: story being told, relationship between elements
11. Symbolism: symbolic objects, meaningful arrangements
12. Spatial Depth: foreground/background layers, perspective
13. Focal Points: what draws attention, visual hierarchy
14. Line & Shape: strong lines, geometric shapes, patterns
15. Typography: fonts, text style, lettering visible
16. Sensory Cues: atmosphere, implied sounds, tactile qualities

CRITICAL: Describe only what you actually see. Do not add, assume, or modify anything."""
            
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
                    "temperature": 0.02,
                    "topK": 5,
                    "topP": 0.3,
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
                
                # Ensure optimal length focusing on accuracy
                if len(text) > 800:
                    # Smart truncation while keeping essential elements
                    parts = text.split(', ')
                    essential_parts = []
                    char_count = 0
                    
                    # Prioritize factual positioning and detailed visual elements
                    priority_keywords = [
                        'seated', 'positioned', 'center', 'left', 'right', 'behind', 'front', 'woman', 'man',
                        'anime', 'style', 'hair', 'clothing', 'background', 'lighting', 'eyes', 'expression',
                        'hands', 'arms', 'legs', 'color', 'digital', 'illustration', 'soft', 'warm'
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