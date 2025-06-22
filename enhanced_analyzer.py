import os
import requests
import logging
import base64
import json
import re
from PIL import Image
from io import BytesIO

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class EnhancedImageAnalyzer:
    """
    Enhanced image analyzer incorporating comprehensive visual analysis criteria
    for superior accuracy and detail in image descriptions.
    """
    
    def __init__(self):
        """Initialize with API key."""
        self.api_key = "AIzaSyCfdO3Mp0rwzgmtQFWMyxyCO6M6wFQMGIY"
        if not self.api_key or self.api_key.strip() == "":
            logger.warning("GEMINI_API_KEY not configured - enhanced analysis will not work")
        else:
            logger.info("Enhanced analyzer initialized successfully with API key")
    
    def is_configured(self):
        """Check if API key is available."""
        return bool(self.api_key)
    
    def analyze_from_url(self, image_url):
        """Analyze image from URL with enhanced comprehensive analysis."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            image_data = base64.b64encode(response.content).decode('utf-8')
            mime_type = response.headers.get('content-type', 'image/jpeg')
            
            return self._analyze_with_enhanced_api(image_data, mime_type)
            
        except Exception as e:
            logger.error(f"Error analyzing image from URL: {str(e)}")
            return {"success": False, "error": f"Failed to analyze image: {str(e)}"}
    
    def analyze_from_file(self, file_path):
        """Analyze image from file with enhanced comprehensive analysis."""
        try:
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
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
            
            return self._analyze_with_enhanced_api(image_data, mime_type)
            
        except Exception as e:
            logger.error(f"Error analyzing image from file: {str(e)}")
            return {"success": False, "error": f"Failed to analyze image: {str(e)}"}
    
    def _analyze_with_enhanced_api(self, image_data, mime_type):
        """Enhanced API call incorporating comprehensive 16-point analysis criteria."""
        try:
            if not self.api_key:
                raise RuntimeError("API key not configured")
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.api_key}"
            
            # Enhanced prompt focusing on accurate object positioning
            enhanced_prompt = """Provide a detailed description of the image, focusing on all aspects of the visual content. Analyze the image Shot type, Run multiple tests, person gender , Camera angle, Setting, Perspective distortions, Dynamic elements, Spatial relationships, Position in frame, Sharpness and Clarity, Noise and Graininess, Pixelation,  Compression Artifacts, focus and depth of field, lighting, focus, and clarity, Clothing, accessories, objects held, object Pose and Body Positioning, including what objects or people are present and their exact locations in the frame, Physical traits , their facial reaction, facial possition, as well as their body posture, arm and leg positioning, and head orientation. Include appearance details such as hair color and style, eye state, skin tone, facial expression, clothing, and accessories, along with any objects being held or interacted with, background, describe the elements of background , background colors, background lighting, and spatial relationships, Evaluate the composition, highlighting balance, symmetry, or asymmetry, and provide insights into any emotional tone or context present in the image, the applicable, discuss the artistic style (e.g., anime, realism, digital art), textures, patterns, any more object if present then tell, image backgroud,  and any symbolism or narrative conveyed through the image. Finally, ensure that the description remains focused on what is observable, without assuming or adding details not visible in the image. Prioritize clarity, accuracy, and thoroughness in capturing the visual elements, with removing the unnecessary things, including any symbolic or emotional undertones that the image may convey. Just give the prompt only"""
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": enhanced_prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": image_data
                            }
                        }
                    ]
                }],
                "generationConfig": {
                    "temperature": 0.5,
                    "topK": 5,
                    "topP": 0.2,
                    "maxOutputTokens": 900
                }
            }
            
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, headers=headers, json=payload, timeout=90)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                raw_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean and optimize the response
                cleaned_text = self._clean_analysis_response(raw_text)
                
                if cleaned_text and len(cleaned_text) >= 100:
                    logger.info(f"Generated enhanced analysis: {len(cleaned_text)} characters")
                    return {"success": True, "prompt": cleaned_text, "analysis_type": "enhanced_comprehensive"}
                else:
                    logger.error("Enhanced analysis produced insufficient content")
                    return {"success": False, "error": "Analysis generated insufficient descriptive content"}
                
            else:
                logger.error("No valid response from Gemini API")
                return {"success": False, "error": "No analysis generated by AI service"}
                
        except Exception as e:
            logger.error(f"Enhanced API call failed: {str(e)}")
            return {"success": False, "error": f"Analysis failed: {str(e)}"}
    
    def _clean_analysis_response(self, raw_text):
        """Preserve detailed analysis while cleaning only unnecessary formatting."""
        try:
            text = raw_text.strip()
            
            # Remove all AI response prefixes and formatting text
            prefixes_to_remove = [
                "Here's a detailed analysis of the image, formatted as requested:",
                "Here's a comprehensive analysis of the image:",
                "Here's the comma-separated description:",
                "Based on the detailed criteria:",
                "Here's a detailed analysis:",
                "Here's the analysis:",
                "Analysis of the image:",
                "Detailed analysis:",
                "Analysis:",
                "Here's what I see:",
                "The image shows:",
                "Looking at this image:",
                "In this image:",
                "I can see:",
                "This image contains:",
                "The visual analysis reveals:",
                "Upon examination:",
                "Visual description:",
                "Image description:",
                "Formatted as requested:",
                "As requested:",
            ]
            
            # Remove prefixes more aggressively
            for prefix in prefixes_to_remove:
                if text.lower().startswith(prefix.lower()):
                    text = text[len(prefix):].strip()
                    break
            
            # Also check for and remove any remaining prefixes at the start
            text = re.sub(r'^(here\'s|this is|the image shows?|i can see|looking at|in this image|upon examination|visual description|image description)[^a-z]*', '', text, flags=re.IGNORECASE)
            
            # Remove markdown formatting but preserve content
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
            text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
            
            # Handle numbered sections - convert to comma-separated format while preserving all details
            # Replace numbered sections with their content
            section_patterns = [
                (r'1\.\s*Color Schemes?:?\s*([^2]+)', r'\1'),
                (r'2\.\s*Objects?:?\s*([^3]+)', r'\1'),
                (r'3\.\s*Textures?:?\s*([^4]+)', r'\1'),
                (r'4\.\s*Emotions?:?\s*([^5]+)', r'\1'),
                (r'5\.\s*Composition:?\s*([^6]+)', r'\1'),
                (r'6\.\s*Lighting:?\s*([^7]+)', r'\1'),
                (r'7\.\s*Context:?\s*([^8]+)', r'\1'),
                (r'8\.\s*Action:?\s*([^9]+)', r'\1'),
                (r'9\.\s*Style:?\s*([^1][^0]?[^.]*)', r'\1'),
                (r'10\.\s*Narrative:?\s*([^1][^1]?[^.]*)', r'\1'),
                (r'11\.\s*Symbolism:?\s*([^1][^2]?[^.]*)', r'\1'),
                (r'12\.\s*Spatial Depth:?\s*([^1][^3]?[^.]*)', r'\1'),
                (r'13\.\s*Focal Point:?\s*([^1][^4]?[^.]*)', r'\1'),
                (r'14\.\s*Line and Shape:?\s*([^1][^5]?[^.]*)', r'\1'),
                (r'15\.\s*Typography:?\s*([^1][^6]?[^.]*)', r'\1'),
                (r'16\.\s*Sound and Sensory:?\s*(.*)', r'\1'),
            ]
            
            extracted_content = []
            for pattern, replacement in section_patterns:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    if content:
                        extracted_content.append(content)
            
            # If we found structured content, use it; otherwise use original
            if extracted_content:
                text = ' '.join(extracted_content)
            
            # Convert newlines and multiple spaces to single spaces
            text = re.sub(r'\n+', ' ', text)
            text = re.sub(r'\s+', ' ', text)
            
            # Convert sentences to comma-separated format while preserving all details
            # Split by periods and join with commas
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            text = ', '.join(sentences)
            
            # Clean up punctuation but preserve important details
            text = re.sub(r'[;:]+', ',', text)  # Convert semicolons and colons to commas
            text = re.sub(r',\s*,+', ',', text)  # Remove multiple consecutive commas
            text = re.sub(r'\s*,\s*', ', ', text)  # Standardize comma spacing
            
            # Remove common filler phrases that add no descriptive value
            filler_phrases = [
                'clearly visible', 'obviously', 'evidently', 'as you can see',
                'it appears that', 'it seems that', 'we can observe',
                'what we see is', 'what is visible', 'can be seen',
                'appears to be', 'seems to be', 'looks like'
            ]
            for filler in filler_phrases:
                text = re.sub(f'\\b{re.escape(filler)}\\b', '', text, flags=re.IGNORECASE)
            
            # Clean spacing
            text = re.sub(r'\s+', ' ', text)
            text = text.strip().rstrip('.,;:')
            
            # Ensure proper comma separation
            parts = [part.strip() for part in text.split(',') if part.strip()]
            text = ', '.join(parts)
            
            # Smart truncation to keep under 900 characters while preserving body details
            if len(text) > 900:
                text = self._smart_truncate_detailed(text, 900)
            
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning analysis response: {str(e)}")
            return raw_text
    
    def _smart_truncate_detailed(self, text, max_length):
        """Intelligently truncate while preserving essential positioning and visual details."""
        if len(text) <= max_length:
            return text
        
        parts = text.split(', ')
        essential_parts = []
        char_count = 0
        
        # High priority keywords for essential elements including detailed body language
        high_priority = [
            'woman', 'man', 'person', 'girl', 'boy', 'character', 'figure',
            'left', 'right', 'center', 'behind', 'front', 'seated', 'standing', 'positioned',
            'posture', 'stance', 'lean', 'tilt', 'orientation', 'body', 'pose', 'shoulder', 'spine',
            'confident', 'relaxed', 'tense', 'open', 'closed', 'dominant', 'submissive', 'defensive', 'inviting',
            'assertive', 'withdrawn', 'energetic', 'tired', 'alert', 'distracted',
            'eyes', 'mouth', 'smiling', 'frowning', 'expression', 'facial', 'eyebrows', 'cheeks', 'jaw',
            'squinting', 'wide', 'narrow', 'parted', 'pursed', 'raised', 'lowered', 'furrowed', 'clenched',
            'arms', 'hands', 'crossed', 'gesturing', 'pointing', 'holding', 'fidgeting', 'reaching', 'welcoming',
            'legs', 'straight', 'bent', 'wide', 'close', 'weight', 'balanced', 'shifted',
            'head', 'tension', 'breathing', 'muscle', 'energy',
            'hair', 'face', 'clothing', 'outfit', 'dress', 'shirt',
            'anime', 'digital', 'realistic', 'illustration', 'portrait'
        ]
        
        # Medium priority keywords
        medium_priority = [
            'background', 'foreground', 'colors', 'lighting', 'shadows', 'composition',
            'warm', 'cool', 'soft', 'bright', 'dark', 'light', 'mood', 'atmosphere'
        ]
        
        # Add high priority parts first
        for part in parts:
            part = part.strip()
            if any(keyword in part.lower() for keyword in high_priority):
                needed_chars = len(part) + (2 if essential_parts else 0)
                if char_count + needed_chars <= max_length:
                    essential_parts.append(part)
                    char_count += needed_chars
        
        # Add medium priority parts if space allows
        for part in parts:
            part = part.strip()
            if part not in essential_parts and any(keyword in part.lower() for keyword in medium_priority):
                needed_chars = len(part) + 2
                if char_count + needed_chars <= max_length:
                    essential_parts.append(part)
                    char_count += needed_chars
        
        # Add any remaining parts if space allows
        for part in parts:
            part = part.strip()
            if part not in essential_parts:
                needed_chars = len(part) + 2
                if char_count + needed_chars <= max_length:
                    essential_parts.append(part)
                    char_count += needed_chars
                else:
                    break
        
        return ', '.join(essential_parts)