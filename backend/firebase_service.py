"""
Firebase Service - Integración con Firebase Authentication + Firestore
Mantiene la ARQUITECTURA DE IDS: solo almacena IDs, no datos de cartas
"""

import firebase_admin
from firebase_admin import credentials, firestore, auth
import os
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict

# Inicializar Firebase Admin SDK
# Soporta dos métodos de configuración:
# 1. Variable de entorno FIREBASE_CONFIG con JSON como string
# 2. Archivo JSON en firebase_config/ (fallback)
import pathlib

firebase_config_env = os.getenv("FIREBASE_CONFIG")

if firebase_config_env:
    # Cargar desde variable de entorno
    try:
        config_dict = json.loads(firebase_config_env)
        cred = credentials.Certificate(config_dict)
        print("✅ Firebase config cargada desde variable de entorno FIREBASE_CONFIG")
    except json.JSONDecodeError as e:
        print(f"❌ Error al parsear FIREBASE_CONFIG: {e}")
        raise Exception("FIREBASE_CONFIG contiene JSON inválido")
else:
    # Cargar desde archivo (método tradicional)
    config_path = pathlib.Path(__file__).parent / "firebase_config" / "fantasy-de-dalt-firebase-adminsdk-fbsvc-061b5456f9.json"
    cred = credentials.Certificate(str(config_path))
    print(f"✅ Firebase config cargada desde archivo: {config_path}")

firebase_admin.initialize_app(cred)

# Cliente de Firestore
db = firestore.client()

# =============================================================================
# COLECCIONES
# =============================================================================

USERS_COLLECTION = "users"
PLAYERS_COLLECTION = "players"
# Colecciones: users (usuarios) y players (jugadores reales con estadísticas)

# =============================================================================
# POOL DE IDS DE CARTAS
# El backend NO genera cartas, solo asigna IDs del catálogo del frontend
# =============================================================================

# Todas las cartas del catálogo del frontend son "common" por ahora
# SINCRONIZADO con cards-catalog.js (card_001 a card_011)
CARD_ID_POOLS = {
    "common": [
        "card_001", "card_002", "card_003", "card_004", "card_005",
        "card_006", "card_007", "card_008", "card_009", "card_010", "card_011"
    ],
    "rare": [
        "card_002", "card_004", "card_006", "card_008"
    ],
    "epic": [
        "card_003", "card_007", "card_011"
    ],
    "legendary": [
        "card_004", "card_008"
    ]
}

# Pool de cartas por posición (para pack de bienvenida)
# SINCRONIZADO con el catálogo del frontend (cards-catalog.js)
CARDS_BY_POSITION = {
    "Base": ["card_002", "card_008"],  # Ian Olcina, Alberto Oteo
    "Escolta": ["card_001", "card_007", "card_010"],  # Àlvar Cano, Tomás Ferreira, David Pascual
    "Alero": ["card_003", "card_006", "card_011"],  # Marc Oliana, Víctor Páez, David López
    "Ala-Pívot": ["card_004", "card_009"],  # Guillem Alsina, Robert Cepeda
    "Pívot": ["card_005"]  # Alejandro de Haro
}

# =============================================================================
# FUNCIONES DE USUARIOS
# =============================================================================

async def get_user_by_username(username: str) -> Optional[Dict]:
    """
    Obtiene un usuario por username
    1 query a Firestore
    """
    users_ref = db.collection(USERS_COLLECTION)
    query = users_ref.where("username", "==", username.lower()).limit(1)
    docs = query.stream()
    
    for doc in docs:
        user_data = doc.to_dict()
        user_data["_id"] = doc.id
        return user_data
    
    return None

async def get_user_by_id(user_id: str) -> Optional[Dict]:
    """
    Obtiene un usuario por ID
    1 query a Firestore
    """
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    doc = doc_ref.get()
    
    if doc.exists:
        user_data = doc.to_dict()
        user_data["_id"] = doc.id
        return user_data
    
    return None

