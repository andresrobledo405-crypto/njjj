/**
 * GSAP ScrollTrigger Animations para Artesanos Panadería v2
 * Incluye: Parallax, Stagger, Counter, Text Reveal, Box Rotation
 */

class GSAPAnimations {
  constructor() {
    this.isMobile = window.innerWidth < 768;
    this.prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    this.animationsEnabled = !this.prefersReducedMotion;
  }

  /**
   * Inicializa todas las animaciones
   */
  init() {
    if (!this.animationsEnabled) {
      console.log('Animaciones deshabilitadas por prefers-reduced-motion');
      return;
    }

    // Esperar a que GSAP esté disponible
    if (typeof gsap === 'undefined') {
      console.warn('GSAP no cargado');
      return;
    }

    // Registrar plugin ScrollTrigger
    if (typeof ScrollTrigger !== 'undefined') {
      gsap.registerPlugin(ScrollTrigger);
    }

    // Ejecutar animaciones
    this.animateParallaxHero();
    this.animateStaggerProducts();
    this.animateNumberCounter();
    this.animateTextReveal();
    this.animateBoxRotation();

    // Refrescar ScrollTrigger en resize
    window.addEventListener('resize', () => {
      ScrollTrigger.refresh();
    });
  }

  /**
   * 1. PARALLAX HERO
   * Fondo se mueve a velocidad diferente al contenido
   */
  animateParallaxHero() {
    const heroSection = document.querySelector('.hero');
    if (!heroSection) return;

    // Velocidad de parallax (reducida en mobile)
    const parallaxIntensity = this.isMobile ? 0.3 : 0.5;

    gsap.to(heroSection, {
      scrollTrigger: {
        trigger: heroSection,
        start: 'top top',
        end: 'bottom top',
        scrub: 1,
        markers: false,
      },
      y: (index, target) => {
        return gsap.getProperty(target, 'offsetHeight') * parallaxIntensity;
      },
      ease: 'none',
    });

    // Fade del contenido hero
    gsap.to('.hero-content', {
      scrollTrigger: {
        trigger: heroSection,
        start: 'top top',
        end: 'bottom top',
        scrub: 1,
      },
      opacity: 0.5,
      y: 30,
      ease: 'none',
    });
  }

  /**
   * 2. STAGGER PRODUCTS
   * Tarjetas entran una por una desde abajo
   */
  animateStaggerProducts() {
    const productCards = document.querySelectorAll('.grid-3 > div, [id="productos-container"] > div');
    if (productCards.length === 0) return;

    // Delay reducido en mobile
    const delayBetween = this.isMobile ? 0.05 : 0.1;

    gsap.from(productCards, {
      scrollTrigger: {
        trigger: '#productos',
        start: 'top center',
        end: 'top center',
        markers: false,
      },
      y: 50,
      opacity: 0,
      duration: 0.8,
      stagger: delayBetween,
      ease: 'back.out(1.2)',
    });
  }

  /**
   * 3. NUMBER COUNTER
   * Anima números en el hero (ej: 2015, números de stats)
   */
  animateNumberCounter() {
    // Buscar elementos con números (h2, h3, h4, p que empiezan con números)
    const numberElements = document.querySelectorAll(
      'h2, h3, h4, p'
    );

    let countersAnimated = false;

    numberElements.forEach((el) => {
      const text = el.textContent.trim();
      const numberMatch = text.match(/^\d+/);

      if (numberMatch && !countersAnimated) {
        const endNumber = parseInt(numberMatch[0]);
        const startNumber = 0;

        const obj = { value: startNumber };

        gsap.to(obj, {
          scrollTrigger: {
            trigger: el,
            start: 'top 80%',
            end: 'top 80%',
            markers: false,
          },
          value: endNumber,
          duration: 1,
          ease: 'power2.out',
          onUpdate: () => {
            const currentValue = Math.floor(obj.value);
            el.textContent = currentValue + text.substring(numberMatch[0].length);
          },
        });

        countersAnimated = true;
      }
    });
  }

  /**
   * 4. TEXT REVEAL
   * Texto aparece letra por letra en h2 principales
   */
  animateTextReveal() {
    const h2Elements = document.querySelectorAll('h2');

    h2Elements.forEach((h2) => {
      // No animar si el texto es muy corto
      if (h2.textContent.length < 10) return;

      const originalText = h2.textContent;
      const chars = originalText.split('');

      // Limpiar el elemento y agregar spans
      h2.innerHTML = chars
        .map((char) =>
          char === ' ' ? '<span style="margin: 0 4px;"></span>' : `<span style="opacity: 0;">${char}</span>`
        )
        .join('');

      const charSpans = h2.querySelectorAll('span');

      // Delay reducido en mobile
      const charDelay = this.isMobile ? 0.02 : 0.05;

      gsap.to(charSpans, {
        scrollTrigger: {
          trigger: h2,
          start: 'top 80%',
          end: 'top 80%',
          markers: false,
        },
        opacity: 1,
        duration: 0.3,
        stagger: charDelay,
        ease: 'back.out(1)',
      });
    });
  }

  /**
   * 5. BOX ROTATION
   * Tarjetas rotan suavemente en scroll (efecto 3D)
   */
  animateBoxRotation() {
    // Aplicar a .card y tarjetas de productos
    const boxes = document.querySelectorAll('.card');

    if (boxes.length === 0) return;

    // Intensidad de rotación (reducida en mobile)
    const rotationIntensity = this.isMobile ? 2 : 5;

    boxes.forEach((box) => {
      gsap.to(box, {
        scrollTrigger: {
          trigger: box,
          start: 'top center',
          end: 'bottom center',
          scrub: 1,
          markers: false,
        },
        rotationY: rotationIntensity,
        rotationX: rotationIntensity * 0.5,
        transformOrigin: '50% 50%',
        ease: 'sine.inOut',
      });
    });
  }

  /**
   * Limpiar animaciones (útil para cleanup)
   */
  kill() {
    if (typeof ScrollTrigger !== 'undefined') {
      ScrollTrigger.getAll().forEach((trigger) => trigger.kill());
    }
  }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    const animations = new GSAPAnimations();
    animations.init();
    window.gsapAnimations = animations; // Exponer globalmente
  });
} else {
  const animations = new GSAPAnimations();
  animations.init();
  window.gsapAnimations = animations;
}
