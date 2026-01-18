<template>
  <div class="home-view">
    <!-- Header con info del usuario -->
    <div class="user-header">
      <div class="user-info">
        <div class="user-avatar">🏀</div>
        <div class="user-details">
          <h2>¡Hola, {{ userName }}!</h2>
          <p class="user-rank">Posición en ranking: #{{ userRank }}</p>
        </div>
      </div>
      <div class="user-stats">
        <div class="stat">
          <span class="stat-value">{{ userPoints }}</span>
          <span class="stat-label">Puntos</span>
        </div>
        <div class="stat">
          <span class="stat-value">{{ userCollection.length }}</span>
          <span class="stat-label">Cartas</span>
        </div>
      </div>
    </div>

    <!-- Próximo partido -->
    <div class="next-match-card">
      <div class="match-badge">PRÓXIMO PARTIDO</div>
      <div class="match-info">
        <div class="team home">
          <span class="team-logo">🏠</span>
          <span class="team-name">Tu Club</span>
        </div>
        <div class="match-vs">VS</div>
        <div class="team away">
          <span class="team-logo">🏀</span>
          <span class="team-name">Rival FC</span>
        </div>
      </div>
      <div class="match-date">
        <span>📅 Sábado 18 Enero</span>
        <span>🕐 18:00h</span>
      </div>
    </div>

    <!-- Sobres sin abrir - CARRUSEL -->
    <div v-if="unopenedPacks.length > 0" class="unopened-packs-section">
      <div class="section-header">
        <h3>🎁 Sobres por abrir</h3>
        <span class="pack-count">{{ unopenedPacks.length }}</span>
      </div>
      
      <div class="carousel-container">
        <button 
          v-if="unopenedPacks.length > 1"
          class="carousel-btn prev" 
          @click="prevPack"
          :disabled="currentPackIndex === 0"
        >
          ←
        </button>
        
        <div class="carousel-wrapper">
          <div 
            class="carousel-track"
            :style="{ transform: `translateX(-${currentPackIndex * 100}%)` }"
          >
            <div 
              v-for="(pack, index) in unopenedPacks" 
              :key="index"
              class="carousel-item"
            >
              <div 
                class="pack-card-3d"
                :class="`pack-${pack.type}`"
              >
                <div class="pack-glow"></div>
                <div class="pack-content">
                  <div class="pack-details">
                    <div class="pack-title">Sobre de cartas</div>
                    <div class="pack-card-count">
                      <span class="count-number">{{ getPackCardCount(pack.type) }}</span>
                      <span class="count-label">cartas</span>
                    </div>
                  </div>
                  <button class="pack-open-btn" @click="handleOpenPack(index)">
                    ABRIR
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <button 
          v-if="unopenedPacks.length > 1"
          class="carousel-btn next" 
          @click="nextPack"
          :disabled="currentPackIndex === unopenedPacks.length - 1"
        >
          →
        </button>
      </div>
      
      <!-- Indicadores de carrusel -->
      <div v-if="unopenedPacks.length > 1" class="carousel-indicators">
        <span 
          v-for="(pack, index) in unopenedPacks" 
          :key="index"
          class="indicator"
          :class="{ active: index === currentPackIndex }"
          @click="currentPackIndex = index"
        ></span>
      </div>
    </div>

    <!-- Acciones rápidas -->
    <div class="quick-actions">
      <button class="action-card primary" @click="$emit('navigate', 'redeem')">
        <div class="action-icon">🎁</div>
        <div class="action-content">
          <h3>Canjear Código</h3>
          <p>Recibe sobres para abrir</p>
        </div>
        <div class="action-arrow">→</div>
      </button>

      <button class="action-card" @click="$emit('navigate', 'lineup')">
        <div class="action-icon">⚔️</div>
        <div class="action-content">
          <h3>Mi Alineación</h3>
          <p>{{ userLineup.length }}/5 jugadores</p>
        </div>
        <div class="action-arrow">→</div>
      </button>

      <button class="action-card" @click="$emit('navigate', 'collection')">
        <div class="action-icon">🃏</div>
        <div class="action-content">
          <h3>Mi Colección</h3>
          <p>{{ userCollection.length }} cartas</p>
        </div>
        <div class="action-arrow">→</div>
      </button>

      <button class="action-card" @click="$emit('navigate', 'rankings')">
        <div class="action-icon">🏆</div>
        <div class="action-content">
          <h3>Rankings</h3>
          <p>Ver clasificación</p>
        </div>
        <div class="action-arrow">→</div>
      </button>
    </div>

    <!-- Colección rápida (últimas cartas) -->
    <div v-if="userCollection.length > 0" class="recent-cards">
      <h3>Últimas cartas obtenidas</h3>
      <div class="cards-preview">
        <div 
          v-for="card in recentCards" 
          :key="card.id"
          class="mini-card"
          :class="`rarity-${card.rareza}`"
        >
          <span class="mini-card-pos">{{ card.posicion }}</span>
          <span class="mini-card-name">{{ card.nombre ? card.nombre.split(' ')[1] || card.nombre : '?' }}</span>
        </div>
      </div>
    </div>

    <!-- Estado vacío - Código de bienvenida -->
    <div v-else class="empty-state">
      <div class="empty-icon">🎁</div>
      <h3>¡Bienvenido a Fantasy Basket!</h3>
      <p>Usa este código especial para obtener tu primera alineación completa.</p>
      
      <div class="welcome-code">
        <div class="code-label">Código de Bienvenida:</div>
        <div class="code-value">BIENVENIDA</div>
        <div class="code-description">5 cartas - Una de cada posición</div>
      </div>
      
      <button class="cta-button" @click="$emit('navigate', 'redeem')">
        <span>🎁</span>
        <span>Canjear código ahora</span>
      </button>
    </div>

    <!-- Pack Opening Component -->
    <PackOpening 
      :is-open="showPackOpening"
      :cards="currentPackCards"
      @close="handlePackOpeningComplete"
      @complete="handlePackOpeningComplete"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useGameStore } from '../composables/useGameStore'
