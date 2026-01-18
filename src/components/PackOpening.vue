<template>
  <div class="pack-opening-overlay" :class="{ active: isOpen }">
    <div class="pack-opening-container">
      <!-- Fondo con partículas -->
      <div class="background-effects">
        <div class="light-rays"></div>
        <div class="particles-container">
          <span v-for="i in 50" :key="i" class="bg-particle" :style="getBgParticleStyle(i)"></span>
        </div>
      </div>

      <!-- Estado: Sobre cerrado -->
      <div v-if="state === 'closed'" class="pack-closed" @click="startOpening">
        <div class="pack-3d" ref="packRef" :style="packStyle" @mousemove="handlePackMove" @mouseleave="handlePackLeave">
          <div class="pack-wrapper">
            <div class="pack-front">
              <div class="pack-design">
                <div class="pack-logo">🏀</div>
                <div class="pack-title">FANTASY BASKET</div>
                <div class="pack-subtitle">SOBRE DE JUGADORES</div>
                <div class="pack-glow"></div>
              </div>
            </div>
            <div class="pack-back"></div>
            <div class="pack-side pack-left"></div>
            <div class="pack-side pack-right"></div>
            <div class="pack-side pack-top"></div>
            <div class="pack-side pack-bottom"></div>
          </div>
        </div>
        <p class="instruction">Toca el sobre para abrirlo</p>
      </div>

      <!-- Estado: Abriendo -->
      <div v-if="state === 'opening'" class="pack-opening-animation">
        <div class="pack-tearing">
          <div class="pack-half pack-half-left"></div>
          <div class="pack-half pack-half-right"></div>
          <div class="light-burst"></div>
        </div>
      </div>

      <!-- Estado: Revelando cartas -->
      <div v-if="state === 'revealing'" class="cards-reveal">
        <div class="cards-container">
          <div 
            v-for="(card, index) in cards" 
            :key="card.id"
            class="card-slot"
            :class="{ 'revealed': revealedCount > index }"
            :style="{ '--delay': `${index * 0.3}s` }"
          >
            <Card3D 
              :card="card" 
              :is-flipped="revealedCount <= index"
              :is-revealed="revealedCount > index"
              @click="openCardDetail(card)"
            />
          </div>
        </div>
        
        <button v-if="revealedCount < cards.length" class="reveal-btn" @click="revealNext">
          Revelar siguiente ({{ cards.length - revealedCount }} restantes)
        </button>
        
        <button v-else class="continue-btn" @click="finish">
          ¡Añadir a mi colección!
        </button>
      </div>

      <!-- Botón cerrar -->
      <button v-if="state !== 'closed'" class="close-btn" @click="close">✕</button>
    </div>
    
    <!-- Modal de detalle de carta -->
    <CardDetailModal 
      :is-open="showCardDetail"
      :card="selectedCard"
      @close="closeCardDetail"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Card3D from './Card3D.vue'
import CardDetailModal from './CardDetailModal.vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  cards: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['close', 'complete'])

const state = ref('closed') // closed, opening, revealing
const revealedCount = ref(0)
const packRef = ref(null)
const packRotateX = ref(0)
const packRotateY = ref(0)

// Card detail modal
const showCardDetail = ref(false)
const selectedCard = ref({})

const packStyle = computed(() => ({
  transform: `rotateX(${packRotateX.value}deg) rotateY(${packRotateY.value}deg)`
}))

function handlePackMove(e) {
  if (!packRef.value) return
  const rect = packRef.value.getBoundingClientRect()
  const x = e.clientX - rect.left
  const y = e.clientY - rect.top
  const centerX = rect.width / 2
  const centerY = rect.height / 2
  
  packRotateY.value = ((x - centerX) / centerX) * 20
  packRotateX.value = -((y - centerY) / centerY) * 20
}

function handlePackLeave() {
  packRotateX.value = 0
  packRotateY.value = 0
}

function startOpening() {
  state.value = 'opening'
  
  setTimeout(() => {
    state.value = 'revealing'
  }, 1500)
}

