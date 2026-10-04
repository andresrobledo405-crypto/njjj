/**
 * Gemini AI Integration Routes
 * Handles image analysis, content generation, and video prompt creation
 */

const express = require('express');
const router = express.Router();
const { GoogleGenerativeAI } = require('@google/generative-ai');
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

// Initialize Gemini (requires GEMINI_API_KEY environment variable)
let genAI;

function initializeGemini() {
  const apiKey = process.env.GEMINI_API_KEY;
  if (!apiKey) {
    console.error('❌ GEMINI_API_KEY not configured in environment variables');
    throw new Error('Gemini API key not configured');
  }
  genAI = new GoogleGenerativeAI(apiKey);
  console.log('✅ Gemini AI initialized successfully');
}

// Initialize on startup
try {
  initializeGemini();
} catch (error) {
  console.error('Warning: Gemini initialization failed. API endpoints may fail.');
}

/**
 * POST /api/gemini/analyze-image
 * Analyze an image from Instagram using Gemini Vision API
 *
 * Request body:
 * {
 *   imageUrl: string,
 *   prompt: string (optional)
 * }
 */
router.post('/analyze-image', async (req, res) => {
  try {
    const { imageUrl, prompt } = req.body;

    if (!imageUrl) {
      return res.status(400).json({ error: 'imageUrl is required' });
    }

    if (!genAI) {
      return res.status(503).json({ error: 'Gemini service not initialized' });
    }

    // Fetch image and convert to base64
    console.log(`📸 Fetching image from: ${imageUrl}`);
    const imageResponse = await fetch(imageUrl);

    if (!imageResponse.ok) {
      throw new Error(`Failed to fetch image: ${imageResponse.statusText}`);
    }

    const buffer = await imageResponse.arrayBuffer();
    const base64 = Buffer.from(buffer).toString('base64');

    // Determine MIME type from URL or default to JPEG
    const mimeType = getMimeType(imageUrl);

    // Create default prompt if not provided
    const analysisPrompt = prompt || `Analiza esta imagen de panadería artesanal.

Proporciona:
1. **Composición Visual**: Describe la disposición de elementos, ángulo, profundidad
2. **Paleta de Colores**: Colores dominantes (hexadecimales)
3. **Calidad**: Evaluación 1-10 de calidad de la foto
4. **Mood/Atmósfera**: Cómo se siente la imagen
5. **SEO Description**: Descripción optimizada para buscadores (100 caracteres max)
6. **Hashtags**: 10 hashtags relevantes y trending
7. **Mejoras Sugeridas**: 3 mejoras para máximo engagement en Instagram

Responde en formato claro, estructurado, listo para copiar-pegar.`;

    // Call Gemini Vision API
    console.log('🤖 Calling Gemini Vision API...');
    const model = genAI.getGenerativeModel({ model: 'gemini-pro-vision' });

    const result = await model.generateContent([
      {
        inlineData: {
          data: base64,
          mimeType: mimeType,
        },
      },
      analysisPrompt,
    ]);

    const analysisText = result.response.text();

    console.log('✅ Image analysis completed');
    res.json({
      success: true,
      analysis: analysisText,
      metadata: {
        imageUrl,
        timestamp: new Date().toISOString(),
        model: 'gemini-pro-vision'
      }
    });

  } catch (error) {
    console.error('❌ Error analyzing image:', error.message);
    res.status(500).json({
      error: 'Failed to analyze image',
      details: error.message
    });
  }
});

/**
 * POST /api/gemini/generate-content
 * Generate marketing content using Gemini Pro
 *
 * Request body:
 * {
 *   prompt: string,
 *   temperature: number (optional, 0-1)
 * }
 */
router.post('/generate-content', async (req, res) => {
  try {
    const { prompt, temperature = 0.7 } = req.body;

    if (!prompt) {
      return res.status(400).json({ error: 'prompt is required' });
    }

    if (!genAI) {
      return res.status(503).json({ error: 'Gemini service not initialized' });
    }

    console.log('✨ Generating content with Gemini Pro...');

    const model = genAI.getGenerativeModel({
      model: 'gemini-pro',
      generationConfig: {
        temperature: temperature,
        topP: 0.95,
        topK: 40,
        maxOutputTokens: 2048,
      }
    });

    const result = await model.generateContent(prompt);
    const contentText = result.response.text();

    console.log('✅ Content generation completed');
    res.json({
      success: true,
      content: contentText,
      metadata: {
        timestamp: new Date().toISOString(),
        model: 'gemini-pro',
        inputLength: prompt.length,
        outputLength: contentText.length
      }
    });

  } catch (error) {
    console.error('❌ Error generating content:', error.message);
    res.status(500).json({
      error: 'Failed to generate content',
      details: error.message
    });
  }
});

