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
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            # Comprehensive analysis prompt based on the 16 detailed criteria
            enhanced_prompt = """Analyze this image using comprehensive visual criteria and provide a clean, accurate description. Focus only on what is directly observable:

COLOR ANALYSIS: Identify dominant colors, color harmonies, contrasts, and their emotional impact on the composition.

OBJECT IDENTIFICATION: List primary subjects, secondary elements, their defining features, positioning, and contextual relationships.

TEXTURE & MATERIALS: Describe visible textures, surface qualities, patterns, and material properties that enhance visual experience.

EMOTIONAL TONE: Analyze the atmosphere, mood, expressions, gestures, and emotional content conveyed through composition.

COMPOSITION STRUCTURE: Examine balance, symmetry, rule of thirds application, perspective angle, and viewer perception influence.

LIGHTING QUALITY: Assess light sources, intensity, warmth/coolness, shadow interaction, and overall lighting effects.

CONTEXTUAL SETTING: Determine indoor/outdoor environment, time indicators, weather conditions, cultural or geographical elements.

ACTION & MOVEMENT: Identify any motion, interactions, activities, and how they contribute to the narrative.

ARTISTIC STYLE: Classify the style (realism, digital art, illustration), techniques used, and their interpretative impact.

NARRATIVE ELEMENTS: Describe the story being told, themes, metaphors, and potential viewer interpretations.

SYMBOLIC CONTENT: Note symbolic objects, gestures, arrangements, and their cultural or abstract meanings.

SPATIAL DEPTH: Analyze depth creation through overlapping, scaling, perspective, and dimensional qualities.

FOCAL POINTS: Identify where attention is drawn, how focus is achieved, and clarity of visual hierarchy.

LINE & SHAPE: Describe line types, shapes used, and their role in guiding movement and structure.

TYPOGRAPHY: If text exists, analyze font styles, relationship to visual content, and functional role.

SENSORY ELEMENTS: Note any implied sounds, textures, or sensory cues that enhance immersion.

REQUIREMENTS:
- Generate comma-separated descriptive phrases
- Use only factual, observable details
- Maintain accuracy over assumptions
- Keep descriptions clean and precise
- Focus on visual elements that enhance understanding
- Target 600-800 characters for optimal detail
- Exclude filler words and redundant phrases

Format: Clean comma-separated phrases describing the comprehensive visual analysis."""
            
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
                    "temperature": 0.1,
                    "topK": 8,
                    "topP": 0.4,
                    "maxOutputTokens": 700
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
                
                if cleaned_text and len(cleaned_text) >= 50:
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
        """Clean and optimize the analysis response for maximum clarity and accuracy."""
        try:
            text = raw_text.strip()
            
            # Remove common AI response prefixes
            prefixes_to_remove = [
                "Here's a comprehensive analysis of the image:",
                "Here's the comma-separated description:",
                "The comma-separated description is:",
                "Based on the comprehensive visual criteria:",
                "Analysis of the image:",
                "Description:",
                "Here's the analysis:",
                "The image shows:",
                "Looking at this image:",
            ]
            
            for prefix in prefixes_to_remove:
                if text.lower().startswith(prefix.lower()):
                    text = text[len(prefix):].strip()
                    break
            
            # Remove markdown formatting and bullet points
            text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
            text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
            text = re.sub(r'^[-•]\s*', '', text, flags=re.MULTILINE)  # Bullet points
            text = re.sub(r'^\d+\.\s*', '', text, flags=re.MULTILINE)  # Numbered lists
            
            # Remove section headers if they exist
            section_patterns = [
                r'COLOR ANALYSIS:?[^\n]*\n?',
                r'OBJECT IDENTIFICATION:?[^\n]*\n?',
                r'TEXTURE & MATERIALS:?[^\n]*\n?',
                r'EMOTIONAL TONE:?[^\n]*\n?',
                r'COMPOSITION:?[^\n]*\n?',
                r'LIGHTING:?[^\n]*\n?',
                r'CONTEXT:?[^\n]*\n?',
                r'ACTION:?[^\n]*\n?',
                r'STYLE:?[^\n]*\n?',
                r'NARRATIVE:?[^\n]*\n?',
                r'SYMBOLIC:?[^\n]*\n?',
                r'SPATIAL:?[^\n]*\n?',
                r'FOCAL:?[^\n]*\n?',
                r'LINE:?[^\n]*\n?',
                r'TYPOGRAPHY:?[^\n]*\n?',
                r'SENSORY:?[^\n]*\n?'
            ]
            
            for pattern in section_patterns:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
            
            # Convert newlines to commas and clean spacing
            text = re.sub(r'\n+', ', ', text)
            text = re.sub(r'\s+', ' ', text)
            
            # Remove filler phrases that add no descriptive value
            filler_phrases = [
                'can be seen', 'appears to be', 'seems to be', 'looks like',
                'it appears', 'we can see', 'visible in the image', 'in this image',
                'the image shows', 'what we see', 'as observed', 'clearly visible',
                'that can be observed', 'which is visible', 'that appears',
                'which seems', 'as seen in', 'evident in'
            ]
            
            for phrase in filler_phrases:
                text = re.sub(f'\\b{re.escape(phrase)}\\b', '', text, flags=re.IGNORECASE)
            
            # Clean punctuation and formatting
            text = re.sub(r'[;:]+', ',', text)  # Convert semicolons and colons to commas
            text = re.sub(r',\s*,+', ',', text)  # Remove multiple consecutive commas
            text = re.sub(r'\s*,\s*', ', ', text)  # Standardize comma spacing
            text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
            
            # Ensure proper comma separation
            parts = [part.strip() for part in text.split(',') if part.strip()]
            text = ', '.join(parts)
            
            # Optimize length while preserving essential details
            if len(text) > 800:
                text = self._smart_truncate(text, 800)
            
            # Final cleanup
            text = text.strip().rstrip('.,;:')
            
            return text
            
        except Exception as e:
            logger.error(f"Error cleaning analysis response: {str(e)}")
            return raw_text
    
    def _smart_truncate(self, text, max_length):
        """Intelligently truncate text while preserving the most important descriptive elements."""
        if len(text) <= max_length:
            return text
        
        parts = text.split(', ')
        essential_parts = []
        char_count = 0
        
        # Priority keywords for essential visual elements
        priority_keywords = [
            # Subject and composition
            'woman', 'man', 'person', 'character', 'figure', 'subject',
            'center', 'foreground', 'background', 'positioned', 'seated', 'standing',
            
            # Visual style and medium
            'anime', 'digital', 'illustration', 'painting', 'photograph', 'realistic',
            'stylized', 'artistic', 'portrait', 'landscape',
            
            # Key visual elements
            'hair', 'eyes', 'face', 'expression', 'clothing', 'outfit',
            'colors', 'lighting', 'shadows', 'composition', 'perspective',
            
            # Emotional and atmospheric
            'mood', 'atmosphere', 'emotion', 'warm', 'cool', 'soft', 'bright',
            'dramatic', 'peaceful', 'energetic'
        ]
        
        # First pass: Add parts with priority keywords
        for part in parts:
            part = part.strip()
            if any(keyword in part.lower() for keyword in priority_keywords):
                if char_count + len(part) + 2 <= max_length:
                    essential_parts.append(part)
                    char_count += len(part) + 2
        
        # Second pass: Add remaining parts if space allows
        for part in parts:
            part = part.strip()
            if part not in essential_parts:
                if char_count + len(part) + 2 <= max_length:
                    essential_parts.append(part)
                    char_count += len(part) + 2
                else:
                    break
        
        return ', '.join(essential_parts)