function revealNext() {
  if (revealedCount.value < props.cards.length) {
    revealedCount.value++
  }
}

function finish() {
  emit('complete', props.cards)
  close()
}

function close() {
  state.value = 'closed'
  revealedCount.value = 0
  emit('close')
}

function getBgParticleStyle(index) {
  return {
    '--x': `${Math.random() * 100}%`,
    '--y': `${Math.random() * 100}%`,
    '--duration': `${3 + Math.random() * 4}s`,
    '--delay': `${Math.random() * 3}s`,
    '--size': `${2 + Math.random() * 4}px`
  }
}

function openCardDetail(card) {
  selectedCard.value = card
  showCardDetail.value = true
}

function closeCardDetail() {
  showCardDetail.value = false
}
</script>

<style scoped>
.pack-opening-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}

.pack-opening-overlay.active {
  opacity: 1;
  pointer-events: all;
}

.pack-opening-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Efectos de fondo */
.background-effects {
  position: absolute;
  inset: 0;
  overflow: hidden;
  pointer-events: none;
}

.light-rays {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 200%;
  height: 200%;
  transform: translate(-50%, -50%);
  background: conic-gradient(
    from 0deg,
    transparent 0deg,
    rgba(255, 200, 100, 0.03) 10deg,
    transparent 20deg,
    rgba(255, 200, 100, 0.03) 30deg,
    transparent 40deg,
    rgba(255, 200, 100, 0.03) 50deg,
    transparent 60deg
  );
  animation: rotate-rays 30s linear infinite;
}

@keyframes rotate-rays {
  from { transform: translate(-50%, -50%) rotate(0deg); }
  to { transform: translate(-50%, -50%) rotate(360deg); }
}

.particles-container {
  position: absolute;
  inset: 0;
}

.bg-particle {
  position: absolute;
  left: var(--x);
  top: var(--y);
  width: var(--size);
  height: var(--size);
  background: rgba(255, 200, 100, 0.6);
  border-radius: 50%;
  animation: float-bg var(--duration) ease-in-out infinite;
  animation-delay: var(--delay);
}

@keyframes float-bg {
  0%, 100% {
    transform: translateY(0) scale(0);
    opacity: 0;
  }
  50% {
    transform: translateY(-100px) scale(1);
    opacity: 0.8;
  }
}

/* Sobre cerrado - 3D */
.pack-closed {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.pack-3d {
  width: 220px;
  height: 320px;
  perspective: 1000px;
  cursor: pointer;
  transition: transform 0.1s ease-out;
}

.pack-wrapper {
  width: 100%;
  height: 100%;
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.5s;
}

.pack-3d:hover .pack-wrapper {
  transform: scale(1.05);
}

.pack-front, .pack-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  border-radius: 12px;
}

