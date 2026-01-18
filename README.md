# Fantasy Basket Club 🏀

Sistema de cartas coleccionables y fantasy para engagement de aficionados de baloncesto.

## 📁 Estructura del Proyecto

```
fantasy-basket/
├── backend/              # API FastAPI (Python)
│   ├── main.py          # Servidor principal
│   └── requirements.txt  # Dependencias Python
├── src/                  # Frontend Vue 3
│   ├── components/       # Componentes reutilizables
│   ├── views/           # Vistas/páginas
│   ├── composables/     # Estado global (store)
│   └── services/        # Servicios (API client)
└── dist/                # Build de producción
```

## 🚀 Instalación y Ejecución

### 1. Backend (Python + FastAPI)

```bash
# Entrar en la carpeta del backend
cd backend

# Crear entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar servidor de desarrollo
uvicorn main:app --reload --port 8000
```

El backend estará disponible en: `http://localhost:8000`

Documentación automática de la API: `http://localhost:8000/docs`

### 2. Frontend (Vue 3 + Vite)

```bash
# Volver a la raíz del proyecto
cd ..

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

El frontend estará disponible en: `http://localhost:5173`

## 🔑 Credenciales de Demo

| Usuario | Contraseña |
|---------|------------|
| demo | demo123 |
| jugador1 | pass123 |

## 🎫 Códigos de Demo

- `DEMO2026` - Sobre estándar
- `BASKET24` - Sobre estándar
- `JORNADA15` - Sobre estándar
- `LEGENDARIO` - Sobre especial con mayor probabilidad de legendaria

## 📡 Endpoints de la API

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión

### Usuario
- `GET /api/user/me` - Obtener datos del usuario actual
- `POST /api/user/lineup` - Guardar alineación

### Códigos
- `POST /api/codes/redeem` - Canjear código y obtener cartas

### Rankings
- `GET /api/rankings?period=monthly` - Obtener rankings

### Otros
- `GET /api/players` - Lista de jugadores del club
- `GET /api/codes/valid` - Códigos válidos (solo demo)

## 🗄️ Modelo de Datos

### Usuario
```json
{
  "id": "user_001",
  "username": "demo",
  "email": "demo@fantasybasket.com",
  "cards": ["card_001", "card_002", ...],
  "lineup": ["card_001", "card_002"],
  "points": 1250,
  "rank": 156
}
```

### Carta
```json
{
  "id": "card_001",
  "playerId": 1,
  "name": "Carlos García",
  "number": 7,
  "position": "PG",
  "positionFull": "Base",
  "photo": "https://...",
  "rarity": "rare",
  "bonus": {
    "condition": "Si mete 2+ triples",
    "effect": "Puntos x1.5",
    "multiplier": 1.5
  }
}
```

## 🎨 Sistema de Raridades

| Rareza | Probabilidad | Multiplicador |
|--------|--------------|---------------|
| Común | 60% | x1 (sin bonus) |
| Rara | 25% | x1.5 |
| Épica | 12% | x2 |
| Legendaria | 3% | x3 |

## 📱 Características

- ✅ Cartas 3D con efecto holográfico
- ✅ Animación de apertura de sobres
- ✅ Efecto de partículas para legendarias
- ✅ Sistema de autenticación
- ✅ Colección de cartas
- ✅ Alineación de equipo
- ✅ Rankings (semanal, mensual, temporada)
- ✅ Canjeo de códigos

## 🔧 Configuración de Producción

### Variables de entorno del Frontend

Crear archivo `.env`:
```env
VITE_API_URL=https://tu-api.com
```

### Build de producción

```bash
# Frontend
npm run build

# El resultado estará en /dist
```

## 📝 Próximos Pasos

1. **Base de datos real**: Migrar de datos hardcodeados a MongoDB/PostgreSQL
2. **JWT**: Implementar autenticación con tokens JWT
3. **Estadísticas reales**: Integración con sistema de stats de la liga
4. **Push notifications**: Alertas de partidos y códigos
5. **PWA**: Convertir en Progressive Web App

## 📄 Licencia

Proyecto privado - Todos los derechos reservados.
