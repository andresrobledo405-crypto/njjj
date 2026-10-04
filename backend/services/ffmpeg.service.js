export const ffmpegService = {
  async generateClips(inputPath, bestMomentStart, platforms = ['tiktok', 'reels', 'shorts']) {
    // MVP: Mock clip generation
    // Real implementation would use fluent-ffmpeg
    const results = {};
    for (const platform of platforms) {
      results[platform] = {
        path: `/tmp/clips/${platform}_${Date.now()}.mp4`,
        size: 15000000, // Mock 15MB
      };
    }
    return results;
  },

  async cleanupTempFiles(clipPaths) {
    // Mock cleanup
    console.log('Cleaned up:', clipPaths);
  },
};
