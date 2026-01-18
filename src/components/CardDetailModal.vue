<template>
  <div class="card-detail-modal" :class="{ active: isOpen }" @click="handleBackgroundClick">
    <div class="modal-content" @click.stop>
      <!-- Botón cerrar -->
      <button class="close-btn" @click="$emit('close')">✕</button>
      
      <!-- Botón para voltear -->
      <button class="flip-btn" @click="toggleFlip">
        <span v-if="!isFlipped">📊 Ver Stats</span>
        <span v-else>🃏 Ver Carta</span>
      </button>
      
      <!-- Contenedor de la carta con flip -->
      <div class="card-flip-wrapper">
        <div class="card-flip-inner" :class="{ flipped: isFlipped }">
          
          <!-- FRENTE: Información de la carta -->
          <div class="card-flip-face card-flip-front" :class="rarityClass">
            <div class="card-glow" :class="rarityClass"></div>
            <div class="card-border" :class="rarityClass"></div>
            
            <div class="card-content">
              <div class="card-header">
                <span class="card-rarity-badge" :class="rarityClass">{{ rarityLabel }}</span>
                <span class="card-number">#{{ card.numero }}</span>
              </div>
              
              <div class="card-image-container">
                <div class="card-image-frame" :class="rarityClass">
                  <img :src="card.foto" :alt="card.nombre" class="player-photo" />
                  <div class="photo-gradient"></div>
                  <div class="position-badge" :class="rarityClass">{{ card.posicion }}</div>
                </div>
              </div>
              
              <div class="card-info">
                <h3 class="card-name">{{ card.nombre }}</h3>
                <p class="card-team">{{ card.equipo }}</p>
                <p class="card-year">Temporada {{ card.año }}</p>
              </div>
              
              <div v-if="card.condicion" class="card-bonus" :class="rarityClass">
                <div class="bonus-icon" :class="rarityClass">⚡</div>
                <div class="bonus-text">
                  <span class="bonus-condition">{{ card.condicion }}</span>
                  <span class="bonus-effect">x{{ card.multiplicador }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- REVERSO: Estadísticas con radar chart -->
          <div class="card-flip-face card-flip-back" :class="rarityClass">
            <div class="card-border" :class="rarityClass"></div>
            
            <div class="stats-content">
              <h3 class="stats-title">Estadísticas</h3>
              <p class="stats-player-name">{{ card.nombre }}</p>
              
              <!-- Radar Chart SVG -->
              <div class="radar-container">
                <svg viewBox="0 0 320 320" class="radar-chart" preserveAspectRatio="xMidYMid meet">
                  <!-- Grid de fondo -->
                  <g class="grid-circles">
                    <circle cx="160" cy="160" r="100" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                    <circle cx="160" cy="160" r="75" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                    <circle cx="160" cy="160" r="50" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                    <circle cx="160" cy="160" r="25" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="1"/>
                  </g>
                  
                  <!-- Líneas desde el centro -->
                  <g class="grid-lines">
                    <line v-for="(stat, index) in statsArray" :key="'line-' + index"
                          :x1="160" :y1="160"
                          :x2="getRadarPoint(index, 100).x"
                          :y2="getRadarPoint(index, 100).y"
                          stroke="rgba(255,255,255,0.15)" stroke-width="1"/>
                  </g>
                  
                  <!-- Polígono de estadísticas -->
                  <polygon 
                    :points="radarPoints"
                    :fill="radarColor"
                    :stroke="radarStrokeColor"
                    stroke-width="3"
                    fill-opacity="0.4"/>
                  
                  <!-- Puntos en cada vértice -->
                  <g class="stat-points">
                    <circle v-for="(point, index) in radarPointsArray" :key="'point-' + index"
                            :cx="point.x" :cy="point.y" r="5"
                            :fill="radarStrokeColor"
                            stroke="#fff"
                            stroke-width="2"/>
                  </g>
                  
                  <!-- Labels y valores -->
                  <g class="stat-labels">
                    <g v-for="(stat, index) in statsArray" :key="'label-group-' + index">
                      <text 
                        :x="getLabelPoint(index).x"
                        :y="getLabelPoint(index).y"
                        text-anchor="middle"
                        fill="white"
                        font-size="13"
                        font-weight="700"
                        class="stat-label-name">
                        {{ stat.name }}
                      </text>
                      <text 
                        :x="getLabelPoint(index).x"
                        :y="getLabelPoint(index).y + 14"
                        text-anchor="middle"
                        :fill="radarStrokeColor"
                        font-size="15"
                        font-weight="800"
                        class="stat-label-value">
                        {{ stat.value }}
                      </text>
                    </g>
                  </g>
                </svg>
              </div>
              
              <!-- Lista de estadísticas adicionales -->
              <div class="stats-list">
                <div v-for="(stat, index) in statsArray" :key="'stat-' + index" class="stat-item">
                  <span class="stat-name">{{ stat.name }}</span>
                  <div class="stat-bar-container">
                    <div class="stat-bar" :style="{ width: stat.value + '%', backgroundColor: radarStrokeColor }"></div>
                  </div>
                  <span class="stat-value">{{ stat.value }}</span>
                </div>
              </div>
            </div>
          </div>
          
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  card: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close'])

const isFlipped = ref(false)

const rarityClass = computed(() => `rarity-${props.card.rareza}`)

const rarityLabel = computed(() => {
  const labels = {
    common: 'COMÚN',
    rare: 'RARA',
    epic: 'ÉPICA',
    legendary: 'LEGENDARIA'
  }
  return labels[props.card.rareza] || 'COMÚN'
})

const radarColor = computed(() => {
  const colors = {
    common: 'rgba(136,136,136,0.5)',
    rare: 'rgba(93,173,226,0.5)',
    epic: 'rgba(155,89,182,0.5)',
    legendary: 'rgba(241,196,15,0.5)'
  }
  return colors[props.card.rareza] || 'rgba(136,136,136,0.5)'
})

const radarStrokeColor = computed(() => {
  const colors = {
    common: '#888',
    rare: '#5dade2',
    epic: '#9b59b6',
    legendary: '#f1c40f'
  }
  return colors[props.card.rareza] || '#888'
})

const statsArray = computed(() => {
  const stats = props.card.stats || {}
  return [
    { name: 'VEL', value: stats.velocidad || 0 },
    { name: 'T3P', value: stats.tiro3 || 0 },
    { name: 'T2P', value: stats.tiro2 || 0 },
    { name: 'FUE', value: stats.fuerza || 0 },
    { name: 'DEF', value: stats.defensa || 0 },
    { name: 'PAS', value: stats.pase || 0 }
  ]
})

// Calcular puntos del radar
function getRadarPoint(index, radius) {
  const angle = (Math.PI * 2 * index) / statsArray.value.length - Math.PI / 2
  const value = statsArray.value[index].value
  const scaledRadius = (radius * value) / 100
  
  return {
    x: 160 + Math.cos(angle) * scaledRadius,
    y: 160 + Math.sin(angle) * scaledRadius
  }
}

function getLabelPoint(index) {
  const angle = (Math.PI * 2 * index) / statsArray.value.length - Math.PI / 2
  const radius = 125
  
  return {
    x: 160 + Math.cos(angle) * radius,
    y: 160 + Math.sin(angle) * radius
  }
}

const radarPoints = computed(() => {
  return statsArray.value.map((_, index) => {
    const point = getRadarPoint(index, 100)
    return `${point.x},${point.y}`
  }).join(' ')
})

const radarPointsArray = computed(() => {
  return statsArray.value.map((_, index) => getRadarPoint(index, 100))
})

function toggleFlip() {
  isFlipped.value = !isFlipped.value
}

function handleBackgroundClick() {
  emit('close')
}
</script>

<style scoped>
.card-detail-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
  padding: 40px 20px;
}

