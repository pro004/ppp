import os
import requests
import logging
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """Class to handle image analysis using Google Gemini Vision API."""
    
    def __init__(self):
        """Initialize the ImageAnalyzer with Gemini API configuration."""
        self.api_key = os.getenv("GEMINI_API_KEY", "AIzaSyCfdO3Mp0rwzgmtQFWMyxyCO6M6wFQMGIY")
        self.model = None
        self._configure_gemini()
    
    def _configure_gemini(self):
        """Configure the Gemini API client."""
        try:
            if not self.api_key:
                logger.error("GEMINI_API_KEY not found in environment variables")
                return
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini API configured successfully")
            
        except Exception as e:
            logger.error(f"Failed to configure Gemini API: {str(e)}")
            self.model = None
    
    def is_configured(self):
        """Check if the Gemini API is properly configured."""
        return self.model is not None
    
    def _validate_image_url(self, url):
        """Validate if the URL is properly formatted and accessible."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid URL format")
            
            # Enhanced headers to work with more domains
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            # Try HEAD request first, fallback to GET if needed
            try:
                response = requests.head(url, headers=headers, timeout=15, allow_redirects=True)
                response.raise_for_status()
                
                # Check content type from HEAD request
                content_type = response.headers.get('content-type', '').lower()
                if content_type and not any(img_type in content_type for img_type in ['image/', 'application/octet-stream']):
                    # Some servers don't return proper content-type in HEAD, try GET
                    response = requests.get(url, headers=headers, timeout=15, allow_redirects=True, stream=True)
                    response.raise_for_status()
                    
            except requests.RequestException:
                # Fallback to GET request if HEAD fails
                response = requests.get(url, headers=headers, timeout=15, allow_redirects=True, stream=True)
                response.raise_for_status()
            
            return True
            
        except requests.RequestException as e:
            raise ValueError(f"Unable to access the image URL: {str(e)}")
        except Exception as e:
            raise ValueError(f"Invalid image URL: {str(e)}")
    
    def _download_image(self, url):
        """Download and validate an image from URL."""
        try:
            self._validate_image_url(url)
            
            # Enhanced headers for better compatibility
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': url,
            }
            
            response = requests.get(url, headers=headers, timeout=30, stream=True)
            response.raise_for_status()
            
            # Load image to validate it
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Check image size and optimize for Gemini
            if image.size[0] > 4096 or image.size[1] > 4096:
                # Resize if too large while maintaining aspect ratio
                image.thumbnail((4096, 4096), Image.Resampling.LANCZOS)
            
            return image
            
        except requests.RequestException as e:
            raise ValueError(f"Failed to download image: {str(e)}")
        except Exception as e:
            raise ValueError(f"Invalid image file: {str(e)}")
    
    def _load_image_from_file(self, file_path):
        """Load and validate an image from file path."""
        try:
            if not os.path.exists(file_path):
                raise ValueError("Image file does not exist")
            
            image = Image.open(file_path)
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Check image size
            if image.size[0] > 4096 or image.size[1] > 4096:
                # Resize if too large
                image.thumbnail((4096, 4096), Image.Resampling.LANCZOS)
            
            return image
            
        except Exception as e:
            raise ValueError(f"Failed to load image file: {str(e)}")
    
    def _generate_prompt(self, image):
        """Generate a detailed, comprehensive prompt for the given image using Gemini."""
        if not self.is_configured():
            raise RuntimeError("Gemini API is not properly configured")
        
        try:
            # Ultra-precise prompt for clean, detailed image description
            system_prompt = """
            Describe this image with maximum precision and detail. Provide ONLY the pure visual description without any introductory phrases, explanations, or commentary. Focus on exact visual elements:

            Physical subjects: precise age, gender, build, posture, facial features, expressions, clothing details, accessories, hairstyles, actions, positions

            Environment: exact location type, architectural elements, furniture, objects, props, spatial relationships, background details

            Visual style: specific art style, medium, technique, rendering quality, artistic influences

            Lighting: light source locations, shadow patterns, highlight placement, contrast levels, atmospheric effects

            Colors: specific color names, saturation levels, temperature, gradients, color relationships

            Composition: framing, perspective, depth, focal points, visual balance, leading elements

            Textures and materials: surface qualities, material types, transparency, reflectivity, wear patterns

            Fine details: text, symbols, patterns, decorative elements, small objects, quality indicators

            Respond with ONLY the detailed visual description. No prefixes like "This image shows" or "The image depicts" - start directly with the description.
            """
            
            start_time = time.time()
            
            # Generate content using Gemini with enhanced parameters
            response = self.model.generate_content([system_prompt, image])
            
            elapsed_time = time.time() - start_time
            logger.info(f"Enhanced Gemini API call completed in {elapsed_time:.2f} seconds")
            
            if response and response.text:
                # Clean up the response text aggressively for pure description
                prompt = response.text.strip()
                
                # Remove quotes if present
                if prompt.startswith('"') and prompt.endswith('"'):
                    prompt = prompt[1:-1]
                
                # Comprehensive list of AI response prefixes to remove
                prefixes_to_remove = [
                    "Here's a detailed description of the image:",
                    "Here's a detailed description:",
                    "Here's the description:",
                    "This image shows:",
                    "This image depicts:",
                    "This image features:",
                    "This image contains:",
                    "The image shows:",
                    "The image depicts:",
                    "The image features:",
                    "The image contains:",
                    "The image displays:",
                    "I can see:",
                    "I observe:",
                    "Looking at this image:",
                    "In this image:",
                    "The scene shows:",
                    "The scene depicts:",
                    "This scene shows:",
                    "This artwork shows:",
                    "This illustration shows:",
                    "This photograph shows:",
                    "This digital art shows:",
                    "Based on the image:",
                    "From what I can see:",
                    "What I see is:",
                    "The visual content shows:",
                    "The visual shows:",
                    "Visually, this shows:",
                    "The picture shows:",
                    "The picture depicts:",
                    "**",
                    "*",
                ]
                
                # Remove prefixes case-insensitively
                for prefix in prefixes_to_remove:
                    if prompt.lower().startswith(prefix.lower()):
                        prompt = prompt[len(prefix):].strip()
                        break
                
                # Remove common suffixes that might indicate meta-commentary
                suffixes_to_remove = [
                    "Overall, this image",
                    "In summary,",
                    "To summarize,",
                    "This description captures",
                    "This prompt would allow",
                ]
                
                for suffix in suffixes_to_remove:
                    if suffix.lower() in prompt.lower():
                        index = prompt.lower().find(suffix.lower())
                        prompt = prompt[:index].strip()
                        break
                
                # Clean up any remaining markdown or formatting
                prompt = prompt.replace("**", "").replace("*", "")
                
                # Normalize whitespace and ensure single spaces
                prompt = ' '.join(prompt.split())
                
                # Remove any trailing periods that might be added by AI
                if prompt.endswith('.'):
                    prompt = prompt[:-1]
                
                logger.info(f"Generated clean prompt: {prompt[:150]}...")
                return prompt
            else:
                logger.error("Empty response from Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"Error generating enhanced prompt with Gemini: {str(e)}")
            raise RuntimeError(f"Failed to analyze image: {str(e)}")
    
    def analyze_from_url(self, image_url):
        """Analyze an image from URL and return a descriptive prompt."""
        try:
            logger.info(f"Downloading image from URL: {image_url}")
            image = self._download_image(image_url)
            
            logger.info("Generating prompt using Gemini API")
            prompt = self._generate_prompt(image)
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error analyzing image from URL: {str(e)}")
            raise
    
    def analyze_from_file(self, file_path):
        """Analyze an image from file path and return a descriptive prompt."""
        try:
            logger.info(f"Loading image from file: {file_path}")
            image = self._load_image_from_file(file_path)
            
            logger.info("Generating prompt using Gemini API")
            prompt = self._generate_prompt(image)
            
            return prompt
            
        except Exception as e:
            logger.error(f"Error analyzing image from file: {str(e)}")
            raise
