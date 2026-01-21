<template>
  <div class="stats-view">
    <div class="stats-header">
      <h1>📊 Estadísticas de Jugadores</h1>
      <p>Visualiza el rendimiento de los jugadores del equipo</p>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading">
      <div class="spinner">⏳</div>
      <p>Cargando estadísticas...</p>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="error-message">
      <span>❌ {{ error }}</span>
    </div>

    <!-- Contenido -->
    <div v-else class="stats-content">
      <!-- Filtro por equipo -->
      <div class="filters">
        <div class="filter-group">
          <label for="team-filter">🏀 Filtrar por equipo:</label>
          <select id="team-filter" v-model="selectedTeam" class="team-select">
            <option value="">Todos los equipos</option>
            <option v-for="team in availableTeams" :key="team" :value="team">
              {{ team }}
            </option>
          </select>
        </div>
      </div>

      <!-- Selector de jugador -->
      <div class="player-selector">
        <h2>Selecciona un jugador ({{ filteredPlayers.length }})</h2>
        <div class="players-grid">
          <button
            v-for="player in filteredPlayers"
            :key="player.playerId"
            class="player-card"
            :class="{ active: selectedPlayer?.playerId === player.playerId }"
            @click="selectPlayer(player)"
          >
            <div class="player-number">{{ player.numero }}</div>
            <div class="player-info">
              <div class="player-name">{{ player.nombre }}</div>
              <div class="player-position">{{ player.posicion }}</div>
            </div>
            <div class="player-stats-preview">
              <div class="stat-mini">
                <span class="stat-label">PTS</span>
                <span class="stat-value">{{ player.promedios?.puntos?.toFixed(1) || 0 }}</span>
              </div>
              <div class="stat-mini">
                <span class="stat-label">VAL</span>
                <span class="stat-value">{{ player.promedios?.valoracion?.toFixed(1) || 0 }}</span>
              </div>
            </div>
          </button>
        </div>
      </div>

      <!-- Detalles del jugador seleccionado -->
      <div v-if="selectedPlayer" class="player-details">
        <!-- Header del jugador -->
        <div class="player-header">
          <div class="player-title">
            <h2>{{ selectedPlayer.nombre }}</h2>
            <div class="player-meta">
              <span class="badge">{{ selectedPlayer.posicion }}</span>
              <span class="badge">Nº {{ selectedPlayer.numero }}</span>
              <span class="badge">{{ selectedPlayer.equipo }}</span>
            </div>
          </div>
          <div class="player-season-stats">
            <div class="season-stat">
              <div class="season-stat-label">Partidos</div>
              <div class="season-stat-value">{{ selectedPlayer.statsTemporada?.partidosJugados || 0 }}</div>
            </div>
            <div class="season-stat highlight">
              <div class="season-stat-label">Puntos Fantasy</div>
              <div class="season-stat-value">{{ selectedPlayer.statsTemporada?.puntosFantasy?.toFixed(1) || 0 }}</div>
            </div>
          </div>
        </div>

        <!-- Gráficos -->
        <div class="charts-container">
          <!-- Promedios (Radar Chart) -->
          <div class="chart-card">
            <h3>⚡ Promedios por Partido</h3>
            <div class="chart-wrapper">
              <Radar :data="radarChartData" :options="radarChartOptions" />
            </div>
          </div>

          <!-- Gráfica General de Estadísticas (Line Chart) -->
          <div class="chart-card">
            <h3>🔗 Comparativa General de Stats</h3>
            <div class="chart-wrapper">
              <Line :data="generalStatsChartData" :options="generalStatsChartOptions" />
            </div>
          </div>

          <!-- Evolución por jornada (Line Chart) -->
          <div class="chart-card">
            <h3>📈 Evolución de Puntos Fantasy</h3>
            <div class="chart-wrapper">
              <Line :data="lineChartData" :options="lineChartOptions" />
            </div>
          </div>

          <!-- Distribución de estadísticas (Bar Chart) -->
          <div class="chart-card full-width">
            <h3>🎯 Estadísticas Totales de Temporada</h3>
            <div class="chart-wrapper">
              <Bar :data="barChartData" :options="barChartOptions" />
            </div>
          </div>
        </div>

        <!-- Mejor partido -->
        <div v-if="selectedPlayer.mejorPartido" class="best-game">
          <h3>🌟 Mejor Partido</h3>
          <div class="best-game-content">
            <div class="best-game-info">
              <span class="best-game-jornada">Jornada {{ selectedPlayer.mejorPartido.jornada }}</span>
              <span class="best-game-date">{{ formatDate(selectedPlayer.mejorPartido.fecha) }}</span>
            </div>
            <div class="best-game-stats">
              <div class="best-stat">
                <span class="best-stat-label">Puntos</span>
                <span class="best-stat-value">{{ selectedPlayer.mejorPartido.puntos }}</span>
              </div>
              <div class="best-stat highlight">
                <span class="best-stat-label">Valoración</span>
                <span class="best-stat-value">{{ selectedPlayer.mejorPartido.valoracion }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Mensaje si no hay jugador seleccionado -->
      <div v-else class="no-selection">
        <span class="no-selection-icon">👆</span>
        <p>Selecciona un jugador para ver sus estadísticas detalladas</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { Line, Bar, Radar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import * as api from '../services/api'

// Registrar componentes de Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  RadialLinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
)

const players = ref([])
const selectedPlayer = ref(null)
const selectedTeam = ref('')
const loading = ref(true)
const error = ref(null)

// Computed: Equipos disponibles
const availableTeams = computed(() => {
  const teams = new Set()
  players.value.forEach(player => {
    if (player.equipo) {
      teams.add(player.equipo)
    }
  })
  return Array.from(teams).sort()
})

// Computed: Jugadores filtrados por equipo
const filteredPlayers = computed(() => {
  if (!selectedTeam.value) {
    return players.value
  }
  return players.value.filter(player => player.equipo === selectedTeam.value)
})

onMounted(async () => {
  await loadPlayers()
})

async function loadPlayers() {
  try {
    loading.value = true
    error.value = null
    const response = await api.getPlayers()
    players.value = response.players || []
    
    // Ordenar por puntos fantasy
    players.value.sort((a, b) => {
      const ptsA = a.statsTemporada?.puntosFantasy || 0
      const ptsB = b.statsTemporada?.puntosFantasy || 0
      return ptsB - ptsA
    })
  } catch (e) {
    error.value = e.message || 'Error al cargar los jugadores'
  } finally {
    loading.value = false
  }
}

function selectPlayer(player) {
  selectedPlayer.value = player
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('es-ES', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

// Datos para el gráfico de radar (promedios)
const radarChartData = computed(() => {
  if (!selectedPlayer.value) return null
  
  const promedios = selectedPlayer.value.promedios || {}
  
  return {
    labels: ['Puntos', 'Asistencias', 'Rebotes', 'Robos', 'Tapones'],
    datasets: [{
      label: 'Promedios',
      data: [
        promedios.puntos || 0,
        promedios.asistencias || 0,
        promedios.rebotes || 0,
        promedios.robos || 0,
        promedios.tapones || 0
      ],
      backgroundColor: 'rgba(243, 156, 18, 0.2)',
      borderColor: 'rgba(243, 156, 18, 1)',
      borderWidth: 2,
      pointBackgroundColor: 'rgba(243, 156, 18, 1)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgba(243, 156, 18, 1)'
    }]
  }
})

const radarChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      titleColor: '#f39c12',
      bodyColor: '#fff'
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      ticks: { color: 'rgba(255, 255, 255, 0.6)' },
      grid: { color: 'rgba(255, 255, 255, 0.1)' },
      pointLabels: { color: 'rgba(255, 255, 255, 0.8)', font: { size: 12 } }
    }
  }
}

