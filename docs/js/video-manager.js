// Gestor de videos - YouTube, MP4, Runway
class VideoManager {
  constructor() {
    this.isMobile = this.detectMobile();
    this.videoInitialized = false;

    this.videos = [
      {
        id: 'hero-video',
        type: 'youtube',
        src: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        title: 'Artesanos Panadería - Presentación',
      },
      {
        id: 'process-video',
        type: 'youtube',
        src: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        title: 'Proceso de Elaboración - Masa Madre',
      },
      {
        id: 'runway-demo',
        type: 'youtube',
        src: 'https://www.youtube.com/embed/dQw4w9WgXcQ',
        title: 'Video IA - Runway ML Demo',
      },
    ];
  }

  // Detect mobile devices
  detectMobile() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
      || window.innerWidth <= 768;
  }

  // Initialize hero video with fallback handling
  initializeHeroVideo() {
    const container = document.getElementById('hero-video-container');
    if (!container || this.videoInitialized) return;

    if (this.isMobile) {
      // Mobile: Hide iframe, show fallback SVG
      const iframe = document.getElementById('hero-iframe');
      if (iframe) {
        iframe.style.display = 'none';
      }
      const svg = document.querySelector('.hero-fallback-svg');
      if (svg) {
        svg.style.display = 'block';
      }
      console.log('📱 Mobile detected: Using SVG fallback');
    } else {
      // Desktop: Show YouTube embed with error handling
      const iframe = document.getElementById('hero-iframe');
      if (iframe) {
        iframe.style.display = 'block';
        iframe.addEventListener('error', () => this.onVideoError());
      }
      console.log('🎥 Desktop: YouTube video loaded');
    }

    this.videoInitialized = true;
  }

  // Handle video loading error with fallback
  onVideoError() {
    console.warn('⚠️ Video failed to load, showing SVG fallback');
    const iframe = document.getElementById('hero-iframe');
    const svg = document.querySelector('.hero-fallback-svg');

    if (iframe) iframe.style.display = 'none';
    if (svg) svg.style.display = 'block';
  }

  getVideoHtml(videoId) {
    const video = this.videos.find(v => v.id === videoId);
    if (!video) return '';

    if (video.type === 'youtube') {
      return `
        <div class="video-container">
          <iframe
            src="${video.src}?autoplay=1&mute=1"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen>
          </iframe>
          <div class="video-meta">
            <h3>${video.title}</h3>
          </div>
        </div>
      `;
    }

    if (video.type === 'mp4') {
      return `
        <div class="video-container">
          <video controls>
            <source src="${video.src}" type="video/mp4">
            Tu navegador no soporta video
          </video>
          <div class="video-meta">
            <h3>${video.title}</h3>
          </div>
        </div>
      `;
    }

    return '';
  }

  renderHeroVideo(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = this.getVideoHtml('hero-video');
    }
  }

  renderGallery(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    container.innerHTML = `
      <div class="video-grid">
        ${this.videos.map(v => `
          <div class="video-item" data-video-id="${v.id}">
            ${this.getVideoHtml(v.id)}
          </div>
        `).join('')}
      </div>
    `;
  }

  playVideo(videoId) {
    const container = document.querySelector(`[data-video-id="${videoId}"]`);
    if (container) {
      container.scrollIntoView({ behavior: 'smooth' });
    }
  }
}

// Crear instancia global
window.videoManager = new VideoManager();
