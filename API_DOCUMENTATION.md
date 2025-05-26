# Image Prompt Extractor API Documentation

## Overview

The Image Prompt Extractor API provides high-accuracy image analysis using Google Gemini Vision AI. It returns clean, detailed visual descriptions without any AI commentary or prefixes.

## Base URL

```
http://localhost:5000
```

## Authentication

No authentication required for the API endpoints. The service uses a pre-configured Gemini API key.

## Rate Limiting

Currently no rate limiting is enforced, but consider implementing rate limiting for production use.

## Content Types

- **Request**: `application/json` for URL analysis, `multipart/form-data` for file uploads
- **Response**: `application/json`

---

## Endpoints

### 1. Analyze Image

**Endpoint:** `POST /api/analyze`

Analyzes an image and returns a comprehensive visual description.

#### Method 1: URL Analysis

**Request:**
```http
POST /api/analyze
Content-Type: application/json

{
  "image_url": "https://example.com/image.jpg"
}
```

**Example with cURL:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://i.ibb.co/MkVH92j3/image.jpg"}'
```

#### Method 2: File Upload

**Request:**
```http
POST /api/analyze
Content-Type: multipart/form-data

image_file: [binary file data]
```

**Example with cURL:**
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "image_file=@/path/to/your/image.jpg"
```

#### Response Format

**Success Response:**
```json
{
  "success": true,
  "prompt": "A young woman with shoulder-length dark brown hair, fair skin, and expressive eyes stands in a modern urban setting. She wears a light blue denim jacket over a white cotton t-shirt, paired with dark wash skinny jeans. The background features glass-fronted commercial buildings with reflective surfaces, creating subtle bokeh effects. Natural daylight illuminates the scene from the left side, casting soft shadows and highlighting the texture of her hair and fabric details."
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Detailed error description"
}
```

#### Status Codes

- `200 OK`: Successful analysis
- `400 Bad Request`: Invalid input (missing URL/file, unsupported format)
- `413 Payload Too Large`: File exceeds 32MB limit
- `500 Internal Server Error`: Processing error or API configuration issue

---

### 2. Health Check

**Endpoint:** `GET /health`

Checks service status and API configuration.

**Request:**
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "Image Prompt Extractor",
  "gemini_configured": true
}
```

---

## Supported Image Formats

### File Formats
- **PNG** (.png)
- **JPEG** (.jpg, .jpeg)
- **GIF** (.gif)
- **WebP** (.webp)
- **BMP** (.bmp)
- **TIFF** (.tiff, .tif)
- **SVG** (.svg)
- **ICO** (.ico)
- **HEIC** (.heic)
- **HEIF** (.heif)
- **AVIF** (.avif)

### Size Limits
- **Maximum file size**: 32MB
- **Recommended dimensions**: Up to 4096x4096 pixels
- **Automatic resizing**: Images larger than 4096px are automatically resized

---

## Domain Compatibility

The service includes enhanced compatibility for major image hosting platforms:

### Fully Supported Domains
- imgur.com
- ibb.co
- postimg.cc
- flickr.com
- Google Drive/Photos
- Dropbox public links
- AWS S3 public URLs
- GitHub raw content
- Discord CDN
- Reddit media

### Headers and User Agent
The service uses browser-like headers to ensure maximum compatibility with protected image URLs.

---

## Response Quality

### Analysis Depth

The API provides comprehensive analysis covering:

1. **Physical Subjects**
   - Age estimation and gender identification
   - Body posture and facial expressions
   - Clothing details and accessories
   - Actions and interactions

2. **Environment & Setting**
   - Location type and architectural elements
   - Time of day and weather conditions
   - Objects, props, and spatial relationships

3. **Technical Aspects**
   - Art style and medium identification
   - Lighting analysis (direction, quality, shadows)
   - Color palette and temperature
   - Composition and framing

4. **Fine Details**
   - Visible text and symbols
   - Patterns and decorative elements
   - Material textures and surfaces
   - Quality indicators

### Output Characteristics

- **No AI Prefixes**: Responses start directly with the description
- **Clean Language**: No "This image shows" or similar phrases
- **Detailed**: Comprehensive coverage of all visual elements
- **Accurate**: High precision in color, style, and content identification
- **Professional**: Suitable for creative and technical applications

---

## Error Handling

### Common Error Scenarios

1. **Invalid URL Format**
```json
{
  "success": false,
  "error": "Invalid URL format"
}
```

2. **Unsupported File Type**
```json
{
  "success": false,
  "error": "Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WebP, BMP, TIFF, SVG, ICO, HEIC, HEIF, AVIF"
}
```

3. **File Too Large**
```json
{
  "success": false,
  "error": "File too large. Maximum size is 32MB."
}
```

4. **Network Error**
```json
{
  "success": false,
  "error": "Unable to access the image URL: Connection timeout"
}
```

5. **API Configuration Error**
```json
{
  "success": false,
  "error": "Gemini API is not properly configured"
}
```

---

## Performance Metrics

### Typical Response Times
- **Small images** (<1MB): 2-3 seconds
- **Medium images** (1-10MB): 3-5 seconds
- **Large images** (10-32MB): 4-7 seconds

### Processing Steps
1. URL validation/file upload (0.1-0.5s)
2. Image download/loading (0.2-2s)
3. Image preprocessing (0.1-0.3s)
4. Gemini API analysis (2-4s)
5. Response cleaning (0.1s)

---

## Integration Examples

### Python
```python
import requests

response = requests.post(
    'http://localhost:5000/api/analyze',
    json={'image_url': 'https://example.com/image.jpg'}
)
result = response.json()
if result['success']:
    print(result['prompt'])
```

### Node.js
```javascript
const response = await fetch('http://localhost:5000/api/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({image_url: 'https://example.com/image.jpg'})
});
const result = await response.json();
if (result.success) {
    console.log(result.prompt);
}
```

### PHP
```php
$response = file_get_contents('http://localhost:5000/api/analyze', false, stream_context_create([
    'http' => [
        'method' => 'POST',
        'header' => 'Content-Type: application/json',
        'content' => json_encode(['image_url' => 'https://example.com/image.jpg'])
    ]
]));
$result = json_decode($response, true);
if ($result['success']) {
    echo $result['prompt'];
}
```

---

## Security Considerations

### File Upload Security
- Automatic file type validation
- Temporary file storage with cleanup
- Size restrictions to prevent DoS
- No file execution or processing beyond image analysis

### URL Security
- URL format validation
- Timeout protection for external requests
- No server-side request forgery (SSRF) protection via validation

### Data Privacy
- No permanent storage of uploaded images
- Temporary files automatically deleted after processing
- No logging of image content or prompts