// Datos para el gráfico de líneas (evolución puntos fantasy)
const lineChartData = computed(() => {
  if (!selectedPlayer.value) return null
  
  const jornadas = selectedPlayer.value.jornadasStats || []
  
  return {
    labels: jornadas.map(j => `J${j.jornada}`),
    datasets: [{
      label: 'Puntos Fantasy',
      data: jornadas.map(j => j.stats.puntosFantasy || 0),
      borderColor: '#3498db',
      backgroundColor: 'rgba(52, 152, 219, 0.1)',
      borderWidth: 3,
      fill: true,
      tension: 0.4,
      pointRadius: 5,
      pointHoverRadius: 7
    }]
  }
})

const lineChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      titleColor: '#3498db',
      bodyColor: '#fff'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { color: 'rgba(255, 255, 255, 0.6)' },
      grid: { color: 'rgba(255, 255, 255, 0.1)' }
    },
    x: {
      ticks: { color: 'rgba(255, 255, 255, 0.6)' },
      grid: { color: 'rgba(255, 255, 255, 0.05)' }
    }
  }
}

// Datos para gráfico de barras (stats totales)
const barChartData = computed(() => {
  if (!selectedPlayer.value) return null
  
  const stats = selectedPlayer.value.statsTemporada || {}
  
  return {
    labels: ['Puntos', 'Asistencias', 'Rebotes', 'Robos', 'Tapones'],
    datasets: [{
      label: 'Total Temporada',
      data: [
        stats.puntos || 0,
        stats.asistencias || 0,
        stats.rebotes || 0,
        stats.robos || 0,
        stats.tapones || 0
      ],
      backgroundColor: [
        'rgba(243, 156, 18, 0.8)',
        'rgba(52, 152, 219, 0.8)',
        'rgba(155, 89, 182, 0.8)',
        'rgba(46, 204, 113, 0.8)',
        'rgba(26, 188, 156, 0.8)'
      ],
      borderColor: [
        'rgba(243, 156, 18, 1)',
        'rgba(52, 152, 219, 1)',
        'rgba(155, 89, 182, 1)',
        'rgba(46, 204, 113, 1)',
        'rgba(26, 188, 156, 1)'
      ],
      borderWidth: 2
    }]
  }
})

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      padding: 12,
      titleColor: '#f39c12',
      bodyColor: '#fff'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { color: 'rgba(255, 255, 255, 0.6)' },
      grid: { color: 'rgba(255, 255, 255, 0.1)' }
    },
    x: {
      ticks: { color: 'rgba(255, 255, 255, 0.6)' },
      grid: { color: 'rgba(255, 255, 255, 0.05)' }
    }
  }
}

