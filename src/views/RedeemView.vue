<template>
  <div class="redeem-view">
    <div class="redeem-header">
      <h1>Canjear Código</h1>
      <p>Introduce el código del partido para obtener tu sobre de cartas</p>
    </div>

    <div class="code-input-section">
      <div class="input-wrapper">
        <input 
          type="text" 
          v-model="code"
          placeholder="XXXXXX"
          maxlength="10"
          @keyup.enter="handleRedeem"
          :disabled="isLoading"
        />
        <span class="input-icon">🎟️</span>
      </div>
      
      <button 
        class="redeem-btn"
        @click="handleRedeem"
        :disabled="!code || isLoading"
      >
        <span v-if="!isLoading">Canjear código</span>
        <span v-else class="loading">Verificando...</span>
      </button>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </div>

    <div class="info-section">
      <h3>¿Dónde encuentro el código?</h3>
      <div class="info-cards">
        <div class="info-card">
          <span class="info-icon">📺</span>
          <span>Pabellón durante los partidos</span>
        </div>
        <div class="info-card">
          <span class="info-icon">📢</span>
          <span>Tus entrenadores</span>
        </div>

      </div>
    </div>

    <!-- Códigos de prueba para demo 
    <div class="demo-section">
      <p>Códigos de demostración disponibles:</p>
      <div class="demo-codes">
        <button 
          v-for="demoCode in demoCodes" 
          :key="demoCode"
          class="demo-code" 
          @click="useDemoCode(demoCode)"
          :disabled="isLoading"
        >
          {{ demoCode }}
        </button>
      </div>
    </div>
-->
    <!-- Modal de apertura de sobre -->
    <PackOpening 
      :is-open="showPackOpening"
      :cards="generatedCards"
      @close="closePack"
      @complete="handlePackComplete"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PackOpening from '../components/PackOpening.vue'
import { useGameStore } from '../composables/useGameStore'

const { redeemCode, addToCollection } = useGameStore()

const code = ref('')
const isLoading = ref(false)
const errorMessage = ref('')
const showPackOpening = ref(false)
const generatedCards = ref([])

// Códigos de demo
const demoCodes = ['DEMO2026', 'BASKET24', 'JORNADA15', 'LEGENDARIO']

async function handleRedeem() {
  if (!code.value) return
  
  errorMessage.value = ''
  isLoading.value = true
  
  try {
    const result = await redeemCode(code.value)
    
    if (result.success && result.new_cards?.length > 0) {
      // Mostrar animación de apertura
      generatedCards.value = result.new_cards
      showPackOpening.value = true
      code.value = ''
    } else {
      errorMessage.value = result.message || 'Error al canjear el código'
    }
  } catch (e) {
    errorMessage.value = e.message || 'Error de conexión'
  } finally {
    isLoading.value = false
  }
}

function useDemoCode(demoCode) {
  code.value = demoCode
  handleRedeem()
}

function closePack() {
  showPackOpening.value = false
  generatedCards.value = []
}

function handlePackComplete(cards) {
  // Las cartas ya se añadieron a la colección en el store cuando se canjeó el código
  // Solo cerramos el modal
  showPackOpening.value = false
  generatedCards.value = []
}
</script>

<style scoped>
.redeem-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 20px;
  max-width: 500px;
  margin: 0 auto;
}

.redeem-header {
  text-align: center;
  margin-bottom: 40px;
}

.redeem-header h1 {
  font-size: 28px;
  color: white;
  margin: 0 0 10px 0;
}

.redeem-header p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  margin: 0;
}

.code-input-section {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 40px;
}

.input-wrapper {
  position: relative;
}

.input-wrapper input {
  width: 100%;
  padding: 20px 20px 20px 60px;
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 4px;
  text-transform: uppercase;
  text-align: center;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  color: white;
  transition: all 0.3s;
}

.input-wrapper input:focus {
  outline: none;
  border-color: #f39c12;
  background: rgba(243, 156, 18, 0.1);
}

.input-wrapper input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.input-icon {
  position: absolute;
  left: 20px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 24px;
}

.redeem-btn {
  padding: 18px;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  border: none;
  border-radius: 16px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.redeem-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(243, 156, 18, 0.4);
}

.redeem-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.loading::after {
  content: '';
  width: 20px;
  height: 20px;
  border: 3px solid transparent;
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-message {
  color: #e74c3c;
  text-align: center;
  font-size: 14px;
  margin: 0;
  padding: 10px;
  background: rgba(231, 76, 60, 0.1);
  border-radius: 8px;
}

.info-section {
  margin-bottom: 40px;
}

.info-section h3 {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin: 0 0 15px 0;
  text-align: center;
}

.info-cards {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.info-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

.info-icon {
  font-size: 24px;
}

.demo-section {
  text-align: center;
  padding: 25px;
  background: rgba(46, 204, 113, 0.1);
  border: 1px dashed rgba(46, 204, 113, 0.3);
  border-radius: 16px;
}

.demo-section p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
  margin: 0 0 15px 0;
}

.demo-codes {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.demo-code {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 2px;
  background: rgba(46, 204, 113, 0.2);
  border: 1px solid #2ecc71;
  border-radius: 8px;
  color: #2ecc71;
  cursor: pointer;
  transition: all 0.3s;
}

.demo-code:hover:not(:disabled) {
  background: rgba(46, 204, 113, 0.3);
  transform: scale(1.05);
}

.demo-code:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
