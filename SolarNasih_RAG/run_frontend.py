"""
Script de lancement pour le frontend Streamlit
Placez ce fichier à la racine du projet
"""

import sys
import os
import subprocess
from pathlib import Path

# Ajouter le dossier racine au PYTHONPATH
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# S'assurer que nous sommes dans le bon répertoire
os.chdir(root_dir)

if __name__ == "__main__":
    print("🌐 Lancement du frontend Streamlit...")
    print("📍 URL: http://localhost:8501")
    
    # Lancer Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/app.py",
        "--server.port=8501",
        "--server.address=0.0.0.0"
    ])