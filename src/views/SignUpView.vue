<template>
  <div class="auth-container">
    <button class="back-btn" @click="$emit('navigate', 'landing')">
      <span class="back-icon">←</span>
      <span>Volver</span>
    </button>

    <div class="auth-card">
      <div class="auth-header">
        <div class="auth-logo">
          <span class="logo-icon">🏀</span>
          <span class="logo-text">Fantasy Basket</span>
        </div>
        <h2 class="auth-title">Crear Cuenta</h2>
        <p class="auth-subtitle">Comienza tu aventura como manager</p>
      </div>

      <form class="auth-form" @submit.prevent="handleSignUp">
        <div class="form-group">
          <label class="form-label">
            <span class="label-icon">👤</span>
            <span>Usuario</span>
          </label>
          <input
            v-model="formData.username"
            type="text"
            class="form-input"
            placeholder="Tu nombre de usuario"
            required
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label class="form-label">
            <span class="label-icon">📧</span>
            <span>Email</span>
          </label>
          <input
            v-model="formData.email"
            type="email"
            class="form-input"
            placeholder="tu@email.com"
            required
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label class="form-label">
            <span class="label-icon">🔒</span>
            <span>Contraseña</span>
          </label>
          <input
            v-model="formData.password"
            type="password"
            class="form-input"
            placeholder="Mínimo 6 caracteres"
            required
            minlength="6"
            :disabled="isLoading"
          />
        </div>

        <div class="form-group">
          <label class="form-label">
            <span class="label-icon">🔒</span>
            <span>Confirmar Contraseña</span>
          </label>
          <input
            v-model="formData.confirmPassword"
            type="password"
            class="form-input"
            placeholder="Repite tu contraseña"
            required
            :disabled="isLoading"
          />
        </div>

        <div v-if="error" class="error-message">
          <span class="error-icon">⚠️</span>
          <span>{{ error }}</span>
        </div>

        <button type="submit" class="submit-btn" :disabled="isLoading">
          <span v-if="!isLoading" class="btn-content">
            <span class="btn-icon">🚀</span>
            <span>Crear Cuenta</span>
          </span>
          <span v-else class="btn-loading">
            <span class="loading-spinner"></span>
            <span>Creando cuenta...</span>
          </span>
        </button>

        <div class="form-footer">
          <p class="footer-text">
            ¿Ya tienes cuenta?
            <button type="button" class="link-btn" @click="$emit('navigate', 'signin')">
              Iniciar Sesión
            </button>
          </p>
        </div>
      </form>

      <div class="welcome-bonus">
        <div class="bonus-icon">🎁</div>
        <div class="bonus-text">
          <strong>Bono de Bienvenida:</strong> 5 cartas gratis al registrarte
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useGameStore } from '../composables/useGameStore'

const emit = defineEmits(['navigate', 'signup-success'])

const { signup, isLoading } = useGameStore()

const formData = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const error = ref('')

async function handleSignUp() {
  error.value = ''
  
  // Validaciones
  if (formData.value.username.length < 3) {
    error.value = 'El usuario debe tener al menos 3 caracteres'
    return
  }
  
  if (formData.value.password.length < 6) {
    error.value = 'La contraseña debe tener al menos 6 caracteres'
    return
  }
  
  if (formData.value.password !== formData.value.confirmPassword) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  
  const result = await signup(
    formData.value.username,
    formData.value.email,
    formData.value.password
  )
  
  if (result.success) {
    emit('signup-success')
  } else {
    error.value = result.error || 'Error al crear la cuenta'
  }
}
</script>

<style scoped>
.auth-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
}

.back-btn {
  position: absolute;
  top: 20px;
  left: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(-3px);
}

.back-icon {
  font-size: 18px;
}

.auth-card {
  width: 100%;
  max-width: 450px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  padding: 40px;
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-header {
  text-align: center;
  margin-bottom: 40px;
}

.auth-logo {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.logo-icon {
  font-size: 36px;
}

.logo-text {
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.auth-title {
  font-size: 28px;
  font-weight: 900;
  margin-bottom: 10px;
}

.auth-subtitle {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.6);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
}

.label-icon {
  font-size: 16px;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  color: white;
  font-size: 15px;
  transition: all 0.3s;
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.form-input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(243, 156, 18, 0.5);
  box-shadow: 0 0 0 3px rgba(243, 156, 18, 0.1);
}

.form-input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: rgba(231, 76, 60, 0.1);
  border: 1px solid rgba(231, 76, 60, 0.3);
  border-radius: 10px;
  color: #e74c3c;
  font-size: 14px;
  animation: shake 0.5s;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-10px); }
  75% { transform: translateX(10px); }
}

.error-icon {
  font-size: 18px;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 10px;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(243, 156, 18, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-content, .btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.btn-icon {
  font-size: 18px;
}

.loading-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-footer {
  text-align: center;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-text {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
}

.link-btn {
  background: none;
  border: none;
  color: #f39c12;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  transition: all 0.3s;
}

.link-btn:hover {
  color: #e67e22;
  text-decoration: underline;
}

.welcome-bonus {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(46, 204, 113, 0.1) 0%, rgba(39, 174, 96, 0.1) 100%);
  border: 1px solid rgba(46, 204, 113, 0.3);
  border-radius: 12px;
}

.bonus-icon {
  font-size: 32px;
}

.bonus-text {
  font-size: 13px;
  line-height: 1.5;
  color: rgba(255, 255, 255, 0.8);
}

.bonus-text strong {
  color: #2ecc71;
  font-weight: 700;
}

/* Responsive */
@media (max-width: 640px) {
  .auth-card {
    padding: 30px 20px;
  }
  
  .back-btn {
    top: 10px;
    left: 10px;
    padding: 10px 16px;
  }
}
</style>
