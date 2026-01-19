import { ref, computed } from 'vue'
import * as api from '../services/api'
import { getCards, groupCardsByRarity, isPlayerInLineup } from '../utils/catalog'

// =============================================================================
// ESTADO GLOBAL
// =============================================================================

// Estado de autenticación
const isLoggedIn = ref(false)
const isLoading = ref(false)
const error = ref(null)

// Datos del usuario
const currentUser = ref(null)
const userCollection = ref([])
// Cambiar a objeto/diccionario con keys por posición
const userLineup = ref({
  base: null,
  escolta: null,
  alero: null,
  alaPivot: null,
  pivot: null
})
const userLineupIds = ref({
  base: null,  // Ahora guarda {id, playerId, multiplicador}
  escolta: null,
  alero: null,
  alaPivot: null,
  pivot: null
})
const userPoints = ref(0)
const userRank = ref(0)
const userName = ref('')
const unopenedPacks = ref([])  // Sobres sin abrir

// Rankings
const rankings = ref([])

// =============================================================================
// INICIALIZACIÓN
// =============================================================================

/**
 * Inicializa la app - comprueba si hay sesión activa
 */
async function initApp() {
  if (api.isAuthenticated()) {
    try {
      isLoading.value = true
      await loadUserData()
      isLoggedIn.value = true
    } catch (e) {
      console.error('Error al restaurar sesión:', e)
      // Token inválido, limpiar
      api.setAuthToken(null)
    } finally {
      isLoading.value = false
    }
  }
}

// =============================================================================
// AUTENTICACIÓN
// =============================================================================

/**
 * Inicia sesión
 */
async function login(username, password) {
  try {
    isLoading.value = true
    error.value = null
    
    const response = await api.login(username, password)
    
    // Cargar datos del usuario desde la respuesta
    setUserData(response.user)
    isLoggedIn.value = true
    
    return { success: true }
  } catch (e) {
    error.value = e.message
    return { success: false, error: e.message }
  } finally {
    isLoading.value = false
  }
}

/**
 * Crea una nueva cuenta
 */
async function signup(username, email, password) {
  try {
    isLoading.value = true
    error.value = null
    
    const response = await api.signup(username, email, password)
    
    console.log('📦 Respuesta del signup:', response)
    console.log('🎴 Card IDs recibidos:', response.user.cardIds)
    
    // Auto-login después del registro
    setUserData(response.user)
    isLoggedIn.value = true
    
    console.log('✅ Colección después de setUserData:', userCollection.value)
    
    return { success: true }
  } catch (e) {
    error.value = e.message
    return { success: false, error: e.message }
  } finally {
    isLoading.value = false
  }
}

/**
 * Cierra sesión
 */
async function logout() {
  try {
    await api.logout()
  } catch (e) {
    // Ignorar errores
  }
  
  // Limpiar estado
  isLoggedIn.value = false
  currentUser.value = null
  userCollection.value = []
  userLineup.value = {
    base: null,
    escolta: null,
    alero: null,
    alaPivot: null,
    pivot: null
  }
  userLineupIds.value = {
    base: null,
    escolta: null,
    alero: null,
    alaPivot: null,
    pivot: null
  }
  userPoints.value = 0
  userRank.value = 0
  userName.value = ''
}

// =============================================================================
// DATOS DE USUARIO
// =============================================================================

/**
 * Carga los datos del usuario desde el backend
 */
async function loadUserData() {
  const userData = await api.getCurrentUser()
  setUserData(userData)
}

/**
 * Establece los datos del usuario en el estado
 * ARQUITECTURA: El backend devuelve SOLO IDs, el frontend los expande
 */
