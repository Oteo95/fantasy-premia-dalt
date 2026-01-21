<template>
  <div 
    class="card-container"
    :class="{ 'is-revealed': isRevealed, 'is-locked': locked }"
    @mousemove="handleMouseMove"
    @mouseleave="handleMouseLeave"
    @click="$emit('click')"
    ref="cardRef"
  >
    <!-- Overlay de bloqueo FUERA del flip para que siempre se vea -->
    <div v-if="locked" class="locked-overlay">
      <div class="locked-icon">🔒</div>
      <div class="locked-text">No obtenida</div>
    </div>
    
    <div class="card-inner" :style="cardStyle">
      <!-- Parte trasera (sobre cerrado - pelota) -->
      <div class="card-face card-back">
        <div class="card-back-design">
          <div class="card-back-logo">🏀</div>
          <div class="card-back-text">FANTASY BASKET</div>
          <div class="card-back-pattern"></div>
        </div>
      </div>
      
      <!-- Parte frontal (carta del jugador con foto) -->
      <div class="card-face card-front" :class="rarityClass">
        <!-- Efecto de brillo de fondo -->
        <div class="card-glow" :class="rarityClass"></div>
        
        <!-- Efecto holográfico para cartas raras+ -->
        <div v-if="card.rareza !== 'common'" class="holographic-effect" :style="holoStyle"></div>
        
        <!-- Efecto de brillo al hover -->
        <div class="shine-effect" :class="{ active: isHovered }"></div>
        
        <!-- Borde con brillo -->
        <div class="card-border" :class="rarityClass"></div>
        
        <!-- Contenido de la carta -->
        <div class="card-content">
          <div class="card-header">
            <span class="card-rarity-badge" :class="rarityClass">{{ rarityLabel }}</span>
            <span class="card-number">#{{ card.numero }}</span>
          </div>
          
          <!-- Foto del jugador -->
          <div class="card-image-container">
            <div class="card-image-frame" :class="rarityClass">
              <img :src="card.foto" :alt="card.nombre" class="player-photo" />
              <div class="photo-gradient"></div>
              <div class="position-badge" :class="rarityClass">{{ card.posicion }}</div>
            </div>
          </div>
          
          <div class="card-info">
            <h3 class="card-name">{{ card.nombre }}</h3>
            <p class="card-position" :class="rarityClass">{{ card.equipo }}</p>
          </div>
          
          <!-- Bonificador (si tiene) -->
          <div v-if="card.condicion" class="card-bonus" :class="rarityClass">
            <div class="bonus-icon" :class="rarityClass">⚡</div>
            <div class="bonus-text">
              <span class="bonus-condition">{{ card.condicion }}</span>
              <span class="bonus-effect">x{{ card.multiplicador }}</span>
            </div>
          </div>
        </div>
        
        <!-- Partículas para legendarias -->
        <div v-if="card.rareza === 'legendary'" class="legendary-particles">
          <span v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></span>
        </div>
        
        <!-- Shimmer para épicas -->
        <div v-if="card.rareza === 'epic'" class="epic-shimmer"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  card: {
    type: Object,
    required: true
  },
  isFlipped: {
    type: Boolean,
    default: false
  },
  isRevealed: {
    type: Boolean,
    default: true
  },
  locked: {
    type: Boolean,
    default: false
  }
})

defineEmits(['click'])

const cardRef = ref(null)
const rotateX = ref(0)
const rotateY = ref(0)
const mouseX = ref(50)
const mouseY = ref(50)
const isHovered = ref(false)

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

// CORRECCIÓN: Lógica de rotación invertida
// isFlipped=true → muestra back (pelota), isFlipped=false → muestra front (foto)
const cardStyle = computed(() => {
  const baseRotateY = props.isFlipped ? 0 : 180
  return {
    transform: `perspective(1000px) rotateX(${rotateX.value}deg) rotateY(${baseRotateY + rotateY.value}deg)`
  }
})

const holoStyle = computed(() => ({
  backgroundPosition: `${mouseX.value}% ${mouseY.value}%`,
  opacity: isHovered.value ? 1 : 0.5
}))

function handleMouseMove(e) {
  if (!cardRef.value) return
  
  const rect = cardRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  
  rotateY.value = ((x - centerX) / centerX) * 20
  rotateX.value = -((y - centerY) / centerY) * 20
  
  mouseX.value = (x / rect.width) * 100
  mouseY.value = (y / rect.height) * 100
  isHovered.value = true
}

function handleMouseLeave() {
  rotateX.value = 0
  rotateY.value = 0
  mouseX.value = 50
  mouseY.value = 50
  isHovered.value = false
}

