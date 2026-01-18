<template>
  <div class="app">
    <!-- Loading inicial -->
    <div v-if="isInitializing" class="loading-screen">
      <div class="loading-content">
        <div class="loading-logo">🏀</div>
        <div class="loading-text">Cargando...</div>
      </div>
    </div>

    <!-- Landing Page / Auth Views -->
    <template v-else-if="!isLoggedIn">
      <LandingView v-if="currentView === 'landing'" @navigate="currentView = $event" />
      <SignInView v-else-if="currentView === 'signin'" 
        @navigate="currentView = $event"
        @login-success="onLoginSuccess" />
      <SignUpView v-else-if="currentView === 'signup'"
        @navigate="currentView = $event"
        @signup-success="onSignUpSuccess" />
    </template>

    <!-- App principal -->
    <template v-else>
      <!-- Header -->
      <header class="app-header">
        <div class="header-left">
          <div class="logo" @click="currentView = 'home'">
            <span class="logo-icon">🏀</span>
            <span class="logo-text">Fantasy Basket</span>
          </div>
        </div>
        <div class="header-right">
          <span class="user-name">{{ userName }}</span>
          <button class="logout-btn" @click="handleLogout" title="Cerrar sesión">
            🚪
          </button>
        </div>
      </header>

      <!-- Main content -->
      <main class="app-main">
        <HomeView v-if="currentView === 'home'" @navigate="currentView = $event" />
        <RedeemView v-else-if="currentView === 'redeem'" />
        <CollectionView v-else-if="currentView === 'collection'" />
        <LineupView v-else-if="currentView === 'lineup'" />
        <RankingsView v-else-if="currentView === 'rankings'" />
      </main>

      <!-- Bottom navigation -->
      <nav class="app-nav">
        <button 
          v-for="item in navItems" 
          :key="item.view"
          class="nav-item"
          :class="{ active: currentView === item.view }"
          @click="currentView = item.view"
        >
          <span class="nav-icon">{{ item.icon }}</span>
          <span class="nav-label">{{ item.label }}</span>
        </button>
      </nav>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from 'vue'
import { useGameStore } from './composables/useGameStore'
import LandingView from './views/LandingView.vue'
import SignInView from './views/SignInView.vue'
import SignUpView from './views/SignUpView.vue'
import HomeView from './views/HomeView.vue'
import RedeemView from './views/RedeemView.vue'
import CollectionView from './views/CollectionView.vue'
import LineupView from './views/LineupView.vue'
import RankingsView from './views/RankingsView.vue'

const { isLoggedIn, isLoading, userName, initApp, logout } = useGameStore()

const currentView = ref('landing')
const isInitializing = ref(true)

const navItems = [
  { view: 'home', icon: '🏠', label: 'Inicio' },
  { view: 'collection', icon: '🃏', label: 'Colección' },
  { view: 'redeem', icon: '🎁', label: 'Canjear' },
  { view: 'lineup', icon: '⚔️', label: 'Alineación' },
  { view: 'rankings', icon: '🏆', label: 'Rankings' },
]

onMounted(async () => {
  // Intentar restaurar sesión
  await initApp()
  isInitializing.value = false
})

// Watcher: cuando el usuario hace login, automáticamente ir a home
watch(isLoggedIn, (newValue) => {
  if (newValue) {
    console.log('✅ Usuario logueado, redirigiendo a home')
    nextTick(() => {
      currentView.value = 'home'
    })
  }
})

function onLoginSuccess() {
  console.log('Login exitoso, isLoggedIn:', isLoggedIn.value)
  currentView.value = 'home'
}

function onSignUpSuccess() {
  console.log('Signup exitoso, isLoggedIn:', isLoggedIn.value)
  currentView.value = 'home'
}

async function handleLogout() {
  await logout()
  currentView.value = 'landing'
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%);
  background-attachment: fixed;
  min-height: 100vh;
  color: white;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
}
</style>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Loading screen */
.loading-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-content {
  text-align: center;
}

.loading-logo {
  font-size: 80px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.1); opacity: 0.8; }
}

.loading-text {
  margin-top: 20px;
  font-size: 18px;
  color: rgba(255, 255, 255, 0.6);
}

/* Header */
.app-header {
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 15px 20px;
  background: rgba(10, 10, 15, 0.9);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 20px;
  font-weight: 800;
  background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.user-name {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

/* Media queries para móvil */
@media (max-width: 768px) {
  .nav-label {
    display: none;
  }

  .nav-item {
    padding: 10px 8px;
  }

  .nav-icon {
    font-size: 26px;
  }

  .app-main {
    padding-bottom: 65px;
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: 12px 15px;
  }

  .logo-text {
    display: none;
  }

  .logo-icon {
    font-size: 32px;
  }

  .user-name {
    display: none;
  }

  .logout-btn {
    width: 32px;
    height: 32px;
    font-size: 16px;
  }

  .nav-icon {
    font-size: 24px;
  }

  .nav-item {
    padding: 8px 2px;
  }

  .app-main {
    padding-bottom: 60px;
  }
}

@media (max-width: 360px) {
  .logo-icon {
    font-size: 28px;
  }

  .nav-item {
    padding: 8px 1px;
  }

  .nav-icon {
    font-size: 22px;
  }

  .nav-label {
    font-size: 8px;
  }
}

@media (max-width: 320px) {
  .nav-item {
    padding: 6px 0;
  }

  .nav-icon {
    font-size: 20px;
  }
}

.logout-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s;
}

.logout-btn:hover {
  background: rgba(231, 76, 60, 0.2);
  border-color: rgba(231, 76, 60, 0.3);
}

/* Main */
.app-main {
  flex: 1;
  padding-bottom: 85px;
  min-height: calc(100vh - 60px);
}

/* Navigation */
.app-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  width: 100%;
  display: flex;
  justify-content: space-evenly;
  align-items: center;
  padding: 10px 0;
  padding-bottom: max(10px, env(safe-area-inset-bottom));
  background: rgba(10, 10, 15, 0.98);
  backdrop-filter: blur(15px);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1000;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.3);
  overflow-x: hidden;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  padding: 8px 4px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  transition: all 0.3s;
  border-radius: 10px;
  flex: 1 1 0;
  min-width: 0;
  max-width: none;
}

.nav-item:hover {
  color: rgba(255, 255, 255, 0.8);
}

.nav-item.active {
  color: #f39c12;
  background: rgba(243, 156, 18, 0.1);
}

.nav-icon {
  font-size: 22px;
  line-height: 1;
}

.nav-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
</style>
