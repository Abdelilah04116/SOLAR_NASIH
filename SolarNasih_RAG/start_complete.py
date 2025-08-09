#!/usr/bin/env python3
"""
Script de démarrage complet pour RAG
Lance l'API FastAPI et l'interface Streamlit
"""
import os
import subprocess
import sys
import time
import signal
from pathlib import Path

def start_api():
    """Démarre l'API FastAPI complète"""
    print("🚀 Démarrage de l'API RAG complète...")
    
    # Configuration du PYTHONPATH pour les imports
    os.environ["PYTHONPATH"] = str(Path.cwd())
    
    api_cmd = [
        sys.executable, "-m", "uvicorn", 
        "src.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", os.getenv("PORT", "8000"),
        "--reload", "False"
    ]
    return subprocess.Popen(api_cmd)

def start_frontend():
    """Démarre l'interface Streamlit"""
    print("🌐 Démarrage de l'interface RAG...")
    
    # Configuration Streamlit pour Render
    streamlit_port = "8501"
    frontend_cmd = [
        sys.executable, "-m", "streamlit", "run", 
        "frontend_simple.py",
        "--server.port", streamlit_port,
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--server.enableCORS", "false",
        "--server.enableXsrfProtection", "false"
    ]
    
    # Mettre à jour l'URL de l'API dans l'interface
    update_api_url()
    
    return subprocess.Popen(frontend_cmd)

def update_api_url():
    """Met à jour l'URL de l'API dans l'interface"""
    frontend_file = Path("frontend_simple.py")
    if frontend_file.exists():
        content = frontend_file.read_text()
        # Remplacer localhost par l'URL courante
        render_url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000")
        api_url = render_url.replace("https://", "http://") if render_url.startswith("https://") else render_url
        
        # Mettre à jour l'URL dans le fichier
        content = content.replace(
            'API_BASE_URL = "http://localhost:8000"',
            f'API_BASE_URL = "{api_url}"'
        )
        frontend_file.write_text(content)
        print(f"✅ API URL mise à jour: {api_url}")

def main():
    """Fonction principale"""
    print("🔍 Solar Nasih RAG - Démarrage complet")
    print("=" * 50)
    
    # Variables d'environnement
    os.environ.setdefault("PYTHONPATH", "/opt/render/project/src")
    
    processes = []
    
    try:
        # Démarrer l'API
        api_process = start_api()
        processes.append(api_process)
        
        # Attendre que l'API démarre
        time.sleep(5)
        
        # Démarrer l'interface
        frontend_process = start_frontend()
        processes.append(frontend_process)
        
        print("✅ Services démarrés:")
        print(f"   📡 API: http://0.0.0.0:{os.getenv('PORT', '8000')}")
        print(f"   🌐 Interface: http://0.0.0.0:8501")
        print("   📚 Documentation: /docs")
        
        # Attendre les processus
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt des services...")
        for process in processes:
            process.terminate()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        for process in processes:
            process.terminate()
        sys.exit(1)

if __name__ == "__main__":
    main()
