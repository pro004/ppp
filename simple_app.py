import os
import logging
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import tempfile
import uuid
import requests
from PIL import Image
import base64
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff', 'tif', 'svg', 'ico', 'heic', 'heif', 'avif'}
UPLOAD_FOLDER = tempfile.gettempdir()

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class SimpleImageAnalyzer:
    """Simple image analyzer that works without heavy dependencies."""
    
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyDaBBWSgg0NnzLvh0m-N9Jhy1i-CuzUhV4")
        
    def is_configured(self):
        """Check if API key is available."""
        return bool(self.api_key)
    
    def analyze_from_url(self, image_url):
        """Analyze image from URL using direct API call."""
        try:
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Convert to base64
            image_data = base64.b64encode(response.content).decode('utf-8')
            
            return self._analyze_with_api(image_data, response.headers.get('content-type', 'image/jpeg'))
            
        except Exception as e:
            logger.error(f"Error analyzing image from URL: {str(e)}")
            return {"success": False, "error": f"Failed to analyze image: {str(e)}"}
    
    def analyze_from_file(self, file_path):
        """Analyze image from file using direct API call."""
        try:
            with open(file_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Detect mime type from file extension
            ext = os.path.splitext(file_path)[1].lower()
            mime_type = {
                '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.png': 'image/png', '.gif': 'image/gif',
                '.webp': 'image/webp', '.bmp': 'image/bmp'
            }.get(ext, 'image/jpeg')
            
            return self._analyze_with_api(image_data, mime_type)
            
        except Exception as e:
            logger.error(f"Error analyzing image from file: {str(e)}")
            return {"success": False, "error": f"Failed to analyze image: {str(e)}"}
    
    def _analyze_with_api(self, image_data, mime_type):
        """Direct API call to Gemini."""
        try:
            import json
            
            api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.api_key}"
            
            prompt = """Analyze this image and provide a detailed, comprehensive description. Focus on:
- Main subjects and objects
- Visual style, colors, lighting
- Composition and perspective  
- Mood and atmosphere
- Important details and context

Provide only the description without any prefixes like "This image shows" or "The image depicts"."""
            
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
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048
                }
            }
            
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            if 'candidates' in result and result['candidates']:
                text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Clean up the response
                prefixes = [
                    "Here's a detailed description of the image:",
                    "Here's a detailed description:",
                    "This image shows:",
                    "This image depicts:",
                    "The image shows:",
                    "The image depicts:",
                    "I can see:",
                    "Looking at this image:",
                    "In this image:",
                ]
                
                for prefix in prefixes:
                    if text.lower().startswith(prefix.lower()):
                        text = text[len(prefix):].strip()
                        break
                
                # Remove markdown formatting
                text = text.replace('**', '').replace('*', '')
                text = ' '.join(text.split())  # Normalize whitespace
                
                if text.endswith('.'):
                    text = text[:-1]
                
                return {"success": True, "prompt": text}
            else:
                return {"success": False, "error": "No valid response from AI service"}
                
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            return {"success": False, "error": f"AI analysis failed: {str(e)}"}

# Initialize the analyzer
analyzer = SimpleImageAnalyzer()

@app.route('/')
def index():
    """Render the main page with the image upload form."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Analyze an image and return a descriptive prompt."""
    try:
        # Check if analyzer is configured
        if not analyzer.is_configured():
            flash('Image analysis service is not properly configured. Please check API key.', 'error')
            return redirect(url_for('index'))
        
        # Get form data
        image_url = request.form.get('image_url', '').strip() if request.form else ''
        uploaded_file = request.files.get('image_file') if request.files else None
        
        # Validate input
        if not image_url and not uploaded_file:
            flash('Please provide either an image URL or upload an image file.', 'error')
            return redirect(url_for('index'))
        
        if image_url and uploaded_file and uploaded_file.filename:
            flash('Please provide either an image URL or upload a file, not both.', 'error')
            return redirect(url_for('index'))
        
        # Process image URL
        if image_url:
            if not image_url.startswith(('http://', 'https://')):
                flash('Please provide a valid image URL starting with http:// or https://', 'error')
                return redirect(url_for('index'))
            
            result = analyzer.analyze_from_url(image_url)
        
        # Process uploaded file
        elif uploaded_file and uploaded_file.filename:
            if not allowed_file(uploaded_file.filename):
                flash('Invalid file type. Please upload a supported image format.', 'error')
                return redirect(url_for('index'))
            
            # Save uploaded file temporarily
            filename = secure_filename(uploaded_file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            try:
                uploaded_file.save(file_path)
                result = analyzer.analyze_from_file(file_path)
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass  # Ignore cleanup errors
        
        else:
            flash('No valid image provided.', 'error')
            return redirect(url_for('index'))
        
        # Handle result
        if result.get('success'):
            prompt = result['prompt']
            # Show the result in a more user-friendly way
            flash(f"🎯 Analysis Complete! Here's your detailed prompt:", 'success')
            flash(prompt, 'prompt')  # Use a special category for the actual prompt
            logger.info(f"Successfully generated prompt: {prompt[:100]}...")
        else:
            error_msg = result.get('error', 'Unknown error occurred during analysis')
            flash(f"❌ Analysis failed: {error_msg}", 'error')
            logger.error(f"Analysis failed: {error_msg}")
        
        return redirect(url_for('index'))
        
    except Exception as e:
        logger.error(f"Unexpected error in analyze_image: {str(e)}")
        flash('An unexpected error occurred. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze_image():
    """API endpoint for image analysis - returns JSON response."""
    try:
        # Check if analyzer is configured
        if not analyzer.is_configured():
            return jsonify({
                'success': False, 
                'error': 'Image analysis service is not properly configured'
            }), 500
        
        # Handle JSON requests (image URL)
        if request.is_json:
            data = request.get_json()
            image_url = data.get('image_url', '').strip()
            
            if not image_url:
                return jsonify({'success': False, 'error': 'image_url is required'}), 400
            
            if not image_url.startswith(('http://', 'https://')):
                return jsonify({'success': False, 'error': 'Invalid image URL format'}), 400
            
            result = analyzer.analyze_from_url(image_url)
            
        # Handle form data (file upload)
        else:
            uploaded_file = request.files.get('image_file')
            
            if not uploaded_file or not uploaded_file.filename:
                return jsonify({'success': False, 'error': 'image_file is required'}), 400
            
            if not allowed_file(uploaded_file.filename):
                return jsonify({'success': False, 'error': 'Invalid file type'}), 400
            
            # Save uploaded file temporarily
            filename = secure_filename(uploaded_file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            
            try:
                uploaded_file.save(file_path)
                result = analyzer.analyze_from_file(file_path)
            finally:
                # Clean up the temporary file
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except:
                        pass  # Ignore cleanup errors
        
        # Return result
        if result.get('success'):
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    status = {
        'status': 'healthy',
        'service': 'Image Prompt Extractor',
        'analyzer_configured': analyzer.is_configured()
    }
    return jsonify(status)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File too large. Maximum size is 32MB.', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(e)}")
    flash('An internal error occurred. Please try again.', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)