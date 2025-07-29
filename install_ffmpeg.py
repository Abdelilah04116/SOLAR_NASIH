#!/usr/bin/env python3
"""
Script d'installation automatique de ffmpeg pour Windows
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil

def check_ffmpeg():
    """Vérifier si ffmpeg est déjà installé"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg est déjà installé!")
            return True
    except FileNotFoundError:
        pass
    return False

def install_with_winget():
    """Installer ffmpeg avec winget"""
    try:
        print("🚀 Tentative d'installation avec winget...")
        result = subprocess.run(['winget', 'install', 'ffmpeg'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Installation avec winget réussie!")
            return True
        else:
            print(f"❌ Échec winget: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ winget non disponible")
        return False

def install_with_chocolatey():
    """Installer ffmpeg avec chocolatey"""
    try:
        print("🚀 Tentative d'installation avec chocolatey...")
        result = subprocess.run(['choco', 'install', 'ffmpeg', '-y'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Installation avec chocolatey réussie!")
            return True
        else:
            print(f"❌ Échec chocolatey: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ chocolatey non disponible")
        return False

def download_ffmpeg_manual():
    """Télécharger ffmpeg manuellement"""
    print("📥 Téléchargement manuel de ffmpeg...")
    
    # URL de ffmpeg pour Windows
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    try:
        # Créer le dossier de téléchargement
        download_dir = os.path.join(os.getcwd(), "ffmpeg_download")
        os.makedirs(download_dir, exist_ok=True)
        
        zip_path = os.path.join(download_dir, "ffmpeg.zip")
        
        print(f"📥 Téléchargement depuis {ffmpeg_url}")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        print("📦 Extraction du fichier zip...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(download_dir)
        
        # Trouver le dossier ffmpeg
        for item in os.listdir(download_dir):
            if item.startswith("ffmpeg-") and os.path.isdir(os.path.join(download_dir, item)):
                ffmpeg_dir = os.path.join(download_dir, item)
                break
        else:
            print("❌ Impossible de trouver le dossier ffmpeg")
            return False
        
        # Copier ffmpeg.exe dans le dossier courant
        ffmpeg_exe = os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe")
        if os.path.exists(ffmpeg_exe):
            shutil.copy2(ffmpeg_exe, "ffmpeg.exe")
            print("✅ ffmpeg.exe copié dans le dossier courant")
            return True
        else:
            print("❌ ffmpeg.exe non trouvé")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du téléchargement: {e}")
        return False

def main():
    """Fonction principale"""
    print("🎬 Installation de ffmpeg pour Solar Nasih")
    print("=" * 50)
    
    # Vérifier si ffmpeg est déjà installé
    if check_ffmpeg():
        return
    
    print("ffmpeg n'est pas installé. Tentative d'installation automatique...")
    
    # Essayer winget
    if install_with_winget():
        return
    
    # Essayer chocolatey
    if install_with_chocolatey():
        return
    
    # Installation manuelle
    print("\n📋 Installation manuelle requise")
    print("1. Télécharger ffmpeg depuis: https://ffmpeg.org/download.html")
    print("2. Extraire le fichier zip")
    print("3. Copier ffmpeg.exe dans le dossier du projet ou l'ajouter au PATH")
    print("4. Redémarrer le terminal")
    
    # Essayer le téléchargement automatique
    print("\n🔄 Tentative de téléchargement automatique...")
    if download_ffmpeg_manual():
        print("✅ ffmpeg installé localement!")
        print("💡 Pour une installation globale, ajoutez ffmpeg.exe au PATH")
    else:
        print("❌ Échec de l'installation automatique")
        print("📋 Veuillez installer ffmpeg manuellement")

if __name__ == "__main__":
    main() 