import PackOpening from '../components/PackOpening.vue'

const { userCollection, userLineup, userPoints, userName, unopenedPacks, openPack } = useGameStore()

defineEmits(['navigate'])

const userRank = computed(() => 156) // Simulado

const recentCards = computed(() => {
  return userCollection.value.slice(-4).reverse()
})

// Pack opening
const showPackOpening = ref(false)
const currentPackCards = ref([])

// Carousel state
const currentPackIndex = ref(0)

function getPackName(type) {
  const names = {
    'welcome': 'Sobre de Bienvenida',
    'standard': 'Sobre Estándar',
    'legendary': 'Sobre Legendario'
  }
  return names[type] || 'Sobre'
}

function getPackCardCount(type) {
  const counts = {
    'welcome': 5,
    'standard': 2,
    'legendary': 3
  }
  return counts[type] || 2
}

function getPackIcon(type) {
  const icons = {
    'welcome': '🎁',
    'standard': '📦',
    'legendary': '✨'
  }
  return icons[type] || '📦'
}

function getRarityLabel(type) {
  const labels = {
    'welcome': 'Bienvenida',
    'standard': 'Estándar',
    'legendary': 'Legendario'
  }
  return labels[type] || 'Estándar'
}

// Carousel functions
function prevPack() {
  if (currentPackIndex.value > 0) {
    currentPackIndex.value--
  }
}

function nextPack() {
  if (currentPackIndex.value < unopenedPacks.value.length - 1) {
    currentPackIndex.value++
  }
}

async function handleOpenPack(packIndex) {
  const result = await openPack(packIndex)
  
  if (result.success && result.newCards) {
    currentPackCards.value = result.newCards
    showPackOpening.value = true
    // Reset carousel position if we opened the current pack
    if (currentPackIndex.value >= unopenedPacks.value.length && unopenedPacks.value.length > 0) {
      currentPackIndex.value = Math.max(0, unopenedPacks.value.length - 1)
    }
  }
}

function handlePackOpeningComplete() {
  showPackOpening.value = false
  currentPackCards.value = []
}
</script>

