import os
import logging
from flask import Flask, request, jsonify, render_template, flash, redirect, url_for
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from optimized_analyzer import OptimizedImageAnalyzer
from comprehensive_analyzer import ComprehensiveImageAnalyzer
from enhanced_analyzer import EnhancedImageAnalyzer
import tempfile
import uuid

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB max file size for better quality
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff', 'tif', 'svg', 'ico', 'heic', 'heif', 'avif'}
UPLOAD_FOLDER = tempfile.gettempdir()

# Initialize all analyzers - enhanced analyzer provides best results
analyzer = OptimizedImageAnalyzer()  # Keep for backward compatibility
comprehensive_analyzer = ComprehensiveImageAnalyzer()  # Detailed analyzer
enhanced_analyzer = EnhancedImageAnalyzer()  # Enhanced analyzer with 16-point criteria

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page with the image upload form."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Analyze an image and return a descriptive prompt."""
    try:
        # Safely handle form data to prevent memory issues
        try:
            image_url = request.form.get('image_url', '').strip() if request.form else ''
            uploaded_file = request.files.get('image_file') if request.files else None
        except Exception as e:
            logger.error(f"Error processing form data: {str(e)}")
            flash('Error processing request. Please try again.', 'error')
            return redirect(url_for('index'))
        
        # Validate input
        if not image_url and not uploaded_file:
            flash('Please provide either an image URL or upload a file.', 'error')
            return redirect(url_for('index'))
        
        if image_url and uploaded_file and uploaded_file.filename:
            flash('Please provide either an image URL or upload a file, not both.', 'error')
            return redirect(url_for('index'))
        
        prompt = None
        
        # Use enhanced analyzer as primary, with fallbacks
        if enhanced_analyzer.is_configured():
            active_analyzer = enhanced_analyzer
        elif comprehensive_analyzer.is_configured():
            active_analyzer = comprehensive_analyzer
        else:
            active_analyzer = analyzer
        result = None
        
        if image_url:
            logger.info(f"Analyzing image from URL: {image_url}")
            result = active_analyzer.analyze_from_url(image_url)
        
        elif uploaded_file and uploaded_file.filename:
            if not allowed_file(uploaded_file.filename):
                flash('Invalid file type. Please upload PNG, JPG, JPEG, GIF, WebP, BMP, TIFF, SVG, ICO, HEIC, HEIF, or AVIF files only.', 'error')
                return redirect(url_for('index'))
            
            # Save uploaded file temporarily
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
            uploaded_file.save(file_path)
            
            try:
                logger.info(f"Analyzing uploaded image: {filename}")
                result = active_analyzer.analyze_from_file(file_path)
            finally:
                # Clean up temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
        
        # Handle response format differences between analyzers
        if result:
            if isinstance(result, dict) and result.get('success'):
                prompt = result.get('prompt', '')
                analysis_type = result.get('analysis_type', 'basic')
                flash(f'Comprehensive analysis successful! ({analysis_type})', 'success')
                return render_template('index.html', prompt=prompt, analysis_type=analysis_type)
            elif isinstance(result, str):
                # Legacy format from optimized analyzer
                flash('Analysis successful!', 'success')
                return render_template('index.html', prompt=result, analysis_type='basic')
            else:
                error_msg = result.get('error', 'Unknown error') if isinstance(result, dict) else 'Analysis failed'
                flash(f'Failed to analyze the image: {error_msg}', 'error')
                return redirect(url_for('index'))
        else:
            flash('Failed to analyze the image. Please try again.', 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        flash(f'Error analyzing image: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/api/analyze', methods=['POST'])
def api_analyze_image():
    """API endpoint for image analysis - returns JSON response."""
    try:
        # Check if request contains JSON data with image URL
        if request.is_json:
            try:
                data = request.get_json()
                image_url = data.get('image_url', '').strip()
            except Exception as e:
                logger.error(f"Error parsing JSON: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Invalid JSON data'
                }), 400
            
            if not image_url:
                return jsonify({
                    'success': False,
                    'error': 'No image URL provided'
                }), 400
            
            logger.info(f"API: Analyzing image from URL: {image_url}")
            # Use same analyzer priority as web app
            if enhanced_analyzer.is_configured():
                active_analyzer = enhanced_analyzer
            elif comprehensive_analyzer.is_configured():
                active_analyzer = comprehensive_analyzer
            else:
                active_analyzer = analyzer
            result = active_analyzer.analyze_from_url(image_url)
            
            # Handle response format differences between analyzers
            if result:
                if isinstance(result, dict):
                    return jsonify(result)
                elif isinstance(result, str):
                    return jsonify({
                        'success': True,
                        'prompt': result,
                        'analysis_type': 'basic'
                    })
            
            return jsonify({
                'success': False,
                'error': 'Failed to analyze the image'
            }), 500
        
        # Handle file upload with memory protection
        elif request.files and 'image_file' in request.files:
            try:
                uploaded_file = request.files['image_file']
            except Exception as e:
                logger.error(f"Error processing file upload: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Error processing file upload'
                }), 400
            
            if not uploaded_file or not uploaded_file.filename:
                return jsonify({
                    'success': False,
                    'error': 'No file uploaded'
                }), 400
            
            if not allowed_file(uploaded_file.filename):
                return jsonify({
                    'success': False,
                    'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WebP, BMP, TIFF, SVG, ICO, HEIC, HEIF, AVIF'
                }), 400
            
            # Save uploaded file temporarily with memory protection
            filename = secure_filename(uploaded_file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
            
            try:
                uploaded_file.save(file_path)
                logger.info(f"API: Analyzing uploaded image: {filename}")
                # Use same analyzer priority as web app
                if enhanced_analyzer.is_configured():
                    active_analyzer = enhanced_analyzer
                elif comprehensive_analyzer.is_configured():
                    active_analyzer = comprehensive_analyzer
                else:
                    active_analyzer = analyzer
                result = active_analyzer.analyze_from_file(file_path)
                
                # Handle response format differences between analyzers
                if result:
                    if isinstance(result, dict):
                        return jsonify(result)
                    elif isinstance(result, str):
                        return jsonify({
                            'success': True,
                            'prompt': result,
                            'analysis_type': 'basic'
                        })
                
                return jsonify({
                    'success': False,
                    'error': 'Failed to analyze the image'
                }), 500
            except Exception as e:
                logger.error(f"Error processing uploaded file: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': f'Error processing file: {str(e)}'
                }), 500
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file: {str(e)}")
        
        else:
            return jsonify({
                'success': False,
                'error': 'No image URL or file provided'
            }), 400
            
    except Exception as e:
        logger.error(f"API Error analyzing image: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error analyzing image: {str(e)}'
        }), 500

@app.route('/health')
def health_check():
    """Health check endpoint."""
    import time
    start_time = time.time()
    
    health_status = {
        'status': 'healthy',
        'service': 'Image Prompt Extractor',
        'version': '1.0.0',
        'timestamp': int(time.time()),
        'gemini_configured': analyzer.is_configured(),
        'uptime': time.time() - start_time,
        'checks': {
            'api_key': analyzer.is_configured(),
            'disk_space': True,
            'memory': True
        }
    }
    
    # Overall health status
    if not analyzer.is_configured():
        health_status['status'] = 'unhealthy'
        health_status['checks']['api_key'] = False
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code

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