.card-detail-modal.active {
  opacity: 1;
  pointer-events: all;
}

.modal-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 30px;
}

.close-btn {
  position: fixed;
  top: 30px;
  right: 30px;
  width: 55px;
  height: 55px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(30, 30, 40, 0.9);
  color: white;
  font-size: 26px;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 2100;
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.close-btn:hover {
  background: rgba(220, 53, 69, 0.9);
  border-color: rgba(255, 255, 255, 0.6);
  transform: rotate(90deg);
  box-shadow: 0 6px 25px rgba(220, 53, 69, 0.6);
}

.flip-btn {
  padding: 16px 40px;
  border-radius: 35px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.95) 0%, rgba(230, 126, 34, 0.95) 100%);
  color: white;
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  z-index: 10;
  box-shadow: 0 6px 25px rgba(243, 156, 18, 0.5);
  backdrop-filter: blur(10px);
  min-width: 200px;
  text-align: center;
}

.flip-btn:hover {
  transform: scale(1.08);
  box-shadow: 0 10px 35px rgba(243, 156, 18, 0.7);
  background: linear-gradient(135deg, rgba(243, 156, 18, 1) 0%, rgba(230, 126, 34, 1) 100%);
}

/* Flip Container */
.card-flip-wrapper {
  perspective: 2000px;
  width: 420px;
  height: 670px;
}

