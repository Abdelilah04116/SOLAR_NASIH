#!/usr/bin/env python3
"""
🔨 SOLAR NASIH - Build Script pour Render
Script qui prépare tout le projet pour le déploiement sur Render
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_prerequisites():
    """Vérifie les prérequis"""
    print("🔍 Vérification des prérequis...")
    
    required_dirs = ['SolarNasih_SMA', 'SolarNasih_RAG', 'SolarNasih_Template']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ Erreur: Répertoire {dir_name} non trouvé")
            return False
    
    print("✅ Tous les composants trouvés")
    return True

def install_python_dependencies():
    """Installe les dépendances Python"""
    print("📦 Installation des dépendances Python...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            "SolarNasih_Deploiement_Complet/requirements_unified.txt"
        ], check=True)
        print("✅ Dépendances Python installées")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation Python: {e}")
        return False

def install_node_dependencies():
    """Installe les dépendances Node.js"""
    print("📦 Installation des dépendances Node.js...")
    
    try:
        # Changer vers le répertoire Template
        os.chdir('SolarNasih_Template')
        
        # Installer les dépendances
        subprocess.run(['npm', 'install'], check=True)
        
        # Build du frontend
        print("🔨 Build du frontend...")
        subprocess.run(['npm', 'run', 'build'], check=True)
        
        # Revenir au répertoire racine
        os.chdir('..')
        
        print("✅ Dépendances Node.js installées et frontend buildé")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation Node.js: {e}")
        return False

def create_environment_file():
    """Crée un fichier d'environnement exemple"""
    print("📝 Création du fichier d'environnement...")
    
    env_content = """# ===== SOLAR NASIH - Variables d'Environnement =====

# API Keys
GEMINI_API_KEY=votre_clé_gemini_ici
TAVILY_API_KEY=votre_clé_tavily_ici
OPENAI_API_KEY=votre_clé_openai_ici
ANTHROPIC_API_KEY=votre_clé_anthropic_ici

# Configuration des ports
SMA_PORT=8000
RAG_PORT=8001
FRONTEND_PORT=3000

# Configuration de l'environnement
PYTHON_VERSION=3.11
NODE_VERSION=18
ENVIRONMENT=production

# URLs des services (seront configurées automatiquement sur Render)
SMA_API_URL=https://votre-app-sma.onrender.com
RAG_API_URL=https://votre-app-rag.onrender.com
FRONTEND_URL=https://votre-app-frontend.onrender.com

# Base de données (optionnel)
REDIS_URL=redis://localhost:6379
QDRANT_URL=http://localhost:6333
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    
    print("✅ Fichier .env.example créé")

def create_startup_script():
    """Crée un script de démarrage pour Render"""
    print("🚀 Création du script de démarrage...")
    
    startup_content = """#!/usr/bin/env python3
# Script de démarrage pour Render
# Ce script est appelé automatiquement par Render

import os
import sys
import subprocess

# Ajouter le répertoire de déploiement au path
sys.path.append('SolarNasih_Deploiement_Complet')

# Importer et exécuter le démarrage unifié
from start_all_unified import main

if __name__ == "__main__":
    main()
"""
    
    with open('startup.py', 'w') as f:
        f.write(startup_content)
    
    print("✅ Script startup.py créé")

def create_render_config():
    """Crée la configuration Render"""
    print("☁️ Création de la configuration Render...")
    
    render_config = """services:
  # Service unifié SolarNasih
  - type: web
    name: solar-nasih-unified
    env: python
    buildCommand: python SolarNasih_Deploiement_Complet/build_for_render.py
    startCommand: python startup.py
    envVars:
      - key: GEMINI_API_KEY
        sync: false
      - key: TAVILY_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: PYTHON_VERSION
        value: 3.11
      - key: NODE_VERSION
        value: 18
      - key: ENVIRONMENT
        value: production
      - key: SMA_PORT
        value: 8000
      - key: RAG_PORT
        value: 8001
      - key: FRONTEND_PORT
        value: 3000

  # Service Redis (optionnel)
  - type: redis
    name: solar-nasih-redis
    plan: free
    maxmemoryPolicy: allkeys-lru

  # Service Qdrant (optionnel)
  - type: web
    name: solar-nasih-qdrant
    env: docker
    dockerfilePath: ./SolarNasih_Deploiement_Complet/Dockerfile.qdrant
    envVars:
      - key: QDRANT__SERVICE__HTTP_PORT
        value: 6333
      - key: QDRANT__SERVICE__GRPC_PORT
        value: 6334
"""
    
    with open('render-unified-config.yaml', 'w') as f:
        f.write(render_config)
    
    print("✅ Configuration render-unified-config.yaml créée")

def main():
    """Fonction principale"""
    print("============================================================")
    print("🔨 SOLAR NASIH - Build Script pour Render")
    print("============================================================")
    
    # Vérifier les prérequis
    if not check_prerequisites():
        sys.exit(1)
    
    # Installer les dépendances Python
    if not install_python_dependencies():
        sys.exit(1)
    
    # Installer les dépendances Node.js
    if not install_node_dependencies():
        sys.exit(1)
    
    # Créer les fichiers de configuration
    create_environment_file()
    create_startup_script()
    create_render_config()
    
    print("")
    print("============================================================")
    print("🎉 BUILD TERMINÉ AVEC SUCCÈS !")
    print("============================================================")
    print("")
    print("📁 Fichiers créés:")
    print("   • .env.example - Variables d'environnement")
    print("   • startup.py - Script de démarrage")
    print("   • render-unified-config.yaml - Configuration Render")
    print("")
    print("🚀 Pour déployer sur Render:")
    print("   1. Copiez le contenu de render-unified-config.yaml")
    print("   2. Créez un nouveau Blueprint sur Render")
    print("   3. Configurez vos variables d'environnement")
    print("   4. Cliquez sur 'Apply'")
    print("")
    print("✅ Build prêt pour le déploiement !")
    print("============================================================")

if __name__ == "__main__":
    main()
