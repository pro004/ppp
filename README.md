# Image Prompt Extractor

A comprehensive image analysis service that generates detailed, comma-separated descriptive prompts using Google Gemini Vision AI.

## Features

- **Comprehensive Analysis**: Detailed body positioning, spatial relationships, and environmental context
- **Precise Positioning**: Exact angles, directional terms, and limb placement descriptions
- **Multiple Input Methods**: URL or file upload support
- **RESTful API**: JSON responses for easy integration
- **Optimized Output**: 700-900 character comma-separated prompts

## API Usage

### Analyze Image from URL
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

### Upload and Analyze File
```bash
curl -X POST http://localhost:5000/api/analyze \
  -F "image_file=@image.jpg"
```

### Response Format
```json
{
  "success": true,
  "prompt": "anime-style illustration, digital painting medium, young woman seated center-frame, legs spread wide apart...",
  "analysis_type": "comprehensive"
}
```

## Improving API Accuracy

### 1. Image Quality
- **High Resolution**: Use images with minimum 512x512 resolution
- **Clear Focus**: Ensure subjects are in sharp focus
- **Good Lighting**: Well-lit images produce more accurate descriptions
- **Minimal Compression**: Use high-quality JPEG or PNG formats

### 2. Image Content Guidelines
- **Clear Subjects**: Avoid heavily cropped or partially visible subjects
- **Unobstructed Views**: Minimize overlapping or hidden elements
- **Stable Positioning**: Clear, defined poses work better than motion blur
- **Consistent Style**: Similar art styles get more consistent results

### 3. Optimal Input Parameters
- **File Size**: 1-5MB images provide best balance of detail and processing speed
- **Aspect Ratio**: Standard ratios (16:9, 4:3, 1:1) work best
- **Color Depth**: Full-color images provide more detailed analysis than grayscale

### 4. API Configuration
- **Temperature Setting**: Lower values (0.05-0.1) for consistent, precise descriptions
- **Token Limits**: 750+ tokens for comprehensive analysis
- **Multiple Requests**: For critical analysis, make 2-3 requests and compare results

### 5. Prompt Consistency Tips
- **Consistent Vocabulary**: The AI learns patterns from similar image types
- **Stable Lighting**: Images with consistent lighting conditions
- **Clear Backgrounds**: Uncluttered backgrounds improve subject focus
- **Standard Poses**: Common poses and positions get more accurate descriptions

### 6. Error Handling
- **Retry Logic**: Implement automatic retries for failed requests
- **Fallback Options**: Have backup analysis methods for edge cases
- **Validation**: Check response length and content quality

### 7. Batch Processing
- **Rate Limiting**: Space requests to avoid quota limits
- **Queue Management**: Process multiple images systematically
- **Result Validation**: Compare batch results for consistency

## Technical Details

- **AI Model**: Google Gemini Vision 1.5 Flash
- **Max File Size**: 32MB
- **Supported Formats**: PNG, JPG, JPEG, GIF, WebP, BMP, TIFF, SVG, ICO, HEIC, HEIF, AVIF
- **Response Time**: 2-10 seconds depending on image complexity
- **Character Output**: 700-900 characters optimized for prompt generation

## Deployment

The service is configured for deployment on:
- Replit (native support)
- Railway
- Render
- Vercel
- Docker

## Environment Variables

- `GEMINI_API_KEY`: Google Gemini API key (required)
- `PORT`: Server port (default: 5000)
- `SESSION_SECRET`: Flask session secret

## Getting Started

1. Set up your Gemini API key
2. Install dependencies: `pip install -r requirements.txt`
3. Start the server: `python main.py`
4. Access the web interface at `http://localhost:5000`

## API Limits and Quotas

- **Request Rate**: Follow Google Gemini API limits
- **Daily Quota**: Monitor usage to avoid quota exhaustion
- **Image Size**: 32MB maximum per request
- **Concurrent Requests**: Limit concurrent connections for stability