.pack-front {
  background: linear-gradient(145deg, #2c3e50 0%, #1a252f 100%);
  border: 3px solid #f39c12;
  box-shadow: 
    0 0 30px rgba(243, 156, 18, 0.3),
    inset 0 0 60px rgba(0, 0, 0, 0.5);
  transform: translateZ(10px);
}

.pack-back {
  background: linear-gradient(145deg, #1a252f 0%, #0d1318 100%);
  transform: translateZ(-10px) rotateY(180deg);
}

.pack-side {
  position: absolute;
  background: linear-gradient(145deg, #243342 0%, #1a252f 100%);
}

.pack-left, .pack-right {
  width: 20px;
  height: 100%;
  top: 0;
}

.pack-left {
  left: 0;
  transform: rotateY(-90deg) translateZ(10px);
}

.pack-right {
  right: 0;
  transform: rotateY(90deg) translateZ(10px);
}

.pack-top, .pack-bottom {
  width: 100%;
  height: 20px;
  left: 0;
}

.pack-top {
  top: 0;
  transform: rotateX(90deg) translateZ(10px);
}

.pack-bottom {
  bottom: 0;
  transform: rotateX(-90deg) translateZ(10px);
}

.pack-design {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.pack-logo {
  font-size: 70px;
  margin-bottom: 20px;
  filter: drop-shadow(0 0 20px rgba(243, 156, 18, 0.8));
  animation: pack-pulse 2s ease-in-out infinite;
}

@keyframes pack-pulse {
  0%, 100% { transform: scale(1); filter: drop-shadow(0 0 20px rgba(243, 156, 18, 0.8)); }
  50% { transform: scale(1.1); filter: drop-shadow(0 0 30px rgba(243, 156, 18, 1)); }
}

.pack-title {
  font-size: 22px;
  font-weight: 800;
  color: #f39c12;
  text-align: center;
  letter-spacing: 2px;
  text-shadow: 0 0 10px rgba(243, 156, 18, 0.5);
}

.pack-subtitle {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
  letter-spacing: 3px;
  margin-top: 8px;
}

.pack-glow {
  position: absolute;
  inset: -50%;
  background: radial-gradient(circle, rgba(243, 156, 18, 0.15) 0%, transparent 70%);
  animation: glow-pulse 3s ease-in-out infinite;
}

@keyframes glow-pulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

.instruction {
  color: rgba(255, 255, 255, 0.7);
  font-size: 16px;
  animation: fade-pulse 2s ease-in-out infinite;
}

@keyframes fade-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

/* Animación de apertura */
.pack-opening-animation {
  position: relative;
  width: 300px;
  height: 400px;
}

.pack-tearing {
  position: relative;
  width: 100%;
  height: 100%;
}

.pack-half {
  position: absolute;
  width: 50%;
  height: 100%;
  background: linear-gradient(145deg, #2c3e50 0%, #1a252f 100%);
  border: 3px solid #f39c12;
}

.pack-half-left {
  left: 0;
  border-radius: 12px 0 0 12px;
  border-right: none;
  animation: tear-left 1.5s ease-out forwards;
  transform-origin: left center;
}

.pack-half-right {
  right: 0;
  border-radius: 0 12px 12px 0;
  border-left: none;
  animation: tear-right 1.5s ease-out forwards;
  transform-origin: right center;
}

@keyframes tear-left {
  0% { transform: translateX(0) rotateY(0); }
  30% { transform: translateX(0) rotateY(0); }
  100% { transform: translateX(-200px) rotateY(-60deg); opacity: 0; }
}

@keyframes tear-right {
  0% { transform: translateX(0) rotateY(0); }
  30% { transform: translateX(0) rotateY(0); }
  100% { transform: translateX(200px) rotateY(60deg); opacity: 0; }
}

.light-burst {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 10px;
  height: 10px;
  background: #fff;
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: burst 1.5s ease-out forwards;
}

@keyframes burst {
  0% { 
    transform: translate(-50%, -50%) scale(1);
    opacity: 0;
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0);
  }
  30% {
    opacity: 0;
  }
  50% { 
    transform: translate(-50%, -50%) scale(1);
    opacity: 1;
    box-shadow: 0 0 20px 10px rgba(255, 255, 255, 0.8);
  }
  100% { 
    transform: translate(-50%, -50%) scale(100);
    opacity: 0;
    box-shadow: 0 0 100px 50px rgba(255, 255, 255, 0);
  }
}

/* Revelación de cartas */
.cards-reveal {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 30px;
}

.cards-container {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 920px;
}

.card-slot {
  opacity: 0;
  transform: translateY(50px);
  transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transition-delay: var(--delay);
}

.card-slot.revealed {
  opacity: 1;
  transform: translateY(0);
}

.reveal-btn, .continue-btn {
  padding: 16px 40px;
  font-size: 18px;
  font-weight: 700;
  border: none;
  border-radius: 30px;
  cursor: pointer;
  transition: all 0.3s;
}

.reveal-btn {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  box-shadow: 0 5px 20px rgba(52, 152, 219, 0.4);
}

.reveal-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 30px rgba(52, 152, 219, 0.6);
}

.continue-btn {
  background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
  color: white;
  box-shadow: 0 5px 20px rgba(46, 204, 113, 0.4);
}

.continue-btn:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 30px rgba(46, 204, 113, 0.6);
}

/* Botón cerrar */
.close-btn {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.5);
}
</style>