function setUserData(userData) {
  currentUser.value = userData
  userName.value = userData.username
  userPoints.value = userData.points
  userRank.value = userData.rank
  unopenedPacks.value = userData.unopenedPacks || []  // Sobres sin abrir
  
  // El backend envía objeto con keys de posición o array (compatibilidad)
  const lineupData = userData.lineupIds || {}
  
  // Si es array (legacy), convertir a objeto con formato antiguo (solo IDs)
  if (Array.isArray(lineupData)) {
    const positions = ['base', 'escolta', 'alero', 'alaPivot', 'pivot']
    userLineupIds.value = {}
    positions.forEach((pos, idx) => {
      const id = lineupData[idx]
      if (id && id !== "") {
        // Migrar formato antiguo al nuevo
        const cards = getCards([id])
        if (cards.length > 0) {
          userLineupIds.value[pos] = {
            id: id,
            playerId: cards[0].playerId || null,
            multiplicador: 1.0
          }
        } else {
          userLineupIds.value[pos] = null
        }
      } else {
        userLineupIds.value[pos] = null
      }
    })
  } else {
    // Es objeto - puede ser formato antiguo (string) o nuevo ({id, playerId, multiplicador})
    userLineupIds.value = {
      base: null,
      escolta: null,
      alero: null,
      alaPivot: null,
      pivot: null
    }
    
    for (const [pos, value] of Object.entries(lineupData)) {
      const normalizedPos = pos === 'ala_pivot' ? 'alaPivot' : pos
      
      if (value) {
        // Verificar si es formato antiguo (string) o nuevo (objeto)
        if (typeof value === 'string') {
          // Formato antiguo: migrar al nuevo
          const cards = getCards([value])
          if (cards.length > 0) {
            userLineupIds.value[normalizedPos] = {
              id: value,
              playerId: cards[0].playerId || null,
              multiplicador: 1.0
            }
          }
        } else if (typeof value === 'object' && value.id) {
          // Formato nuevo: usar directamente
          userLineupIds.value[normalizedPos] = {
            id: value.id,
            playerId: value.playerId || null,
            multiplicador: value.multiplicador || 1.0
          }
        }
      }
    }
  }
  
  // Expandir IDs a objetos completos usando el catálogo
  const cardIds = userData.cardIds || []
  userCollection.value = getCards(cardIds)
  
  // Expandir lineup usando las keys
  userLineup.value = {
    base: null,
    escolta: null,
    alero: null,
    alaPivot: null,
    pivot: null
  }
  
  for (const [position, lineupData] of Object.entries(userLineupIds.value)) {
    if (lineupData && lineupData.id) {
      const cards = getCards([lineupData.id])
      userLineup.value[position] = cards.length > 0 ? cards[0] : null
    }
  }
}

// =============================================================================
// COLECCIÓN Y ALINEACIÓN
// =============================================================================

/**
 * Añade cartas a la colección usando IDs
 * Recibe IDs del backend y los expande con el catálogo
 */
function addToCollection(cardIds) {
  const newCards = getCards(cardIds)
  userCollection.value.push(...newCards)
  
  // Actualizar también los IDs en el usuario actual
  if (currentUser.value && currentUser.value.cardIds) {
    currentUser.value.cardIds.push(...cardIds)
  }
}

/**
 * Añade una carta a la alineación en una posición específica
 * @param {Object} card - La carta a añadir
 * @param {String} position - La key de posición ('base', 'escolta', 'alero', 'alaPivot', 'pivot')
 * @param {Number} multiplicador - Multiplicador de puntos (default: 1.0)
 */
async function addToLineup(card, position, multiplicador = 1.0) {
  // Validar posición
  const validPositions = ['base', 'escolta', 'alero', 'alaPivot', 'pivot']
  if (!validPositions.includes(position)) {
    return { success: false, error: 'Posición inválida' }
  }
  
  // Verificar si la posición ya está ocupada
  if (userLineup.value[position] && userLineup.value[position].nombre) {
    return { success: false, error: 'Esta posición ya está ocupada' }
  }
  
  // Verificar si el jugador ya está en la alineación
  const playerName = card.nombre
  const isAlreadyInLineup = Object.values(userLineup.value).some(c => c && c.nombre === playerName)
  if (isAlreadyInLineup) {
    return { success: false, error: 'Ya tienes una carta de este jugador en la alineación' }
  }
  
  // Guardar estado anterior por si hay que revertir
  const prevCard = userLineup.value[position]
  const prevId = userLineupIds.value[position]
  
  // Log para debugging
  console.log('🎴 Añadiendo carta a lineup:', {
    cardId: card.id,
    cardName: card.nombre,
    playerId: card.playerId,
    fullCard: card
  })
  
  // Actualizar localmente primero (optimistic update)
  userLineup.value[position] = card
  userLineupIds.value[position] = {
    id: card.id,
    playerId: card.playerId || null,
    multiplicador: multiplicador
  }
  
  // Sincronizar con backend (enviar objeto completo, filtrando posiciones vacías)
  try {
    // Crear objeto solo con posiciones ocupadas
    const idsToSave = {}
    for (const [pos, lineupData] of Object.entries(userLineupIds.value)) {
      if (lineupData && lineupData.id) {
        idsToSave[pos] = {
          id: lineupData.id,
          playerId: lineupData.playerId,
          multiplicador: lineupData.multiplicador
        }
      }
    }
    await api.saveLineup(idsToSave)
    return { success: true }
  } catch (e) {
    // Revertir si falla
    userLineup.value[position] = prevCard
    userLineupIds.value[position] = prevId
    return { success: false, error: e.message }
  }
}