/**
 * POST /api/gemini/generate-runway-prompt
 * Generate optimized prompts for Runway/Pika video generation
 *
 * Request body:
 * {
 *   productName: string,
 *   imageAnalysis: string,
 *   style: string (optional)
 * }
 */
router.post('/generate-runway-prompt', async (req, res) => {
  try {
    const { productName, imageAnalysis, style = 'cinematic' } = req.body;

    if (!productName || !imageAnalysis) {
      return res.status(400).json({
        error: 'productName and imageAnalysis are required'
      });
    }

    if (!genAI) {
      return res.status(503).json({ error: 'Gemini service not initialized' });
    }

    const prompt = `Eres un experto en creación de prompts para Runway ML y Pika AI.

Basado en este análisis de imagen:
${imageAnalysis}

Genera 3 prompts PERFECTOS para crear videos de 15-20 segundos del producto: "${productName}"

Cada prompt debe:
- Ser muy descriptivo y específico (150-300 palabras)
- Incluir: escena, producto (${productName}), lighting, audio, mood, text overlay, CTA
- Ser pronto para copiar-pegar directamente en Runway o Pika
- Enfatizar estilo cinematográfico (slow-motion, food porn, high-quality)
- Mencionar que es panadería artesanal de La Serena, Chile
- Incluir ubicación/branding: @artesanospanaderials

Estilos sugeridos:
1. "Cinematic Food Documentary" - Estilo documental de comida
2. "Artisan Craftsmanship" - Mostrando el proceso de elaboración
3. "Instagram Reel Trending" - Viral, dinámico, con música moderna

Formato de respuesta:

**Opción 1: Cinematic Food Documentary**
[Prompt 1 completo, 150-300 palabras]

**Opción 2: Artisan Craftsmanship**
[Prompt 2 completo, 150-300 palabras]

**Opción 3: Instagram Reel Trending**
[Prompt 3 completo, 150-300 palabras]

Asegúrate de que cada prompt sea específico, detallado y listo para usar inmediatamente.`;

    console.log('🎬 Generating Runway prompts...');

    const model = genAI.getGenerativeModel({
      model: 'gemini-pro',
      generationConfig: {
        temperature: 0.8,
        topP: 0.95,
        topK: 40,
        maxOutputTokens: 3000,
      }
    });

    const result = await model.generateContent(prompt);
    const prompText = result.response.text();

    console.log('✅ Runway prompts generated');
    res.json({
      success: true,
      prompts: prompText,
      metadata: {
        timestamp: new Date().toISOString(),
        model: 'gemini-pro',
        productName,
        style
      }
    });

  } catch (error) {
    console.error('❌ Error generating Runway prompts:', error.message);
    res.status(500).json({
      error: 'Failed to generate Runway prompts',
      details: error.message
    });
  }
});

/**
 * POST /api/gemini/predict-engagement
 * Predict engagement metrics and recommendations
 *
 * Request body:
 * {
 *   imageAnalysis: string,
 *   hashtags: string[]
 * }
 */
