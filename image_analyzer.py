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
            
            # Check if URL is accessible
            response = requests.head(url, timeout=10, allow_redirects=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                raise ValueError("URL does not point to an image")
            
            return True
            
        except requests.RequestException as e:
            raise ValueError(f"Unable to access the image URL: {str(e)}")
        except Exception as e:
            raise ValueError(f"Invalid image URL: {str(e)}")
    
    def _download_image(self, url):
        """Download and validate an image from URL."""
        try:
            self._validate_image_url(url)
            
            response = requests.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Load image to validate it
            image = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Check image size
            if image.size[0] > 4096 or image.size[1] > 4096:
                # Resize if too large
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
        """Generate a descriptive prompt for the given image using Gemini."""
        if not self.is_configured():
            raise RuntimeError("Gemini API is not properly configured")
        
        try:
            # Create a detailed prompt for better image analysis
            system_prompt = """
            Analyze this image and create a detailed, descriptive prompt that captures:
            1. The main subject(s) and their actions
            2. The setting and environment
            3. Visual style, lighting, and mood
            4. Colors, composition, and artistic elements
            5. Any notable details or objects
            
            Provide a clear, comprehensive description in 2-3 sentences that would help someone recreate or understand this image. Focus on being descriptive and accurate rather than interpretive.
            """
            
            start_time = time.time()
            
            # Generate content using Gemini
            response = self.model.generate_content([system_prompt, image])
            
            elapsed_time = time.time() - start_time
            logger.info(f"Gemini API call completed in {elapsed_time:.2f} seconds")
            
            if response and response.text:
                # Clean up the response text
                prompt = response.text.strip()
                
                # Remove any potential prefixes or formatting
                if prompt.startswith('"') and prompt.endswith('"'):
                    prompt = prompt[1:-1]
                
                logger.info(f"Generated prompt: {prompt[:100]}...")
                return prompt
            else:
                logger.error("Empty response from Gemini API")
                return None
                
        except Exception as e:
            logger.error(f"Error generating prompt with Gemini: {str(e)}")
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