/**
 * Quita una carta de la alineación por posición
 * @param {String} position - La key de posición
 */
async function removeFromLineup(position) {
  // Validar posición
  const validPositions = ['base', 'escolta', 'alero', 'alaPivot', 'pivot']
  if (!validPositions.includes(position)) {
    return { success: false, error: 'Posición inválida' }
  }
  
  // Verificar si hay una carta en esa posición
  if (!userLineup.value[position]) {
    return { success: false, error: 'No hay carta en esta posición' }
  }
  
  // Guardar estado anterior por si hay que revertir
  const prevCard = userLineup.value[position]
  const prevId = userLineupIds.value[position]
  
  // Actualizar localmente
  userLineup.value[position] = null
  userLineupIds.value[position] = null
  
  // Sincronizar con backend (enviar objeto completo, filtrando posiciones vacías)
  try {
    // Crear objeto solo con posiciones ocupadas
    const idsToSave = {}
    for (const [pos, lineupData] of Object.entries(userLineupIds.value)) {
      if (lineupData && lineupData.id) {
        idsToSave[pos] = {
          id: lineupData.id,
          playerId: lineupData.playerId,
          multiplicador: lineupData.multiplicador
        }
      }
    }
    await api.saveLineup(idsToSave)
    return { success: true }
  } catch (e) {
    // Revertir si falla
    userLineup.value[position] = prevCard
    userLineupIds.value[position] = prevId
    return { success: false, error: e.message }
  }
}

// =============================================================================
// CÓDIGOS Y SOBRES
// =============================================================================

/**
 * Canjea un código y añade un sobre sin abrir al inventario
 * ARQUITECTURA: El backend añade el sobre, no genera cartas aún
 */
async function redeemCode(code) {
  try {
    const response = await api.redeemCode(code)
    
    if (response.success) {
      // Recargar datos del usuario para actualizar sobres sin abrir
      await loadUserData()
      
      return {
        success: true,
        message: response.message,
        packType: response.packType
      }
    }
    
    return response
  } catch (e) {
    return { success: false, message: e.message }
  }
}

/**
 * Abre un sobre del inventario y devuelve las cartas obtenidas
 * ARQUITECTURA: El backend devuelve SOLO IDs, el frontend los expande
 */
async function openPack(packIndex) {
  try {
    const response = await api.openPack(packIndex)
    
    if (response.success && response.newCardIds) {
      // El backend devolvió SOLO IDs
      // Expandir y añadir al estado local
      addToCollection(response.newCardIds)
      
      // Actualizar sobres sin abrir localmente (optimistic update)
      unopenedPacks.value = unopenedPacks.value.filter((_, index) => index !== packIndex)
      
      // Preparar respuesta con cartas completas para las animaciones
      const newCards = getCards(response.newCardIds)
      return {
        success: true,
        message: response.message,
        newCards: newCards,  // Cartas completas para animación
        packType: response.packType
      }
    }
    
    return response
  } catch (e) {
    return { success: false, message: e.message, newCards: [] }
  }
}

// =============================================================================
// RANKINGS
// =============================================================================

/**
 * Carga los rankings del backend
 */
async function loadRankings(period = 'monthly') {
  try {
    const response = await api.getRankings(period)
    rankings.value = response.rankings
    return response.rankings
  } catch (e) {
    console.error('Error cargando rankings:', e)
    return []
  }
}

// =============================================================================
// COMPUTED
// =============================================================================

const collectionByRarity = computed(() => {
  // Agrupar cartas por rareza usando la utilidad del catálogo
  const cardIds = currentUser.value?.cardIds || []
  return groupCardsByRarity(cardIds)
})

const lineupFull = computed(() => {
  // Verificar que todas las 5 posiciones estén ocupadas (no sean null)
  return Object.values(userLineup.value).every(card => card !== null)
})

// =============================================================================
// EXPORT
// =============================================================================

export function useGameStore() {
  return {
    // Estado
    isLoggedIn,
    isLoading,
    error,
    currentUser,
    userCollection,
    userLineup,
    userLineupIds,
    userPoints,
    userRank,
    userName,
    unopenedPacks,
    rankings,
    
    // Computed
    collectionByRarity,
    lineupFull,
    
    // Auth
    initApp,
    login,
    signup,
    logout,
    
    // Data
    loadUserData,
    loadRankings,
    
    // Collection & Lineup
    addToCollection,
    addToLineup,
    removeFromLineup,
    
    // Codes & Packs
    redeemCode,
    openPack
  }
}
