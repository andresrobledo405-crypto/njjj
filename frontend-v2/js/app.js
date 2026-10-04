// Orquestrador principal
class ArtesanosApp {
  constructor() {
    this.config = {
      BACKEND_URL: 'http://localhost:3000',
      GEMINI_ENDPOINT: '/api/gemini',
      productsFile: '/data/productos.json',
    };
    this.productos = [];
    this.init();
  }

  async init() {
    console.log('🍞 Iniciando Artesanos v2...');

    // Cargar productos
    await this.loadProducts();

    // Renderizar productos
    this.renderProducts();

    // Inicializar sistemas
    this.initParticles();
    this.initIntersectionObserver();
    this.initGemini();
    this.initVideoGallery();
    this.initInstagram();

    console.log('✅ Artesanos v2 listo');
  }

  async loadProducts() {
    try {
      const response = await fetch(this.config.productsFile);
      const data = await response.json();
      this.productos = data.productos;
      console.log(`📦 ${this.productos.length} productos cargados`);
    } catch (e) {
      console.error('Error cargando productos:', e);
    }
  }

  renderProducts() {
    const container = document.getElementById('productos-container');
    if (!container) return;

    container.innerHTML = this.productos.map(p => `
      <div class="product-card" data-product-id="${p.id}">
        <div class="product-image">
          ${p.imagen ? `<img src="${p.imagen}" alt="${p.nombre}" loading="lazy">` : `<span>🍞</span>`}
        </div>
        <div class="product-info">
          <h3 class="product-name">${p.nombre}</h3>
          <p class="product-description">${p.descripcion}</p>
          <div class="product-tags">
            ${p.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}
          </div>
          <div class="product-price">${p.precio}</div>
          <div class="product-gemini">
            <button class="analyze-btn" onclick="app.analyzeProduct('${p.id}')">
              <span class="gemini-icon">✨</span> Analizar con IA
            </button>
          </div>
        </div>
      </div>
    `).join('');
  }

  initParticles() {
    const canvas = document.getElementById('particles-canvas');
    if (canvas) {
      const particleSystem = new ParticleSystem(canvas);
      particleSystem.start();
    }
  }

  initIntersectionObserver() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('fade-in');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });

    document.querySelectorAll('.card, .product-card, .video-container').forEach(el => {
      observer.observe(el);
    });
  }

  async initGemini() {
    window.gemini = new GeminiClient(this.config.BACKEND_URL);
    console.log('🤖 Gemini AI integrado');
  }

  initVideoGallery() {
    window.videoManager = new VideoManager();
    console.log('🎬 Video manager listo');
  }

  initInstagram() {
    window.instagramLoader = new InstagramLoader();
    console.log('📷 Instagram loader listo');
  }

  async analyzeProduct(productId) {
    const product = this.productos.find(p => p.id === productId);
    if (!product) return;

    console.log(`Analizando: ${product.nombre}`);

    try {
      const result = await window.gemini.analyzeProduct(product);
      this.showProductAnalysis(product, result);
    } catch (e) {
      console.error('Error analizando producto:', e);
      alert('Error al analizar con IA');
    }
  }

  showProductAnalysis(product, analysis) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
      <div class="modal-content">
        <span class="close-btn" onclick="this.parentElement.parentElement.remove()">×</span>
        <h2>${product.nombre}</h2>
        <div class="analysis-content">
          ${analysis || 'Cargando análisis...'}
        </div>
      </div>
    `;
    document.body.appendChild(modal);
  }
}

// Iniciar app
const app = new ArtesanosApp();
