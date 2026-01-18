/**
 * UTILIDADES PARA ACCESO AL CATÁLOGO
 * 
 * Funciones para convertir IDs de cartas en objetos completos
 * usando el catálogo estático del frontend.
 */

import { CARDS_CATALOG, PLAYER_IDS } from '../data/cards-catalog'

/**
 * Obtiene una carta completa por su ID
 * @param {string} cardId - ID de la carta (ej: "card_001")
 * @returns {object|null} Carta completa o null si no existe
 */
export function getCard(cardId) {
  return CARDS_CATALOG[cardId] || null
}

/**
 * Convierte array de IDs en array de cartas completas
 * @param {string[]} cardIds - Array de IDs de cartas
 * @returns {object[]} Array de cartas completas
 */
export function getCards(cardIds) {
  if (!Array.isArray(cardIds)) return []
  return cardIds.map(id => CARDS_CATALOG[id]).filter(Boolean)
}

/**
 * Filtra cartas por rareza
 * @param {string[]} cardIds - Array de IDs de cartas
 * @param {string} rarity - Rareza a filtrar (common|rare|epic|legendary)
 * @returns {object[]} Array de cartas de la rareza especificada
 */
export function getCardsByRarity(cardIds, rarity) {
  return getCards(cardIds).filter(card => card.rareza === rarity)
}

/**
 * Obtiene todas las cartas del catálogo (para debug/admin)
 * @returns {object[]} Array con todas las cartas del catálogo
 */
export function getAllCards() {
  return Object.values(CARDS_CATALOG)
}

/**
 * Agrupa cartas por rareza
 * @param {string[]} cardIds - Array de IDs de cartas
 * @returns {object} Objeto con cartas agrupadas por rareza
 */
export function groupCardsByRarity(cardIds) {
  const cards = getCards(cardIds)
  const grouped = {
    legendary: [],
    epic: [],
    rare: [],
    common: []
  }
  
  cards.forEach(card => {
    if (grouped[card.rareza]) {
      grouped[card.rareza].push(card)
    }
  })
  
  return grouped
}

/**
 * Obtiene el ID del jugador a partir de una carta
 * @param {object} card - Carta
 * @returns {number|null} ID del jugador
 */
export function getPlayerIdFromCard(card) {
  return PLAYER_IDS[card.nombre] || null
}

/**
 * Verifica si un jugador ya está en la alineación
 * @param {string[]} lineupIds - IDs de cartas en la alineación
 * @param {string} cardId - ID de la carta a verificar
 * @returns {boolean} true si el jugador ya está en la alineación
 */
export function isPlayerInLineup(lineupIds, cardId) {
  const card = getCard(cardId)
  if (!card) return false
  
  const playerName = card.nombre
  const lineupCards = getCards(lineupIds)
  
  return lineupCards.some(c => c.nombre === playerName)
}

/**
 * Obtiene estadísticas agregadas de una colección de cartas
 * @param {string[]} cardIds - Array de IDs de cartas
 * @returns {object} Objeto con estadísticas
 */
export function getCollectionStats(cardIds) {
  const cards = getCards(cardIds)
  
  return {
    total: cards.length,
    byRarity: {
      common: cards.filter(c => c.rareza === 'common').length,
      rare: cards.filter(c => c.rareza === 'rare').length,
      epic: cards.filter(c => c.rareza === 'epic').length,
      legendary: cards.filter(c => c.rareza === 'legendary').length
    },
    byPosition: cards.reduce((acc, card) => {
      acc[card.posicion] = (acc[card.posicion] || 0) + 1
      return acc
    }, {})
  }
}

/**
 * Obtiene el color según la rareza
 * @param {string} rarity - Rareza de la carta
 * @returns {string} Código de color hexadecimal
 */
export function getRarityColor(rarity) {
  const colors = {
    common: '#888888',
    rare: '#5dade2',
    epic: '#9b59b6',
    legendary: '#f1c40f'
  }
  return colors[rarity] || colors.common
}

/**
 * Obtiene el multiplicador según la rareza
 * @param {string} rarity - Rareza de la carta
 * @returns {number} Multiplicador de puntos
 */
export function getRarityMultiplier(rarity) {
  const multipliers = {
    common: 1,
    rare: 1.5,
    epic: 2,
    legendary: 3
  }
  return multipliers[rarity] || 1
}