// Función para calcular percentil de un valor en un array
function calculatePercentile(value, values) {
  if (values.length === 0) return 50
  const sorted = [...values].sort((a, b) => a - b)
  const index = sorted.findIndex(v => v >= value)
  if (index === -1) return 100
  return Math.round((index / sorted.length) * 100)
}

// Datos para gráfica general de línea (PERCENTILES - todos los jugadores)
// POLÍGONO CERRADO: Empieza y termina SIEMPRE en percentil 50 (mediana) para todos
const generalStatsChartData = computed(() => {
  if (!selectedPlayer.value) return null
  
  // Solo estas estadísticas: Puntos, Asistencias, Rebotes, Robos, Tapones
  const statKeys = ['puntos', 'asistencias', 'rebotes', 'robos', 'tapones']
  const allValues = {}
  
  // Recopilar todos los valores de cada estadística
  statKeys.forEach(key => {
    allValues[key] = filteredPlayers.value.map(p => p.promedios?.[key] || 0)
  })
  
  const datasets = []
  
  // Crear un dataset para cada jugador filtrado con percentiles
  filteredPlayers.value.forEach(player => {
    const promedios = player.promedios || {}
    const isSelected = player.playerId === selectedPlayer.value.playerId
    
    // POLÍGONO CERRADO: Inicio en 50, stats, fin en 50
    const percentilesData = [
      50, // Punto inicial FIJO en percentil 50
      calculatePercentile(promedios.puntos || 0, allValues.puntos),
      calculatePercentile(promedios.asistencias || 0, allValues.asistencias),
      calculatePercentile(promedios.rebotes || 0, allValues.rebotes),
      calculatePercentile(promedios.robos || 0, allValues.robos),
      calculatePercentile(promedios.tapones || 0, allValues.tapones),
      50  // Punto final FIJO en percentil 50 (cierra el polígono)
    ]
    
    datasets.push({
      label: player.nombre,
      data: percentilesData,
      borderColor: isSelected ? '#9b59b6' : 'rgba(255, 255, 255, 0.15)',
      backgroundColor: isSelected ? 'rgba(155, 89, 182, 0.1)' : 'transparent',
      borderWidth: isSelected ? 4 : 1,
      fill: isSelected,
      tension: 0.4,
      pointRadius: isSelected ? 6 : 2,
      pointHoverRadius: isSelected ? 8 : 4,
      pointBackgroundColor: isSelected ? '#9b59b6' : 'rgba(255, 255, 255, 0.3)',
      pointBorderColor: isSelected ? '#fff' : 'transparent',
      pointBorderWidth: isSelected ? 2 : 0,
      order: isSelected ? 0 : 1
    })
  })
  
  return {
    labels: ['', 'Puntos', 'Asistencias', 'Rebotes', 'Robos', 'Tapones', ''],
    datasets
  }
})

