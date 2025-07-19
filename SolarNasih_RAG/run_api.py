"""
Script de lancement simplifié pour l'API
"""

import sys
import os
import uvicorn
from pathlib import Path

# Configuration du chemin
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))
os.chdir(root_dir)

if __name__ == "__main__":
    print("🚀 Lancement de l'API RAG Multimodal (version simplifiée)...")
    
    # Lancer directement avec uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )