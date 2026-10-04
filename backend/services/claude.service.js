import axios from 'axios';
import { config } from '../config/env.js';

export const claudeService = {
  async analyzeVideo(transcript, frames = []) {
    const limitedFrames = frames.slice(0, 10);
    const messageContent = [
      {
        type: 'text',
        text: `Eres un experto en contenido viral. Analiza este video.

Transcripción: "${transcript}"

Responde SOLO en JSON:
{
  "viral_scores": {"tiktok": 8, "reels": 6, "shorts": 7, "linkedin": 3},
  "best_moment": {"start_sec": 5, "end_sec": 30},
  "hashtags": ["#SaaS", "#Startup"],
  "needs_captions": true,
  "recommended_duration": {"tiktok": 45, "reels": 60, "shorts": 50}
}`,
      },
    ];

    for (const frame of limitedFrames) {
      messageContent.push({
        type: 'image',
        source: { type: 'base64', media_type: 'image/jpeg', data: frame },
      });
    }

    try {
      const response = await axios.post(
        'https://api.anthropic.com/v1/messages',
        {
          model: 'claude-3-5-sonnet-20241022',
          max_tokens: 1024,
          messages: [{ role: 'user', content: messageContent }],
        },
        { headers: { 'x-api-key': config.claude.apiKey, 'anthropic-version': '2023-06-01' } }
      );

      const jsonText = response.data.content[0].text;
      const analysis = JSON.parse(jsonText);
      return analysis;
    } catch (error) {
      console.error('Claude error:', error.response?.data || error.message);
      throw new Error('Failed to analyze video');
    }
  },
};