const generalStatsChartOptions = {
  responsive: true,
  maintainAspectRatio: true,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(0, 0, 0, 0.9)',
      padding: 14,
      titleColor: '#9b59b6',
      bodyColor: '#fff',
      callbacks: {
        label: function(context) {
          return `${context.dataset.label}: Percentil ${context.parsed.y}`
        }
      }
    }
  },
  scales: {
    y: {
      min: 0,
      max: 100,
      ticks: { 
        color: 'rgba(255, 255, 255, 0.6)',
        callback: function(value) {
          return value + '%'
        }
      },
      grid: { 
        color: 'rgba(255, 255, 255, 0.1)',
        // Línea especial en percentil 50 (mediana)
        drawTicks: true
      },
      title: {
        display: true,
        text: 'Percentil (0-100)',
        color: 'rgba(255, 255, 255, 0.8)',
        font: { size: 14, weight: 'bold' }
      }
    },
    x: {
      ticks: { color: 'rgba(255, 255, 255, 0.6)' },
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
      title: {
        display: true,
        text: 'Estadísticas',
        color: 'rgba(255, 255, 255, 0.8)',
        font: { size: 14, weight: 'bold' }
      }
    }
  }
}
</script>

<style scoped>
.stats-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.stats-header {
  text-align: center;
  margin-bottom: 40px;
}

.stats-header h1 {
  font-size: 32px;
  color: white;
  margin: 0 0 10px 0;
}

.stats-header p {
  color: rgba(255, 255, 255, 0.6);
  margin: 0;
}

/* Loading y error */
.loading, .error-message {
  text-align: center;
  padding: 60px 20px;
}

.spinner {
  font-size: 48px;
  animation: pulse 1.5s ease-in-out infinite;
}

.error-message {
  color: #e74c3c;
  font-size: 18px;
}

/* Filtros */
.filters {
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.08), rgba(230, 126, 34, 0.04));
  border: 2px solid rgba(243, 156, 18, 0.2);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

.filter-group {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  max-width: 600px;
  margin: 0 auto;
}

.filter-group label {
  color: #f39c12;
  font-size: 17px;
  font-weight: 700;
  white-space: nowrap;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.team-select {
  flex: 1;
  max-width: 400px;
  padding: 14px 20px;
  background: rgba(26, 26, 46, 0.8);
  border: 2px solid rgba(243, 156, 18, 0.3);
  border-radius: 12px;
  color: white;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.team-select:hover {
  background: rgba(243, 156, 18, 0.15);
  border-color: rgba(243, 156, 18, 0.6);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 156, 18, 0.3);
}

.team-select:focus {
  outline: none;
  border-color: #f39c12;
  background: rgba(243, 156, 18, 0.2);
  box-shadow: 0 0 0 4px rgba(243, 156, 18, 0.15);
}

.team-select option {
  background: #1a1a2e;
  color: white;
  padding: 12px;
}

/* Selector de jugador */
.player-selector {
  margin-bottom: 40px;
}

.player-selector h2 {
  color: white;
  font-size: 20px;
  margin-bottom: 20px;
}

.players-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 15px;
}

.player-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
  color: white;
  text-align: left;
}

.player-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(243, 156, 18, 0.4);
  transform: translateY(-2px);
}

.player-card.active {
  background: rgba(243, 156, 18, 0.15);
  border-color: rgba(243, 156, 18, 0.6);
}

.player-number {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(243, 156, 18, 0.2);
  border: 2px solid rgba(243, 156, 18, 0.4);
  border-radius: 10px;
  font-weight: 800;
  font-size: 20px;
  color: #f39c12;
}

.player-info {
  flex: 1;
}

.player-name {
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 4px;
}

.player-position {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.player-stats-preview {
  display: flex;
  gap: 10px;
}

.stat-mini {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 5px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
}

.stat-label {
  font-size: 10px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
}

.stat-value {
  font-size: 14px;
  font-weight: 700;
  color: #f39c12;
}

/* Detalles del jugador */
.player-details {
  animation: fadeIn 0.5s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.player-header {
  background: linear-gradient(135deg, rgba(243, 156, 18, 0.1), rgba(230, 126, 34, 0.05));
  border: 2px solid rgba(243, 156, 18, 0.3);
  border-radius: 16px;
  padding: 25px;
  margin-bottom: 30px;
}

.player-title h2 {
  font-size: 28px;
  color: white;
  margin: 0 0 10px 0;
}

.player-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.badge {
  padding: 6px 12px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.player-season-stats {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}

.season-stat {
  flex: 1;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  text-align: center;
}

.season-stat.highlight {
  background: rgba(243, 156, 18, 0.15);
  border-color: rgba(243, 156, 18, 0.3);
}

.season-stat-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  text-transform: uppercase;
  margin-bottom: 8px;
}

.season-stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #f39c12;
}

/* Gráficos */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 25px;
  margin-bottom: 30px;
  justify-items: center;
}

