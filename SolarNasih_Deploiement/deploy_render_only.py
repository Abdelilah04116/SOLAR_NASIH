#!/usr/bin/env python3
"""
Script de déploiement Render sans modifier le projet principal
"""

import os
import subprocess
import sys

def print_instructions():
    """Affiche les instructions de déploiement"""
    print("🚀 Déploiement Render - Solar Nasih SMA")
    print("=" * 50)
    print()
    print("📋 INSTRUCTIONS POUR RENDER :")
    print()
    print("1. Allez sur https://render.com")
    print("2. Créez un nouveau Web Service")
    print("3. Connectez votre repo GitHub : https://github.com/Abdelilah04116/SOLAR_NASIH")
    print("4. Configurez comme suit :")
    print()
    print("🔧 BUILD COMMAND :")
    print("pip install fastapi uvicorn pydantic google-generativeai tavily-python langgraph langchain python-dotenv requests")
    print()
    print("🚀 START COMMAND :")
    print("cd SolarNasih_SMA && uvicorn main:app --host 0.0.0.0 --port $PORT")
    print()
    print("⚙️ VARIABLES D'ENVIRONNEMENT :")
    print("PYTHON_VERSION=3.11.0")
    print("GEMINI_API_KEY=votre_clé_gemini")
    print("TAVILY_API_KEY=votre_clé_tavily")
    print("ENVIRONMENT=production")
    print()
    print("✅ Déploiement terminé !")
    print("🌐 URL : https://solar-nasih-api.onrender.com")
    print("📚 Documentation : https://solar-nasih-api.onrender.com/docs")

def create_temp_files():
    """Crée des fichiers temporaires pour le déploiement"""
    print("📁 Création de fichiers temporaires...")
    
    # Créer un requirements.txt temporaire
    requirements_content = """# Requirements temporaire pour déploiement
fastapi
uvicorn
pydantic
google-generativeai
tavily-python
langgraph
langchain
python-dotenv
requests
"""
    
    # Créer un runtime.txt temporaire
    runtime_content = "python-3.11.0\n"
    
    # Sauvegarder dans le dossier de déploiement
    with open("requirements_temp.txt", "w") as f:
        f.write(requirements_content)
    
    with open("runtime_temp.txt", "w") as f:
        f.write(runtime_content)
    
    print("✅ Fichiers temporaires créés :")
    print("   - requirements_temp.txt")
    print("   - runtime_temp.txt")
    print()
    print("📋 Pour utiliser ces fichiers :")
    print("   1. Copiez requirements_temp.txt vers votre projet")
    print("   2. Copiez runtime_temp.txt vers votre projet")
    print("   3. Poussez sur GitHub")
    print("   4. Déployez sur Render")

def main():
    """Fonction principale"""
    if len(sys.argv) > 1 and sys.argv[1] == "--temp":
        create_temp_files()
    else:
        print_instructions()

if __name__ == "__main__":
    main() 