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
            
            # Enhanced comprehensive prompt preserving real positioning and details
            enhanced_prompt = """Analyze this image using the following detailed criteria and provide EXACTLY what you see:

1. Color Schemes: What are the dominant colors? Are there contrasts, harmonies, or complementary colors? How do the colors influence the mood, focus, or emotion?

2. Objects: What are the primary subjects or objects? What are their defining features or roles? Are there background or secondary elements that add context, symbolism, or depth?

3. Textures: What textures or surface qualities can you observe? Are there patterns, materials, or visual effects that enhance the tactile or visual experience?

4. Emotions: What is the emotional tone or atmosphere? Are there human or animal expressions, postures, or gestures that convey emotion? How does the emotional content align with the composition or lighting?

5. Composition: Is the image balanced, asymmetrical, or centered? Does it follow the rule of thirds, symmetry, or other compositional principles? What perspective or angle is used and how does it influence viewer perception?

6. Lighting: What is the light source? Is the lighting soft or harsh, warm or cool? How does it interact with the subjects and shadows?

7. Context: What is the setting? What time of day, season, or weather conditions are shown? Are there cultural, historical, or geographical clues?

8. Action: Is there any movement or implied motion? What are the subjects doing or interacting with? How do actions contribute to the story or message?

9. Style: What artistic style is used? Are there notable techniques? How does the style affect interpretation?

10. Narrative: What story or scenario is being told or implied? What themes, metaphors, or symbols are present?

11. Symbolism: Are there symbolic objects, gestures, or arrangements? What abstract ideas or cultural meanings might they represent?

12. Spatial Depth: How is a sense of space or distance created? Does the image feel flat or deep?

13. Focal Point: Where does the viewer's eye go first? How is attention drawn? Is the focal point clearly defined?

14. Line and Shape: What types of lines and shapes are used? How do they guide movement, emotion, or structure?

15. Typography: If text is present, what fonts or lettering styles are used? How does the typography relate to the visual tone?

16. Sound and Sensory Cues: Are there any sounds or sensory cues? How do they support the visual elements?

CRITICAL REQUIREMENTS:
- Describe EXACT positioning of people/objects (left, right, center, behind, in front, seated, standing, etc.)
- Include ALL visible details: clothing, hair, facial expressions, hand positions, body poses
- Preserve ALL background elements, colors, lighting, and setting details
- Keep ALL descriptive information - DO NOT remove or truncate important visual details
- Use precise, factual descriptions of what is actually visible
- Format as detailed comma-separated phrases capturing the complete visual analysis"""
            
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
                    "temperature": 0.05,
                    "topK": 5,
                    "topP": 0.2,
                    "maxOutputTokens": 1200
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
            
            # Only remove clear AI response prefixes, keep all content
            minimal_prefixes = [
                "Here's a comprehensive analysis of the image:",
                "Here's the comma-separated description:",
                "Based on the detailed criteria:",
                "Analysis:",
            ]
            
            for prefix in minimal_prefixes:
                if text.lower().startswith(prefix.lower()):
                    text = text[len(prefix):].strip()
                    break
            
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
            
            # Only remove minimal filler words that add no value
            minimal_fillers = ['clearly', 'obviously', 'evidently']
            for filler in minimal_fillers:
                text = re.sub(f'\\b{filler}\\b', '', text, flags=re.IGNORECASE)
            
            # Clean spacing
            text = re.sub(r'\s+', ' ', text)
            text = text.strip().rstrip('.,;:')
            
            # Ensure proper comma separation
            parts = [part.strip() for part in text.split(',') if part.strip()]
            text = ', '.join(parts)
            
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