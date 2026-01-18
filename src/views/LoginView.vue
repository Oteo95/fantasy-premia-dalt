<template>
  <div class="login-view">
    <div class="login-container">
      <!-- Logo y título -->
      <div class="login-header">
        <div class="logo-large">🏀</div>
        <h1>Fantasy Basket</h1>
        <p>Inicia sesión para acceder a tu colección</p>
      </div>

      <!-- Formulario de login -->
      <form class="login-form" @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Usuario</label>
          <input 
            type="text" 
            id="username"
            v-model="username"
            placeholder="Tu nombre de usuario"
            :disabled="isLoading"
            autocomplete="username"
          />
        </div>

        <div class="input-group">
          <label for="password">Contraseña</label>
          <input 
            type="password" 
            id="password"
            v-model="password"
            placeholder="Tu contraseña"
            :disabled="isLoading"
            autocomplete="current-password"
          />
        </div>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>

        <button type="submit" class="login-btn" :disabled="isLoading || !username || !password">
          <span v-if="!isLoading">Entrar</span>
          <span v-else class="loading-text">
            <span class="spinner"></span>
            Iniciando sesión...
          </span>
        </button>
      </form>

      <!-- Credenciales de demo -->
      <div class="demo-credentials">
        <p>¿Quieres probar? Usa estas credenciales:</p>
        <div class="credentials-box">
          <div class="credential">
            <span class="label">Usuario:</span>
            <span class="value">demo</span>
          </div>
          <div class="credential">
            <span class="label">Contraseña:</span>
            <span class="value">demo123</span>
          </div>
        </div>
        <button class="demo-btn" @click="fillDemo" :disabled="isLoading">
          Usar credenciales de demo
        </button>
      </div>

      <!-- Aviso backend -->
      <div class="backend-notice">
        <p>⚠️ Asegúrate de que el backend está corriendo:</p>
        <code>cd backend && uvicorn main:app --reload</code>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGameStore } from '../composables/useGameStore'

const emit = defineEmits(['login-success'])

const { login, isLoading } = useGameStore()

const username = ref('')
const password = ref('')
const errorMessage = ref('')

async function handleLogin() {
  errorMessage.value = ''
  
  const result = await login(username.value, password.value)
  
  if (result.success) {
    emit('login-success')
  } else {
    errorMessage.value = result.error || 'Error al iniciar sesión'
  }
}

function fillDemo() {
  username.value = 'demo'
  password.value = 'demo123'
}
</script>

<style scoped>
.login-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.logo-large {
  font-size: 80px;
  margin-bottom: 15px;
  filter: drop-shadow(0 0 30px rgba(243, 156, 18, 0.5));
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.login-header h1 {
  font-size: 32px;
  margin: 0;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.login-header p {
  color: rgba(255, 255, 255, 0.6);
  margin: 10px 0 0 0;
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 30px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.8);
}

.input-group input {
  padding: 16px;
  font-size: 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  color: white;
  transition: all 0.3s;
}

.input-group input:focus {
  outline: none;
  border-color: #f39c12;
  background: rgba(243, 156, 18, 0.1);
}

.input-group input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
  margin: 0;
  padding: 12px;
  background: rgba(231, 76, 60, 0.1);
  border-radius: 8px;
}

.login-btn {
  padding: 18px;
  font-size: 18px;
  font-weight: 700;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  border: none;
  border-radius: 12px;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(243, 156, 18, 0.4);
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-text {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.spinner {
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

.demo-credentials {
  background: rgba(46, 204, 113, 0.1);
  border: 1px solid rgba(46, 204, 113, 0.2);
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  margin-bottom: 20px;
}

.demo-credentials > p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 13px;
  margin: 0 0 15px 0;
}

.credentials-box {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 15px;
}

.credential {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.credential .label {
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
  text-transform: uppercase;
  letter-spacing: 1px;
}

.credential .value {
  font-size: 18px;
  font-weight: 700;
  color: #2ecc71;
  font-family: monospace;
}

.demo-btn {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  background: rgba(46, 204, 113, 0.2);
  border: 1px solid #2ecc71;
  border-radius: 8px;
  color: #2ecc71;
  cursor: pointer;
  transition: all 0.3s;
}

.demo-btn:hover:not(:disabled) {
  background: rgba(46, 204, 113, 0.3);
}

.demo-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.backend-notice {
  text-align: center;
  padding: 15px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px dashed rgba(255, 255, 255, 0.1);
}

.backend-notice p {
  color: rgba(255, 255, 255, 0.5);
  font-size: 12px;
  margin: 0 0 10px 0;
}

.backend-notice code {
  display: block;
  padding: 10px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  color: #3498db;
  font-size: 12px;
}
</style>