.chart-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 25px;
  width: 100%;
  max-width: 700px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart-card.full-width {
  grid-column: 1 / -1;
  max-width: 100%;
}

.chart-card h3 {
  color: white;
  font-size: 18px;
  margin: 0 0 20px 0;
  text-align: center;
  width: 100%;
}

.chart-wrapper {
  position: relative;
  height: 300px;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Mejor partido */
.best-game {
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.1), rgba(39, 174, 96, 0.05));
  border: 2px solid rgba(46, 204, 113, 0.3);
  border-radius: 16px;
  padding: 25px;
}

.best-game h3 {
  color: white;
  font-size: 20px;
  margin: 0 0 15px 0;
}

.best-game-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
}

.best-game-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.best-game-jornada {
  font-size: 18px;
  font-weight: 700;
  color: #2ecc71;
}

.best-game-date {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.best-game-stats {
  display: flex;
  gap: 25px;
}

.best-stat {
  text-align: center;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
}

.best-stat.highlight {
  background: rgba(46, 204, 113, 0.15);
  border: 1px solid rgba(46, 204, 113, 0.3);
}

.best-stat-label {
  display: block;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 6px;
  text-transform: uppercase;
}

.best-stat-value {
  display: block;
  font-size: 24px;
  font-weight: 800;
  color: #2ecc71;
}

/* No selection */
.no-selection {
  text-align: center;
  padding: 80px 20px;
}

.no-selection-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 20px;
}

.no-selection p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 16px;
}

/* Responsive */
@media (max-width: 768px) {
  .stats-view {
    padding: 15px;
  }

  .stats-header {
    margin-bottom: 25px;
  }

  .stats-header h1 {
    font-size: 24px;
  }

  .filters {
    padding: 15px;
    margin-bottom: 20px;
  }

  .filter-group {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }

  .filter-group label {
    font-size: 14px;
  }

  .team-select {
    max-width: none;
    width: 100%;
  }

  .players-grid {
    grid-template-columns: 1fr;
  }

  .charts-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .chart-card.full-width {
    grid-column: 1;
  }

  .player-season-stats {
    flex-direction: column;
    gap: 15px;
  }

  .best-game-content {
    flex-direction: column;
    align-items: flex-start;
  }

  .best-game-stats {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .stats-view {
    padding: 12px;
  }

  .stats-header {
    margin-bottom: 20px;
  }

  .stats-header h1 {
    font-size: 20px;
  }

  .stats-header p {
    font-size: 13px;
  }

  .filters {
    padding: 12px;
  }

  .filter-group label {
    font-size: 13px;
  }

  .team-select {
    padding: 10px 12px;
    font-size: 14px;
  }

  .player-selector h2 {
    font-size: 18px;
  }

  .player-card {
    padding: 10px;
    gap: 10px;
  }

  .player-number {
    width: 42px;
    height: 42px;
    font-size: 16px;
  }

  .player-name {
    font-size: 13px;
  }

  .player-position {
    font-size: 11px;
  }

  .player-stats-preview {
    gap: 6px;
  }

  .stat-mini {
    padding: 4px 8px;
  }

  .player-header {
    padding: 16px;
    margin-bottom: 20px;
  }

  .player-title h2 {
    font-size: 20px;
  }

  .badge {
    padding: 4px 10px;
    font-size: 11px;
  }

  .season-stat {
    padding: 12px;
  }

  .season-stat-label {
    font-size: 11px;
  }

  .season-stat-value {
    font-size: 24px;
  }

  .charts-container {
    gap: 15px;
    margin-bottom: 20px;
  }

  .chart-card {
    padding: 16px;
  }

  .chart-card h3 {
    font-size: 16px;
    margin-bottom: 15px;
  }

  .chart-wrapper {
    height: 220px;
  }

  .best-game {
    padding: 16px;
  }

  .best-game h3 {
    font-size: 18px;
  }

  .best-game-jornada {
    font-size: 16px;
  }

  .best-game-date {
    font-size: 13px;
  }

  .best-game-stats {
    gap: 15px;
  }

  .best-stat {
    padding: 10px 16px;
  }

  .best-stat-label {
    font-size: 11px;
  }

  .best-stat-value {
    font-size: 20px;
  }

  .no-selection {
    padding: 60px 15px;
  }

  .no-selection-icon {
    font-size: 48px;
  }

  .no-selection p {
    font-size: 14px;
  }
}
</style>
