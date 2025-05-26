/**
 * Image Prompt Extractor - JavaScript Integration Examples
 * 
 * This file demonstrates various ways to integrate with the Image Prompt Extractor API
 * using modern JavaScript (ES6+) and different environments.
 */

// =============================================================================
// 1. Basic Fetch API Example (Browser/Node.js)
// =============================================================================

/**
 * Analyzes an image from URL using the Image Prompt Extractor API
 * @param {string} imageUrl - The URL of the image to analyze
 * @param {string} apiBaseUrl - Base URL of the API (default: http://localhost:5000)
 * @returns {Promise<Object>} - API response with prompt or error
 */
async function analyzeImageFromUrl(imageUrl, apiBaseUrl = 'http://localhost:5000') {
    try {
        const response = await fetch(`${apiBaseUrl}/api/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                image_url: imageUrl
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error analyzing image:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

/**
 * Analyzes an uploaded file using the Image Prompt Extractor API
 * @param {File} file - The image file to upload and analyze
 * @param {string} apiBaseUrl - Base URL of the API
 * @returns {Promise<Object>} - API response with prompt or error
 */
async function analyzeImageFromFile(file, apiBaseUrl = 'http://localhost:5000') {
    try {
        const formData = new FormData();
        formData.append('image_file', file);

        const response = await fetch(`${apiBaseUrl}/api/analyze`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error analyzing image file:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

// =============================================================================
// 2. Usage Examples
// =============================================================================

// Example 1: Analyze image from URL
async function exampleUrlAnalysis() {
    console.log('🔍 Analyzing image from URL...');
    
    const imageUrl = 'https://i.ibb.co/MkVH92j3/image.jpg';
    const result = await analyzeImageFromUrl(imageUrl);
    
    if (result.success) {
        console.log('✅ Analysis successful!');
        console.log('📝 Generated prompt:', result.prompt);
    } else {
        console.error('❌ Analysis failed:', result.error);
    }
}

// Example 2: Analyze uploaded file (Browser environment)
function setupFileUploadExample() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.png,.jpg,.jpeg,.gif,.webp,.bmp,.tiff,.svg,.ico,.heic,.heif,.avif';
    
    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;
        
        console.log('📁 Analyzing uploaded file:', file.name);
        
        const result = await analyzeImageFromFile(file);
        
        if (result.success) {
            console.log('✅ File analysis successful!');
            console.log('📝 Generated prompt:', result.prompt);
        } else {
            console.error('❌ File analysis failed:', result.error);
        }
    });
    
    // Add to page for testing
    document.body.appendChild(fileInput);
}

// =============================================================================
// 3. Advanced Integration Class
// =============================================================================

/**
 * Advanced Image Prompt Extractor client with additional features
 */
class ImagePromptExtractor {
    constructor(apiBaseUrl = 'http://localhost:5000', options = {}) {
        this.apiBaseUrl = apiBaseUrl;
        this.options = {
            timeout: 30000,
            retryAttempts: 3,
            ...options
        };
    }

    /**
     * Check if the API service is healthy
     * @returns {Promise<boolean>} - Service health status
     */
    async checkHealth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/health`);
            const health = await response.json();
            return health.status === 'healthy' && health.gemini_configured;
        } catch (error) {
            console.error('Health check failed:', error);
            return false;
        }
    }

    /**
     * Analyze image with retry logic and progress tracking
     * @param {string|File} input - Image URL or File object
     * @param {Function} onProgress - Progress callback function
     * @returns {Promise<Object>} - Analysis result
     */
    async analyze(input, onProgress = () => {}) {
        const isFile = input instanceof File;
        
        onProgress({ stage: 'starting', message: 'Initializing analysis...' });
        
        // Check service health first
        onProgress({ stage: 'health_check', message: 'Checking service availability...' });
        const isHealthy = await this.checkHealth();
        if (!isHealthy) {
            throw new Error('Service is not available or not properly configured');
        }

        // Perform analysis with retry logic
        let lastError;
        for (let attempt = 1; attempt <= this.options.retryAttempts; attempt++) {
            try {
                onProgress({ 
                    stage: 'analyzing', 
                    message: `Analyzing image... (Attempt ${attempt}/${this.options.retryAttempts})` 
                });

                const result = isFile 
                    ? await this.analyzeImageFromFile(input)
                    : await this.analyzeImageFromUrl(input);

                if (result.success) {
                    onProgress({ stage: 'complete', message: 'Analysis completed successfully!' });
                    return result;
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                lastError = error;
                if (attempt < this.options.retryAttempts) {
                    onProgress({ 
                        stage: 'retrying', 
                        message: `Attempt ${attempt} failed, retrying...` 
                    });
                    await this.delay(1000 * attempt); // Exponential backoff
                }
            }
        }

        onProgress({ stage: 'error', message: 'Analysis failed after all retry attempts' });
        throw lastError;
    }

    /**
     * Analyze multiple images concurrently with rate limiting
     * @param {Array} inputs - Array of image URLs or Files
     * @param {number} concurrency - Maximum concurrent requests
     * @param {Function} onProgress - Progress callback
     * @returns {Promise<Array>} - Array of analysis results
     */
    async analyzeBatch(inputs, concurrency = 3, onProgress = () => {}) {
        const results = [];
        const semaphore = new Semaphore(concurrency);
        
        const promises = inputs.map(async (input, index) => {
            await semaphore.acquire();
            try {
                onProgress({ 
                    stage: 'batch_progress', 
                    completed: results.length, 
                    total: inputs.length,
                    current: index 
                });
                
                const result = await this.analyze(input);
                results.push({ index, input, result });
                return result;
            } finally {
                semaphore.release();
            }
        });

        await Promise.all(promises);
        onProgress({ stage: 'batch_complete', completed: results.length, total: inputs.length });
        
        return results.sort((a, b) => a.index - b.index).map(r => r.result);
    }

    async analyzeImageFromUrl(imageUrl) {
        return analyzeImageFromUrl(imageUrl, this.apiBaseUrl);
    }

    async analyzeImageFromFile(file) {
        return analyzeImageFromFile(file, this.apiBaseUrl);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// =============================================================================
// 4. Utility Classes
// =============================================================================

/**
 * Simple semaphore for concurrency control
 */
class Semaphore {
    constructor(maxConcurrency) {
        this.maxConcurrency = maxConcurrency;
        this.currentConcurrency = 0;
        this.queue = [];
    }

    async acquire() {
        return new Promise((resolve) => {
            if (this.currentConcurrency < this.maxConcurrency) {
                this.currentConcurrency++;
                resolve();
            } else {
                this.queue.push(resolve);
            }
        });
    }

    release() {
        this.currentConcurrency--;
        if (this.queue.length > 0) {
            const next = this.queue.shift();
            this.currentConcurrency++;
            next();
        }
    }
}

// =============================================================================
// 5. React Hook Example
// =============================================================================

/**
 * React hook for image analysis
 * @param {string} apiBaseUrl - API base URL
 * @returns {Object} - Hook state and methods
 */
function useImageAnalyzer(apiBaseUrl = 'http://localhost:5000') {
    const [state, setState] = React.useState({
        isAnalyzing: false,
        result: null,
        error: null,
        progress: null
    });

    const analyzer = React.useMemo(() => 
        new ImagePromptExtractor(apiBaseUrl), [apiBaseUrl]
    );

    const analyze = React.useCallback(async (input) => {
        setState(prev => ({ ...prev, isAnalyzing: true, error: null, result: null }));
        
        try {
            const result = await analyzer.analyze(input, (progress) => {
                setState(prev => ({ ...prev, progress }));
            });
            
            setState(prev => ({ 
                ...prev, 
                isAnalyzing: false, 
                result, 
                progress: null 
            }));
            
            return result;
        } catch (error) {
            setState(prev => ({ 
                ...prev, 
                isAnalyzing: false, 
                error: error.message,
                progress: null 
            }));
            throw error;
        }
    }, [analyzer]);

    return {
        ...state,
        analyze,
        analyzer
    };
}

// =============================================================================
// 6. Vue.js Composition API Example
// =============================================================================

/**
 * Vue.js composable for image analysis
 */
function useImageAnalysis(apiBaseUrl = 'http://localhost:5000') {
    const isAnalyzing = Vue.ref(false);
    const result = Vue.ref(null);
    const error = Vue.ref(null);
    const progress = Vue.ref(null);

    const analyzer = new ImagePromptExtractor(apiBaseUrl);

    const analyze = async (input) => {
        isAnalyzing.value = true;
        error.value = null;
        result.value = null;

        try {
            const analysisResult = await analyzer.analyze(input, (progressInfo) => {
                progress.value = progressInfo;
            });

            result.value = analysisResult;
            return analysisResult;
        } catch (err) {
            error.value = err.message;
            throw err;
        } finally {
            isAnalyzing.value = false;
            progress.value = null;
        }
    };

    return {
        isAnalyzing: Vue.readonly(isAnalyzing),
        result: Vue.readonly(result),
        error: Vue.readonly(error),
        progress: Vue.readonly(progress),
        analyze,
        analyzer
    };
}

// =============================================================================
// 7. Usage Examples for Different Scenarios
// =============================================================================

// Example: E-commerce product analysis
async function analyzeProductImages() {
    const extractor = new ImagePromptExtractor();
    const productUrls = [
        'https://example.com/product1.jpg',
        'https://example.com/product2.jpg',
        'https://example.com/product3.jpg'
    ];

    console.log('🛍️ Analyzing product images...');
    
    const results = await extractor.analyzeBatch(productUrls, 2, (progress) => {
        console.log(`Progress: ${progress.completed}/${progress.total} completed`);
    });

    results.forEach((result, index) => {
        if (result.success) {
            console.log(`Product ${index + 1}: ${result.prompt}`);
        }
    });
}

// Example: Content moderation
async function moderateImageContent(imageUrl) {
    const extractor = new ImagePromptExtractor();
    const result = await extractor.analyze(imageUrl);
    
    if (result.success) {
        const prompt = result.prompt.toLowerCase();
        
        // Simple content filtering (extend as needed)
        const inappropriateKeywords = ['explicit', 'nude', 'violence'];
        const isAppropriate = !inappropriateKeywords.some(keyword => 
            prompt.includes(keyword)
        );
        
        return {
            isAppropriate,
            description: result.prompt,
            confidence: 'high' // You could implement confidence scoring
        };
    }
    
    throw new Error('Failed to analyze image for moderation');
}

// Example: SEO alt text generation
async function generateAltText(imageUrl, maxLength = 125) {
    const extractor = new ImagePromptExtractor();
    const result = await extractor.analyze(imageUrl);
    
    if (result.success) {
        let altText = result.prompt;
        
        // Truncate if too long for SEO
        if (altText.length > maxLength) {
            altText = altText.substring(0, maxLength - 3) + '...';
        }
        
        return altText;
    }
    
    throw new Error('Failed to generate alt text');
}

// =============================================================================
// 8. Export for Module Systems
// =============================================================================

// ES6 Modules
export {
    analyzeImageFromUrl,
    analyzeImageFromFile,
    ImagePromptExtractor,
    useImageAnalyzer,
    useImageAnalysis
};

// CommonJS (Node.js)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        analyzeImageFromUrl,
        analyzeImageFromFile,
        ImagePromptExtractor,
        useImageAnalyzer,
        useImageAnalysis
    };
}

// =============================================================================
// 9. Quick Test Function
// =============================================================================

/**
 * Quick test function to verify the API is working
 */
async function quickTest() {
    console.log('🧪 Running quick API test...');
    
    const testImage = 'https://i.ibb.co/MkVH92j3/image.jpg';
    const result = await analyzeImageFromUrl(testImage);
    
    if (result.success) {
        console.log('✅ API test successful!');
        console.log('📝 Sample prompt:', result.prompt.substring(0, 100) + '...');
        return true;
    } else {
        console.error('❌ API test failed:', result.error);
        return false;
    }
}

// Auto-run test if this script is executed directly
if (typeof window === 'undefined' && require.main === module) {
    quickTest();
}