.card-flip-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.8s;
  transform-style: preserve-3d;
}

.card-flip-inner.flipped {
  transform: rotateY(180deg);
}

.card-flip-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 20px;
  background: linear-gradient(180deg, #12121a 0%, #0a0a0f 100%);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
}

.card-flip-front {
  /* Frente de la carta */
}

.card-flip-back {
  transform: rotateY(180deg);
}

/* Estilos de la carta (frente) */
.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 60%;
  opacity: 0.3;
  pointer-events: none;
  border-radius: 20px 20px 0 0;
}

.card-glow.rarity-common { background: radial-gradient(ellipse at 50% 0%, rgba(136,136,136,0.3) 0%, transparent 70%); }
.card-glow.rarity-rare { background: radial-gradient(ellipse at 50% 0%, rgba(93,173,226,0.5) 0%, transparent 70%); }
.card-glow.rarity-epic { background: radial-gradient(ellipse at 50% 0%, rgba(155,89,182,0.5) 0%, transparent 70%); }
.card-glow.rarity-legendary { background: radial-gradient(ellipse at 50% 0%, rgba(241,196,15,0.6) 0%, transparent 70%); }

.card-border {
  position: absolute;
  inset: 0;
  border-radius: 20px;
  pointer-events: none;
  z-index: 1;
}

