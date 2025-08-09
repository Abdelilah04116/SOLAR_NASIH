#!/usr/bin/env python3
"""
Script de déploiement automatique pour Solar Nasih sur Render
Déploie automatiquement SMA et RAG sur Render, et configure le frontend pour Vercel
"""

import os
import json
import requests
import subprocess
from typing import Dict, Any

class RenderDeployer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.render.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def create_service(self, service_config: Dict[str, Any]) -> Dict[str, Any]:
        """Crée un service sur Render"""
        response = requests.post(
            f"{self.base_url}/services",
            headers=self.headers,
            json=service_config
        )
        response.raise_for_status()
        return response.json()
    
    def create_sma_service(self, repo_url: str, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """Crée le service SMA"""
        config = {
            "type": "web_service",
            "name": "solar-nasih-sma",
            "repo": repo_url,
            "rootDir": "SolarNasih_SMA",
            "buildCommand": "pip install -r ../SolarNasih_Deploiement_Complet/requirements_sma.txt",
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "envVars": [
                {"key": k, "value": v} for k, v in env_vars.items()
            ],
            "plan": "starter",
            "region": "oregon",
            "python": "3.11"
        }
        return self.create_service(config)
    
    def create_rag_service(self, repo_url: str, env_vars: Dict[str, str]) -> Dict[str, Any]:
        """Crée le service RAG"""
        config = {
            "type": "web_service",
            "name": "solar-nasih-rag",
            "repo": repo_url,
            "rootDir": "SolarNasih_RAG",
            "buildCommand": "pip install -r ../SolarNasih_Deploiement_Complet/requirements_rag.txt",
            "startCommand": "uvicorn api_simple:app --host 0.0.0.0 --port $PORT",
            "envVars": [
                {"key": k, "value": v} for k, v in env_vars.items()
            ],
            "plan": "starter",
            "region": "oregon",
            "python": "3.11"
        }
        return self.create_service(config)

def load_env_file(file_path: str) -> Dict[str, str]:
    """Charge les variables d'environnement depuis un fichier .env"""
    env_vars = {}
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    return env_vars

def create_vercel_config(sma_url: str, rag_url: str) -> None:
    """Met à jour la configuration Vercel avec les URLs des services"""
    vercel_config = {
        "version": 2,
        "name": "solar-nasih-frontend",
        "builds": [
            {
                "src": "package.json",
                "use": "@vercel/static-build",
                "config": {"distDir": "dist"}
            }
        ],
        "routes": [
            {"src": "/api/(.*)", "dest": "/api/$1"},
            {"src": "/(.*)", "dest": "/index.html"}
        ],
        "env": {
            "VITE_SMA_API_URL": sma_url,
            "VITE_RAG_API_URL": rag_url,
            "VITE_APP_NAME": "SolarNasih",
            "VITE_APP_VERSION": "1.0.0",
            "VITE_ENVIRONMENT": "production"
        },
        "headers": [
            {
                "source": "/(.*)",
                "headers": [
                    {"key": "X-Content-Type-Options", "value": "nosniff"},
                    {"key": "X-Frame-Options", "value": "DENY"},
                    {"key": "X-XSS-Protection", "value": "1; mode=block"}
                ]
            }
        ]
    }
    
    with open("../SolarNasih_Template/vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)

def main():
    print("🚀 Déploiement automatique de Solar Nasih")
    print("=" * 50)
    
    # Vérifier les prérequis
    render_api_key = os.getenv("RENDER_API_KEY")
    if not render_api_key:
        print("❌ RENDER_API_KEY non définie")
        print("Obtenez votre clé API sur https://dashboard.render.com/account")
        return
    
    repo_url = input("📝 URL du repository GitHub: ")
    if not repo_url:
        print("❌ URL du repository requise")
        return
    
    # Charger les variables d'environnement
    env_vars = load_env_file("env.example")
    
    # Demander les API Keys
    print("\n🔑 Configuration des API Keys:")
    env_vars["GEMINI_API_KEY"] = input("GEMINI_API_KEY (obligatoire): ")
    env_vars["OPENAI_API_KEY"] = input("OPENAI_API_KEY (optionnel): ") or ""
    env_vars["ANTHROPIC_API_KEY"] = input("ANTHROPIC_API_KEY (optionnel): ") or ""
    env_vars["TAVILY_API_KEY"] = input("TAVILY_API_KEY (optionnel): ") or ""
    
    if not env_vars["GEMINI_API_KEY"]:
        print("❌ GEMINI_API_KEY est obligatoire")
        return
    
    # Initialiser le déployeur
    deployer = RenderDeployer(render_api_key)
    
    try:
        # Déployer SMA
        print("\n🤖 Déploiement du service SMA...")
        sma_service = deployer.create_sma_service(repo_url, env_vars)
        sma_url = f"https://{sma_service['service']['slug']}.onrender.com"
        print(f"✅ SMA déployé: {sma_url}")
        
        # Déployer RAG
        print("\n🔍 Déploiement du service RAG...")
        rag_service = deployer.create_rag_service(repo_url, env_vars)
        rag_url = f"https://{rag_service['service']['slug']}.onrender.com"
        print(f"✅ RAG déployé: {rag_url}")
        
        # Configurer Vercel
        print("\n🌐 Configuration du frontend pour Vercel...")
        create_vercel_config(sma_url, rag_url)
        print("✅ Configuration Vercel mise à jour")
        
        # Instructions finales
        print("\n🎉 Déploiement terminé!")
        print("=" * 50)
        print(f"🤖 SMA: {sma_url}")
        print(f"🔍 RAG: {rag_url}")
        print("\n📋 Prochaines étapes:")
        print("1. Attendez que les services terminent leur build (~5-10 min)")
        print("2. Vérifiez les services:")
        print(f"   curl {sma_url}/health")
        print(f"   curl {rag_url}/health")
        print("3. Déployez le frontend sur Vercel:")
        print("   cd ../SolarNasih_Template")
        print("   vercel --prod")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return

if __name__ == "__main__":
    main()
