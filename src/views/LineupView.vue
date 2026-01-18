<template>
  <div class="lineup-view">
    <div class="lineup-header">
      <h1>Mi Alineación</h1>
      <p>Selecciona 5 cartas para la próxima jornada</p>
    </div>

    <!-- Grid de alineación -->
    <div class="lineup-grid">
      <div 
        v-for="position in lineupPositions" 
        :key="position.key"
        class="lineup-slot"
      >
        <div v-if="userLineup[position.key] && userLineup[position.key].nombre" class="slot-filled" @click="openDetailModal(userLineup[position.key])">
          <Card3D 
            :card="userLineup[position.key]" 
            :isFlipped="false" 
            :isRevealed="true"
          />
          <button class="remove-btn" @click.stop="handleRemove(position.key)">✕</button>
        </div>
        
        <div v-else class="slot-empty" @click="openModal(position.key, position.name)">
          <span class="slot-icon">{{ getPositionIcon(position.name) }}</span>
          <span class="slot-name">{{ position.name }}</span>
          <span class="add-icon">+</span>
        </div>
      </div>
    </div>

    <!-- Botón guardar -->
    <div class="save-section">
      <button class="save-btn" @click="saveLineup" :disabled="isSaving">
        {{ isSaving ? '⏳ Guardando...' : '💾 Guardar Alineación' }}
      </button>
    </div>

    <!-- Mensaje -->
    <div v-if="message" class="message" :class="message.type">
      {{ message.text }}
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal" @click.self="closeModal">
      <div class="modal-content">
        <h2>Selecciona {{ selectedPositionName }}</h2>
        
        <div v-if="availableCards.length > 0" class="cards-list">
          <div 
            v-for="card in availableCards" 
            :key="card.id"
            class="card-item"
            @click="addCard(card)"
          >
            <span class="card-pos">{{ card.posicion }}</span>
            <div class="card-info">
              <span class="card-name">{{ card.nombre }}</span>
              <span class="card-team">{{ card.equipo }}</span>
            </div>
          </div>
        </div>
        
        <div v-else class="no-cards">
          No tienes jugadores para esta posición
        </div>
        
        <button class="close-btn" @click="closeModal">Cerrar</button>
      </div>
    </div>

    <!-- Modal de detalle de carta -->
    <CardDetailModal 
      v-if="showDetailModal && selectedCard"
      :isOpen="true"
      :card="selectedCard"
      @close="closeDetailModal"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Card3D from '../components/Card3D.vue'
import CardDetailModal from '../components/CardDetailModal.vue'
import { useGameStore } from '../composables/useGameStore'
import * as api from '../services/api'

const { userCollection, userLineup, userLineupIds, addToLineup, removeFromLineup } = useGameStore()

// Mapeo de posiciones: nombre visible -> key interna
const lineupPositions = [
  { name: 'Base', key: 'base' },
  { name: 'Escolta', key: 'escolta' },
  { name: 'Alero', key: 'alero' },
  { name: 'Ala-Pívot', key: 'alaPivot' },
  { name: 'Pívot', key: 'pivot' }
]
const showModal = ref(false)
const selectedPositionKey = ref(null)
const selectedPositionName = ref('')
const isSaving = ref(false)
const message = ref(null)
const showDetailModal = ref(false)
const selectedCard = ref(null)

const availableCards = computed(() => {
  if (!selectedPositionName.value) return []
  
  // Asegurar que userLineup es un objeto
  const lineup = userLineup.value || {}
  const lineupNames = Object.values(lineup)
    .filter(c => c && c.nombre)
    .map(c => c.nombre)
  
  return userCollection.value.filter(card => 
    card.posicion === selectedPositionName.value && 
    !lineupNames.includes(card.nombre)
  )
})

function getPositionIcon(position) {
  const icons = {
    'Base': '🎯',
    'Escolta': '⚡',
    'Alero': '🔥',
    'Ala-Pívot': '💪',
    'Pívot': '🏔️'
  }
  return icons[position] || '🏀'
}

function openModal(positionKey, positionName) {
  selectedPositionKey.value = positionKey
  selectedPositionName.value = positionName
  showModal.value = true
}

function closeModal() {
  showModal.value = false
  selectedPositionKey.value = null
  selectedPositionName.value = ''
}

async function addCard(card) {
  const result = await addToLineup(card, selectedPositionKey.value)
  if (result.success !== false) {
    showMessage('✅ Jugador añadido', 'success')
    closeModal()
  } else {
    showMessage('❌ ' + result.error, 'error')
  }
}

async function handleRemove(positionKey) {
  const result = await removeFromLineup(positionKey)
  if (result.success !== false) {
    showMessage('✅ Jugador eliminado', 'success')
  }
}

async function saveLineup() {
  isSaving.value = true
  try {
    // Enviar objeto solo con posiciones ocupadas
    const idsToSave = {}
    for (const [pos, id] of Object.entries(userLineupIds.value)) {
      if (id && id !== "") {
        idsToSave[pos] = id
      }
    }
    await api.saveLineup(idsToSave)
    showMessage('✅ Alineación guardada', 'success')
  } catch (e) {
    showMessage('❌ Error al guardar', 'error')
  } finally {
    isSaving.value = false
  }
}

function showMessage(text, type) {
  message.value = { text, type }
  setTimeout(() => message.value = null, 3000)
}

function openDetailModal(card) {
  console.log('Abriendo modal de detalle para:', card.nombre)
  selectedCard.value = card
  showDetailModal.value = true
}

