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
            
            # Enhanced prompt focusing on accurate body positioning and language
            enhanced_prompt = """Create a detailed comma-separated description of this image. Be extremely precise about body positioning and body language.

CRITICAL RULE: DESCRIBE THE IMAGE AS IT IS - DO NOT CHANGE OR MODIFY ANYTHING

BODY POSITIONING (Critical - be accurate, only describe visible parts):
- Exact posture: only describe if clearly visible - sitting, standing, lying, leaning, crouching, kneeling (specify surface/object only if visible)
- Spine alignment: straight, curved, arched, slouched, tilted (only if visible)
- Shoulder position: level, raised, dropped, rolled forward, back (only if visible)
- Head orientation: facing forward, turned left/right, tilted, looking up/down (only if visible)
- Arm placement: at sides, crossed, raised, extended, bent, one up/one down (only if arms are visible)
- Hand position: describe exact hand placement - open palms, closed fists, pointing direction, touching specific objects or body parts, hand gestures, finger positions, what each hand is doing separately (only if hands are clearly visible)
- Leg positioning: together, apart, crossed, bent, straight, weight distribution (only if legs are visible)
- Foot placement: flat, on tiptoes, one foot forward, turned in/out (only if feet are visible)
- IMPORTANT: Do not describe body parts that are cropped out, hidden, or not clearly shown - describe exactly what you see without changing anything

BODY LANGUAGE (Critical - observe actual expression):
- Overall energy: relaxed, tense, confident, nervous, alert, tired
- Openness: open posture vs closed/defensive posture
- Engagement: actively engaged, withdrawn, distracted, focused
- Confidence level: confident stance vs uncertain body language
- Emotional state visible through posture: happy, sad, angry, surprised, neutral

PHYSICAL DETAILS:
- Hair color and style exactly as visible
- Eye state: open, closed, looking direction, expression
- Clothing items and colors specifically visible
- Skin tone as actually appears
- Body parts positioning: describe each visible limb's exact position and orientation as they actually appear in the image
- Visible body proportions and spatial relationships only for what is clearly shown
- Object positioning: describe visible body objects (arms, legs, torso, head) only as they actually appear, no assumptions
- Any accessories or objects being held/worn

BACKGROUND DETAILS (Critical - be comprehensive and accurate):
- Specific background objects: furniture (chairs, tables, beds, shelves), walls, windows, doors, decorative items, plants, artwork
- Background colors and patterns: exact color names (pure white, cream, light blue, dark gray, etc.), color intensity (bright, muted, pastel, vibrant), patterns (stripes, dots, floral, geometric), textures (smooth paint, rough texture, fabric, wood grain), wall finishes (painted walls, wallpaper, brick, wood paneling)
- Architectural elements: ceiling details (height, color, texture), floor type (hardwood, carpet, tile, concrete), moldings, baseboards, crown molding, fixtures (light fixtures, outlets, switches)
- Environmental setting: indoor/outdoor specification, room type (bedroom, living room, kitchen, office, studio), natural elements (trees, sky, grass), weather conditions if outdoor
- Background depth: multiple layers - what's immediately behind subject, mid-distance objects, far background elements
- Background lighting: natural vs artificial light, shadows cast on walls, reflections on surfaces, light sources visible (lamps, windows), brightness variations across background
- Background text or signage: any visible words, letters, symbols, logos, signs, posters, books
- Background spatial relationship: detailed description of what's positioned to the left, right, above, and below the main subject, including distance and relative positioning

SETTING & STYLE:
- Lighting quality and direction
- Color palette and artistic style
- Overall composition and framing
- Artistic medium and technique

Format as comma-separated phrases. Be factual about what you actually see. Do not assume or add details not clearly visible."""
            
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