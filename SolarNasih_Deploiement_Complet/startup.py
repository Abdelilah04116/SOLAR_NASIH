#!/usr/bin/env python3
"""
🚀 SOLAR NASIH - Script de Démarrage pour Render
Ce script démarre le serveur principal qui écoute sur le port de Render
"""

import os
import sys
import subprocess
import threading
import time

# Ajouter le répertoire de déploiement au path
sys.path.append('SolarNasih_Deploiement_Complet')

def start_background_services():
    """Démarre les services SMA, RAG et Frontend en arrière-plan"""
    print("🚀 Démarrage des services en arrière-plan...")
    
    # Démarrer SMA
    def start_sma():
        os.chdir('SolarNasih_SMA')
        subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"])
        os.chdir('..')
    
    # Démarrer RAG
    def start_rag():
        os.chdir('SolarNasih_RAG')
        subprocess.Popen([sys.executable, "-m", "uvicorn", "api_simple:app", "--host", "0.0.0.0", "--port", "8001"])
        os.chdir('..')
    
    # Démarrer Frontend
    def start_frontend():
        os.chdir('SolarNasih_Template')
        if not os.path.exists('node_modules'):
            subprocess.run(['npm', 'install'], check=True)
        subprocess.Popen(['npm', 'run', 'preview', '--', '--host', '0.0.0.0', '--port', '3000'])
        os.chdir('..')
    
    # Démarrer les services en parallèle
    threading.Thread(target=start_sma, daemon=True).start()
    time.sleep(2)
    threading.Thread(target=start_rag, daemon=True).start()
    time.sleep(2)
    threading.Thread(target=start_frontend, daemon=True).start()

if __name__ == "__main__":
    # Démarrer les services en arrière-plan
    start_background_services()
    
    # Attendre un peu que les services démarrent
    time.sleep(5)
    
    # Importer et démarrer le serveur principal
    from render_main import app
    import uvicorn
    
    port = int(os.getenv('PORT', '10000'))
    print(f"🎉 Démarrage du serveur principal sur le port {port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)
