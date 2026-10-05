// Sistema de partículas - Harina/Pan cayendo
class ParticleSystem {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.particles = [];
    this.running = false;
    this.particleCount = 50;

    this.resizeCanvas();
    window.addEventListener('resize', () => this.resizeCanvas());
  }

  resizeCanvas() {
    this.canvas.width = window.innerWidth;
    this.canvas.height = Math.min(window.innerHeight, 600);
  }

  createParticles() {
    for (let i = 0; i < this.particleCount; i++) {
      this.particles.push({
        x: Math.random() * this.canvas.width,
        y: Math.random() * this.canvas.height - this.canvas.height,
        size: Math.random() * 4 + 2,
        opacity: Math.random() * 0.5 + 0.3,
        velocityY: Math.random() * 1 + 0.5,
        velocityX: (Math.random() - 0.5) * 0.5,
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.05,
      });
    }
  }

  update() {
    this.particles.forEach(p => {
      p.y += p.velocityY;
      p.x += p.velocityX;
      p.rotation += p.rotationSpeed;

      // Recyclar partículas que salen de pantalla
      if (p.y > this.canvas.height) {
        p.y = -10;
        p.x = Math.random() * this.canvas.width;
      }

      if (p.x < 0 || p.x > this.canvas.width) {
        p.x = (p.x + this.canvas.width) % this.canvas.width;
      }
    });
  }

  draw() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

    this.particles.forEach(p => {
      this.ctx.save();
      this.ctx.translate(p.x, p.y);
      this.ctx.rotate(p.rotation);

      // Dibujar partícula como círculo
      this.ctx.globalAlpha = p.opacity;
      this.ctx.fillStyle = '#d4a574';
      this.ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);

      this.ctx.restore();
    });
  }

  animate() {
    if (!this.running) return;

    this.update();
    this.draw();
    requestAnimationFrame(() => this.animate());
  }

  start() {
    if (!this.running) {
      this.running = true;
      this.createParticles();
      this.animate();
      console.log('🌾 Particle system iniciado');
    }
  }

  stop() {
    this.running = false;
    this.particles = [];
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }
}
