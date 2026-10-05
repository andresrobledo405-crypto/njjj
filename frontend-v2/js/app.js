// Orquestrador principal
class ArtesanosApp {
  constructor() {
    this.config = {
      BACKEND_URL: 'http://localhost:3000',
      GEMINI_ENDPOINT: '/api/gemini',
      productsFile: '/data/productos.json',
    };
    this.productos = [];
    this.testimonios = [
      {
        avatar: '👨‍🍳',
        nombre: 'Carlos Mendoza',
        stars: '⭐⭐⭐⭐⭐',
        quote: 'El mejor pan que he probado en La Serena. La masa madre tiene un sabor incomparable y la textura es perfecta.'
      },
      {
        avatar: '👩‍💼',
        nombre: 'María García',
        stars: '⭐⭐⭐⭐⭐',
        quote: 'Desayunar con el pan de Artesanos se ha convertido en mi ritual diario. Siempre fresco y de excelente calidad.'
      },
      {
        avatar: '👴',
        nombre: 'Jorge López',
        stars: '⭐⭐⭐⭐⭐',
        quote: 'Llevo 30 años comiendo pan y este es el más cercano a la tradición panadería. ¡Felicitaciones al equipo!'
      }
    ];
    this.faqs = [
      {
        pregunta: '¿Qué ingredientes usan en el pan?',
        respuesta: 'Utilizamos solo ingredientes naturales: harina de trigo premium, agua filtrada, sal marina y masa madre casera. No usamos aditivos ni conservantes artificiales.'
      },
      {
        pregunta: '¿Cuál es el proceso de fermentación?',
        respuesta: 'Nuestro pan se fermenta lentamente entre 24-48 horas. Este proceso desarrolla sabor completo, mejora la digestibilidad y crea la estructura característica de nuestro pan artesanal.'
      },
      {
        pregunta: '¿A qué hora puedo comprar el pan?',
        respuesta: 'Estamos abiertos de lunes a viernes de 7am a 8pm, y sábados de 8am a 6pm. Los domingos vendemos hasta agotar stock. Recomendamos comprar temprano para mejores variedades.'
      },
      {
        pregunta: '¿Hacen entregas a domicilio?',
        respuesta: 'Sí, hacemos entregas en La Serena y sectores cercanos. Para pedidos a domicilio, contacta al +56 9 7204 4704 con 24 horas de anticipación.'
      },
      {
        pregunta: '¿Tienen opciones sin gluten?',
        respuesta: 'Actualmente no ofrecemos pan sin gluten. Contáctanos para futuras disponibilidades o si tienes alergias específicas, podemos explorar alternativas.'
      },
      {
        pregunta: '¿Cuánto tiempo se conserva el pan?',
        respuesta: 'El pan artesanal es mejor consumir dentro de 24-48 horas. Se conserva mejor en bolsa de papel a temperatura ambiente. Si deseas guardarlo más tiempo, congélalo hasta 30 días.'
      }
    ];
    this.init();
  }

  async init() {
    console.log('🍞 Iniciando Artesanos v2...');

    // Cargar productos
    await this.loadProducts();

    // Renderizar productos y nuevas secciones
    this.renderProducts();
    this.renderTestimonios();
    this.renderFAQ();

    // Inicializar sistemas
    this.initParticles();
    this.initIntersectionObserver();
    this.initGemini();
    this.initVideoGallery();
    this.initInstagram();
    this.initAccordion();

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

    document.querySelectorAll('.card, .product-card, .video-container, .testimonial-card').forEach(el => {
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

  renderTestimonios() {
    const container = document.getElementById('testimonios-container');
    if (!container) return;

    container.innerHTML = this.testimonios.map(t => `
      <div class="testimonial-card">
        <div class="testimonial-avatar">${t.avatar}</div>
        <div class="testimonial-stars">${t.stars}</div>
        <p class="testimonial-quote">"${t.quote}"</p>
        <p class="testimonial-author">— ${t.nombre}</p>
      </div>
    `).join('');
  }

  renderFAQ() {
    const container = document.getElementById('faq-container');
    if (!container) return;

    container.innerHTML = this.faqs.map((faq, index) => `
      <div class="faq-item" data-faq-index="${index}">
        <div class="faq-header">
          <h4>${faq.pregunta}</h4>
          <span class="faq-toggle">∧</span>
        </div>
        <div class="faq-content">
          <p class="faq-text">${faq.respuesta}</p>
        </div>
      </div>
    `).join('');
  }

  initAccordion() {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
      const header = item.querySelector('.faq-header');

      header.addEventListener('click', () => {
        const isActive = item.classList.contains('active');

        // Cerrar otros acordeones si uno se abre
        faqItems.forEach(otherItem => {
          if (otherItem !== item) {
            otherItem.classList.remove('active');
          }
        });

        // Toggle del item actual
        item.classList.toggle('active');
      });
    });
  }
}

// Iniciar app
const app = new ArtesanosApp();
