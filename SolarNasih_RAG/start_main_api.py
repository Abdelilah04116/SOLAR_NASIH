#!/usr/bin/env python3
"""
Script de démarrage pour l'API principale RAG
Lance uniquement l'API complète de src/api/main.py
"""
import os
import sys
import uvicorn
from pathlib import Path

def main():
    """Démarre l'API principale"""
    print("🚀 Solar Nasih RAG - API Principale")
    print("=" * 50)
    
    # Configuration du PYTHONPATH
    root_path = Path(__file__).parent
    os.environ["PYTHONPATH"] = str(root_path)
    sys.path.insert(0, str(root_path))
    
    # Configuration des variables d'environnement
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"📡 Démarrage de l'API sur {host}:{port}")
    print(f"🔧 PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"🌍 Environnement: {os.getenv('ENVIRONMENT', 'development')}")
    
    # Configuration uvicorn
    config = {
        "app": "src.api.main:app",
        "host": host,
        "port": port,
        "reload": False,
        "workers": 1,
        "log_level": "info",
        "access_log": True
    }
    
    try:
        uvicorn.run(**config)
    except Exception as e:
        print(f"❌ Erreur de démarrage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