async def get_user_by_email(email: str) -> Optional[Dict]:
    """
    Obtiene un usuario por email desde Firestore
    1 query a Firestore
    """
    users_ref = db.collection(USERS_COLLECTION)
    query = users_ref.where("email", "==", email.lower()).limit(1)
    docs = query.stream()
    
    for doc in docs:
        user_data = doc.to_dict()
        user_data["_id"] = doc.id
        return user_data
    
    return None

async def verify_user_login(email: str, password: str) -> Optional[Dict]:
    """
    Verifica las credenciales del usuario usando Firebase Authentication
    Nota: Firebase Admin SDK no puede verificar contraseñas directamente,
    por lo que usamos un enfoque híbrido:
    1. Buscamos el usuario por email en Firestore
    2. Para producción, se debe usar Firebase Auth en el frontend
    """
    try:
        # Obtener usuario de Firebase Auth por email
        firebase_user = auth.get_user_by_email(email)
        
        # Obtener datos del usuario de Firestore
        user_data = await get_user_by_id(firebase_user.uid)
        
        if user_data:
            # Actualizar última conexión
            doc_ref = db.collection(USERS_COLLECTION).document(firebase_user.uid)
            doc_ref.update({"lastLogin": firestore.SERVER_TIMESTAMP})
            
            return user_data
        
        return None
        
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        print(f"❌ Error en login: {str(e)}")
        return None

async def create_user(username: str, password: str, email: str) -> Dict:
    """
    Crea un nuevo usuario en Firebase Authentication Y Firestore
    1. Crea usuario en Firebase Authentication
    2. Crea documento en Firestore con colección VACÍA (sin cartas iniciales)
    """
    # Verificar si el usuario ya existe en Firestore
    existing_user = await get_user_by_username(username)
    if existing_user:
        raise Exception("El nombre de usuario ya está en uso")
    
    try:
        # 1. Crear usuario en Firebase Authentication
        firebase_user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        
        print(f"✅ Usuario creado en Firebase Auth: {firebase_user.uid}")
        
        # 2. Crear documento en Firestore usando el UID de Firebase Auth
        # Usuario inicia con colección VACÍA
        user_data = {
            "username": username.lower(),
            "email": email,
            "cardIds": [],  # Colección vacía - el usuario debe canjear códigos
            "lineupIds": [],  # Alineación vacía
            "unopenedPacks": [],  # Sobres sin abrir
            "points": 0,
            "rank": 0,
            "redeemedCodes": [],
            "createdAt": firestore.SERVER_TIMESTAMP,
            "lastLogin": firestore.SERVER_TIMESTAMP,
            "authUid": firebase_user.uid  # Vinculamos con Firebase Auth
        }
        
        # Usar el UID de Firebase Auth como ID del documento en Firestore
        doc_ref = db.collection(USERS_COLLECTION).document(firebase_user.uid)
        doc_ref.set(user_data)
        user_data["_id"] = firebase_user.uid
        
        print(f"✅ Usuario creado en Firestore con colección vacía: {firebase_user.uid}")
        
        return user_data
        
    except auth.EmailAlreadyExistsError:
        raise Exception("El email ya está registrado")
    except Exception as e:
        print(f"❌ Error creando usuario: {str(e)}")
        raise Exception(f"Error al crear el usuario: {str(e)}")

async def update_user_cards(user_id: str, card_ids: List[str]) -> bool:
    """
    Actualiza las cartas del usuario (SOLO IDs)
    1 query a Firestore
    """
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    doc_ref.update({"cardIds": card_ids})
    return True

async def update_user_lineup(user_id: str, lineup_ids: Dict) -> bool:
    """
    Actualiza la alineación del usuario
    Guarda diccionario con keys de posición y valores con {id, playerId, multiplicador}
    1 query a Firestore
    """
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    doc_ref.update({"lineupIds": lineup_ids})
    return True

