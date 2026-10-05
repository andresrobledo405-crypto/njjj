// Cliente Gemini API
class GeminiClient {
  constructor(backendUrl) {
    this.backendUrl = backendUrl;
  }

  async analyzeProduct(product) {
    try {
      const response = await fetch(`${this.backendUrl}/api/gemini/analyze-product`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: product.nombre,
          description: product.descripcion,
          topic: product.geminiTopic,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      return data.analysis || 'Análisis no disponible';
    } catch (e) {
      console.error('Error Gemini:', e);
      return `Análisis local: ${product.nombre} es un pan artesanal premium elaborado con ingredientes selectos.`;
    }
  }

  async generateCaption(productName, imageUrl) {
    try {
      const response = await fetch(`${this.backendUrl}/api/gemini/generate-caption`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          productName,
          imageUrl,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      return data.caption || '';
    } catch (e) {
      console.error('Error generando caption:', e);
      return `Descubre ${productName} - Pan artesanal hecho con pasión 🍞`;
    }
  }

  async generateVideoPrompt(productName, description) {
    try {
      const response = await fetch(`${this.backendUrl}/api/gemini/generate-video-prompt`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          productName,
          description,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      return data.prompts || [];
    } catch (e) {
      console.error('Error generando video prompt:', e);
      return [`Artesanal bakery product: ${productName}`];
    }
  }

  async predictEngagement(productName, imageUrl) {
    try {
      const response = await fetch(`${this.backendUrl}/api/gemini/predict-engagement`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          productName,
          imageUrl,
        }),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      return data.prediction || {};
    } catch (e) {
      console.error('Error prediciendo engagement:', e);
      return { likes: '🔮', comments: '🔮', shares: '🔮' };
    }
  }
}
