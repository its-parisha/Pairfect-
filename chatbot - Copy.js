const express = require('express');
const { Configuration, OpenAIApi } = require('openai');
const franc = require('franc'); // For language detection
require('dotenv').config(); // Load environment variables

const app = express();
app.use(express.json()); // Parse JSON requests

// OpenAI Configuration
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

// In-memory storage for conversation history (use a DB in production)
const conversationHistory = {};

// Supported languages (ISO codes)
const supportedLanguages = {
  eng: 'English',
  hin: 'Hindi',
  mar: 'Marathi',
  tel: 'Telugu',
  kan: 'Kannada',
};

// Function to detect language
function detectLanguage(text) {
  const lang = franc(text, { minLength: 3 }); // Detect with minimum length
  return supportedLanguages[lang] ? lang : 'eng'; // Default to English if not supported
}

// Function to generate OpenAI prompt
function buildPrompt(userMessage, language, history) {
  const langName = supportedLanguages[language] || 'English';
  const context = history.length > 0 ? `Previous conversation: ${history.join(' ')}` : '';
  
  return `
You are an intelligent, multilingual chatbot for a digital twin–based system. Your role is to assist users with:
- System analysis (e.g., evaluating digital twin models, performance metrics).
- Future planning and prediction (e.g., forecasting trends, scenario simulations).
- Low-cost solution recommendations (e.g., affordable tools, optimizations).
- New technology and market trends (e.g., AI advancements, IoT in digital twins).
- General suggestions and query answering.

Respond in ${langName} language. Be context-aware, helpful, and concise. Use the conversation history for continuity.

${context}

User query: ${userMessage}

Response:
  `;
}

// Chat endpoint
app.post('/chat', async (req, res) => {
  const { message, sessionId } = req.body; // sessionId to track user sessions

  if (!message || !sessionId) {
    return res.status(400).json({ error: 'Message and sessionId are required.' });
  }

  try {
    // Detect language
    const detectedLang = detectLanguage(message);

    // Get or initialize conversation history
    if (!conversationHistory[sessionId]) {
      conversationHistory[sessionId] = [];
    }
    const history = conversationHistory[sessionId];

    // Build prompt
    const prompt = buildPrompt(message, detectedLang, history);

    // Call OpenAI API
    const response = await openai.createCompletion({
      model: 'text-davinci-003', // Or 'gpt-3.5-turbo' for chat models; adjust as needed
      prompt: prompt,
      max_tokens: 500,
      temperature: 0.7, // For creativity
    });

    const botResponse = response.data.choices[0].text.trim();

    // Update history
    history.push(`User: ${message}`);
    history.push(`Bot: ${botResponse}`);
    if (history.length > 20) history.splice(0, 2); // Limit history to last 10 exchanges

    res.json({ response: botResponse, language: supportedLanguages[detectedLang] });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'An error occurred while processing your request.' });
  }
});

// Start server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Chatbot server running on port ${PORT}`);
});
