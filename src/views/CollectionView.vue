<template>
  <div class="collection-view">
    <div class="collection-header">
      <h1>Mi Colección</h1>
      <div class="progress-info">
        <p class="progress-text">
          <span class="owned">{{ collectionProgress.owned }}</span> / {{ collectionProgress.total }} cartas
        </p>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: collectionProgress.percentage + '%' }"></div>
        </div>
        <p class="progress-percentage">{{ collectionProgress.percentage }}% completado</p>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filters">
      <button 
        v-for="filter in filters" 
        :key="filter.value"
        class="filter-btn"
        :class="{ active: activeFilter === filter.value, [filter.value]: true }"
        @click="activeFilter = filter.value"
      >
        {{ filter.label }}
        <span class="count">{{ getOwnedCount(filter.value) }}/{{ getCount(filter.value) }}</span>
      </button>
    </div>

    <!-- Grid de cartas -->
    <div v-if="filteredCards.length > 0" class="cards-grid">
      <div 
        v-for="card in filteredCards" 
        :key="card.id"
        class="card-wrapper"
        :class="{ locked: card.locked }"
        @click="card.owned && selectCard(card)"
      >
        <Card3D :card="card" :locked="card.locked" />
      </div>
    </div>

    <!-- Estado vacío -->
    <div v-else class="empty-state">
      <div class="empty-icon">📭</div>
      <h3>No tienes cartas{{ activeFilter !== 'all' ? ' de esta rareza' : '' }}</h3>
      <p>Canjea códigos en los partidos para obtener más cartas</p>
    </div>

    <!-- Modal de detalle de carta con stats -->
    <CardDetailModal 
      :is-open="!!selectedCard"
      :card="selectedCard || {}"
      @close="selectedCard = null"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import Card3D from '../components/Card3D.vue'
import CardDetailModal from '../components/CardDetailModal.vue'
import { useGameStore } from '../composables/useGameStore'
import { CARDS_CATALOG } from '../data/cards-catalog'

const { 
  userCollection, 
  userLineup, 
  lineupFull,
  addToLineup, 
  removeFromLineup 
} = useGameStore()

const activeFilter = ref('all')
const selectedCard = ref(null)

const filters = [
  { label: 'Todas', value: 'all' },
  { label: 'Legendarias', value: 'legendary' },
  { label: 'Épicas', value: 'epic' },
  { label: 'Raras', value: 'rare' },
  { label: 'Comunes', value: 'common' },
]

// Todas las cartas del catálogo con información de si el usuario las tiene
const allCardsWithStatus = computed(() => {
  return Object.values(CARDS_CATALOG).map(catalogCard => {
    const ownedCard = userCollection.value.find(c => c.id === catalogCard.id)
    return {
      ...catalogCard,
      owned: !!ownedCard,
      locked: !ownedCard
    }
  })
})

// Progreso de la colección
const collectionProgress = computed(() => {
  const total = Object.keys(CARDS_CATALOG).length
  const owned = userCollection.value.length
  const percentage = Math.round((owned / total) * 100)
  return { owned, total, percentage }
})

const filteredCards = computed(() => {
  let cards = allCardsWithStatus.value
  
  if (activeFilter.value !== 'all') {
    cards = cards.filter(card => card.rareza === activeFilter.value)
  }
  
  return cards
})

function getCount(filter) {
  if (filter === 'all') return allCardsWithStatus.value.length
  return allCardsWithStatus.value.filter(c => c.rareza === filter).length
}

function getOwnedCount(filter) {
  if (filter === 'all') return userCollection.value.length
  return userCollection.value.filter(c => c.rareza === filter).length
}

function selectCard(card) {
  selectedCard.value = card
}

function isInLineup(card) {
  return Object.values(userLineup.value).some(c => c && c.id === card.id)
}

function handleAddToLineup(card) {
  if (addToLineup(card)) {
    selectedCard.value = null
  }
}