async def add_unopened_pack(user_id: str, pack_type: str) -> bool:
    """
    Añade un sobre sin abrir al inventario del usuario
    1 query a Firestore
    """
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    pack_data = {
        "type": pack_type,
        "timestamp": datetime.now().isoformat()  # Usar ISO string en lugar de SERVER_TIMESTAMP
    }
    doc_ref.update({
        "unopenedPacks": firestore.ArrayUnion([pack_data])
    })
    return True

async def remove_unopened_pack(user_id: str, pack_index: int) -> bool:
    """
    Remueve un sobre del inventario de sobres sin abrir
    1 query a Firestore - requiere leer primero
    """
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    doc = doc_ref.get()
    
    if doc.exists:
        user_data = doc.to_dict()
        unopened_packs = user_data.get("unopenedPacks", [])
        
        if 0 <= pack_index < len(unopened_packs):
            unopened_packs.pop(pack_index)
            doc_ref.update({"unopenedPacks": unopened_packs})
            return True
    
    return False

async def add_redeemed_code(user_id: str, code: str) -> bool:
    """
    Añade un código a la lista de códigos canjeados
    1 query a Firestore
    """
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    doc_ref.update({
        "redeemedCodes": firestore.ArrayUnion([code])
    })
    return True

# =============================================================================
# CÓDIGOS CANJEABLES (DESDE ARCHIVO JSON)
# =============================================================================

# Ruta del archivo JSON de códigos
CODES_JSON_PATH = pathlib.Path(__file__).parent / "codes.json"

def load_codes() -> Dict:
    """
    Carga los códigos desde el archivo JSON
    """
    try:
        if CODES_JSON_PATH.exists():
            with open(CODES_JSON_PATH, 'r', encoding='utf-8') as f:
                codes_data = json.load(f)
                # Convertir strings ISO a datetime
                for code, data in codes_data.items():
                    if isinstance(data.get("validUntil"), str):
                        data["validUntil"] = datetime.fromisoformat(data["validUntil"])
                return codes_data
        else:
            print(f"⚠️  Archivo de códigos no encontrado: {CODES_JSON_PATH}")
            return {}
    except Exception as e:
        print(f"❌ Error cargando códigos: {str(e)}")
        return {}

