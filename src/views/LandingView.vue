<template>
  <div class="landing">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div class="hero-badge">
          <span class="badge-icon">🏆</span>
          <span class="badge-text">Temporada 2026</span>
        </div>
        
        <h1 class="hero-title">
          <span class="title-main">Fantasy Basket</span>
          <span class="title-sub">Club</span>
        </h1>
        
        <p class="hero-description">
          Colecciona cartas de tus jugadores favoritos, crea tu alineación perfecta
          y compite en rankings globales.
        </p>
        
        <div class="hero-buttons">
          <button class="btn btn-primary" @click="$emit('navigate', 'signup')">
            <span class="btn-icon">🚀</span>
            <span>Comenzar Ahora</span>
          </button>
          <button class="btn btn-secondary" @click="$emit('navigate', 'signin')">
            <span class="btn-icon">🔑</span>
            <span>Iniciar Sesión</span>
          </button>
        </div>
        
        <div class="hero-stats">
          <div class="stat">
            <div class="stat-value">10K+</div>
            <div class="stat-label">Jugadores</div>
          </div>
          <div class="stat">
            <div class="stat-value">50+</div>
            <div class="stat-label">Cartas Únicas</div>
          </div>
          <div class="stat">
            <div class="stat-value">24/7</div>
            <div class="stat-label">Rankings Activos</div>
          </div>
        </div>
      </div>
      
      <!-- Animated cards -->
      <div class="floating-cards">
        <div class="floating-card card-1">🏀</div>
        <div class="floating-card card-2">⭐</div>
        <div class="floating-card card-3">🔥</div>
        <div class="floating-card card-4">💎</div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="container">
        <h2 class="section-title">
          <span class="title-highlight">¿Cómo</span> Funciona?
        </h2>
        
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon">🃏</div>
            <h3 class="feature-title">Colecciona Cartas</h3>
            <p class="feature-description">
              Obtén cartas de diferentes rarezas: común, rara, épica y legendaria.
              Cada carta tiene estadísticas únicas.
            </p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">⚔️</div>
            <h3 class="feature-title">Crea tu Alineación</h3>
            <p class="feature-description">
              Selecciona hasta 5 cartas para formar tu equipo ideal.
              Combina estrategias y maximiza puntos.
            </p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">🎁</div>
            <h3 class="feature-title">Canjea Códigos</h3>
            <p class="feature-description">
              Usa códigos especiales para obtener sobres con nuevas cartas.
              ¡Cada código es una sorpresa!
            </p>
          </div>
          
          <div class="feature-card">
            <div class="feature-icon">🏆</div>
            <h3 class="feature-title">Compite en Rankings</h3>
            <p class="feature-description">
              Gana puntos basados en el rendimiento real de tus jugadores.
              Escala posiciones y conviértete en el mejor.
            </p>
          </div>
        </div>
      </div>
    </section>

    <!-- Rarities Section -->
    <section class="rarities">
      <div class="container">
        <h2 class="section-title">
          Rarezas de <span class="title-highlight">Cartas</span>
        </h2>
        
        <div class="rarities-grid">
          <div class="rarity-card common">
            <div class="rarity-icon">⚪</div>
            <h3 class="rarity-name">Común</h3>
            <div class="rarity-multiplier">x1</div>
            <p class="rarity-description">Cartas base con estadísticas estándar</p>
          </div>
          
          <div class="rarity-card rare">
            <div class="rarity-icon">🔵</div>
            <h3 class="rarity-name">Rara</h3>
            <div class="rarity-multiplier">x1.5</div>
            <p class="rarity-description">Bonificador condicional</p>
          </div>
          
          <div class="rarity-card epic">
            <div class="rarity-icon">🟣</div>
            <h3 class="rarity-name">Épica</h3>
            <div class="rarity-multiplier">x2</div>
            <p class="rarity-description">Doble puntos con condición</p>
          </div>
          
          <div class="rarity-card legendary">
            <div class="rarity-icon">🟡</div>
            <h3 class="rarity-name">Legendaria</h3>
            <div class="rarity-multiplier">x3</div>
            <p class="rarity-description">Triple puntos - Ultra rara</p>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta">
      <div class="cta-content">
        <h2 class="cta-title">¿Listo para Comenzar?</h2>
        <p class="cta-description">
          Únete a miles de jugadores y crea tu equipo legendario hoy.
        </p>
        <button class="btn btn-cta" @click="$emit('navigate', 'signup')">
          <span class="btn-icon">🎮</span>
          <span>Crear Cuenta Gratis</span>
        </button>
      </div>
    </section>

    <!-- Footer -->
    <footer class="footer">
      <div class="footer-content">
        <div class="footer-logo">
          <span class="logo-icon">🏀</span>
          <span class="logo-text">Fantasy Basket Club</span>
        </div>
        <p class="footer-text">© 2026 - Temporada Actual</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
defineEmits(['navigate'])
</script>

<style scoped>
.landing {
  min-height: 100vh;
}

