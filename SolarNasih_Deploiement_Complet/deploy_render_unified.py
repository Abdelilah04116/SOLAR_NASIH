#!/usr/bin/env python3
"""
🚀 SOLAR NASIH - Déploiement Unifié sur Render
Script pour déployer tous les composants avec une seule commande
"""

import os
import sys
import subprocess
import yaml
from pathlib import Path

def create_unified_render_config():
    """Crée la configuration unifiée pour Render"""
    
    config = {
        'services': [
            # Service SMA
            {
                'type': 'web',
                'name': 'solar-nasih-sma',
                'env': 'python',
                'buildCommand': 'pip install -r SolarNasih_Deploiement_Complet/requirements_sma.txt',
                'startCommand': 'cd SolarNasih_SMA && uvicorn main:app --host 0.0.0.0 --port $PORT',
                'envVars': [
                    {'key': 'GEMINI_API_KEY', 'sync': False},
                    {'key': 'TAVILY_API_KEY', 'sync': False},
                    {'key': 'PYTHON_VERSION', 'value': '3.11'},
                    {'key': 'ENVIRONMENT', 'value': 'production'},
                    {'key': 'REDIS_URL', 'fromService': {'type': 'redis', 'name': 'solar-nasih-redis', 'property': 'connectionString'}}
                ]
            },
            # Service RAG
            {
                'type': 'web',
                'name': 'solar-nasih-rag',
                'env': 'python',
                'buildCommand': 'pip install -r SolarNasih_Deploiement_Complet/requirements_rag.txt',
                'startCommand': 'cd SolarNasih_RAG && uvicorn api_simple:app --host 0.0.0.0 --port $PORT',
                'envVars': [
                    {'key': 'GEMINI_API_KEY', 'sync': False},
                    {'key': 'OPENAI_API_KEY', 'sync': False},
                    {'key': 'ANTHROPIC_API_KEY', 'sync': False},
                    {'key': 'PYTHON_VERSION', 'value': '3.11'},
                    {'key': 'ENVIRONMENT', 'value': 'production'},
                    {'key': 'QDRANT_URL', 'fromService': {'type': 'web', 'name': 'solar-nasih-qdrant', 'property': 'url'}},
                    {'key': 'REDIS_URL', 'fromService': {'type': 'redis', 'name': 'solar-nasih-redis', 'property': 'connectionString'}}
                ]
            },
            # Service Frontend
            {
                'type': 'web',
                'name': 'solar-nasih-frontend',
                'env': 'node',
                'buildCommand': 'cd SolarNasih_Template && npm install && npm run build',
                'startCommand': 'cd SolarNasih_Template && npm run preview -- --host 0.0.0.0 --port $PORT',
                'envVars': [
                    {'key': 'NODE_VERSION', 'value': '18'},
                    {'key': 'NODE_ENV', 'value': 'production'},
                    {'key': 'VITE_SMA_API_URL', 'fromService': {'type': 'web', 'name': 'solar-nasih-sma', 'property': 'url'}},
                    {'key': 'VITE_RAG_API_URL', 'fromService': {'type': 'web', 'name': 'solar-nasih-rag', 'property': 'url'}}
                ]
            },
            # Service Redis
            {
                'type': 'redis',
                'name': 'solar-nasih-redis',
                'plan': 'free',
                'maxmemoryPolicy': 'allkeys-lru'
            },
            # Service Qdrant
            {
                'type': 'web',
                'name': 'solar-nasih-qdrant',
                'env': 'docker',
                'dockerfilePath': './SolarNasih_Deploiement_Complet/Dockerfile.qdrant',
                'envVars': [
                    {'key': 'QDRANT__SERVICE__HTTP_PORT', 'value': '6333'},
                    {'key': 'QDRANT__SERVICE__GRPC_PORT', 'value': '6334'}
                ]
            }
        ]
    }
    
    # Sauvegarder la configuration
    with open('render-unified.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    return config

def create_unified_deploy_script():
    """Crée le script de déploiement unifié"""
    
    script_content = '''#!/bin/bash
# 🚀 SOLAR NASIH - Script de Déploiement Unifié
# Ce script déploie tous les composants sur Render

set -e

echo "============================================================"
echo "🚀 SOLAR NASIH - Déploiement Unifié"
echo "============================================================"

# Vérification des prérequis
echo "🔍 Vérification des prérequis..."

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "SolarNasih_SMA" ] || [ ! -d "SolarNasih_RAG" ] || [ ! -d "SolarNasih_Template" ]; then
    echo "❌ Erreur: Composants manquants"
    echo "   Assurez-vous d'être dans le répertoire racine du projet"
    exit 1
fi

echo "✅ Tous les composants trouvés"

# Créer la configuration Render
echo "📝 Création de la configuration Render..."
python SolarNasih_Deploiement_Complet/deploy_render_unified.py

echo "✅ Configuration créée: render-unified.yaml"

# Instructions pour l'utilisateur
echo ""
echo "============================================================"
echo "🎯 PROCHAINES ÉTAPES POUR RENDER:"
echo "============================================================"
echo ""
echo "1. 🌐 Allez sur https://render.com"
echo "2. 🔗 Connectez votre repository Git"
echo "3. 📋 Créez un nouveau Blueprint"
echo "4. 📄 Copiez le contenu de render-unified.yaml"
echo "5. 🔑 Configurez vos variables d'environnement:"
echo "   - GEMINI_API_KEY"
echo "   - TAVILY_API_KEY"
echo "   - OPENAI_API_KEY"
echo "   - ANTHROPIC_API_KEY"
echo "6. 🚀 Cliquez sur 'Apply' pour déployer"
echo ""
echo "📊 Services qui seront créés:"
echo "   • solar-nasih-sma (API SMA)"
echo "   • solar-nasih-rag (API RAG)"
echo "   • solar-nasih-frontend (Interface)"
echo "   • solar-nasih-redis (Cache)"
echo "   • solar-nasih-qdrant (Base vectorielle)"
echo ""
echo "✅ Déploiement unifié prêt !"
echo "============================================================"
'''

    with open('deploy-unified.sh', 'w') as f:
        f.write(script_content)
    
    # Rendre le script exécutable (pour Unix/Linux)
    try:
        os.chmod('deploy-unified.sh', 0o755)
    except:
        pass

def create_single_command_deploy():
    """Crée un script pour une seule commande de déploiement"""
    
    # Script PowerShell pour Windows
    powershell_script = '''# 🚀 SOLAR NASIH - Déploiement Unifié (PowerShell)
# Exécutez ce script pour déployer tout le projet

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🚀 SOLAR NASIH - Déploiement Unifié" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan

# Vérification des prérequis
Write-Host "🔍 Vérification des prérequis..." -ForegroundColor Yellow

if (-not (Test-Path "SolarNasih_SMA") -or -not (Test-Path "SolarNasih_RAG") -or -not (Test-Path "SolarNasih_Template")) {
    Write-Host "❌ Erreur: Composants manquants" -ForegroundColor Red
    Write-Host "   Assurez-vous d'être dans le répertoire racine du projet" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Tous les composants trouvés" -ForegroundColor Green

# Créer la configuration Render
Write-Host "📝 Création de la configuration Render..." -ForegroundColor Yellow
python SolarNasih_Deploiement_Complet/deploy_render_unified.py

Write-Host "✅ Configuration créée: render-unified.yaml" -ForegroundColor Green

# Afficher les instructions
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "🎯 PROCHAINES ÉTAPES POUR RENDER:" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. 🌐 Allez sur https://render.com" -ForegroundColor White
Write-Host "2. 🔗 Connectez votre repository Git" -ForegroundColor White
Write-Host "3. 📋 Créez un nouveau Blueprint" -ForegroundColor White
Write-Host "4. 📄 Copiez le contenu de render-unified.yaml" -ForegroundColor White
Write-Host "5. 🔑 Configurez vos variables d'environnement:" -ForegroundColor White
Write-Host "   - GEMINI_API_KEY" -ForegroundColor Gray
Write-Host "   - TAVILY_API_KEY" -ForegroundColor Gray
Write-Host "   - OPENAI_API_KEY" -ForegroundColor Gray
Write-Host "   - ANTHROPIC_API_KEY" -ForegroundColor Gray
Write-Host "6. 🚀 Cliquez sur 'Apply' pour déployer" -ForegroundColor White
Write-Host ""
Write-Host "📊 Services qui seront créés:" -ForegroundColor Green
Write-Host "   • solar-nasih-sma (API SMA)" -ForegroundColor White
Write-Host "   • solar-nasih-rag (API RAG)" -ForegroundColor White
Write-Host "   • solar-nasih-frontend (Interface)" -ForegroundColor White
Write-Host "   • solar-nasih-redis (Cache)" -ForegroundColor White
Write-Host "   • solar-nasih-qdrant (Base vectorielle)" -ForegroundColor White
Write-Host ""
Write-Host "✅ Déploiement unifié prêt !" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
'''

    with open('deploy-unified.ps1', 'w') as f:
        f.write(powershell_script)

def main():
    """Fonction principale"""
    
    print("============================================================")
    print("🚀 SOLAR NASIH - Configuration de Déploiement Unifié")
    print("============================================================")
    
    # Vérifier les prérequis
    required_dirs = ['SolarNasih_SMA', 'SolarNasih_RAG', 'SolarNasih_Template']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ Erreur: Répertoire {dir_name} non trouvé")
            print("   Assurez-vous d'être dans le répertoire racine du projet")
            sys.exit(1)
    
    print("✅ Tous les composants trouvés")
    
    # Créer les fichiers de déploiement
    print("📝 Création des fichiers de déploiement...")
    
    # Configuration Render
    create_unified_render_config()
    print("✅ render-unified.yaml créé")
    
    # Scripts de déploiement
    create_unified_deploy_script()
    print("✅ deploy-unified.sh créé")
    
    create_single_command_deploy()
    print("✅ deploy-unified.ps1 créé")
    
    print("")
    print("============================================================")
    print("🎯 UTILISATION:")
    print("============================================================")
    print("")
    print("Sur Windows (PowerShell):")
    print("   .\\deploy-unified.ps1")
    print("")
    print("Sur Linux/Mac (Bash):")
    print("   ./deploy-unified.sh")
    print("")
    print("Ou directement:")
    print("   python SolarNasih_Deploiement_Complet/deploy_render_unified.py")
    print("")
    print("✅ Configuration terminée !")
    print("============================================================")

if __name__ == "__main__":
    main()
