/**
 * API Service - Maneja todas las llamadas al backend
 * En desarrollo, el backend corre en localhost:8000
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Token de sesión (se guarda en memoria y localStorage)
let authToken = localStorage.getItem('authToken') || null

/**
 * Configura el token de autenticación
 */
export function setAuthToken(token) {
  authToken = token
  if (token) {
    localStorage.setItem('authToken', token)
  } else {
    localStorage.removeItem('authToken')
  }
}

/**
 * Obtiene el token actual
 */
export function getAuthToken() {
  return authToken
}

/**
 * Verifica si hay sesión activa
 */
export function isAuthenticated() {
  return !!authToken
}

/**
 * Realiza una petición a la API
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers
  }
  
  // Añadir token de autenticación si existe
  if (authToken) {
    // Usamos Basic Auth con el token como password (simplificado)
    headers['Authorization'] = `Basic ${btoa(`user:${authToken}`)}`
  }
  
  try {
    const response = await fetch(url, {
      ...options,
      headers
    })
    
    // Si es 401, limpiar sesión
    if (response.status === 401) {
      setAuthToken(null)
      throw new Error('Sesión expirada. Por favor, inicia sesión de nuevo.')
    }
    
    const data = await response.json()
    
    if (!response.ok) {
      throw new Error(data.detail || 'Error en la petición')
    }
    
    return data
  } catch (error) {
    // Si es error de red, puede que el backend no esté corriendo
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      console.warn('Backend no disponible, usando modo offline')
      throw new Error('No se puede conectar con el servidor. Comprueba que el backend está corriendo.')
    }
    throw error
  }
}

// =============================================================================
// AUTH API
// =============================================================================

/**
 * Inicia sesión
 * El backend devuelve SOLO IDs. El frontend los expande con el catálogo local.
 * Transferencia: ~200 bytes
 * @returns {Promise<{token: string, user: {id, username, cardIds, lineupIds, points, rank}}>}
 */
export async function login(username, password) {
  const response = await apiRequest('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password })
  })
  
  // Guardar token
  setAuthToken(response.token)
  
  // Respuesta contiene:
  // - token: string
  // - user.cardIds: string[] (solo IDs, no datos completos)
  // - user.lineupIds: string[] (solo IDs)
  // - user.points, user.rank, etc.
  
  return response
}

/**
 * Registra un nuevo usuario
 * @returns {Promise<{token: string, user: object}>}
 */
export async function signup(username, email, password) {
  const response = await apiRequest('/api/auth/signup', {
    method: 'POST',
    body: JSON.stringify({ username, email, password })
  })
  
  // Guardar token (auto-login)
  setAuthToken(response.token)
  
  return response
}

/**
 * Cierra sesión
 */
export async function logout() {
  try {
    await apiRequest('/api/auth/logout', { method: 'POST' })
  } catch (e) {
    // Ignorar errores al cerrar sesión
  }
  setAuthToken(null)
}

// =============================================================================
// USER API
// =============================================================================

/**
 * Obtiene los datos del usuario actual
 * Esta es la llamada principal al cargar la app
 * @returns {Promise<{id, username, cards, lineup, points, rank}>}
 */
export async function getCurrentUser() {
  return apiRequest('/api/user/me')
}

/**
 * Guarda la alineación del usuario
 * @param {string[]} cardIds - Lista de IDs de cartas
 */
export async function saveLineup(cardIds) {
  return apiRequest('/api/user/lineup', {
    method: 'POST',
    body: JSON.stringify({ lineup: cardIds })
  })
}

// =============================================================================
// CODES API
// =============================================================================

/**
 * Canjea un código y obtiene un sobre sin abrir
 * El backend añade el sobre al inventario del usuario
 * @param {string} code - Código a canjear
 * @returns {Promise<{success, message, packType: string}>}
 */
export async function redeemCode(code) {
  return apiRequest('/api/codes/redeem', {
    method: 'POST',
    body: JSON.stringify({ code })
  })
}

/**
 * Abre un sobre del inventario y obtiene las cartas
 * El backend devuelve SOLO IDs de las nuevas cartas.
 * @param {number} packIndex - Índice del sobre a abrir
 * @returns {Promise<{success, message, newCardIds: string[], packType: string}>}
 */
export async function openPack(packIndex) {
  return apiRequest('/api/packs/open', {
    method: 'POST',
    body: JSON.stringify({ packIndex })
  })
}

// =============================================================================
// RANKINGS API
// =============================================================================

/**
 * Obtiene el ranking
 * @param {string} period - 'weekly', 'monthly', 'season'
 */
export async function getRankings(period = 'monthly') {
  return apiRequest(`/api/rankings?period=${period}`)
}

// =============================================================================
// PLAYERS API
// =============================================================================

/**
 * Obtiene la lista de jugadores del club
 */
export async function getPlayers() {
  return apiRequest('/api/players')
}
