#!/usr/bin/env python3
"""
Script de déploiement automatique pour Solar Nasih Complet sur Render
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def print_banner():
    """Affiche la bannière du script"""
    print("=" * 60)
    print("🚀 SOLAR NASIH - Déploiement Complet Automatique")
    print("=" * 60)
    print("Ce script va vous aider à déployer tous les composants :")
    print("• SMA (Solar Management Assistant)")
    print("• RAG (Retrieval-Augmented Generation)")
    print("• Frontend (React/TypeScript)")
    print("=" * 60)

def check_requirements():
    """Vérifie les prérequis"""
    print("🔍 Vérification des prérequis...")
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("SolarNasih_SMA").exists():
        print("❌ Erreur: Répertoire SolarNasih_SMA non trouvé")
        print("   Assurez-vous d'être dans le répertoire racine du projet")
        return False
    
    if not Path("SolarNasih_RAG").exists():
        print("❌ Erreur: Répertoire SolarNasih_RAG non trouvé")
        return False
    
    if not Path("SolarNasih_Template").exists():
        print("❌ Erreur: Répertoire SolarNasih_Template non trouvé")
        return False
    
    print("✅ Tous les composants trouvés")
    return True

def create_env_file():
    """Crée le fichier .env à partir du template"""
    print("📝 Création du fichier .env...")
    
    env_example = Path("SolarNasih_Deploiement_Complet/env.example")
    env_file = Path(".env")
    
    if env_example.exists():
        if not env_file.exists():
            subprocess.run(["cp", str(env_example), str(env_file)])
            print("✅ Fichier .env créé à partir du template")
            print("⚠️  N'oubliez pas de configurer vos clés API dans .env")
        else:
            print("ℹ️  Fichier .env existe déjà")
    else:
        print("❌ Fichier env.example non trouvé")

def generate_render_config():
    """Génère la configuration Render"""
    print("⚙️  Génération de la configuration Render...")
    
    config = {
        "services": [
            {
                "type": "web",
                "name": "solar-nasih-sma",
                "env": "python",
                "plan": "free",
                "buildCommand": "pip install -r SolarNasih_Deploiement_Complet/requirements_sma.txt",
                "startCommand": "cd SolarNasih_SMA && uvicorn main:app --host 0.0.0.0 --port $PORT",
                "envVars": [
                    {"key": "PYTHON_VERSION", "value": "3.11.0"},
                    {"key": "GEMINI_API_KEY", "sync": False},
                    {"key": "TAVILY_API_KEY", "sync": False},
                    {"key": "ENVIRONMENT", "value": "production"}
                ]
            },
            {
                "type": "web",
                "name": "solar-nasih-rag",
                "env": "python",
                "plan": "free",
                "buildCommand": "pip install -r SolarNasih_Deploiement_Complet/requirements_rag.txt",
                "startCommand": "cd SolarNasih_RAG && uvicorn api_simple:app --host 0.0.0.0 --port $PORT",
                "envVars": [
                    {"key": "PYTHON_VERSION", "value": "3.11.0"},
                    {"key": "OPENAI_API_KEY", "sync": False},
                    {"key": "ANTHROPIC_API_KEY", "sync": False},
                    {"key": "ENVIRONMENT", "value": "production"}
                ]
            },
            {
                "type": "web",
                "name": "solar-nasih-frontend",
                "env": "node",
                "plan": "free",
                "buildCommand": "cd SolarNasih_Template && npm install && npm run build",
                "startCommand": "cd SolarNasih_Template && npm run preview -- --host 0.0.0.0 --port $PORT",
                "envVars": [
                    {"key": "NODE_VERSION", "value": "18"},
                    {"key": "NODE_ENV", "value": "production"}
                ]
            }
        ]
    }
    
    with open("render-complete.yaml", "w") as f:
        import yaml
        yaml.dump(config, f, default_flow_style=False)
    
    print("✅ Configuration Render générée (render-complete.yaml)")

def show_deployment_instructions():
    """Affiche les instructions de déploiement"""
    print("\n" + "=" * 60)
    print("📋 INSTRUCTIONS DE DÉPLOIEMENT")
    print("=" * 60)
    
    print("\n1️⃣  PRÉPARATION :")
    print("   • Configurez vos clés API dans le fichier .env")
    print("   • Assurez-vous que votre code est sur GitHub")
    
    print("\n2️⃣  DÉPLOIEMENT SUR RENDER :")
    print("   • Allez sur https://render.com")
    print("   • Créez un nouveau compte ou connectez-vous")
    print("   • Cliquez sur 'New +' → 'Blueprint'")
    print("   • Connectez votre repo GitHub")
    print("   • Sélectionnez le fichier render-complete.yaml")
    print("   • Configurez vos variables d'environnement")
    print("   • Cliquez sur 'Apply'")
    
    print("\n3️⃣  CONFIGURATION MANUELLE (Alternative) :")
    print("   • Créez 3 Web Services séparés sur Render")
    print("   • Utilisez les commandes de deploy_commands_complete.txt")
    
    print("\n4️⃣  VÉRIFICATION :")
    print("   • Frontend : https://solar-nasih-frontend.onrender.com")
    print("   • SMA API : https://solar-nasih-sma.onrender.com")
    print("   • RAG API : https://solar-nasih-rag.onrender.com")

def show_docker_instructions():
    """Affiche les instructions pour Docker"""
    print("\n" + "=" * 60)
    print("🐳 DÉPLOIEMENT DOCKER LOCAL")
    print("=" * 60)
    
    print("\n1️⃣  PRÉPARATION :")
    print("   • Assurez-vous que Docker et Docker Compose sont installés")
    print("   • Configurez vos clés API dans le fichier .env")
    
    print("\n2️⃣  DÉMARRAGE :")
    print("   cd SolarNasih_Deploiement_Complet")
    print("   docker-compose up -d")
    
    print("\n3️⃣  VÉRIFICATION :")
    print("   • Frontend : http://localhost:3000")
    print("   • SMA API : http://localhost:8000")
    print("   • RAG API : http://localhost:8001")
    print("   • Qdrant : http://localhost:6333")
    print("   • Redis : redis://localhost:6379")

def main():
    """Fonction principale"""
    print_banner()
    
    if not check_requirements():
        sys.exit(1)
    
    create_env_file()
    generate_render_config()
    
    print("\n" + "=" * 60)
    print("🎯 CHOIX DE DÉPLOIEMENT")
    print("=" * 60)
    print("1. Déploiement sur Render (Cloud)")
    print("2. Déploiement Docker local")
    print("3. Instructions complètes")
    
    choice = input("\nChoisissez une option (1-3) : ").strip()
    
    if choice == "1":
        show_deployment_instructions()
    elif choice == "2":
        show_docker_instructions()
    elif choice == "3":
        show_deployment_instructions()
        show_docker_instructions()
    else:
        print("❌ Option invalide")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Déploiement configuré avec succès !")
    print("=" * 60)

if __name__ == "__main__":
    main()
