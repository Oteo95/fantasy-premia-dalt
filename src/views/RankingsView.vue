<template>
  <div class="rankings-view">
    <div class="rankings-header">
      <h1>Rankings</h1>
      <p>Clasificación de la comunidad</p>
    </div>

    <!-- Tabs de rankings -->
    <div class="ranking-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.value"
        class="tab-btn"
        :class="{ active: activeTab === tab.value }"
        @click="changeTab(tab.value)"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="isLoadingRankings" class="loading-state">
      <div class="spinner"></div>
      <p>Cargando rankings...</p>
    </div>

    <template v-else>
      <!-- Podio Top 3 -->
      <div v-if="rankings.length >= 3" class="podium">
        <div class="podium-item second">
          <div class="podium-avatar">🥈</div>
          <div class="podium-name">{{ rankings[1]?.username }}</div>
          <div class="podium-points">{{ rankings[1]?.points }} pts</div>
          <div class="podium-stand">2</div>
        </div>
        <div class="podium-item first">
          <div class="podium-crown">👑</div>
          <div class="podium-avatar">🥇</div>
          <div class="podium-name">{{ rankings[0]?.username }}</div>
          <div class="podium-points">{{ rankings[0]?.points }} pts</div>
          <div class="podium-stand">1</div>
        </div>
        <div class="podium-item third">
          <div class="podium-avatar">🥉</div>
          <div class="podium-name">{{ rankings[2]?.username }}</div>
          <div class="podium-points">{{ rankings[2]?.points }} pts</div>
          <div class="podium-stand">3</div>
        </div>
      </div>

      <!-- Tu posición -->
      <div class="your-position">
        <div class="position-badge">Tu posición</div>
        <div class="position-content">
          <span class="position-rank">#{{ userRank }}</span>
          <span class="position-name">{{ userName }}</span>
          <span class="position-points">{{ userPoints }} pts</span>
        </div>
      </div>

      <!-- Lista de ranking -->
      <div class="ranking-list">
        <div 
          v-for="(player, index) in rankings.slice(3)" 
          :key="player.rank"
          class="ranking-item"
          :class="{ highlight: player.rank === userRank }"
        >
          <span class="rank">{{ player.rank }}</span>
          <span class="name">{{ player.username }}</span>
          <span class="points">{{ player.points }} pts</span>
          <span class="trend" :class="getTrendClass(index)">
            {{ getTrendIcon(index) }}
          </span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useGameStore } from '../composables/useGameStore'

const { rankings, userName, userPoints, userRank, loadRankings } = useGameStore()

const activeTab = ref('monthly')
const isLoadingRankings = ref(false)

const tabs = [
  { label: 'Jornada', value: 'weekly' },
  { label: 'Mensual', value: 'monthly' },
  { label: 'Temporada', value: 'season' },
]

onMounted(() => {
  fetchRankings()
})

async function fetchRankings() {
  isLoadingRankings.value = true
  await loadRankings(activeTab.value)
  isLoadingRankings.value = false
}

async function changeTab(tab) {
  activeTab.value = tab
  await fetchRankings()
}

function getTrendClass(index) {
  const trends = ['up', 'down', 'same', 'up', 'down', 'up', 'same']
  return trends[index % trends.length]
}

function getTrendIcon(index) {
  const trends = ['↑', '↓', '―', '↑', '↓', '↑', '―']
  return trends[index % trends.length]
}
</script>

<style scoped>
.rankings-view {
  padding: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.rankings-header {
  text-align: center;
  margin-bottom: 20px;
}

.rankings-header h1 {
  font-size: 28px;
  color: white;
  margin: 0;
}

.rankings-header p {
  color: rgba(255, 255, 255, 0.6);
  margin: 5px 0 0 0;
}

.ranking-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  background: rgba(255, 255, 255, 0.05);
  padding: 5px;
  border-radius: 12px;
}

.tab-btn {
  flex: 1;
  padding: 12px;
  font-size: 14px;
  font-weight: 600;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn.active {
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  color: white;
}

/* Loading */
.loading-state {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top-color: #f39c12;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state p {
  color: rgba(255, 255, 255, 0.6);
}

/* Podio */
.podium {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
  padding: 20px 0;
}

.podium-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.podium-item.first {
  order: 2;
}

.podium-item.second {
  order: 1;
}

.podium-item.third {
  order: 3;
}

.podium-crown {
  font-size: 24px;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}

.podium-avatar {
  font-size: 40px;
}

.podium-name {
  font-size: 12px;
  color: white;
  font-weight: 600;
  max-width: 80px;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.podium-points {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.6);
}

.podium-stand {
  width: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 800;
  color: white;
  border-radius: 8px 8px 0 0;
}

.podium-item.first .podium-stand {
  height: 80px;
  background: linear-gradient(180deg, #f1c40f 0%, #d4ac0d 100%);
}

.podium-item.second .podium-stand {
  height: 60px;
  background: linear-gradient(180deg, #bdc3c7 0%, #95a5a6 100%);
}

.podium-item.third .podium-stand {
  height: 45px;
  background: linear-gradient(180deg, #e67e22 0%, #d35400 100%);
}

/* Tu posición */
.your-position {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.2) 0%, rgba(39, 174, 96, 0.2) 100%);
  border: 1px solid rgba(46, 204, 113, 0.3);
  border-radius: 12px;
  padding: 15px;
  margin-bottom: 20px;
}

.position-badge {
  font-size: 10px;
  color: #2ecc71;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 10px;
}

.position-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.position-rank {
  font-size: 24px;
  font-weight: 800;
  color: white;
}

.position-name {
  flex: 1;
  font-size: 16px;
  font-weight: 600;
  color: white;
}

.position-points {
  font-size: 16px;
  font-weight: 700;
  color: #2ecc71;
}

/* Lista de ranking */
.ranking-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.ranking-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  transition: all 0.3s;
}

.ranking-item:hover {
  background: rgba(255, 255, 255, 0.06);
}

.ranking-item.highlight {
  background: rgba(243, 156, 18, 0.1);
  border: 1px solid rgba(243, 156, 18, 0.3);
}

.rank {
  width: 30px;
  font-size: 14px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.5);
}

.name {
  flex: 1;
  font-size: 14px;
  color: white;
}

.points {
  font-size: 14px;
  font-weight: 700;
  color: #f39c12;
}

.trend {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  border-radius: 50%;
}

.trend.up {
  color: #2ecc71;
  background: rgba(46, 204, 113, 0.1);
}

.trend.down {
  color: #e74c3c;
  background: rgba(231, 76, 60, 0.1);
}

.trend.same {
  color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.05);
}
</style>
