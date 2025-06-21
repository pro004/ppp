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
            
            # Streamlined prompt matching enhanced analyzer
            prompt = """Analyze this image and describe exactly what you see. Use comma-separated format.

IMAGE QUALITY: resolution, clarity, lighting quality, focus
BODY POSITIONING: posture, arm/hand positions, leg stance
APPEARANCE: hair, eyes, clothing, accessories  
BACKGROUND: objects, colors, lighting, setting
CRITERIA: include only clearly present elements

Describe visible objects even if they don't match standard criteria."""
            
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
                
                # Clean response and extract meaningful tags
                text = text.replace('**', '').replace('*', '')
                
                # If structured response, extract tag content only
                if any(indicator in text.lower() for indicator in ['what type:', 'who/what:', 'wearing:', 'doing:', 'where:']):
                    parts = text.split('\n')
                    clean_tags = []
                    
                    for part in parts:
                        if ':' in part:
                            tag_content = part.split(':', 1)[1].strip()
                            if tag_content and not tag_content.lower().startswith(('what', 'who', 'where')):
                                clean_tags.append(tag_content)
                    
                    if clean_tags:
                        text = ', '.join(clean_tags)
                
                # Remove common filler phrases that add no value
                unwanted_phrases = [
                    'clearly visible', 'can be seen', 'appears to be', 'seems to be',
                    'what you actually see', 'actual', 'visible in the image',
                    'in this image', 'the image shows'
                ]
                
                for phrase in unwanted_phrases:
                    text = text.replace(phrase, '')
                
                # Clean formatting
                text = text.replace('; ', ', ').replace(': ', ', ')
                text = text.replace(' and ', ', ').replace('  ', ' ')
                text = ' '.join(text.split()).strip().rstrip('.,;:')
                
                # Validate final result
                if len(text) < 20:
                    logger.error(f"Processed text too short: '{text}'")
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