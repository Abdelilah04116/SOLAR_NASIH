"""
Lanceur simplifié pour test rapide
"""

import sys
import os
import time
import subprocess
import threading
from pathlib import Path

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
os.chdir(root_dir)

def start_infrastructure():
    """Démarre les services d'infrastructure"""
    print("🐳 Démarrage des services Docker...")
    
    try:
        # Redémarrer les conteneurs existants
        subprocess.run(["docker", "start", "rag-qdrant"], capture_output=True)
        subprocess.run(["docker", "start", "rag-redis"], capture_output=True)
        print("✅ Services Docker redémarrés")
        return True
    except Exception as e:
        print(f"⚠️ Erreur Docker: {e}")
        return False

def start_api():
    """Démarre l'API en mode simple"""
    print("⚡ Démarrage de l'API...")
    try:
        # Utiliser la version simplifiée
        subprocess.run([sys.executable, "-m", "uvicorn", "src.api.main_simple:app", 
                       "--host", "0.0.0.0", "--port", "8000", "--reload"])
    except Exception as e:
        print(f"❌ Erreur API: {e}")

def start_frontend():
    """Démarre le frontend"""
    print("🌐 Démarrage du frontend...")
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])
    except Exception as e:
        print(f"❌ Erreur frontend: {e}")

def main():
    print("🚀 RAG Multimodal - Lancement simplifié")
    print("=" * 50)
    
    # Démarrer l'infrastructure
    start_infrastructure()
    time.sleep(5)
    
    # Démarrer l'API dans un thread
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    
    # Attendre l'API
    time.sleep(3)
    
    print("🎉 Système prêt !")
    print("📍 API: http://localhost:8000")
    print("📍 Docs: http://localhost:8000/docs") 
    print("📍 Frontend: http://localhost:8501")
    print("=" * 50)
    
    # Démarrer le frontend
    start_frontend()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système...")