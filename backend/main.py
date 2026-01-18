"""
Fantasy Basket Club - Backend API Principal
Este archivo usa la implementación con Firebase Authentication + Firestore

Para ejecutar: python backend/main.py
"""

# Importar la app de main_firebase que tiene toda la lógica con Firebase
from main_firebase import app

# Este archivo sirve como punto de entrada principal
# Toda la lógica está en main_firebase.py

if __name__ == "__main__":
    import uvicorn
    print("🚀 Iniciando Fantasy Basket API con Firebase...")
    print("📍 Servidor corriendo en: http://localhost:8000")
    print("📖 Documentación: http://localhost:8000/docs")
    print("🔥 Usando Firebase Authentication + Firestore")
    uvicorn.run(app, host="0.0.0.0", port=8000)
