# Image Prompt Extractor

## Overview

The Image Prompt Extractor is a web service that analyzes images and generates clean comma-separated descriptive prompts using Google Gemini Vision AI. The application provides both Python/Flask and Node.js/Express implementations, offering a RESTful API and web interface for prompt generation. It supports multiple image formats and input methods (URL or file upload) with comprehensive error handling and rate limiting.

## System Architecture

### Backend Architecture
- **Primary Implementation**: Python Flask web application with Gunicorn WSGI server
- **Alternative Implementation**: Node.js Express server (dual-language support)
- **AI Integration**: Google Gemini Vision AI (gemini-1.5-flash model) for image analysis
- **Session Management**: Flask sessions with configurable secret key
- **File Handling**: Temporary file storage with 32MB upload limit
- **Rate Limiting**: Basic request throttling to prevent API quota exhaustion

### Frontend Architecture
- **Web Interface**: Server-side rendered HTML templates using Flask/Jinja2
- **Styling**: Bootstrap 5 with custom CSS and Font Awesome icons
- **Form Handling**: Multi-part form data for file uploads and JSON for URL analysis
- **Real-time Feedback**: Flash messages for user notifications and error handling

### Deployment Strategy
- **Multi-platform Support**: Configured for Replit, Railway, Render, Vercel, and Docker
- **Process Management**: Gunicorn for Python, PM2-ready for Node.js
- **Health Monitoring**: Health check endpoints for deployment platforms
- **Environment Configuration**: Environment variables for API keys and server settings

## Key Components

### Core Application Files
- **main.py**: Application entry point and Flask app initialization
- **app.py**: Main Flask application with routing and request handling
- **image_analyzer.py**: Google Gemini AI integration and image processing logic
- **server.js**: Node.js Express alternative implementation

### API Layer
- **REST Endpoints**: `/api/analyze` for programmatic access
- **Input Methods**: Support for both image URLs and file uploads
- **Response Format**: Standardized JSON responses with success/error handling
- **File Support**: PNG, JPG, JPEG, GIF, WebP, BMP, TIFF, SVG, ICO, HEIC, HEIF, AVIF

### Configuration Management
- **Environment Variables**: GEMINI_API_KEY, PORT, NODE_ENV, SESSION_SECRET
- **Deployment Configs**: Platform-specific configuration files for various hosting services
- **Dependencies**: Python (pyproject.toml) and Node.js (package.json) package management

## Data Flow

1. **Request Reception**: Web interface or API receives image input (URL or file)
2. **Input Validation**: File type checking and size limits enforcement
3. **Image Processing**: PIL/Sharp for image optimization and format conversion
4. **AI Analysis**: Google Gemini Vision AI processes image and generates description
5. **Response Generation**: Clean prompt extraction without AI prefixes or commentary
6. **Result Delivery**: JSON response for API or web page rendering for UI

## External Dependencies

### AI Services
- **Google Gemini Vision AI**: Primary image analysis engine
- **API Configuration**: Requires GEMINI_API_KEY environment variable
- **Model Selection**: gemini-1.5-flash for optimal balance of speed and accuracy

### Python Dependencies
- **Flask**: Web framework and templating
- **Gunicorn**: WSGI HTTP server for production
- **Pillow**: Image processing and format handling
- **Requests**: HTTP client for URL-based image fetching
- **google-generativeai**: Official Google Gemini SDK

### Node.js Dependencies
- **Express**: Web framework
- **Multer**: File upload handling
- **Sharp**: Image processing
- **Axios**: HTTP client
- **@google/generative-ai**: Google Gemini SDK for Node.js

## Deployment Strategy

### Platform Support
- **Replit**: Native support with .replit configuration and workflow automation
- **Railway**: JSON configuration with health checks and auto-scaling
- **Render**: YAML configuration for web service deployment
- **Vercel**: Serverless deployment configuration for Node.js version
- **Docker**: Multi-stage build with security best practices

### Production Considerations
- **Health Monitoring**: `/health` endpoint for platform health checks
- **Rate Limiting**: Request throttling to prevent API quota exhaustion
- **Security**: Helmet.js security headers, file type validation, size limits
- **Scaling**: Gunicorn worker processes, Express cluster-ready architecture

## Changelog

- June 19, 2025: Initial setup
- June 19, 2025: Fixed system dependency issues and created simplified image analyzer
- June 19, 2025: Updated web interface layout for side-by-side image and prompt display
- June 19, 2025: Enhanced with forensic precision - exact positioning, angles, spatial relationships with precise directional terms (3 sentences, observable facts only)
- June 21, 2025: Enhanced analyzer with detailed visual elements including hair color, eye states, skin tone, hand placement, artistic details, and background accuracy for precise image reproduction
- June 21, 2025: Fixed body positioning and body language accuracy with precise posture detection
- June 21, 2025: Fixed body positioning accuracy to describe exactly what's visible without changing or modifying the image content
- June 21, 2025: Added comprehensive background details detection including furniture, architectural elements, spatial relationships, and environmental setting
- June 21, 2025: Enhanced background analysis with detailed color specification, architectural elements, lighting analysis, and spatial positioning while maintaining careful focus on actual body positioning
- June 21, 2025: Added comprehensive clothing details analysis and implemented conditional 16-point analysis criteria (only included if clearly present in image)

## User Preferences

Preferred communication style: Simple, everyday language.
Preferred analysis style: Detailed, accurate comma-separated prompts (600-800 characters) with specific visual elements including hair color/style, eye states, skin tone, clothing details, hand placement, artistic style, lighting, and background accuracy for precise image reproduction.