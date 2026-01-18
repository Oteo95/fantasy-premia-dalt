"""
Fantasy Basket Club - Backend API con Firebase
ARQUITECTURA DE IDS + Firestore

PRINCIPIO FUNDAMENTAL:
- El backend SOLO almacena y devuelve IDs de cartas
- El frontend contiene el catálogo completo en el bundle
- Transferencia mínima: ~200 bytes en login, ~100 bytes en canjeo
- Máximo 1 query por request
- Datos persistentes en Firestore
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from typing import Optional
import secrets
import random
from datetime import datetime
from google.cloud import firestore

# Importar servicios de Firebase
import firebase_service as fb

app = FastAPI(
    title="Fantasy Basket Club API",
    description="API para el sistema de cartas coleccionables de Fantasy Basket con Firebase",
    version="2.0.0"
)

# CORS para permitir llamadas desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar el dominio del frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBasic()

# =============================================================================
# MODELOS PYDANTIC
# =============================================================================

class LoginRequest(BaseModel):
    username: str
    password: str

class SignUpRequest(BaseModel):
    username: str
    email: str
    password: str

class LoginResponse(BaseModel):
    token: str
    user: dict

class RedeemCodeRequest(BaseModel):
    code: str

class RedeemCodeResponse(BaseModel):
    success: bool
    message: str
    packType: str

class OpenPackRequest(BaseModel):
    packIndex: int

class OpenPackResponse(BaseModel):
    success: bool
    message: str
    newCardIds: list[str]
    packType: str

class SaveLineupRequest(BaseModel):
    lineup: dict[str, str]  # Cambiado de list a dict

# =============================================================================
# FUNCIONES AUXILIARES
# =============================================================================

def generate_token() -> str:
    """Genera un token de sesión aleatorio"""
    return secrets.token_hex(32)

async def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> dict:
    """Obtiene el usuario actual a partir del token en el header"""
    token = credentials.password
    
    # Buscar sesión en memoria (no async)
    session = fb.get_session(token)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Basic"},
        )
    
    # Obtener usuario de Firestore
    user = await fb.get_user_by_id(session["userId"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    
    return user

def generate_pack_ids(pack_type: str = "standard") -> list[str]:
    """
    Genera un sobre de cartas del pool
    NO devuelve datos completos, solo IDs
    
    - welcome: 5 cartas (una por posición)
    - standard: 2 cartas aleatorias
    - legendary: 3 cartas especiales
    """
    card_ids = []
    
    if pack_type == "welcome":
        # Pack de bienvenida: 5 cartas, una de cada posición (aleatorias)
        card_ids.append(random.choice(fb.CARDS_BY_POSITION["Base"]))
        card_ids.append(random.choice(fb.CARDS_BY_POSITION["Escolta"]))
        card_ids.append(random.choice(fb.CARDS_BY_POSITION["Alero"]))
        card_ids.append(random.choice(fb.CARDS_BY_POSITION["Ala-Pívot"]))
        card_ids.append(random.choice(fb.CARDS_BY_POSITION["Pívot"]))
    elif pack_type == "legendary":
        # Pack legendario: 3 cartas especiales
        card_ids.append(random.choice(fb.CARD_ID_POOLS["common"] + fb.CARD_ID_POOLS["rare"]))
        card_ids.append(random.choice(fb.CARD_ID_POOLS["epic"] + fb.CARD_ID_POOLS["legendary"]))
        card_ids.append(random.choice(fb.CARD_ID_POOLS["legendary"]))
    else:
        # Pack estándar: 2 cartas aleatorias
        # Primera carta
        roll1 = random.random() * 100
        if roll1 < 60:
            card_ids.append(random.choice(fb.CARD_ID_POOLS["common"]))
        elif roll1 < 85:
            card_ids.append(random.choice(fb.CARD_ID_POOLS["rare"]))
        elif roll1 < 97:
            card_ids.append(random.choice(fb.CARD_ID_POOLS["epic"]))
        else:
            card_ids.append(random.choice(fb.CARD_ID_POOLS["legendary"]))
        
        # Segunda carta
        roll2 = random.random() * 100
        if roll2 < 60:
            card_ids.append(random.choice(fb.CARD_ID_POOLS["common"]))
        elif roll2 < 85:
            card_ids.append(random.choice(fb.CARD_ID_POOLS["rare"]))
        elif roll2 < 97:
            card_ids.append(random.choice(fb.CARD_ID_POOLS["epic"]))
        else:
            card_ids.append(random.choice(fb.CARD_ID_POOLS["legendary"]))
    
    return card_ids

# =============================================================================
# EVENTOS DE INICIO
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Inicializa Firebase al arrancar"""
    await fb.initialize_firebase()

# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "message": "Fantasy Basket Club API v2.0 - Firebase + Arquitectura de IDs",
        "firebase": "✅ Conectado"
    }