function closeDetailModal() {
  console.log('Cerrando modal de detalle')
  showDetailModal.value = false
  selectedCard.value = null
}
</script>

<style scoped>
.lineup-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.lineup-header {
  text-align: center;
  margin-bottom: 30px;
}

.lineup-header h1 {
  font-size: 32px;
  color: white;
  margin: 0 0 10px 0;
}

.lineup-header p {
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* Grid */
.lineup-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(200px, 250px));
  gap: 25px;
  margin-bottom: 40px;
  justify-content: center;
}

.lineup-slot {
  min-height: 350px;
}

.slot-filled {
  position: relative;
  height: 100%;
  cursor: pointer;
}

.slot-filled :deep(.card-container) {
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.remove-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 35px;
  height: 35px;
  background: rgba(231, 76, 60, 0.9);
  border: 2px solid white;
  border-radius: 50%;
  color: white;
  font-size: 18px;
  cursor: pointer;
  z-index: 100;
  transition: all 0.3s;
}

.remove-btn:hover {
  background: #e74c3c;
  transform: rotate(90deg) scale(1.1);
}

.slot-empty {
  height: 100%;
  min-height: 350px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 3px dashed rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.slot-empty:hover {
  border-color: rgba(243, 156, 18, 0.6);
  background: rgba(243, 156, 18, 0.05);
  transform: translateY(-5px);
}

.slot-icon {
  font-size: 48px;
}

.slot-name {
  font-size: 16px;
  font-weight: 700;
  color: white;
  text-transform: uppercase;
}

.add-icon {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  color: rgba(255, 255, 255, 0.4);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
}

/* Guardar */
.save-section {
  text-align: center;
  margin-bottom: 30px;
}

.save-btn {
  padding: 18px 50px;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 5px 20px rgba(46, 204, 113, 0.4);
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(46, 204, 113, 0.6);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Mensaje */
.message {
  padding: 15px 20px;
  border-radius: 12px;
  margin-bottom: 25px;
  font-weight: 600;
  text-align: center;
}

.message.success {
  background: rgba(46, 204, 113, 0.2);
  border: 2px solid rgba(46, 204, 113, 0.5);
  color: #2ecc71;
}

.message.error {
  background: rgba(231, 76, 60, 0.2);
  border: 2px solid rgba(231, 76, 60, 0.5);
  color: #e74c3c;
}

/* Modal */
.modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.95);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #1a1a2e;
  border-radius: 20px;
  padding: 30px;
  max-width: 600px;
  width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-content h2 {
  color: white;
  margin: 0 0 20px 0;
  text-align: center;
}

.cards-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 20px;
}

.card-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.card-item:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(243, 156, 18, 0.5);
  transform: translateX(5px);
}

.card-pos {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(243, 156, 18, 0.2);
  border: 2px solid rgba(243, 156, 18, 0.4);
  border-radius: 10px;
  color: #f39c12;
  font-weight: 800;
  font-size: 14px;
}

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.card-name {
  color: white;
  font-weight: 700;
  font-size: 16px;
}

.card-team {
  color: rgba(255, 255, 255, 0.5);
  font-size: 13px;
}

.no-cards {
  text-align: center;
  padding: 40px;
  color: rgba(255, 255, 255, 0.6);
}

.close-btn {
  width: 100%;
  padding: 15px;
  font-size: 16px;
  font-weight: 700;
  background: rgba(231, 76, 60, 0.2);
  border: 2px solid rgba(231, 76, 60, 0.4);
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.close-btn:hover {
  background: rgba(231, 76, 60, 0.3);
  transform: translateY(-2px);
}

/* Responsive */
@media (max-width: 1400px) {
  .lineup-grid {
    grid-template-columns: repeat(5, minmax(180px, 220px));
    gap: 20px;
  }
}

@media (max-width: 1100px) {
  .lineup-grid {
    grid-template-columns: repeat(3, minmax(180px, 220px));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .lineup-grid {
    grid-template-columns: repeat(2, minmax(160px, 200px));
    gap: 15px;
  }
  
  .slot-empty {
    min-height: 280px;
  }
}

@media (max-width: 480px) {
  .lineup-view {
    padding: 15px 10px;
  }

  .lineup-header h1 {
    font-size: 24px;
  }

  .lineup-header p {
    font-size: 13px;
  }

  .lineup-grid {
    grid-template-columns: repeat(2, minmax(140px, 1fr));
    gap: 10px;
  }
  
  .slot-empty {
    min-height: 220px;
  }
  
  .slot-icon {
    font-size: 36px;
  }
  
  .slot-name {
    font-size: 12px;
  }

  .add-icon {
    width: 40px;
    height: 40px;
    font-size: 24px;
  }

  .remove-btn {
    width: 30px;
    height: 30px;
    font-size: 16px;
    top: 8px;
    right: 8px;
  }

  .save-btn {
    padding: 14px 30px;
    font-size: 16px;
    width: 100%;
  }

  .modal-content {
    padding: 20px 15px;
  }

  .modal-content h2 {
    font-size: 20px;
  }

  .card-item {
    padding: 12px;
  }

  .card-pos {
    width: 44px;
    height: 44px;
    font-size: 13px;
  }

  .card-name {
    font-size: 14px;
  }

  .card-team {
    font-size: 12px;
  }
}

@media (max-width: 360px) {
  .lineup-grid {
    grid-template-columns: 1fr;
  }

  .slot-empty {
    min-height: 200px;
  }

  .lineup-header h1 {
    font-size: 22px;
  }
}
</style>
