import { createClient } from '@supabase/supabase-js';
import { config } from '../config/env.js';

const supabase = createClient(config.supabase.url, config.supabase.key);

export const supabaseService = {
  async createVideo(userId, { title, filename }) {
    const { data: video, error } = await supabase
      .from('videos')
      .insert([{ user_id: userId, title: title || filename, status: 'uploaded' }])
      .select()
      .single();
    if (error) throw error;
    return video;
  },

  async updateVideoStatus(videoId, status, metadata = {}) {
    const { data: video, error } = await supabase
      .from('videos')
      .update({ status, ...metadata, updated_at: new Date() })
      .eq('id', videoId)
      .select()
      .single();
    if (error) throw error;
    return video;
  },

  async getVideo(videoId, userId) {
    const { data: video, error } = await supabase
      .from('videos')
      .select('*')
      .eq('id', videoId)
      .eq('user_id', userId)
      .single();
    if (error) throw error;
    return video;
  },

  async listVideos(userId) {
    const { data: videos, error } = await supabase
      .from('videos')
      .select('*')
      .eq('user_id', userId)
      .order('created_at', { ascending: false });
    if (error) throw error;
    return videos;
  },

  async createClip(videoId, platform, clipData) {
    const { data: clip, error } = await supabase
      .from('clips')
      .insert([{ video_id: videoId, platform, ...clipData }])
      .select()
      .single();
    if (error) throw error;
    return clip;
  },

  async getClips(videoId) {
    const { data: clips, error } = await supabase
      .from('clips')
      .select('*')
      .eq('video_id', videoId);
    if (error) throw error;
    return clips;
  },
};
