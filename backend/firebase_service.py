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
# Solo una colección: users. No se guardan sesiones ni códigos en Firestore.

# =============================================================================
# POOL DE IDS DE CARTAS
# El backend NO genera cartas, solo asigna IDs del catálogo del frontend
# =============================================================================

CARD_ID_POOLS = {
    "common": [
        "card_001", "card_005", "card_009", "card_013", "card_017", "card_021"
    ],
    "rare": [
        "card_002", "card_006", "card_010", "card_014", "card_018", "card_022"
    ],
    "epic": [
        "card_003", "card_007", "card_011", "card_015", "card_019", "card_023"
    ],
    "legendary": [
        "card_004", "card_008", "card_012", "card_016", "card_020", "card_024"
    ]
}

# Pool de cartas por posición (para pack de bienvenida)
# Incluye todas las variantes de cada jugador
CARDS_BY_POSITION = {
    "Base": ["card_001", "card_002", "card_003", "card_004", "card_021", "card_022", "card_023", "card_024"],
    "Escolta": ["card_005", "card_006", "card_007", "card_008"],
    "Alero": ["card_009", "card_010", "card_011", "card_012"],
    "Ala-Pívot": ["card_013", "card_014", "card_015", "card_016"],
    "Pívot": ["card_017", "card_018", "card_019", "card_020"]
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

async def update_user_lineup(user_id: str, lineup_ids: List[str]) -> bool:
    """
    Actualiza la alineación del usuario (SOLO IDs)
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