.rarity-common .card-border { border: 4px solid #888; }
.rarity-rare .card-border { border: 4px solid #5dade2; box-shadow: inset 0 0 30px rgba(93, 173, 226, 0.3), 0 0 30px rgba(93, 173, 226, 0.5); }
.rarity-epic .card-border { border: 4px solid #9b59b6; box-shadow: inset 0 0 30px rgba(155, 89, 182, 0.3), 0 0 30px rgba(155, 89, 182, 0.6); }
.rarity-legendary .card-border { border: 4px solid #f1c40f; box-shadow: inset 0 0 40px rgba(241, 196, 15, 0.3), 0 0 40px rgba(241, 196, 15, 0.7); animation: legendary-glow 2s ease-in-out infinite; }

@keyframes legendary-glow {
  0%, 100% { box-shadow: inset 0 0 40px rgba(241, 196, 15, 0.3), 0 0 35px rgba(241, 196, 15, 0.7); }
  50% { box-shadow: inset 0 0 50px rgba(241, 196, 15, 0.5), 0 0 50px rgba(241, 196, 15, 0.9); }
}

.card-content {
  position: relative;
  height: 100%;
  padding: 20px;
  display: flex;
  flex-direction: column;
  z-index: 5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.card-rarity-badge {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 2px;
  padding: 6px 14px;
  border-radius: 8px;
}

.card-rarity-badge.rarity-common { background: linear-gradient(135deg, #555 0%, #333 100%); color: #fff; }
.card-rarity-badge.rarity-rare { background: linear-gradient(135deg, #5dade2 0%, #2980b9 100%); color: #fff; box-shadow: 0 3px 15px rgba(93, 173, 226, 0.6); }
.card-rarity-badge.rarity-epic { background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); color: #fff; box-shadow: 0 3px 15px rgba(155, 89, 182, 0.6); }
.card-rarity-badge.rarity-legendary { background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%); color: #000; box-shadow: 0 3px 15px rgba(241, 196, 15, 0.7); }

.card-number {
  color: rgba(255,255,255,0.8);
  font-size: 24px;
  font-weight: 800;
  text-shadow: 0 2px 6px rgba(0,0,0,0.5);
}

.card-image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
}

.card-image-frame {
  width: 300px;
  height: 320px;
  border-radius: 16px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 15px 40px rgba(0,0,0,0.6);
}

.card-image-frame.rarity-common { border: 3px solid rgba(136,136,136,0.5); }
.card-image-frame.rarity-rare { border: 3px solid rgba(93,173,226,0.5); box-shadow: 0 15px 40px rgba(0,0,0,0.6), 0 0 30px rgba(93,173,226,0.4); }
.card-image-frame.rarity-epic { border: 3px solid rgba(155,89,182,0.5); box-shadow: 0 15px 40px rgba(0,0,0,0.6), 0 0 30px rgba(155,89,182,0.4); }
.card-image-frame.rarity-legendary { border: 3px solid rgba(241,196,15,0.5); box-shadow: 0 15px 40px rgba(0,0,0,0.6), 0 0 35px rgba(241,196,15,0.5); }

.player-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(transparent, rgba(0,0,0,0.9));
  pointer-events: none;
}

.position-badge {
  position: absolute;
  bottom: 12px;
  left: 12px;
  background: rgba(0,0,0,0.8);
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 700;
  backdrop-filter: blur(6px);
}

.position-badge.rarity-common { color: #888; }
.position-badge.rarity-rare { color: #5dade2; }
.position-badge.rarity-epic { color: #9b59b6; }
.position-badge.rarity-legendary { color: #f1c40f; }

.card-info {
  text-align: center;
  padding: 15px 0;
}

.card-name {
  color: white;
  font-size: 28px;
  font-weight: 800;
  margin: 0 0 8px 0;
  text-shadow: 0 3px 6px rgba(0,0,0,0.6);
}

.card-team {
  font-size: 14px;
  color: rgba(255,255,255,0.7);
  margin: 0 0 4px 0;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600;
}

.card-year {
  font-size: 12px;
  color: rgba(255,255,255,0.5);
  margin: 0;
}

.card-bonus {
  background: rgba(0,0,0,0.5);
  border-radius: 12px;
  padding: 12px 15px;
  display: flex;
  align-items: center;
  gap: 12px;
  backdrop-filter: blur(6px);
  margin-top: 10px;
}

.card-bonus.rarity-rare { border: 2px solid rgba(93,173,226,0.4); }
.card-bonus.rarity-epic { border: 2px solid rgba(155,89,182,0.4); }
.card-bonus.rarity-legendary { border: 2px solid rgba(241,196,15,0.4); }

.bonus-icon {
  width: 50px;
  height: 50px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.bonus-icon.rarity-rare { background: linear-gradient(135deg, #5dade2 0%, #2980b9 100%); box-shadow: 0 5px 15px rgba(93,173,226,0.5); }
.bonus-icon.rarity-epic { background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%); box-shadow: 0 5px 15px rgba(155,89,182,0.5); }
.bonus-icon.rarity-legendary { background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%); box-shadow: 0 5px 15px rgba(241,196,15,0.5); }

.bonus-text {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.bonus-condition {
  font-size: 13px;
  color: rgba(255,255,255,0.8);
}

.bonus-effect {
  font-size: 18px;
  font-weight: 700;
  color: #2ecc71;
}

/* Estilos de estadísticas (reverso) */
.stats-content {
  position: relative;
  height: 100%;
  padding: 20px 15px 15px 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 5;
  overflow-y: auto;
}

.stats-title {
  color: white;
  font-size: 20px;
  font-weight: 800;
  margin: 0 0 3px 0;
  text-align: center;
  text-shadow: 0 2px 6px rgba(0,0,0,0.6);
}

.stats-player-name {
  color: rgba(255,255,255,0.7);
  font-size: 14px;
  font-weight: 600;
  margin: 0 0 15px 0;
  text-align: center;
}

.radar-container {
  width: 100%;
  max-width: 280px;
  margin-bottom: 15px;
  padding: 10px 0;
}

.radar-chart {
  width: 100%;
  height: auto;
  filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3));
}

.stat-label-name,
.stat-label-value {
  text-shadow: 0 2px 4px rgba(0,0,0,0.8);
}

/* Lista de estadísticas */
.stats-list {
  width: 100%;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  background: rgba(0,0,0,0.3);
  border-radius: 8px;
  backdrop-filter: blur(5px);
}

.stat-name {
  color: white;
  font-size: 11px;
  font-weight: 700;
  min-width: 35px;
}

.stat-bar-container {
  flex: 1;
  height: 8px;
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
  overflow: hidden;
}

.stat-bar {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.stat-value {
  color: white;
  font-size: 12px;
  font-weight: 800;
  min-width: 30px;
  text-align: right;
}

/* Responsive */
@media (max-width: 768px) {
  .card-detail-modal {
    padding: 30px 15px;
  }

  .card-flip-wrapper {
    width: 90vw;
    max-width: 350px;
    height: auto;
    aspect-ratio: 2/3;
    min-height: 450px;
  }
  
  .card-content {
    padding: 15px;
  }

  .card-name {
    font-size: 22px;
  }

  .card-team {
    font-size: 13px;
  }
  
  .card-image-frame {
    width: 220px;
    height: 240px;
  }
  
  .radar-container {
    max-width: 260px;
  }
  
  .stats-title {
    font-size: 18px;
  }

  .close-btn {
    top: 20px;
    right: 20px;
    width: 50px;
    height: 50px;
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .card-detail-modal {
    padding: 20px 10px;
  }

  .card-flip-wrapper {
    width: 90vw;
    max-width: 280px;
    height: 75vh;
    max-height: 500px;
  }

  .modal-content {
    gap: 15px;
  }

  .card-content {
    padding: 12px;
  }

  .card-header {
    margin-bottom: 8px;
  }

  .card-rarity-badge {
    font-size: 9px;
    padding: 4px 10px;
    letter-spacing: 1px;
  }

  .card-number {
    font-size: 16px;
  }
  
  .card-image-container {
    padding: 4px 0;
    flex: 0 1 auto;
  }

  .card-image-frame {
    width: 100%;
    max-width: 180px;
    height: 180px;
  }

  .card-info {
    padding: 8px 0;
  }
  
  .card-name {
    font-size: 16px;
    margin-bottom: 4px;
  }

  .card-team {
    font-size: 11px;
    letter-spacing: 1px;
  }

  .card-year {
    font-size: 10px;
  }

  .position-badge {
    font-size: 12px;
    padding: 4px 8px;
  }

  .card-bonus {
    padding: 8px 10px;
    gap: 8px;
    margin-top: 6px;
  }

  .bonus-icon {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .bonus-condition {
    font-size: 9px;
  }

  .bonus-effect {
    font-size: 13px;
  }

  /* Stats back side - solo radar chart en móvil */
  .stats-content {
    padding: 12px 8px 8px 8px;
    overflow-y: auto;
    justify-content: center;
  }

  .stats-title {
    font-size: 16px;
    margin-bottom: 2px;
  }

  .stats-player-name {
    font-size: 11px;
    margin-bottom: 15px;
  }
  
  /* Radar chart más grande y centrado */
  .radar-container {
    max-width: 240px;
    padding: 10px 0;
    margin-bottom: 0;
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .radar-chart {
    max-height: 240px;
  }

  .stat-label-name {
    font-size: 10px;
  }

  .stat-label-value {
    font-size: 13px;
  }

  /* Ocultar barras de estadísticas en móvil */
  .stats-list {
    display: none !important;
  }
  
  .flip-btn {
    padding: 10px 16px;
    font-size: 13px;
    min-width: 120px;
  }

  .close-btn {
    top: 12px;
    right: 12px;
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
}

@media (max-width: 360px) {
  .card-flip-wrapper {
    width: 95vw;
    max-width: 260px;
  }

  .card-image-frame {
    max-width: 180px;
    height: 180px;
  }

  .card-name {
    font-size: 16px;
  }

  .radar-container {
    max-width: 200px;
  }

  .stats-title {
    font-size: 15px;
  }
}
</style>