<style scoped>
.home-view {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.user-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  margin-bottom: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-avatar {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
}

.user-details h2 {
  margin: 0;
  font-size: 18px;
  color: white;
}

.user-rank {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

.user-stats {
  display: flex;
  gap: 20px;
}

.stat {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #f39c12;
}

.stat-label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
}

/* Próximo partido */
.next-match-card {
  background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.match-badge {
  font-size: 10px;
  font-weight: 700;
  color: #2ecc71;
  letter-spacing: 2px;
  margin-bottom: 15px;
}

.match-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 15px;
}

.team {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.team-logo {
  font-size: 40px;
}

.team-name {
  font-size: 14px;
  color: white;
  font-weight: 600;
}

.match-vs {
  font-size: 20px;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.3);
}

.match-date {
  display: flex;
  justify-content: center;
  gap: 20px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.6);
}

/* Sobres sin abrir - CARRUSEL */
.unopened-packs-section {
  margin-bottom: 30px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.section-header h3 {
  font-size: 18px;
  color: white;
  margin: 0;
}

.pack-count {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  color: white;
  font-size: 14px;
  font-weight: 700;
  padding: 6px 16px;
  border-radius: 20px;
  box-shadow: 0 4px 15px rgba(243, 156, 18, 0.3);
}

/* Carrusel Container */
.carousel-container {
  position: relative;
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.carousel-wrapper {
  flex: 1;
  overflow: hidden;
  border-radius: 20px;
}

.carousel-track {
  display: flex;
  transition: transform 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.carousel-item {
  min-width: 100%;
  padding: 25px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Pack Card 3D - Estilo sobre de cromos con textura y VOLUMEN */
.pack-card-3d {
  position: relative;
  aspect-ratio: 2/3;
  max-width: 200px;
  width: 100%;
  border-radius: 12px;
  transform-style: preserve-3d;
  transition: all 0.4s ease;
  transform: perspective(1200px) rotateY(-12deg) rotateX(3deg);
  filter: drop-shadow(0 8px 20px rgba(0, 0, 0, 0.4));
}

.pack-card-3d:hover {
  transform: perspective(1200px) rotateY(0deg) rotateX(0deg) translateY(-8px) scale(1.05);
  filter: drop-shadow(0 15px 40px rgba(0, 0, 0, 0.6));
}

/* Cara frontal del sobre con volumen */
.pack-card-3d .pack-content {
  position: relative;
  height: 100%;
  border-radius: 12px;
  overflow: hidden;
  /* Sombras internas para simular grosor */
  box-shadow: 
    inset 0 3px 2px rgba(255, 255, 255, 0.5),
    inset 0 -3px 12px rgba(0, 0, 0, 0.4),
    inset 6px 0 15px rgba(0, 0, 0, 0.3),
    inset -6px 0 15px rgba(255, 255, 255, 0.3),
    /* Bulto central donde están las cartas */
    inset 0 -80px 100px -40px rgba(0, 0, 0, 0.25);
}

/* Lado izquierdo del sobre (efecto 3D) */
.pack-card-3d::before {
  content: '';
  position: absolute;
  top: 0;
  left: -8px;
  width: 8px;
  height: 100%;
  background: linear-gradient(to right, rgba(0, 0, 0, 0.6), transparent);
  transform: rotateY(-90deg);
  transform-origin: right;
  z-index: -1;
}

/* Lado superior del sobre (efecto 3D) */
.pack-card-3d::after {
  content: '';
  position: absolute;
  top: -8px;
  left: 0;
  width: 100%;
  height: 8px;
  background: linear-gradient(to bottom, rgba(0, 0, 0, 0.4), transparent);
  transform: rotateX(90deg);
  transform-origin: bottom;
  z-index: -1;
}


/* Fondos con imagen base (todos iguales) */
.pack-card-3d {
  background-image: url('../assets/sobre.png');
  background-size: cover;
  background-position: center;
}

/* Glow externo sutil (sin color) */
.pack-glow {
  position: absolute;
  inset: -3px;
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.4s;
  pointer-events: none;
  z-index: -1;
  filter: blur(20px);
  background: rgba(255, 255, 255, 0.3);
}

.pack-card-3d:hover .pack-glow {
  opacity: 0.4;
  filter: blur(25px);
}

.pack-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  padding: 30px 20px 20px 20px;
  height: 100%;
  z-index: 3;
  /* Textura de papel metalizado con patrón */
  background-image: 
    /* Patrón de diamantes holográfico */
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent 10px,
      rgba(255, 255, 255, 0.02) 10px,
      rgba(255, 255, 255, 0.02) 20px
    ),
    repeating-linear-gradient(
      -45deg,
      transparent,
      transparent 10px,
      rgba(255, 255, 255, 0.02) 10px,
      rgba(255, 255, 255, 0.02) 20px
    ),
    /* Textura de puntos */
    radial-gradient(circle at 25% 25%, rgba(255, 255, 255, 0.05) 1px, transparent 1px),
    radial-gradient(circle at 75% 75%, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
    /* Brillo holográfico animado */
    linear-gradient(
      110deg,
      transparent 0%,
      transparent 40%,
      rgba(255, 255, 255, 0.6) 45%,
      rgba(255, 255, 255, 0.8) 50%,
      rgba(255, 255, 255, 0.6) 55%,
      transparent 60%,
      transparent 100%
    );
  background-size: 20px 20px, 20px 20px, 4px 4px, 4px 4px, 300% 300%;
  background-position: 0 0, 0 0, 0 0, 2px 2px, 0% 0%;
  animation: holographic-sweep 6s ease-in-out infinite;
}

@keyframes holographic-sweep {
  0%, 100% {
    background-position: 0 0, 0 0, 0 0, 2px 2px, -100% 0%;
  }
  50% {
    background-position: 0 0, 0 0, 0 0, 2px 2px, 200% 0%;
  }
}

/* Overlay de textura granulada */
.pack-content::before {
  content: '';
  position: absolute;
  inset: 0;
  background-image: 
    url("data:image/svg+xml,%3Csvg width='100' height='100' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' /%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='100' height='100' filter='url(%23noise)' opacity='0.08'/%3E%3C/svg%3E");
  opacity: 0.4;
  pointer-events: none;
  z-index: 1;
  mix-blend-mode: overlay;
}

/* Logo o marca en el centro del sobre */
.pack-content::after {
  content: '🏀';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 180px;
  opacity: 0.08;
  pointer-events: none;
  z-index: 0;
  filter: blur(2px);
}

.pack-details {
  text-align: center;
}

.pack-title {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 12px;
  text-shadow: 0 1px 2px rgba(255, 255, 255, 0.3);
}

.pack-card-count {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 8px;
}

.count-number {
  font-size: 40px;
  font-weight: 900;
  color: #e67e22;
  text-shadow: 0 2px 4px rgba(230, 126, 34, 0.3);
}

.count-label {
  font-size: 16px;
  color: #34495e;
  font-weight: 600;
}

.pack-open-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 16px 40px;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  border: none;
  border-radius: 30px;
  color: white;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 6px 20px rgba(243, 156, 18, 0.4);
}

.pack-open-btn:hover {
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 10px 30px rgba(243, 156, 18, 0.6);
}

.pack-open-btn:active {
  transform: translateY(-1px) scale(1.02);
}

.btn-icon {
  font-size: 20px;
  animation: sparkle 1.5s ease-in-out infinite;
}

@keyframes sparkle {
  0%, 100% { transform: rotate(0deg) scale(1); }
  25% { transform: rotate(-15deg) scale(1.2); }
  75% { transform: rotate(15deg) scale(1.2); }
}

/* Carousel Buttons */
.carousel-btn {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  color: white;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
}

.carousel-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  transform: scale(1.1);
}

.carousel-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.carousel-btn.prev:hover:not(:disabled) {
  transform: scale(1.1) translateX(-3px);
}

.carousel-btn.next:hover:not(:disabled) {
  transform: scale(1.1) translateX(3px);
}

/* Carousel Indicators */
.carousel-indicators {
  display: flex;
  justify-content: center;
  gap: 10px;
  padding: 10px 0;
}

.indicator {
  width: 10px;
  height: 10px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.3s;
}

.indicator:hover {
  background: rgba(255, 255, 255, 0.5);
  transform: scale(1.2);
}

.indicator.active {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  width: 30px;
  border-radius: 5px;
  box-shadow: 0 0 10px rgba(243, 156, 18, 0.5);
}

/* Acciones rápidas */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 30px;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  text-align: left;
  width: 100%;
}