# -----------------------------------------------------------------------------
# AUTENTICACIÓN
# -----------------------------------------------------------------------------

@app.post("/api/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Inicia sesión con email o username + password
    Soporta login con Firebase Authentication
    
    ARQUITECTURA: El backend devuelve SOLO IDs (~200 bytes)
    El frontend expande los IDs usando su catálogo local
    1 query a Firestore por request
    """
    # Intentar buscar por email si contiene @, sino por username
    if '@' in request.username:
        # Es un email
        user = await fb.get_user_by_email(request.username)
    else:
        # Es un username
        user = await fb.get_user_by_username(request.username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email/Usuario o contraseña incorrectos"
        )
    
    # Verificar si tiene campo authUid (usuario con Firebase Auth)
    if user.get("authUid"):
        # Usuario creado con Firebase Authentication
        # Verificar que existe en Firebase Auth
        try:
            firebase_user = await fb.verify_user_login(user.get("email"), request.password)
            if not firebase_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Usuario o contraseña incorrectos"
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
    else:
        # Usuario antiguo sin Firebase Auth (demo user)
        if user.get("password") != request.password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario o contraseña incorrectos"
            )
    
    # Generar token de sesión en memoria (no async)
    token = generate_token()
    fb.create_session(user["_id"], token)
    
    # Construir respuesta: SOLO IDs, NO datos completos
    # Transferencia: ~200 bytes
    user_data = {
        "id": user["_id"],
        "username": user["username"],
        "cardIds": user.get("cardIds", []),  # SOLO IDs
        "lineupIds": user.get("lineupIds", []),  # SOLO IDs
        "unopenedPacks": user.get("unopenedPacks", []),  # Sobres sin abrir
        "points": user.get("points", 0),
        "rank": user.get("rank", 0)
    }
    
    return LoginResponse(token=token, user=user_data)

@app.post("/api/auth/signup", response_model=LoginResponse)
async def signup(request: SignUpRequest):
    """
    Registra un nuevo usuario y lo loguea automáticamente
    
    ARQUITECTURA: El backend devuelve SOLO IDs (~200 bytes)
    Crea el usuario en Firebase Authentication + Firestore con cartas iniciales
    """
    print(f"📝 Intento de registro: username={request.username}, email={request.email}")
    
    # Crear usuario en Firebase Auth + Firestore
    try:
        new_user = await fb.create_user(
            request.username,
            request.password,
            request.email
        )
        print(f"✅ Usuario creado exitosamente: {new_user['_id']}")
    except Exception as e:
        print(f"❌ Error en signup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Generar token de sesión en memoria (no async)
    token = generate_token()
    fb.create_session(new_user["_id"], token)
    
    # Construir respuesta: SOLO IDs, NO datos completos
    user_data = {
        "id": new_user["_id"],
        "username": new_user["username"],
        "cardIds": new_user.get("cardIds", []),
        "lineupIds": new_user.get("lineupIds", []),
        "unopenedPacks": new_user.get("unopenedPacks", []),  # Sobres sin abrir
        "points": new_user.get("points", 0),
        "rank": new_user.get("rank", 0)
    }
    
    return LoginResponse(token=token, user=user_data)

@app.post("/api/auth/logout")
async def logout(user: dict = Depends(get_current_user)):
    """Cierra la sesión del usuario"""
    # Aquí habría que obtener el token del header para eliminarlo
    # Por simplicidad, retornamos success
    return {"success": True, "message": "Sesión cerrada"}

# -----------------------------------------------------------------------------
# USUARIO
# -----------------------------------------------------------------------------

@app.get("/api/user/me")
async def get_current_user_data(user: dict = Depends(get_current_user)):
    """
    Obtiene los datos del usuario actual - SOLO IDs
    El frontend expande los IDs con su catálogo local
    """
    return {
        "id": user["_id"],
        "username": user["username"],
        "cardIds": user.get("cardIds", []),
        "lineupIds": user.get("lineupIds", []),
        "unopenedPacks": user.get("unopenedPacks", []),  # Sobres sin abrir
        "points": user.get("points", 0),
        "rank": user.get("rank", 0)
    }

@app.post("/api/user/lineup")
async def save_lineup(request: SaveLineupRequest, user: dict = Depends(get_current_user)):
    """
    Guarda la alineación del usuario como diccionario
    Recibe y devuelve diccionario con keys de posición
    1 query a Firestore
    """
    # Validar posiciones válidas
    valid_positions = ["base", "escolta", "alero", "alaPivot", "pivot"]
    for position in request.lineup.keys():
        if position not in valid_positions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Posición inválida: {position}"
            )
    
    # Validar que todas las cartas pertenecen al usuario
    user_card_ids = user.get("cardIds", [])
    for card_id in request.lineup.values():
        if card_id and card_id not in user_card_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La carta {card_id} no pertenece al usuario"
            )
    
    # Validar máximo 5 posiciones
    if len(request.lineup) > 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La alineación no puede tener más de 5 posiciones"
        )
    
    # Guardar alineación en Firestore (diccionario con keys de posición)
    await fb.update_user_lineup(user["_id"], request.lineup)
    
    return {
        "success": True,
        "message": "Alineación guardada"
    }

# -----------------------------------------------------------------------------
# CÓDIGOS Y SOBRES
# -----------------------------------------------------------------------------

@app.post("/api/codes/redeem", response_model=RedeemCodeResponse)
async def redeem_code(request: RedeemCodeRequest, user: dict = Depends(get_current_user)):
    """
    Canjea un código y añade un sobre sin abrir al inventario del usuario
    
    ARQUITECTURA: El backend añade un sobre al inventario
    El usuario debe abrir el sobre para obtener las cartas
    1 query a Firestore
    """
    code = request.code.upper()
    
    # Verificar que el código existe en memoria (no async)
    code_data = fb.get_code(code)
    
    if not code_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código inválido"
        )
    
    # Verificar que no haya expirado
    if code_data.get("validUntil") and datetime.now() > code_data["validUntil"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este código ha expirado"
        )
    
    # Verificar que el usuario no haya canjeado este código antes
    redeemed_codes = user.get("redeemedCodes", [])
    if code in redeemed_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya has canjeado este código"
        )
    
    # Obtener tipo de sobre
    pack_type = code_data.get("packType", "standard")
    
    # Añadir sobre sin abrir al inventario del usuario
    await fb.add_unopened_pack(user["_id"], pack_type)
    
    # Marcar código como canjeado
    await fb.add_redeemed_code(user["_id"], code)
    
    # Mensaje según el tipo de sobre
    pack_messages = {
        "welcome": "¡Código canjeado! Has recibido un sobre de bienvenida (5 cartas)",
        "standard": "¡Código canjeado! Has recibido un sobre estándar (2 cartas)",
        "legendary": "¡Código canjeado! Has recibido un sobre legendario (3 cartas)"
    }
    
    return RedeemCodeResponse(
        success=True,
        message=pack_messages.get(pack_type, "¡Código canjeado! Has recibido un sobre"),
        packType=pack_type
    )

@app.post("/api/packs/open", response_model=OpenPackResponse)
async def open_pack(request: OpenPackRequest, user: dict = Depends(get_current_user)):
    """
    Abre un sobre del inventario y devuelve las cartas obtenidas
    
    ARQUITECTURA: El backend genera IDs del pool y los añade a la colección del usuario
    1-2 queries a Firestore
    """
    unopened_packs = user.get("unopenedPacks", [])
    
    # Validar que el índice es válido
    if request.packIndex < 0 or request.packIndex >= len(unopened_packs):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Índice de sobre inválido"
        )
    
    # Obtener el tipo de sobre
    pack = unopened_packs[request.packIndex]
    pack_type = pack.get("type", "standard")
    
    # Generar cartas según el tipo de sobre
    new_card_ids = generate_pack_ids(pack_type)
    
    # Añadir cartas a la colección del usuario
    current_card_ids = user.get("cardIds", [])
    updated_card_ids = current_card_ids + new_card_ids
    await fb.update_user_cards(user["_id"], updated_card_ids)
    
    # Remover el sobre del inventario
    await fb.remove_unopened_pack(user["_id"], request.packIndex)
    
    # Mensaje según el tipo de sobre
    pack_names = {
        "welcome": "sobre de bienvenida",
        "standard": "sobre estándar",
        "legendary": "sobre legendario"
    }
    
    return OpenPackResponse(
        success=True,
        message=f"¡Has abierto un {pack_names.get(pack_type, 'sobre')}!",
        newCardIds=new_card_ids,
        packType=pack_type
    )

# -----------------------------------------------------------------------------
# RANKINGS
# -----------------------------------------------------------------------------

@app.get("/api/rankings")
async def get_rankings(period: str = "monthly"):
    """
    Obtiene el ranking de jugadores desde Firestore
    period: 'weekly', 'monthly', 'season'
    """
    # Obtener todos los usuarios ordenados por puntos (descendente)
    users_ref = fb.db.collection(fb.USERS_COLLECTION)
    query = users_ref.order_by("points", direction=firestore.Query.DESCENDING).limit(10)
    
    rankings = []
    rank = 1
    for doc in query.stream():
        user_data = doc.to_dict()
        rankings.append({
            "rank": rank,
            "username": user_data.get("username", "Usuario"),
            "points": user_data.get("points", 0)
        })
        rank += 1
    
    return {
        "period": period,
        "rankings": rankings
    }

# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