def save_codes(codes: Dict) -> bool:
    """
    Guarda los códigos en el archivo JSON
    """
    try:
        # Convertir datetime a strings ISO antes de guardar
        codes_to_save = {}
        for code, data in codes.items():
            data_copy = data.copy()
            if isinstance(data_copy.get("validUntil"), datetime):
                data_copy["validUntil"] = data_copy["validUntil"].isoformat()
            codes_to_save[code] = data_copy
        
        with open(CODES_JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(codes_to_save, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error guardando códigos: {str(e)}")
        return False

def get_code(code: str) -> Optional[Dict]:
    """
    Obtiene información de un código desde el archivo JSON
    """
    codes = load_codes()
    code_upper = code.upper()
    
    if code_upper in codes:
        code_data = codes[code_upper].copy()
        code_data["code"] = code_upper
        
        # Verificar si está activo
        if not code_data.get("active", True):
            return None
        
        return code_data
    return None

def get_all_codes() -> Dict:
    """
    Obtiene todos los códigos del archivo JSON
    """
    return load_codes()

def add_code(code: str, pack_type: str, valid_until: datetime, description: str = "", active: bool = True) -> bool:
    """
    Añade un nuevo código al archivo JSON
    """
    codes = load_codes()
    code_upper = code.upper()
    
    if code_upper in codes:
        return False  # El código ya existe
    
    codes[code_upper] = {
        "packType": pack_type,
        "validUntil": valid_until,
        "description": description,
        "active": active
    }
    
    return save_codes(codes)

def update_code(code: str, pack_type: Optional[str] = None, valid_until: Optional[datetime] = None, 
                description: Optional[str] = None, active: Optional[bool] = None) -> bool:
    """
    Actualiza un código existente en el archivo JSON
    """
    codes = load_codes()
    code_upper = code.upper()
    
    if code_upper not in codes:
        return False  # El código no existe
    
    if pack_type is not None:
        codes[code_upper]["packType"] = pack_type
    if valid_until is not None:
        codes[code_upper]["validUntil"] = valid_until
    if description is not None:
        codes[code_upper]["description"] = description
    if active is not None:
        codes[code_upper]["active"] = active
    
    return save_codes(codes)

def delete_code(code: str) -> bool:
    """
    Elimina un código del archivo JSON
    """
    codes = load_codes()
    code_upper = code.upper()
    
    if code_upper not in codes:
        return False  # El código no existe
    
    del codes[code_upper]
    return save_codes(codes)

# =============================================================================
# SESIONES (EN MEMORIA - NO SE GUARDAN EN FIRESTORE)
# =============================================================================

# Diccionario en memoria para sesiones activas {token: {userId, expiresAt}}
active_sessions = {}

def create_session(user_id: str, token: str) -> bool:
    """
    Crea una sesión en memoria (no en Firestore)
    """
    active_sessions[token] = {
        "userId": user_id,
        "expiresAt": datetime.now() + timedelta(days=7)
    }
    return True

def get_session(token: str) -> Optional[Dict]:
    """
    Obtiene una sesión desde memoria (no Firestore)
    """
    if token in active_sessions:
        session = active_sessions[token]
        
        # Verificar si ha expirado
        if datetime.now() > session["expiresAt"]:
            del active_sessions[token]
            return None
        
        return session
    
    return None

def delete_session(token: str) -> bool:
    """
    Elimina una sesión de memoria (no de Firestore)
    """
    if token in active_sessions:
        del active_sessions[token]
    return True

# =============================================================================
# FUNCIONES DE CÁLCULO DE ESTADÍSTICAS
# =============================================================================

def calcular_valoracion_acb(stats: Dict) -> float:
    """
    Calcula la valoración ACB de un jugador
    Fórmula: (Puntos + Rebotes + Asistencias + Robos + Tapones + Tiros Anotados) - 
             (Tiros Fallados + Pérdidas + Tiros Libres Fallados + Faltas)
    """
    tiros_anotados = stats.get("tiros2Anotados", 0) + stats.get("tiros3Anotados", 0)
    tiros_fallados = (
        (stats.get("tiros2Intentados", 0) - stats.get("tiros2Anotados", 0)) +
        (stats.get("tiros3Intentados", 0) - stats.get("tiros3Anotados", 0))
    )
    tl_fallados = stats.get("tirosLibresIntentados", 0) - stats.get("tirosLibresAnotados", 0)
    
    valoracion = (
        stats.get("puntos", 0) +
        stats.get("rebotes", 0) +
        stats.get("asistencias", 0) +
        stats.get("robos", 0) +
        stats.get("tapones", 0) +
        tiros_anotados -
        tiros_fallados -
        stats.get("perdidas", 0) -
        tl_fallados -
        stats.get("faltas", 0)
    )
    
    return round(valoracion, 2)

def calcular_puntos_fantasy(stats: Dict, victoria: bool = False) -> float:
    """
    Calcula los puntos fantasy de un jugador
    Sistema propio con bonificaciones por logros
    """
    puntos_base = (
        stats.get("puntos", 0) * 1.0 +
        stats.get("asistencias", 0) * 1.5 +
        stats.get("rebotes", 0) * 1.2 +
        stats.get("robos", 0) * 3.0 +
        stats.get("tapones", 0) * 3.0 -
        stats.get("perdidas", 0) * 1.0 -
        stats.get("faltas", 0) * 0.5
    )
    
    # Bonus por doble-doble (2 stats con 10+)
    stats_10_plus = sum([
        stats.get("puntos", 0) >= 10,
        stats.get("rebotes", 0) >= 10,
        stats.get("asistencias", 0) >= 10,
        stats.get("robos", 0) >= 10,
        stats.get("tapones", 0) >= 10
    ])
    
    if stats_10_plus >= 2:
        puntos_base += 5.0  # Doble-doble bonus
    if stats_10_plus >= 3:
        puntos_base += 15.0  # Triple-doble bonus (adicional)
    
    # Bonus por victoria
    if victoria:
        puntos_base += 2.0
    
    return round(puntos_base, 2)

def calcular_promedios(stats_temporada: Dict, partidos_jugados: int) -> Dict:
    """
    Calcula los promedios por partido
    """
    if partidos_jugados == 0:
        return {
            "puntos": 0.0,
            "asistencias": 0.0,
            "rebotes": 0.0,
            "robos": 0.0,
            "tapones": 0.0,
            "valoracion": 0.0,
            "puntosFantasy": 0.0
        }
    
    return {
        "puntos": round(stats_temporada.get("puntos", 0) / partidos_jugados, 2),
        "asistencias": round(stats_temporada.get("asistencias", 0) / partidos_jugados, 2),
        "rebotes": round(stats_temporada.get("rebotes", 0) / partidos_jugados, 2),
        "robos": round(stats_temporada.get("robos", 0) / partidos_jugados, 2),
        "tapones": round(stats_temporada.get("tapones", 0) / partidos_jugados, 2),
        "valoracion": round(stats_temporada.get("valoracion", 0) / partidos_jugados, 2),
        "puntosFantasy": round(stats_temporada.get("puntosFantasy", 0) / partidos_jugados, 2)
    }

# =============================================================================
# FUNCIONES DE JUGADORES Y ESTADÍSTICAS
# =============================================================================

async def get_all_players(active_only: bool = True) -> List[Dict]:
    """
    Obtiene todos los jugadores
    """
    players_ref = db.collection(PLAYERS_COLLECTION)
    
    if active_only:
        query = players_ref.where("activo", "==", True)
    else:
        query = players_ref
    
    players = []
    for doc in query.stream():
        player_data = doc.to_dict()
        player_data["playerId"] = doc.id
        players.append(player_data)
    
    return players

async def get_player_by_id(player_id: str) -> Optional[Dict]:
    """
    Obtiene un jugador por ID
    """
    doc_ref = db.collection(PLAYERS_COLLECTION).document(player_id)
    doc = doc_ref.get()
    
    if doc.exists:
        player_data = doc.to_dict()
        player_data["playerId"] = doc.id
        return player_data
    
    return None

async def create_player(player_data: Dict) -> str:
    """
    Crea un nuevo jugador
    """
    # Estructura inicial del jugador
    new_player = {
        "nombre": player_data["nombre"],
        "numero": player_data.get("numero", 0),
        "posicion": player_data["posicion"],
        "equipo": player_data.get("equipo", "Premia de Dalt - Senior Masc. A"),
        "activo": player_data.get("activo", True),
        "cardIds": player_data.get("cardIds", []),
        "statsTemporada": {
            "partidosJugados": 0,
            "minutosJugados": 0,
            "puntos": 0,
            "asistencias": 0,
            "rebotes": 0,
            "rebotesOfensivos": 0,
            "rebotesDefensivos": 0,
            "robos": 0,
            "tapones": 0,
            "perdidas": 0,
            "faltas": 0,
            "tiros2Anotados": 0,
            "tiros2Intentados": 0,
            "tiros3Anotados": 0,
            "tiros3Intentados": 0,
            "tirosLibresAnotados": 0,
            "tirosLibresIntentados": 0,
            "valoracion": 0.0,
            "puntosFantasy": 0.0
        },
        "promedios": {
            "puntos": 0.0,
            "asistencias": 0.0,
            "rebotes": 0.0,
            "robos": 0.0,
            "tapones": 0.0,
            "valoracion": 0.0,
            "puntosFantasy": 0.0
        },
        "mejorPartido": None,
        "jornadasStats": [],
        "createdAt": firestore.SERVER_TIMESTAMP
    }
    
    doc_ref = db.collection(PLAYERS_COLLECTION).add(new_player)
    return doc_ref[1].id

async def add_jornada_stats(player_id: str, jornada_data: Dict) -> Dict:
    """
    Añade estadísticas de una jornada a un jugador
    Actualiza las estadísticas de temporada y promedios automáticamente
    """
    player = await get_player_by_id(player_id)
    if not player:
        raise Exception(f"Jugador {player_id} no encontrado")
    
    # Verificar que la jornada no exista ya
    jornadas_existentes = player.get("jornadasStats", [])
    jornada_num = jornada_data.get("jornada")
    
    for j in jornadas_existentes:
        if j.get("jornada") == jornada_num:
            raise Exception(f"Ya existen estadísticas para la jornada {jornada_num}")
    
    stats = jornada_data["stats"]
    
    # Calcular valoración y puntos fantasy
    stats["valoracion"] = calcular_valoracion_acb(stats)
    stats["puntosFantasy"] = calcular_puntos_fantasy(stats, jornada_data.get("victoria", False))
    
    # Preparar datos de la jornada
    nueva_jornada = {
        "jornada": jornada_num,
        "fecha": jornada_data["fecha"],
        "rival": jornada_data["rival"],
        "local": jornada_data.get("local", True),
        "resultado": jornada_data.get("resultado", ""),
        "victoria": jornada_data.get("victoria", False),
        "stats": stats
    }
    
    # Actualizar estadísticas de temporada
    stats_temporada = player.get("statsTemporada", {})
    stats_temporada["partidosJugados"] = stats_temporada.get("partidosJugados", 0) + 1
    
    for key in ["minutosJugados", "puntos", "asistencias", "rebotes", "rebotesOfensivos", 
                "rebotesDefensivos", "robos", "tapones", "perdidas", "faltas",
                "tiros2Anotados", "tiros2Intentados", "tiros3Anotados", "tiros3Intentados",
                "tirosLibresAnotados", "tirosLibresIntentados"]:
        stats_temporada[key] = stats_temporada.get(key, 0) + stats.get(key, 0)
    
    stats_temporada["valoracion"] = round(stats_temporada.get("valoracion", 0) + stats["valoracion"], 2)
    stats_temporada["puntosFantasy"] = round(stats_temporada.get("puntosFantasy", 0) + stats["puntosFantasy"], 2)
    
    # Calcular promedios
    promedios = calcular_promedios(stats_temporada, stats_temporada["partidosJugados"])
    
    # Actualizar mejor partido
    mejor_partido = player.get("mejorPartido")
    if not mejor_partido or stats["valoracion"] > mejor_partido.get("valoracion", 0):
        mejor_partido = {
            "jornada": jornada_num,
            "fecha": jornada_data["fecha"],
            "puntos": stats["puntos"],
            "valoracion": stats["valoracion"]
        }
    
    # Añadir jornada al array
    jornadas_existentes.append(nueva_jornada)
    
    # Ordenar jornadas por número
    jornadas_existentes.sort(key=lambda x: x["jornada"])
    
    # Actualizar documento
    doc_ref = db.collection(PLAYERS_COLLECTION).document(player_id)
    doc_ref.update({
        "statsTemporada": stats_temporada,
        "promedios": promedios,
        "mejorPartido": mejor_partido,
        "jornadasStats": jornadas_existentes
    })
    
    return {
        "valoracion": stats["valoracion"],
        "puntosFantasy": stats["puntosFantasy"],
        "dobleDoble": sum([
            stats.get("puntos", 0) >= 10,
            stats.get("rebotes", 0) >= 10,
            stats.get("asistencias", 0) >= 10,
            stats.get("robos", 0) >= 10,
            stats.get("tapones", 0) >= 10
        ]) >= 2
    }

async def update_jornada_stats(player_id: str, jornada_num: int, stats_update: Dict) -> bool:
    """
    Actualiza las estadísticas de una jornada existente
    Recalcula todas las estadísticas de temporada
    """
    player = await get_player_by_id(player_id)
    if not player:
        return False
    
    jornadas = player.get("jornadasStats", [])
    jornada_encontrada = False
    
    for i, jornada in enumerate(jornadas):
        if jornada["jornada"] == jornada_num:
            # Actualizar stats
            jornada["stats"].update(stats_update)
            
            # Recalcular valoración y puntos fantasy
            jornada["stats"]["valoracion"] = calcular_valoracion_acb(jornada["stats"])
            jornada["stats"]["puntosFantasy"] = calcular_puntos_fantasy(
                jornada["stats"], 
                jornada.get("victoria", False)
            )
            
            jornadas[i] = jornada
            jornada_encontrada = True
            break
    
    if not jornada_encontrada:
        return False
    
    # Recalcular todas las estadísticas de temporada
    stats_temporada = {
        "partidosJugados": len(jornadas),
        "minutosJugados": 0,
        "puntos": 0,
        "asistencias": 0,
        "rebotes": 0,
        "rebotesOfensivos": 0,
        "rebotesDefensivos": 0,
        "robos": 0,
        "tapones": 0,
        "perdidas": 0,
        "faltas": 0,
        "tiros2Anotados": 0,
        "tiros2Intentados": 0,
        "tiros3Anotados": 0,
        "tiros3Intentados": 0,
        "tirosLibresAnotados": 0,
        "tirosLibresIntentados": 0,
        "valoracion": 0.0,
        "puntosFantasy": 0.0
    }
    
    mejor_partido = None
    
    for jornada in jornadas:
        s = jornada["stats"]
        for key in stats_temporada.keys():
            if key not in ["partidosJugados"]:
                stats_temporada[key] += s.get(key, 0)
        
        if not mejor_partido or s["valoracion"] > mejor_partido.get("valoracion", 0):
            mejor_partido = {
                "jornada": jornada["jornada"],
                "fecha": jornada["fecha"],
                "puntos": s["puntos"],
                "valoracion": s["valoracion"]
            }
    
    # Redondear
    stats_temporada["valoracion"] = round(stats_temporada["valoracion"], 2)
    stats_temporada["puntosFantasy"] = round(stats_temporada["puntosFantasy"], 2)
    
    # Calcular promedios
    promedios = calcular_promedios(stats_temporada, stats_temporada["partidosJugados"])
    
    # Actualizar documento
    doc_ref = db.collection(PLAYERS_COLLECTION).document(player_id)
    doc_ref.update({
        "statsTemporada": stats_temporada,
        "promedios": promedios,
        "mejorPartido": mejor_partido,
        "jornadasStats": jornadas
    })
    
    return True

async def delete_jornada_stats(player_id: str, jornada_num: int) -> bool:
    """
    Elimina las estadísticas de una jornada y recalcula la temporada
    """
    player = await get_player_by_id(player_id)
    if not player:
        return False
    
    jornadas = player.get("jornadasStats", [])
    jornadas_filtradas = [j for j in jornadas if j["jornada"] != jornada_num]
    
    if len(jornadas_filtradas) == len(jornadas):
        return False  # No se encontró la jornada
    
    # Recalcular estadísticas de temporada
    if len(jornadas_filtradas) == 0:
        # Sin jornadas, resetear stats
        stats_temporada = {
            "partidosJugados": 0,
            "minutosJugados": 0,
            "puntos": 0,
            "asistencias": 0,
            "rebotes": 0,
            "rebotesOfensivos": 0,
            "rebotesDefensivos": 0,
            "robos": 0,
            "tapones": 0,
            "perdidas": 0,
            "faltas": 0,
            "tiros2Anotados": 0,
            "tiros2Intentados": 0,
            "tiros3Anotados": 0,
            "tiros3Intentados": 0,
            "tirosLibresAnotados": 0,
            "tirosLibresIntentados": 0,
            "valoracion": 0.0,
            "puntosFantasy": 0.0
        }
        promedios = calcular_promedios(stats_temporada, 0)
        mejor_partido = None
    else:
        # Recalcular desde cero
        stats_temporada = {
            "partidosJugados": len(jornadas_filtradas),
            "minutosJugados": 0,
            "puntos": 0,
            "asistencias": 0,
            "rebotes": 0,
            "rebotesOfensivos": 0,
            "rebotesDefensivos": 0,
            "robos": 0,
            "tapones": 0,
            "perdidas": 0,
            "faltas": 0,
            "tiros2Anotados": 0,
            "tiros2Intentados": 0,
            "tiros3Anotados": 0,
            "tiros3Intentados": 0,
            "tirosLibresAnotados": 0,
            "tirosLibresIntentados": 0,
            "valoracion": 0.0,
            "puntosFantasy": 0.0
        }
        
        mejor_partido = None
        
        for jornada in jornadas_filtradas:
            s = jornada["stats"]
            for key in stats_temporada.keys():
                if key not in ["partidosJugados"]:
                    stats_temporada[key] += s.get(key, 0)
            
            if not mejor_partido or s["valoracion"] > mejor_partido.get("valoracion", 0):
                mejor_partido = {
                    "jornada": jornada["jornada"],
                    "fecha": jornada["fecha"],
                    "puntos": s["puntos"],
                    "valoracion": s["valoracion"]
                }
        
        stats_temporada["valoracion"] = round(stats_temporada["valoracion"], 2)
        stats_temporada["puntosFantasy"] = round(stats_temporada["puntosFantasy"], 2)
        promedios = calcular_promedios(stats_temporada, stats_temporada["partidosJugados"])
    
    # Actualizar documento
    doc_ref = db.collection(PLAYERS_COLLECTION).document(player_id)
    doc_ref.update({
        "statsTemporada": stats_temporada,
        "promedios": promedios,
        "mejorPartido": mejor_partido,
        "jornadasStats": jornadas_filtradas
    })
    
    return True

async def get_players_ranking(limit: int = 10, order_by: str = "puntosFantasy") -> List[Dict]:
    """
    Obtiene el ranking de jugadores
    """
    players = await get_all_players(active_only=True)
    
    # Ordenar por el campo especificado en statsTemporada
    if order_by == "puntosFantasy":
        players.sort(key=lambda p: p.get("statsTemporada", {}).get("puntosFantasy", 0), reverse=True)
    elif order_by == "puntos":
        players.sort(key=lambda p: p.get("statsTemporada", {}).get("puntos", 0), reverse=True)
    elif order_by == "valoracion":
        players.sort(key=lambda p: p.get("statsTemporada", {}).get("valoracion", 0), reverse=True)
    else:
        players.sort(key=lambda p: p.get("statsTemporada", {}).get("puntosFantasy", 0), reverse=True)
    
    # Limitar resultados
    players = players[:limit]
    
    # Añadir ranking
    ranking = []
    for i, player in enumerate(players, 1):
        ranking.append({
            "rank": i,
            "playerId": player["playerId"],
            "nombre": player["nombre"],
            "posicion": player["posicion"],
            "statsTemporada": player.get("statsTemporada", {}),
            "promedios": player.get("promedios", {})
        })
    
    return ranking

# =============================================================================
# FUNCIONES DE INICIALIZACIÓN
# =============================================================================

async def init_demo_user():
    """
    Inicializa usuario demo si no existe
    """
    existing_user = await get_user_by_username("demo")
    
    if not existing_user:
        user_data = {
            "username": "demo",
            "password": "demo123",
            "email": "demo@fantasybasket.com",
            "cardIds": ["card_001", "card_002", "card_005", "card_009", "card_013"],
            "lineupIds": ["card_002", "card_005"],
            "points": 1250,
            "rank": 156,
            "redeemedCodes": [],
            "createdAt": firestore.SERVER_TIMESTAMP,
            "lastLogin": firestore.SERVER_TIMESTAMP
        }
        
        db.collection(USERS_COLLECTION).add(user_data)
        print("✅ Usuario demo creado en Firestore")
    else:
        print("ℹ️  Usuario demo ya existe en Firestore")

async def initialize_firebase():
    """
    Inicializa datos necesarios en Firebase
    Solo crea el usuario demo si no existe
    Los códigos se cargan desde archivo JSON
    """
    print("🔥 Inicializando Firebase...")
    codes = load_codes()
    print(f"📋 Códigos disponibles desde JSON: {', '.join(codes.keys())}")
    await init_demo_user()
    print("✅ Firebase inicializado correctamente")