.action-card:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.action-card.primary {
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.2) 0%, rgba(230, 126, 34, 0.2) 100%);
  border-color: rgba(243, 156, 18, 0.3);
}

.action-card.primary:hover {
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.3) 0%, rgba(230, 126, 34, 0.3) 100%);
}

.action-icon {
  font-size: 28px;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.action-content {
  flex: 1;
}

.action-content h3 {
  margin: 0;
  font-size: 16px;
  color: white;
}

.action-content p {
  margin: 4px 0 0 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.5);
}

.action-arrow {
  font-size: 20px;
  color: rgba(255, 255, 255, 0.3);
}

/* Cartas recientes */
.recent-cards h3 {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 12px;
}

.cards-preview {
  display: flex;
  gap: 10px;
}

.mini-card {
  flex: 1;
  padding: 12px 8px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  text-align: center;
  border: 2px solid transparent;
}

.mini-card.rarity-common { border-color: #888; }
.mini-card.rarity-rare { border-color: #5dade2; }
.mini-card.rarity-epic { border-color: #9b59b6; }
.mini-card.rarity-legendary { border-color: #f1c40f; box-shadow: 0 0 10px rgba(241, 196, 15, 0.3); }

.mini-card-pos {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.mini-card-name {
  display: block;
  font-size: 10px;
  color: rgba(255, 255, 255, 0.6);
  margin-top: 4px;
}

/* Estado vacío */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 2px dashed rgba(255, 255, 255, 0.1);
}

.empty-icon {
  font-size: 60px;
  margin-bottom: 15px;
}

.empty-state h3 {
  color: white;
  margin: 0 0 10px 0;
}

.empty-state p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0 0 25px 0;
}

.welcome-code {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.1) 0%, rgba(39, 174, 96, 0.1) 100%);
  border: 2px solid rgba(46, 204, 113, 0.3);
  border-radius: 16px;
  padding: 20px;
  margin: 0 auto 25px auto;
  max-width: 300px;
  animation: glow 2s ease-in-out infinite;
}

@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 10px rgba(46, 204, 113, 0.2);
  }
  50% {
    box-shadow: 0 0 20px rgba(46, 204, 113, 0.4);
  }
}

