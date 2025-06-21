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
            
            # Comprehensive visual analysis prompt
            comprehensive_prompt = """Analyze this image in comprehensive detail, covering ALL key aspects:

**1. IMAGE TYPE & STYLE:**
- Identify the type of image (human, animal, anime character, object, landscape, abstract art, architecture, etc.)
- Specify if it's realistic, stylized, cartoonish, or another artistic approach
- Note the artistic style (photography, digital art, painting, sketch, 3D render, etc.)

**2. SUBJECT ANALYSIS:**
For humans: Describe age range, apparent gender, ethnicity, facial features, hairstyle and color, clothing details, pose, body language, expression, and any distinguishing traits or accessories.

For anime characters: Describe the art style, facial features, eye color and style, hairstyle and color, clothing and outfit details, facial expression, pose, and background setting.

For objects: Describe type, shape, size, material, color, condition, function, and any visible text or markings.

For landscapes: Include setting type (urban, rural, natural), time of day, weather conditions, elements present (trees, mountains, water, animals), and overall mood.

For abstract art: Focus on colors, shapes, patterns, mood, symbolism, artistic technique, and emotional impact.

**3. COMPOSITION & TECHNICAL ELEMENTS:**
- Framing and perspective (close-up, wide shot, bird's eye, etc.)
- Focus and depth of field (what's sharp vs blurred)
- Symmetry, balance, and leading lines
- Rule of thirds application
- Foreground, middle ground, and background elements

**4. LIGHTING & ATMOSPHERE:**
- Light source(s) and direction (natural/artificial, front/back/side lighting)
- Quality of light (soft, harsh, diffused, dramatic)
- Shadows and highlights
- Time of day indicators
- Weather and atmospheric conditions

**5. COLOR & TEXTURE:**
- Dominant color palette and temperature (warm, cool, neutral)
- Color harmony and contrast
- Texture descriptions (smooth, rough, glossy, matte, fabric, metal, etc.)
- Overall tone (bright, dark, vibrant, muted, high contrast, low contrast)

**6. BACKGROUND & ENVIRONMENT:**
- Detailed background description
- Relationship between subject and environment
- Spatial relationships and positioning
- Environmental context and setting

**7. EMOTIONAL & SYMBOLIC IMPACT:**
- Mood and atmosphere conveyed
- Emotional response evoked
- Symbolic elements or themes
- Cultural or contextual significance
- Message or story being told

**8. MOVEMENT & ACTION:**
- Any motion or action captured
- Dynamic elements vs static composition
- Energy level and movement direction
- Interaction between elements

**9. TECHNICAL QUALITY & EFFECTS:**
- Image quality and clarity
- Any visual effects or filters applied
- Processing style (natural, HDR, vintage, etc.)
- Notable technical aspects

Provide a detailed, nuanced description that captures all visual, emotional, and contextual elements. Be specific about spatial relationships, precise colors, exact positioning, and observable details. Focus on what you can clearly see and analyze."""
            
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
                    "temperature": 0.2,
                    "topK": 20,
                    "topP": 0.8,
                    "maxOutputTokens": 2048
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean up the response while preserving comprehensive content
                logger.debug(f"Raw comprehensive analysis response: {text[:300]}...")
                
                # Remove common prefixes that don't add value
                prefixes_to_remove = [
                    "Here's a comprehensive analysis of the image:",
                    "Here's a detailed analysis:",
                    "Analysis of the image:",
                    "Comprehensive analysis:",
                    "**Analysis:**",
                    "Looking at this image,"
                ]
                
                for prefix in prefixes_to_remove:
                    if text.lower().startswith(prefix.lower()):
                        text = text[len(prefix):].strip()
                        break
                
                # Clean up markdown formatting while preserving structure
                text = text.replace('**', '').replace('*', '')
                
                # Ensure the analysis is comprehensive and detailed
                if len(text) < 200:
                    logger.warning(f"Analysis seems too brief: {len(text)} characters")
                
                logger.info(f"Generated comprehensive analysis: {len(text)} characters")
                return {"success": True, "prompt": text, "analysis_type": "comprehensive"}
                
            else:
                logger.error("No valid response from Gemini API")
                return {"success": False, "error": "No analysis generated by AI service"}
                
        except Exception as e:
            logger.error(f"Comprehensive API call failed: {str(e)}")
            return {"success": False, "error": f"Analysis failed: {str(e)}"}