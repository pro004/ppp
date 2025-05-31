// Simple test script for Node.js version
const axios = require('axios');

async function testHealth() {
  try {
    const response = await axios.get('http://localhost:5000/health');
    console.log('Health check:', response.data);
  } catch (error) {
    console.error('Health check failed:', error.message);
  }
}

async function testImageAnalysis() {
  try {
    const response = await axios.post('http://localhost:5000/api/analyze', {
      image_url: 'https://i.ibb.co/MkVH92j3/image.jpg'
    });
    console.log('Image analysis test:', response.data);
  } catch (error) {
    console.error('Image analysis failed:', error.message);
  }
}

async function runTests() {
  console.log('Testing Node.js Image Prompt Extractor...');
  await testHealth();
  await testImageAnalysis();
}

if (require.main === module) {
  runTests();
}

module.exports = { testHealth, testImageAnalysis };