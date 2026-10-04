import express from 'express';
import multer from 'multer';
import { authMiddleware } from '../middleware/auth.js';
import { supabaseService } from '../services/supabase.service.js';
import { claudeService } from '../services/claude.service.js';
import { ffmpegService } from '../services/ffmpeg.service.js';
import { validateFileSize, validateVideoFormat } from '../utils/validators.js';

const router = express.Router();
const upload = multer({ storage: multer.memoryStorage() });

router.post('/upload', authMiddleware, upload.single('video'), async (req, res) => {
  try {
    const { file } = req;
    const { title } = req.body;
    const userId = req.user.userId;

    if (!file) return res.status(400).json({ error: 'No file provided' });
    if (!validateFileSize(file.size)) return res.status(400).json({ error: 'File too large' });
    if (!validateVideoFormat(file.originalname)) return res.status(400).json({ error: 'Invalid format' });

    const video = await supabaseService.createVideo(userId, {
      title: title || file.originalname,
      filename: file.originalname,
    });

    res.status(201).json({
      video: { id: video.id, title: video.title, status: 'uploaded' },
      next: 'Call POST /videos/:id/process to generate clips',
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/', authMiddleware, async (req, res) => {
  try {
    const videos = await supabaseService.listVideos(req.user.userId);
    res.json({ videos });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.get('/:id', authMiddleware, async (req, res) => {
  try {
    const video = await supabaseService.getVideo(req.params.id, req.user.userId);
    const clips = await supabaseService.getClips(video.id);
    res.json({ video, clips });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

router.post('/:id/process', authMiddleware, async (req, res) => {
  try {
    const videoId = req.params.id;
    const video = await supabaseService.getVideo(videoId, req.user.userId);

    if (!video) return res.status(404).json({ error: 'Video not found' });

    await supabaseService.updateVideoStatus(videoId, 'processing');

    // Mock analysis (real would call Claude)
    const analysis = {
      viral_scores: { tiktok: 8, reels: 6, shorts: 7, linkedin: 3 },
      best_moment: { start_sec: 5, end_sec: 30 },
      hashtags: ['#SaaS', '#Startup', '#Tech'],
      needs_captions: true,
    };

    // Mock clip generation (real would call FFmpeg)
    const clipUrls = {
      tiktok: `https://example.com/clips/${videoId}/tiktok.mp4`,
      reels: `https://example.com/clips/${videoId}/reels.mp4`,
      shorts: `https://example.com/clips/${videoId}/shorts.mp4`,
    };

    await supabaseService.updateVideoStatus(videoId, 'ready', {
      viral_score_tiktok: analysis.viral_scores.tiktok,
      viral_score_reels: analysis.viral_scores.reels,
      viral_score_shorts: analysis.viral_scores.shorts,
      viral_score_linkedin: analysis.viral_scores.linkedin,
      best_moment_start: analysis.best_moment.start_sec,
      best_moment_end: analysis.best_moment.end_sec,
    });

    for (const [platform, url] of Object.entries(clipUrls)) {
      await supabaseService.createClip(videoId, platform, {
        clip_url: url,
        status: 'draft',
        duration_sec: 45,
      });
    }

    res.json({ message: 'Video processed', analysis, clips: clipUrls });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

export default router;
