#!/usr/bin/env node
/**
 * Professional Video Production Monitoring Dashboard
 */

function getSystemStats() {
  const os = require('os');
  return {
    timestamp: new Date().toISOString(),
    uptime: os.uptime(),
    cpus: os.cpus().length,
    memory: {
      total: (os.totalmem() / (1024 ** 3)).toFixed(2) + ' GB',
      free: (os.freemem() / (1024 ** 3)).toFixed(2) + ' GB',
      usage: (((os.totalmem() - os.freemem()) / os.totalmem()) * 100).toFixed(1) + '%'
    }
  };
}

function getProductionStats() {
  const fs = require('fs');
  const path = require('path');

  let stats = {
    total_videos: 0,
    total_size_gb: 0,
    platform_distribution: {
      youtube: 0,
      tiktok: 0,
      instagram: 0,
      facebook: 0,
      twitter: 0
    }
  };

  const exportsDir = 'exports';
  if (fs.existsSync(exportsDir)) {
    const platforms = fs.readdirSync(exportsDir);
    for (const platform of platforms) {
      const dir = path.join(exportsDir, platform);
      const files = fs.readdirSync(dir).filter(f => f.endsWith('.mp4'));
      stats.platform_distribution[platform] = files.length;
      stats.total_videos += files.length;

      for (const file of files) {
        const stat = fs.statSync(path.join(dir, file));
        stats.total_size_gb += stat.size / (1024 ** 3);
      }
    }
  }

  return stats;
}

function displayDashboard() {
  const systemStats = getSystemStats();
  const prodStats = getProductionStats();

  console.clear();
  console.log(`
╔════════════════════════════════════════════════════════════════╗
║            PROFESSIONAL VIDEO PRODUCTION DASHBOARD            ║
║                    System & Production Stats                   ║
╚════════════════════════════════════════════════════════════════╝

📊 SYSTEM INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Timestamp:        ${systemStats.timestamp}
  CPU Cores:        ${systemStats.cpus}
  Memory Total:     ${systemStats.memory.total}
  Memory Free:      ${systemStats.memory.free}
  Memory Usage:     ${systemStats.memory.usage}
  System Uptime:    ${(systemStats.uptime / 3600).toFixed(1)} hours

📺 PRODUCTION STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Total Videos:     ${prodStats.total_videos}
  Total Size:       ${prodStats.total_size_gb.toFixed(2)} GB

  Platform Distribution:
    YouTube:        ${prodStats.platform_distribution.youtube} videos
    TikTok:         ${prodStats.platform_distribution.tiktok} videos
    Instagram:      ${prodStats.platform_distribution.instagram} videos
    Facebook:       ${prodStats.platform_distribution.facebook} videos
    Twitter:        ${prodStats.platform_distribution.twitter} videos

🚀 QUICK ACTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Submit job:     node video-automation-engine.js submit <config>
  Process queue:  node video-automation-engine.js process
  View report:    node video-automation-engine.js report
  Check status:   node video-automation-engine.js jobs

⚙️  CONFIGURATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Quality Preset:   Professional (CRF 14)
  Resolution:       1080×1920 (vertical)
  FPS:              30
  Audio:            AAC 192kbps, 48kHz
  Platforms:        5 (YouTube, TikTok, IG, FB, Twitter)

`);
}

// Run dashboard
displayDashboard();

// Auto-refresh every 30 seconds
setInterval(displayDashboard, 30000);