.code-label {
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 8px;
}

.code-value {
  font-size: 32px;
  font-weight: 900;
  color: #2ecc71;
  font-family: 'Courier New', monospace;
  letter-spacing: 3px;
  margin-bottom: 8px;
  text-shadow: 0 0 10px rgba(46, 204, 113, 0.3);
}

.code-description {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  font-weight: 600;
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 40px;
  font-size: 16px;
  font-weight: 700;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  border: none;
  border-radius: 30px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.cta-button:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(243, 156, 18, 0.4);
}

/* Responsive móvil */
@media (max-width: 640px) {
  .home-view {
    padding: 15px;
  }

  .user-header {
    padding: 15px;
    flex-direction: column;
    gap: 15px;
  }

  .user-info {
    width: 100%;
    justify-content: center;
  }

  .user-stats {
    width: 100%;
    justify-content: center;
  }

  .user-avatar {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }

  .user-details h2 {
    font-size: 16px;
  }

  .stat-value {
    font-size: 20px;
  }

  .next-match-card {
    padding: 15px;
  }

  .team-logo {
    font-size: 32px;
  }

  .team-name {
    font-size: 12px;
  }

  .match-vs {
    font-size: 16px;
  }

  .section-header h3 {
    font-size: 16px;
  }

  .carousel-btn {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }

  .pack-card-3d {
    max-width: 180px;
  }

  .pack-title {
    font-size: 14px;
  }

  .count-number {
    font-size: 32px;
  }

  .count-label {
    font-size: 14px;
  }

  .pack-open-btn {
    padding: 12px 30px;
    font-size: 14px;
  }

  .action-card {
    padding: 14px 16px;
  }

  .action-icon {
    width: 44px;
    height: 44px;
    font-size: 24px;
  }

  .action-content h3 {
    font-size: 15px;
  }

  .action-content p {
    font-size: 12px;
  }

  .mini-card {
    padding: 10px 6px;
  }

  .mini-card-pos {
    font-size: 16px;
  }

  .mini-card-name {
    font-size: 9px;
  }
}

@media (max-width: 380px) {
  .home-view {
    padding: 10px;
  }

  .pack-card-3d {
    max-width: 160px;
  }

  .carousel-btn {
    width: 36px;
    height: 36px;
    font-size: 18px;
  }

  .action-icon {
    width: 40px;
    height: 40px;
    font-size: 22px;
  }
}
</style>
