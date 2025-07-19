"""
Script de démarrage rapide - vérifie tout et lance l'application
"""

import sys
import os
import subprocess
from pathlib import Path

def check_requirements():
    """Vérifie les prérequis"""
    print("🔍 Vérification des prérequis...")
    
    # Vérifier Python
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ requis")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Vérifier l'environnement virtuel
    if not (Path("venv").exists() or Path(".venv").exists()):
        print("❌ Environnement virtuel non trouvé")
        print("Exécutez: python -m venv venv")
        return False
    print("✅ Environnement virtuel trouvé")
    
    # Vérifier .env
    if not Path(".env").exists():
        print("⚠️ Fichier .env non trouvé, copie depuis .env.example")
        if Path(".env.example").exists():
            import shutil
            shutil.copy(".env.example", ".env")
            print("📝 Veuillez éditer .env avec vos clés API")
        else:
            print("❌ .env.example non trouvé")
            return False
    print("✅ Fichier .env trouvé")
    
    return True

def main():
    """Point d'entrée principal"""
    print("🚀 RAG Multimodal - Démarrage rapide")
    print("=" * 40)
    
    if not check_requirements():
        print("\n❌ Prérequis non satisfaits")
        return 1
    
    print("\n🎯 Lancement de l'application...")
    
    # Lancer le script principal
    try:
        subprocess.run([sys.executable, "start.py"], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé par l'utilisateur")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erreur lors du lancement: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())