router.post('/predict-engagement', async (req, res) => {
  try {
    const { imageAnalysis, hashtags = [] } = req.body;

    if (!imageAnalysis) {
      return res.status(400).json({ error: 'imageAnalysis is required' });
    }

    if (!genAI) {
      return res.status(503).json({ error: 'Gemini service not initialized' });
    }

    const prompt = `Eres un analista de social media especializado en marketing de alimentos y panaderías.

Basado en este análisis de imagen de Instagram:
${imageAnalysis}

Hashtags sugeridos: ${hashtags.join(', ')}

Proporciona predicciones de engagement:

1. **Tipo de Contenido Más Engagable**: Qué tipo específico de video/contenido funcionará mejor
2. **Mejor Hora de Publicación**: Día y hora optimal
3. **Formato Recomendado**: Feed post / Reel / Story / Carousel
4. **CTA Más Efectivo**: Llamada a la acción que genera mayor engagement
5. **Engagement Potencial**: Estimación de likes, comments, shares (basada en datos de panaderías similares)
6. **Tendencias a Explotar**: Qué tendencias actuales se alinean con este contenido
7. **Versiones Alternativas**: 2 variaciones del contenido que también funcionarían bien

Responde en formato claro, estructurado, con datos específicos cuando sea posible.`;

    console.log('📊 Predicting engagement metrics...');

    const model = genAI.getGenerativeModel({
      model: 'gemini-pro',
      generationConfig: {
        temperature: 0.6,
        topP: 0.95,
        topK: 40,
        maxOutputTokens: 2000,
      }
    });

    const result = await model.generateContent(prompt);
    const predictionText = result.response.text();

    console.log('✅ Engagement prediction completed');
    res.json({
      success: true,
      prediction: predictionText,
      metadata: {
        timestamp: new Date().toISOString(),
        model: 'gemini-pro',
        hashtagCount: hashtags.length
      }
    });

  } catch (error) {
    console.error('❌ Error predicting engagement:', error.message);
    res.status(500).json({
      error: 'Failed to predict engagement',
      details: error.message
    });
  }
});

/**
 * POST /api/gemini/analyze-batch
 * Analyze multiple images in batch
 *
 * Request body:
 * {
 *   images: Array<{ url: string, productName: string }>
 * }
 */
router.post('/analyze-batch', async (req, res) => {
  try {
    const { images } = req.body;

    if (!Array.isArray(images) || images.length === 0) {
      return res.status(400).json({ error: 'images array is required' });
    }

    if (!genAI) {
      return res.status(503).json({ error: 'Gemini service not initialized' });
    }

    console.log(`📸 Batch analyzing ${images.length} images...`);

    const results = [];
    for (let i = 0; i < images.length; i++) {
      const { url, productName } = images[i];

      try {
        const imageResponse = await fetch(url);
        if (!imageResponse.ok) throw new Error('Failed to fetch image');

        const buffer = await imageResponse.arrayBuffer();
        const base64 = Buffer.from(buffer).toString('base64');
        const mimeType = getMimeType(url);

        const model = genAI.getGenerativeModel({ model: 'gemini-pro-vision' });
        const result = await model.generateContent([
          {
            inlineData: {
              data: base64,
              mimeType: mimeType,
            },
          },
          `Analiza esta imagen de ${productName}. Proporciona: composición, colores, calidad (1-10), mood, y 5 hashtags.`,
        ]);

        results.push({
          success: true,
          productName,
          analysis: result.response.text()
        });
      } catch (error) {
        results.push({
          success: false,
          productName,
          error: error.message
        });
      }

      // Rate limiting: delay between requests
      if (i < images.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    console.log('✅ Batch analysis completed');
    res.json({
      success: true,
      results,
      metadata: {
        timestamp: new Date().toISOString(),
        totalImages: images.length,
        successCount: results.filter(r => r.success).length
      }
    });

  } catch (error) {
    console.error('❌ Error in batch analysis:', error.message);
    res.status(500).json({
      error: 'Failed to analyze batch',
      details: error.message
    });
  }
});

/**
 * GET /api/gemini/health
 * Health check for Gemini service
 */
router.get('/health', async (req, res) => {
  try {
    if (!genAI) {
      return res.status(503).json({
        status: 'offline',
        message: 'Gemini API key not configured'
      });
    }

    // Try a simple text generation to verify API is working
    const model = genAI.getGenerativeModel({ model: 'gemini-pro' });
    await model.generateContent('Test');

    res.json({
      status: 'online',
      service: 'Gemini AI',
      models: ['gemini-pro', 'gemini-pro-vision'],
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    res.status(503).json({
      status: 'offline',
      error: error.message
    });
  }
});

/**
 * Helper: Detect MIME type from URL
 */
function getMimeType(url) {
  const ext = url.toLowerCase().split('.').pop().split('?')[0];
  const mimeTypes = {
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'webp': 'image/webp'
  };
  return mimeTypes[ext] || 'image/jpeg';
}

module.exports = router;
