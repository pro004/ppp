import os
import requests
import logging
import base64
import json
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

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
            
            # Comprehensive 10-point analysis prompt
            prompt = """Analyze this image comprehensively and describe using comma-separated tags covering:

1. Image Type: human/anime/object/landscape/abstract/architecture/animal/nature, style (realistic/stylized/cartoonish)
2. Subject Details: age, gender, ethnicity, facial features, hairstyle, clothing, accessories, expression, pose
3. Composition: framing (close-up/wide-angle), focus, perspective, lighting (natural/artificial, shadows, highlights)
4. Colors & Textures: dominant colors, contrast, saturation, surface textures, tone
5. Background & Environment: setting, depth, background elements
6. Artistic Style: medium, art movement, effects, technique
7. Emotional Impact: mood, feelings evoked, symbolism, cultural significance
8. Movement & Action: static/dynamic, motion elements, gestures, energy
9. Composition Techniques: rule of thirds, symmetry, leading lines, balance
10. Unique Features: special objects, interactions, framing details

Generate detailed comma-separated tags covering all visible aspects."""
            
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
                    "temperature": 0.2,
                    "topK": 20,
                    "topP": 0.7,
                    "maxOutputTokens": 500
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Improved cleaning that preserves actual content
                logger.debug(f"Raw API response: {text[:200]}...")
                
                # Only remove clear prefixes, not content
                simple_prefixes = [
                    "Here's a comprehensive analysis of the image:",
                    "Here's a detailed analysis:",
                    "Analysis:",
                    "Tags:",
                ]
                
                for prefix in simple_prefixes:
                    if text.startswith(prefix):
                        text = text[len(prefix):].strip()
                        break
                
                # Clean numbered format and extract tags
                if any(marker in text for marker in ['1.', '2.', '**1.', '**2.']):
                    # Remove markdown formatting first
                    text = text.replace('**', '').replace('*', '')
                    
                    # Extract content from numbered sections
                    import re
                    # Find all content after numbers and colons
                    pattern = r'\d+\.\s*[^:]*:\s*([^0-9]+?)(?=\d+\.|$)'
                    matches = re.findall(pattern, text, re.DOTALL)
                    
                    if matches:
                        # Join all extracted content
                        extracted_content = []
                        for match in matches:
                            cleaned = match.strip().replace('\n', ' ')
                            if cleaned:
                                extracted_content.append(cleaned)
                        text = ', '.join(extracted_content)
                    else:
                        # Fallback: remove section headers manually
                        lines = text.split('\n')
                        content_lines = []
                        for line in lines:
                            line = line.strip()
                            if line and not any(skip in line for skip in [
                                '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.',
                                'Image Type:', 'Subject Details:', 'Composition:'
                            ]):
                                content_lines.append(line)
                        text = ' '.join(content_lines)
                
                # Basic formatting cleanup
                text = text.replace('**', '').replace('*', '')
                text = text.replace('; ', ', ').replace(': ', ', ')
                text = ' '.join(text.split())
                text = text.strip().rstrip('.,;:')
                
                # Final validation
                if len(text) < 30:
                    logger.error(f"Final text too short after cleaning: '{text}'")
                    return None
                
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
                
                # Smart truncation while preserving comprehensive analysis
                if len(text) > 680:
                    # Split by commas and prioritize important tags
                    parts = text.split(', ')
                    essential_tags = []
                    char_count = 0
                    
                    # Prioritize essential descriptors first
                    priority_keywords = [
                        'human', 'anime', 'object', 'landscape', 'realistic', 'stylized',
                        'male', 'female', 'age', 'hair', 'clothing', 'expression',
                        'foreground', 'background', 'center', 'left', 'right',
                        'lighting', 'colors', 'composition', 'mood'
                    ]
                    
                    # Add high priority tags first
                    for part in parts:
                        part = part.strip()
                        if any(keyword in part.lower() for keyword in priority_keywords):
                            tag_length = len(part) + (2 if essential_tags else 0)
                            if char_count + tag_length <= 675:
                                essential_tags.append(part)
                                char_count += tag_length
                    
                    # Add remaining tags if space allows
                    for part in parts:
                        part = part.strip()
                        if part not in essential_tags:
                            tag_length = len(part) + (2 if essential_tags else 0)
                            if char_count + tag_length <= 675:
                                essential_tags.append(part)
                                char_count += tag_length
                            else:
                                break
                    
                    text = ', '.join(essential_tags)
                
                # Final character count check
                logger.info(f"Comprehensive analysis length: {len(text)} characters")
                
                logger.info(f"Generated optimized prompt: {text[:100]}...")
                return text
            else:
                logger.error("No valid response from Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            return None