/* Hero Section */
.hero {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  overflow: hidden;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background: 
    radial-gradient(circle at 20% 50%, rgba(243, 156, 18, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(155, 89, 182, 0.1) 0%, transparent 50%);
  animation: bgPulse 10s ease-in-out infinite;
}

@keyframes bgPulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

.hero-content {
  position: relative;
  z-index: 10;
  text-align: center;
  max-width: 700px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(243, 156, 18, 0.1);
  border: 1px solid rgba(243, 156, 18, 0.3);
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 30px;
  animation: fadeInDown 1s ease-out;
}

.badge-icon {
  font-size: 16px;
}

.hero-title {
  font-size: clamp(48px, 10vw, 72px);
  font-weight: 900;
  margin-bottom: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  animation: fadeInUp 1s ease-out 0.2s backwards;
}

.title-main {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.title-sub {
  font-size: 0.6em;
  color: rgba(255, 255, 255, 0.7);
  line-height: 1;
}

.hero-description {
  font-size: 18px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 40px;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  animation: fadeInUp 1s ease-out 0.4s backwards;
}

.hero-buttons {
  display: flex;
  gap: 15px;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 60px;
  animation: fadeInUp 1s ease-out 0.6s backwards;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(243, 156, 18, 0.4);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 156, 18, 0.5);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.hero-stats {
  display: flex;
  justify-content: center;
  gap: 60px;
  flex-wrap: wrap;
  animation: fadeInUp 1s ease-out 0.8s backwards;
}

.stat {
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 900;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
  margin-top: 5px;
}

/* Floating Cards */
.floating-cards {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.floating-card {
  position: absolute;
  font-size: 60px;
  opacity: 0.1;
  animation: float 20s ease-in-out infinite;
}

.card-1 {
  top: 10%;
  left: 10%;
  animation-delay: 0s;
}

.card-2 {
  top: 70%;
  left: 15%;
  animation-delay: 5s;
}

.card-3 {
  top: 20%;
  right: 10%;
  animation-delay: 10s;
}

.card-4 {
  bottom: 15%;
  right: 15%;
  animation-delay: 15s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0) rotate(0deg);
  }
  25% {
    transform: translateY(-30px) rotate(5deg);
  }
  50% {
    transform: translateY(-15px) rotate(-5deg);
  }
  75% {
    transform: translateY(-40px) rotate(3deg);
  }
}

/* Sections */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.section-title {
  text-align: center;
  font-size: clamp(32px, 6vw, 48px);
  font-weight: 900;
  margin-bottom: 60px;
}

.title-highlight {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Features */
.features {
  padding: 100px 20px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 30px;
}

.feature-card {
  padding: 40px 30px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  text-align: center;
  transition: all 0.3s;
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-5px);
  border-color: rgba(243, 156, 18, 0.3);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 15px;
}

.feature-description {
  font-size: 15px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.6);
}

/* Rarities */
.rarities {
  padding: 100px 20px;
  background: rgba(0, 0, 0, 0.3);
}

.rarities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.rarity-card {
  padding: 30px 20px;
  border-radius: 16px;
  text-align: center;
  border: 2px solid;
  transition: all 0.3s;
}

.rarity-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.rarity-card.common {
  background: rgba(136, 136, 136, 0.1);
  border-color: #888888;
}

.rarity-card.rare {
  background: rgba(93, 173, 226, 0.1);
  border-color: #5dade2;
}

.rarity-card.epic {
  background: rgba(155, 89, 182, 0.1);
  border-color: #9b59b6;
}

.rarity-card.legendary {
  background: rgba(241, 196, 15, 0.1);
  border-color: #f1c40f;
}

.rarity-icon {
  font-size: 40px;
  margin-bottom: 15px;
}

.rarity-name {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 10px;
}

.rarity-multiplier {
  font-size: 28px;
  font-weight: 900;
  margin-bottom: 10px;
  opacity: 0.9;
}

.rarity-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* CTA */
.cta {
  padding: 100px 20px;
  text-align: center;
}

.cta-content {
  max-width: 600px;
  margin: 0 auto;
}

.cta-title {
  font-size: clamp(32px, 6vw, 48px);
  font-weight: 900;
  margin-bottom: 20px;
}

.cta-description {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.7);
  margin-bottom: 40px;
}

.btn-cta {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(243, 156, 18, 0.4);
  font-size: 18px;
  padding: 20px 40px;
}

.btn-cta:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(243, 156, 18, 0.6);
}

/* Footer */
.footer {
  padding: 40px 20px;
  background: rgba(0, 0, 0, 0.5);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-content {
  text-align: center;
}

.footer-logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 18px;
  font-weight: 800;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.footer-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.5);
}

/* Animations */
@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 768px) {
  .hero {
    min-height: auto;
    padding: 60px 20px;
  }
  
  .hero-stats {
    gap: 40px;
  }
  
  .features, .rarities, .cta {
    padding: 60px 20px;
  }
}
</style>
