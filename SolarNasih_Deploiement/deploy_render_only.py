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
    print("pip install -r requirements.txt")
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
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
httpx==0.25.0
pydantic==2.5.0
pydantic-settings==2.1.0
langchain==0.1.0
langgraph==0.0.26
langchain-google-genai==0.0.6
google-generativeai==0.3.2
tavily-python==0.3.0
python-dotenv==1.0.0
jinja2==3.1.2
requests==2.31.0
PyYAML==6.0.1
speechrecognition==3.10.0
gtts==2.4.0
python-docx==1.1.0
openpyxl==3.1.2
fpdf2==2.7.6
markdown==3.5.1
beautifulsoup4==4.12.2
streamlit==1.28.0
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