function getParticleStyle(index) {
  const angle = (index / 20) * 360
  const delay = Math.random() * 2
  const duration = 2 + Math.random() * 2
  return {
    '--angle': `${angle}deg`,
    '--delay': `${delay}s`,
    '--duration': `${duration}s`
  }
}
</script>

<style scoped>
.card-container {
  width: 280px;
  height: 420px;
  perspective: 1000px;
  cursor: pointer;
}

.card-inner {
  position: relative;
  width: 100%;
  height: 100%;
  transition: transform 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transform-style: preserve-3d;
}

.card-face {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 16px;
  overflow: hidden;
}

/* Parte trasera - Pelota */
.card-back {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: 3px solid #f39c12;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3), 0 0 30px rgba(243, 156, 18, 0.2);
}

.card-back-design {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
}

.card-back-logo {
  font-size: 80px;
  z-index: 2;
  filter: drop-shadow(0 0 20px rgba(255, 165, 0, 0.5));
  animation: pulse 2s ease-in-out infinite;
}

.card-back-text {
  font-size: 18px;
  font-weight: 800;
  color: #f39c12;
  margin-top: 15px;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(243, 156, 18, 0.5);
  z-index: 2;
}

.card-back-pattern {
  position: absolute;
  inset: 0;
  background-image: 
    repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.02) 10px, rgba(255,255,255,0.02) 20px);
}

@keyframes pulse {
  0%, 100% { transform: scale(1); filter: drop-shadow(0 0 20px rgba(255, 165, 0, 0.5)); }
  50% { transform: scale(1.08); filter: drop-shadow(0 0 35px rgba(255, 165, 0, 0.8)); }
}

/* Parte frontal - Foto del jugador */
.card-front {
  transform: rotateY(180deg);
  background: linear-gradient(180deg, #12121a 0%, #0a0a0f 100%);
}

/* Glow de fondo según rareza */
.card-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 60%;
  opacity: 0.3;
  pointer-events: none;
}

.card-glow.rarity-common { background: radial-gradient(ellipse at 50% 0%, rgba(136,136,136,0.3) 0%, transparent 70%); }
.card-glow.rarity-rare { background: radial-gradient(ellipse at 50% 0%, rgba(93,173,226,0.5) 0%, transparent 70%); }
.card-glow.rarity-epic { background: radial-gradient(ellipse at 50% 0%, rgba(155,89,182,0.5) 0%, transparent 70%); }
.card-glow.rarity-legendary { background: radial-gradient(ellipse at 50% 0%, rgba(241,196,15,0.6) 0%, transparent 70%); }

.card-border {
  position: absolute;
  inset: 0;
  border-radius: 16px;
  pointer-events: none;
  z-index: 10;
}

/* Raridades - Bordes y colores */
.rarity-common .card-border,
.card-front.rarity-common {
  border: 3px solid #888;
}

.rarity-rare .card-border,
.card-front.rarity-rare {
  border: 3px solid #5dade2;
  box-shadow: inset 0 0 20px rgba(93, 173, 226, 0.2), 0 0 20px rgba(93, 173, 226, 0.4);
}

.rarity-epic .card-border,
.card-front.rarity-epic {
  border: 3px solid #9b59b6;
  box-shadow: inset 0 0 20px rgba(155, 89, 182, 0.2), 0 0 20px rgba(155, 89, 182, 0.5);
}

.rarity-legendary .card-border,
.card-front.rarity-legendary {
  border: 3px solid #f1c40f;
  box-shadow: inset 0 0 30px rgba(241, 196, 15, 0.2), 0 0 30px rgba(241, 196, 15, 0.6);
  animation: legendary-glow 2s ease-in-out infinite;
}

@keyframes legendary-glow {
  0%, 100% { 
    box-shadow: inset 0 0 30px rgba(241, 196, 15, 0.2), 0 0 25px rgba(241, 196, 15, 0.6);
  }
  50% { 
    box-shadow: inset 0 0 40px rgba(241, 196, 15, 0.4), 0 0 40px rgba(241, 196, 15, 0.8);
  }
}

/* Efecto holográfico */
.holographic-effect {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    125deg,
    transparent 0%,
    rgba(255, 0, 255, 0.15) 20%,
    rgba(0, 255, 255, 0.15) 40%,
    rgba(255, 255, 0, 0.12) 60%,
    rgba(0, 255, 0, 0.15) 80%,
    transparent 100%
  );
  background-size: 200% 200%;
  mix-blend-mode: overlay;
  pointer-events: none;
  transition: opacity 0.3s;
  z-index: 11;
}

