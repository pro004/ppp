const express = require('express');
const multer = require('multer');
const axios = require('axios');
const sharp = require('sharp');
const path = require('path');
const fs = require('fs');
const cors = require('cors');
const helmet = require('helmet');
const { GoogleGenerativeAI } = require('@google/generative-ai');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json({ limit: '32mb' }));
app.use(express.urlencoded({ extended: true, limit: '32mb' }));
app.use(express.static('static'));

// Configure multer for file uploads
const storage = multer.memoryStorage();
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 32 * 1024 * 1024, // 32MB
  },
  fileFilter: (req, file, cb) => {
    const allowedTypes = ['image/png', 'image/jpg', 'image/jpeg', 'image/gif', 'image/webp', 'image/bmp', 'image/tiff', 'image/svg+xml', 'image/x-icon', 'image/heic', 'image/heif', 'image/avif'];
    if (allowedTypes.includes(file.mimetype)) {
      cb(null, true);
    } else {
      cb(new Error('Invalid file type. Only image files are allowed.'), false);
    }
  }
});

// Initialize Gemini AI
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });

// Rate limiting
let requestCount = 0;
let lastResetTime = Date.now();

function rateLimit() {
  const now = Date.now();
  if (now - lastResetTime > 60000) { // Reset every minute
    requestCount = 0;
    lastResetTime = now;
  }
  
  if (requestCount >= 15) {
    const waitTime = 60000 - (now - lastResetTime);
    if (waitTime > 0) {
      console.log(`Rate limit reached, waiting ${waitTime}ms...`);
      return new Promise(resolve => setTimeout(resolve, waitTime));
    }
  }
  
  requestCount++;
  return Promise.resolve();
}

// Image processing function
async function processImage(imageBuffer) {
  try {
    // Use sharp to process and optimize the image
    const processedImage = await sharp(imageBuffer)
      .resize(2048, 2048, { 
        fit: 'inside', 
        withoutEnlargement: true 
      })
      .jpeg({ quality: 85 })
      .toBuffer();
    
    return processedImage;
  } catch (error) {
    throw new Error(`Image processing failed: ${error.message}`);
  }
}

// Download image from URL
async function downloadImage(url) {
  try {
    const response = await axios.get(url, {
      responseType: 'arraybuffer',
      timeout: 30000,
      maxContentLength: 32 * 1024 * 1024,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
      }
    });
    
    return Buffer.from(response.data);
  } catch (error) {
    throw new Error(`Failed to download image: ${error.message}`);
  }
}

// Generate prompt using Gemini
async function generatePrompt(imageBuffer) {
  await rateLimit();
  
  const systemPrompt = `
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
  `;

  try {
    const imageParts = [{
      inlineData: {
        data: imageBuffer.toString('base64'),
        mimeType: 'image/jpeg'
      }
    }];

    const result = await model.generateContent([systemPrompt, ...imageParts]);
    const response = await result.response;
    let prompt = response.text().trim();

    // Clean up response
    if (prompt.startsWith('"') && prompt.endsWith('"')) {
      prompt = prompt.slice(1, -1);
    }

    // Remove common AI prefixes
    const prefixes = [
      "Here's a detailed description of the image:",
      "Here's a detailed description:",
      "This image shows:",
      "This image depicts:",
      "The image shows:",
      "The image depicts:",
      "I can see:",
      "Looking at this image:",
      "In this image:",
    ];

    for (const prefix of prefixes) {
      if (prompt.toLowerCase().startsWith(prefix.toLowerCase())) {
        prompt = prompt.slice(prefix.length).trim();
        break;
      }
    }

    // Clean up formatting
    prompt = prompt.replace(/\*\*/g, '').replace(/\*/g, '');
    prompt = prompt.replace(/\s+/g, ' ').trim();
    
    if (prompt.endsWith('.')) {
      prompt = prompt.slice(0, -1);
    }

    return prompt;
  } catch (error) {
    throw new Error(`Failed to generate prompt: ${error.message}`);
  }
}

// Routes
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'templates', 'index.html'));
});

app.post('/analyze', upload.single('image_file'), async (req, res) => {
  try {
    const { image_url } = req.body;
    let imageBuffer;

    if (image_url && req.file) {
      return res.status(400).json({
        success: false,
        error: 'Please provide either an image URL or upload a file, not both.'
      });
    }

    if (!image_url && !req.file) {
      return res.status(400).json({
        success: false,
        error: 'Please provide either an image URL or upload a file.'
      });
    }

    if (image_url) {
      console.log(`Analyzing image from URL: ${image_url}`);
      imageBuffer = await downloadImage(image_url);
    } else if (req.file) {
      console.log(`Analyzing uploaded image: ${req.file.originalname}`);
      imageBuffer = req.file.buffer;
    }

    const processedImage = await processImage(imageBuffer);
    const prompt = await generatePrompt(processedImage);

    if (req.headers.accept && req.headers.accept.includes('application/json')) {
      res.json({
        success: true,
        prompt: prompt
      });
    } else {
      // For web form submissions, redirect back with results
      res.redirect(`/?success=true&prompt=${encodeURIComponent(prompt)}`);
    }

  } catch (error) {
    console.error('Error analyzing image:', error.message);
    
    if (req.headers.accept && req.headers.accept.includes('application/json')) {
      res.status(500).json({
        success: false,
        error: error.message
      });
    } else {
      res.redirect(`/?error=${encodeURIComponent(error.message)}`);
    }
  }
});

app.post('/api/analyze', upload.single('image_file'), async (req, res) => {
  try {
    const { image_url } = req.body;
    let imageBuffer;

    if (image_url && req.file) {
      return res.status(400).json({
        success: false,
        error: 'Please provide either an image URL or upload a file, not both.'
      });
    }

    if (!image_url && !req.file) {
      return res.status(400).json({
        success: false,
        error: 'Please provide either an image URL or upload a file.'
      });
    }

    if (image_url) {
      console.log(`API: Analyzing image from URL: ${image_url}`);
      imageBuffer = await downloadImage(image_url);
    } else if (req.file) {
      console.log(`API: Analyzing uploaded image: ${req.file.originalname}`);
      imageBuffer = req.file.buffer;
    }

    const processedImage = await processImage(imageBuffer);
    const prompt = await generatePrompt(processedImage);

    res.json({
      success: true,
      prompt: prompt
    });

  } catch (error) {
    console.error('API Error analyzing image:', error.message);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    service: 'Image Prompt Extractor (Node.js)',
    gemini_configured: !!process.env.GEMINI_API_KEY
  });
});

// Error handling middleware
app.use((error, req, res, next) => {
  if (error instanceof multer.MulterError) {
    if (error.code === 'LIMIT_FILE_SIZE') {
      return res.status(413).json({
        success: false,
        error: 'File too large. Maximum size is 32MB.'
      });
    }
  }
  
  console.error('Unhandled error:', error);
  res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Node.js Image Prompt Extractor server running on port ${PORT}`);
  console.log(`Gemini API configured: ${!!process.env.GEMINI_API_KEY}`);
});