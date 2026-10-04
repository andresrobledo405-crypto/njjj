// Cargador de contenido Instagram (Manual + Gemini)
class InstagramLoader {
  constructor() {
    this.posts = [];
    this.maxPosts = 6;
    this.loadFromStorage();
  }

  loadFromStorage() {
    const stored = localStorage.getItem('artesanos-instagram-posts');
    if (stored) {
      this.posts = JSON.parse(stored);
    }
  }

  saveToStorage() {
    localStorage.setItem('artesanos-instagram-posts', JSON.stringify(this.posts));
  }

  async addPost(imageUrl, caption = '') {
    // Si no hay caption, generar con Gemini
    let finalCaption = caption;
    if (!caption && window.gemini) {
      finalCaption = await window.gemini.generateCaption('Artesanos Panadería', imageUrl);
    }

    const post = {
      id: `post-${Date.now()}`,
      imageUrl,
      caption: finalCaption,
      likes: Math.floor(Math.random() * 500) + 50,
      comments: Math.floor(Math.random() * 50) + 5,
      timestamp: new Date().toISOString(),
    };

    this.posts.unshift(post);
    if (this.posts.length > this.maxPosts) {
      this.posts.pop();
    }

    this.saveToStorage();
    return post;
  }

  removePost(postId) {
    this.posts = this.posts.filter(p => p.id !== postId);
    this.saveToStorage();
  }

  async renderFeed(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (this.posts.length === 0) {
      container.innerHTML = `
        <div class="instagram-empty">
          <p>📷 Sube tus primeras imágenes desde Instagram</p>
          <button onclick="document.getElementById('image-upload').click()" class="cta-button">
            + Subir Imagen
          </button>
          <input type="file" id="image-upload" style="display:none;" accept="image/*"
            onchange="window.instagramLoader.handleImageUpload(event)">
        </div>
      `;
      return;
    }

    container.innerHTML = `
      <div class="instagram-feed">
        ${this.posts.map(post => `
          <div class="instagram-post">
            <div class="instagram-image">
              <img src="${post.imageUrl}" alt="Post" loading="lazy">
            </div>
            <div class="instagram-info">
              <p class="caption">${post.caption}</p>
              <div class="engagement">
                <span>❤️ ${post.likes}</span>
                <span>💬 ${post.comments}</span>
                <button class="remove-btn" onclick="window.instagramLoader.removePost('${post.id}'); window.instagramLoader.renderFeed('${containerId}')">
                  ✕ Eliminar
                </button>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
      <button onclick="document.getElementById('image-upload').click()" class="cta-button" style="margin-top: 20px;">
        + Agregar más imágenes
      </button>
      <input type="file" id="image-upload" style="display:none;" accept="image/*"
        onchange="window.instagramLoader.handleImageUpload(event)">
    `;
  }

  handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = async (e) => {
      const imageUrl = e.target.result;
      await this.addPost(imageUrl);

      // Re-renderizar feed
      const containerId = document.querySelector('.instagram-feed')?.parentElement.id;
      if (containerId) {
        this.renderFeed(containerId);
      }
    };

    reader.readAsDataURL(file);
    event.target.value = '';
  }

  async renderPostModal(postId) {
    const post = this.posts.find(p => p.id === postId);
    if (!post) return;

    const analysis = await window.gemini?.generateVideoPrompt('Artesanos', post.caption);

    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <span class="close-btn" onclick="this.parentElement.parentElement.remove()">×</span>
        <h2>Análisis Post Instagram</h2>
        <img src="${post.imageUrl}" alt="Post" style="max-width: 100%; margin: 20px 0;">
        <p><strong>Caption:</strong> ${post.caption}</p>
        <p><strong>Engagement:</strong> ${post.likes} likes, ${post.comments} comments</p>

        ${analysis ? `
          <h3>Prompts para Video (Runway ML):</h3>
          <div class="prompts-list">
            ${analysis.map((p, i) => `
              <div class="prompt-item">
                <p><strong>Opción ${i + 1}:</strong></p>
                <p style="font-style: italic;">${p}</p>
              </div>
            `).join('')}
          </div>
        ` : ''}
      </div>
    `;

    document.body.appendChild(modal);
  }
}

// Estilos para Instagram
const instagramStyles = `
.instagram-feed {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.instagram-post {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transition: transform 0.3s ease;
}

.instagram-post:hover {
  transform: translateY(-4px);
}

.instagram-image {
  width: 100%;
  height: 280px;
  overflow: hidden;
  background: #f0f0f0;
}

.instagram-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.instagram-info {
  padding: 16px;
}

.caption {
  font-size: 0.9rem;
  color: #333;
  margin-bottom: 12px;
  line-height: 1.4;
}

.engagement {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 0.85rem;
  color: #666;
}

.remove-btn {
  background: #ff4757;
  color: white;
  border: none;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.75rem;
  margin-left: auto;
}

.remove-btn:hover {
  background: #ff3838;
}

.instagram-empty {
  text-align: center;
  padding: 40px 20px;
  color: #666;
}

.prompts-list {
  background: #f9f7f4;
  padding: 16px;
  border-radius: 8px;
  margin-top: 12px;
}

.prompt-item {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.prompt-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}
`;

// Inyectar estilos
if (document.head) {
  const style = document.createElement('style');
  style.textContent = instagramStyles;
  document.head.appendChild(style);
}