/* Efecto shine */
.shine-effect {
  position: absolute;
  top: 0;
  left: -100%;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  pointer-events: none;
  z-index: 12;
  transition: transform 0.6s ease-out;
}

.shine-effect.active {
  transform: translateX(400%);
}

/* Contenido */
.card-content {
  position: relative;
  height: 100%;
  padding: 12px 16px 16px 16px;
  display: flex;
  flex-direction: column;
  z-index: 5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-rarity-badge {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1.5px;
  padding: 5px 12px;
  border-radius: 6px;
}

.card-rarity-badge.rarity-common { 
  background: linear-gradient(135deg, #555 0%, #333 100%);
  color: #fff; 
}
.card-rarity-badge.rarity-rare { 
  background: linear-gradient(135deg, #5dade2 0%, #2980b9 100%);
  color: #fff;
  box-shadow: 0 2px 10px rgba(93, 173, 226, 0.5);
}
.card-rarity-badge.rarity-epic { 
  background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
  color: #fff;
  box-shadow: 0 2px 10px rgba(155, 89, 182, 0.5);
}
.card-rarity-badge.rarity-legendary { 
  background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);
  color: #000;
  box-shadow: 0 2px 10px rgba(241, 196, 15, 0.6);
}

.card-number {
  color: rgba(255,255,255,0.7);
  font-size: 18px;
  font-weight: 800;
  text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

/* Foto del jugador */
.card-image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px 0;
}

.card-image-frame {
  width: 200px;
  height: 220px;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.card-image-frame.rarity-common { border: 2px solid rgba(136,136,136,0.4); }
.card-image-frame.rarity-rare { 
  border: 2px solid rgba(93,173,226,0.4);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(93,173,226,0.3);
}
.card-image-frame.rarity-epic { 
  border: 2px solid rgba(155,89,182,0.4);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 20px rgba(155,89,182,0.3);
}
.card-image-frame.rarity-legendary { 
  border: 2px solid rgba(241,196,15,0.4);
  box-shadow: 0 10px 30px rgba(0,0,0,0.5), 0 0 25px rgba(241,196,15,0.4);
}

.player-photo {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.rarity-legendary .player-photo {
  filter: contrast(1.1) saturate(1.2);
}

.photo-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 40%;
  background: linear-gradient(transparent, rgba(0,0,0,0.8));
  pointer-events: none;
}

.position-badge {
  position: absolute;
  bottom: 8px;
  left: 8px;
  background: rgba(0,0,0,0.7);
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 700;
  backdrop-filter: blur(4px);
}

.position-badge.rarity-common { color: #888; }
.position-badge.rarity-rare { color: #5dade2; }
.position-badge.rarity-epic { color: #9b59b6; }
.position-badge.rarity-legendary { color: #f1c40f; }

.card-info {
  text-align: center;
  padding: 8px 0;
  background: linear-gradient(transparent, rgba(0,0,0,0.3));
}

.card-name {
  color: white;
  font-size: 22px;
  font-weight: 800;
  margin: 0;
  text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}

.card-position {
  font-size: 12px;
  margin: 4px 0 0 0;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600;
}

.card-position.rarity-common { color: #888; }
.card-position.rarity-rare { color: #5dade2; }
.card-position.rarity-epic { color: #9b59b6; }
.card-position.rarity-legendary { color: #f1c40f; }

/* Bonificador */
.card-bonus {
  background: rgba(0,0,0,0.4);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  backdrop-filter: blur(4px);
}

.card-bonus.rarity-rare { border: 1px solid rgba(93,173,226,0.3); }
.card-bonus.rarity-epic { border: 1px solid rgba(155,89,182,0.3); }
.card-bonus.rarity-legendary { border: 1px solid rgba(241,196,15,0.3); }

.bonus-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.bonus-icon.rarity-rare { 
  background: linear-gradient(135deg, #5dade2 0%, #2980b9 100%);
  box-shadow: 0 4px 12px rgba(93,173,226,0.4);
}
.bonus-icon.rarity-epic { 
  background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
  box-shadow: 0 4px 12px rgba(155,89,182,0.4);
}
.bonus-icon.rarity-legendary { 
  background: linear-gradient(135deg, #f1c40f 0%, #f39c12 100%);
  box-shadow: 0 4px 12px rgba(241,196,15,0.4);
}

.bonus-text {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.bonus-condition {
  font-size: 11px;
  color: rgba(255,255,255,0.7);
}

.bonus-effect {
  font-size: 14px;
  font-weight: 700;
  color: #2ecc71;
}

/* Partículas legendarias */
.legendary-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 20;
}

.particle {
  position: absolute;
  width: 4px;
  height: 4px;
  background: #f1c40f;
  border-radius: 50%;
  top: 50%;
  left: 50%;
  animation: float-particle var(--duration) ease-in-out infinite;
  animation-delay: var(--delay);
  box-shadow: 0 0 8px #f1c40f, 0 0 12px #f39c12;
}

@keyframes float-particle {
  0%, 100% {
    transform: translate(-50%, -50%) rotate(var(--angle)) translateY(0) scale(0);
    opacity: 0;
  }
  50% {
    transform: translate(-50%, -50%) rotate(var(--angle)) translateY(-150px) scale(1);
    opacity: 1;
  }
}

/* Epic shimmer */
.epic-shimmer {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(circle at 50% 50%, transparent 30%, rgba(155, 89, 182, 0.15) 70%);
  animation: epic-pulse 3s ease-in-out infinite;
  z-index: 6;
}

@keyframes epic-pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

/* Animación de revelación */
.card-container:not(.is-revealed) {
  transform: scale(0.8);
  opacity: 0;
}

.card-container.is-revealed {
  animation: card-reveal 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

@keyframes card-reveal {
  0% {
    transform: scale(0.5);
    opacity: 0;
  }
  50% {
    transform: scale(1.05);
    opacity: 1;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Overlay de bloqueo */
.locked-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(2px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 100;
  border-radius: 16px;
}

.locked-icon {
  font-size: 50px;
  margin-bottom: 10px;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.5));
}

.locked-text {
  font-size: 16px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.95);
  text-transform: uppercase;
  letter-spacing: 2px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}

/* Efecto de oscurecimiento para cartas bloqueadas */
.card-container.is-locked {
  opacity: 0.85;
  filter: grayscale(40%) brightness(0.85);
}

.card-container.is-locked:hover {
  opacity: 0.95;
  filter: grayscale(30%) brightness(0.95);
}

/* Responsive móvil */
@media (max-width: 768px) {
  .card-container {
    width: 100%;
    min-width: 200px;
    max-width: 240px;
    height: auto;
    aspect-ratio: 2/3;
  }

  .card-image-frame {
    width: 160px;
    height: 180px;
  }

  .card-name {
    font-size: 18px;
  }

  .card-position {
    font-size: 11px;
  }

  .card-rarity-badge {
    font-size: 9px;
    padding: 4px 10px;
  }

  .card-number {
    font-size: 16px;
  }

  .position-badge {
    font-size: 12px;
    padding: 3px 8px;
  }

  .card-back-logo {
    font-size: 60px;
  }

  .card-back-text {
    font-size: 14px;
  }

  .locked-icon {
    font-size: 40px;
  }

  .locked-text {
    font-size: 14px;
  }
}

@media (max-width: 480px) {
  .card-container {
    width: 100%;
    min-width: 160px;
    max-width: 200px;
    height: auto;
    aspect-ratio: 5/7;
  }

  .card-content {
    padding: 8px 10px 10px 10px;
    gap: 6px;
  }

  .card-image-container {
    padding: 4px 0;
  }

  .card-image-frame {
    width: 100%;
    max-width: 140px;
    height: 140px;
  }

  .card-name {
    font-size: 13px;
    line-height: 1.2;
  }

  .card-position {
    font-size: 10px;
    letter-spacing: 1px;
  }

  .card-info {
    padding: 6px 0;
  }

  .card-rarity-badge {
    font-size: 8px;
    padding: 3px 8px;
    letter-spacing: 1px;
  }

  .card-number {
    font-size: 14px;
  }

  .position-badge {
    font-size: 11px;
    padding: 3px 6px;
    bottom: 6px;
    left: 6px;
  }

  .card-bonus {
    padding: 6px 8px;
  }

  .bonus-icon {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }

  .bonus-condition {
    font-size: 9px;
  }

  .bonus-effect {
    font-size: 11px;
  }

  .card-header {
    flex-wrap: nowrap;
    gap: 4px;
  }

  .card-back-logo {
    font-size: 50px;
  }

  .card-back-text {
    font-size: 12px;
  }

  .locked-icon {
    font-size: 35px;
  }

  .locked-text {
    font-size: 12px;
    letter-spacing: 1px;
  }
}

@media (max-width: 360px) {
  .card-container {
    min-width: 150px;
    max-width: 180px;
  }

  .card-content {
    padding: 6px 8px 8px 8px;
  }

  .card-image-frame {
    max-width: 120px;
    height: 120px;
  }

  .card-name {
    font-size: 12px;
  }

  .card-rarity-badge {
    font-size: 7px;
    padding: 2px 6px;
  }

  .card-number {
    font-size: 12px;
  }

  .position-badge {
    font-size: 10px;
  }
}
</style>