function handleRemoveFromLineup(card) {
  removeFromLineup(card.id)
  selectedCard.value = null
}
</script>

<style scoped>
.collection-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.collection-header {
  text-align: center;
  margin-bottom: 30px;
}

.collection-header h1 {
  font-size: 28px;
  color: white;
  margin: 0 0 15px 0;
}

.progress-info {
  max-width: 400px;
  margin: 0 auto;
}

.progress-text {
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 10px 0;
  font-size: 16px;
}

.progress-text .owned {
  color: #f39c12;
  font-weight: 700;
  font-size: 18px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 8px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f39c12 0%, #e67e22 100%);
  border-radius: 10px;
  transition: width 0.5s ease;
  box-shadow: 0 0 10px rgba(243, 156, 18, 0.5);
}

.progress-percentage {
  color: rgba(255, 255, 255, 0.5);
  margin: 0;
  font-size: 13px;
}

.filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: center;
  margin-bottom: 30px;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid transparent;
  border-radius: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.filter-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.filter-btn.active {
  border-color: currentColor;
  background: rgba(255, 255, 255, 0.1);
}

.filter-btn.all.active { border-color: #fff; color: #fff; }
.filter-btn.legendary.active { border-color: #f1c40f; color: #f1c40f; }
.filter-btn.epic.active { border-color: #9b59b6; color: #9b59b6; }
.filter-btn.rare.active { border-color: #5dade2; color: #5dade2; }
.filter-btn.common.active { border-color: #888; color: #888; }

.count {
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  justify-items: center;
  align-items: start;
}

.card-wrapper {
  cursor: pointer;
  transition: transform 0.3s;
}

.card-wrapper:hover {
  transform: scale(1.02);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
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
  margin: 0;
}

/* Modal */
.card-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 25px;
}

.card-actions {
  display: flex;
  gap: 15px;
}

.action-btn {
  padding: 14px 30px;
  font-size: 16px;
  font-weight: 700;
  border: none;
  border-radius: 25px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn.add {
  background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
  color: white;
}

.action-btn.add:hover:not(:disabled) {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(46, 204, 113, 0.4);
}

.action-btn.add:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-btn.remove {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
}

.action-btn.remove:hover {
  transform: scale(1.05);
  box-shadow: 0 5px 20px rgba(231, 76, 60, 0.4);
}

.close-modal {
  position: absolute;
  top: -60px;
  right: -60px;
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  color: white;
  font-size: 24px;
  cursor: pointer;
  transition: all 0.3s;
}

.close-modal:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Responsive móvil */
@media (max-width: 768px) {
  .collection-view {
    padding: 15px;
  }

  .collection-header h1 {
    font-size: 24px;
  }

  .progress-info {
    max-width: 100%;
  }

  .cards-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 15px;
  }

  .filters {
    gap: 8px;
  }

  .filter-btn {
    padding: 8px 12px;
    font-size: 13px;
  }

  .count {
    font-size: 11px;
  }
}

@media (max-width: 480px) {
  .collection-view {
    padding: 10px;
  }

  .collection-header h1 {
    font-size: 22px;
  }

  .progress-text {
    font-size: 14px;
  }

  .progress-text .owned {
    font-size: 16px;
  }

  .cards-grid {
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 10px;
    justify-items: center;
  }

  .filters {
    gap: 6px;
  }

  .filter-btn {
    padding: 6px 8px;
    font-size: 11px;
    flex: 1 1 auto;
    min-width: 0;
    gap: 4px;
  }

  .count {
    padding: 2px 6px;
    font-size: 10px;
    white-space: nowrap;
  }
}

@media (max-width: 360px) {
  .collection-view {
    padding: 8px;
  }

  .collection-header h1 {
    font-size: 20px;
  }

  .filter-btn {
    font-size: 11px;
    padding: 6px 8px;
  }

  .cards-grid {
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 8px;
  }
}
</style>
