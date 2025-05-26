# Image Prompt Extractor

A high-performance Flask web service that extracts detailed, accurate prompts from images using Google Gemini Vision AI. Get comprehensive visual descriptions without any unnecessary AI commentary - just pure, detailed image analysis.

## ✨ Features

- **Ultra-Accurate Analysis**: Leverages Google Gemini Vision AI for precise image understanding
- **Clean Output**: Returns only pure visual descriptions without AI prefixes or commentary
- **Multiple Input Methods**: Supports both image URLs and file uploads
- **Comprehensive Format Support**: PNG, JPG, JPEG, GIF, WebP, BMP, TIFF, SVG, ICO, HEIC, HEIF, AVIF
- **Fast Processing**: Optimized for speed with enhanced domain compatibility
- **RESTful API**: Easy integration with any application
- **Web Interface**: User-friendly interface for testing and manual analysis
- **Large File Support**: Handles images up to 32MB

## 🚀 Quick Start

### API Usage

**Analyze from URL:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

**Response:**
```json
{
  "success": true,
  "prompt": "A young woman with shoulder-length dark brown hair, fair skin, and expressive eyes stands in a modern urban setting..."
}
```

### Web Interface

Visit `http://localhost:5000` to use the interactive web interface for:
- Testing with image URLs
- Uploading local files
- Copying generated prompts
- API documentation

## 📋 API Documentation

### Endpoints

#### POST `/api/analyze`

Analyzes an image and returns a detailed descriptive prompt.

**Request Methods:**

1. **JSON with Image URL:**
```json
{
  "image_url": "https://example.com/image.jpg"
}
```

2. **Form Data with File Upload:**
```
Content-Type: multipart/form-data
image_file: [binary file data]
```

**Response Format:**
```json
{
  "success": true,
  "prompt": "Detailed visual description..."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Error description"
}
```

#### GET `/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Image Prompt Extractor",
  "gemini_configured": true
}
```

## 🔧 Configuration

### Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key (required)
- `SESSION_SECRET`: Flask session secret (optional, auto-generated if not provided)

### Supported Image Formats

- **Raster**: PNG, JPG, JPEG, GIF, WebP, BMP, TIFF, HEIC, HEIF, AVIF
- **Vector**: SVG
- **Icons**: ICO
- **Maximum Size**: 32MB

## 🌐 Domain Compatibility

Enhanced compatibility with all major image hosting services:
- imgur.com
- ibb.co
- postimg.cc
- flickr.com
- Google Drive/Photos
- Dropbox
- AWS S3
- And many more...

## 📊 Response Quality

The system provides extremely detailed analysis covering:

- **Physical Subjects**: Age, gender, build, posture, expressions, clothing
- **Environment**: Location, architecture, objects, spatial relationships
- **Visual Style**: Art style, technique, rendering quality
- **Lighting**: Source locations, shadows, highlights, atmosphere
- **Colors**: Specific color names, saturation, temperature
- **Composition**: Framing, perspective, depth, focal points
- **Materials**: Textures, surfaces, transparency, reflectivity
- **Fine Details**: Text, symbols, patterns, decorative elements

## 🛠️ Error Handling

- **413**: File too large (>32MB)
- **400**: Invalid input (missing URL/file, unsupported format)
- **500**: Internal server error (API issues, processing errors)

## 🔒 Security

- Secure file handling with temporary storage cleanup
- Input validation and sanitization
- Rate limiting ready (configure as needed)
- HTTPS support via proxy middleware

## 📈 Performance

- Average processing time: 2-4 seconds
- Optimized image preprocessing
- Memory-efficient handling
- Automatic image resizing for large files

## 🧪 Testing

Test the service with the provided example image:
```
https://i.ibb.co/MkVH92j3/image.jpg
```

## 📄 License

This project is ready for production use with proper API key configuration.

## 🤝 Support

For issues or questions, ensure your Gemini API key is properly configured and check the health endpoint for service status.