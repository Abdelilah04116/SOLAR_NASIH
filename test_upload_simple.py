#!/usr/bin/env python3
"""
Test simple d'upload de document
"""

import requests
import os

def test_upload():
    """Test d'upload d'un fichier texte simple"""
    
    # Créer un fichier de test
    test_content = "Ceci est un test d'upload de document pour vérifier l'indexation automatique."
    
    with open("test_upload.txt", "w", encoding="utf-8") as f:
        f.write(test_content)
    
    try:
        print("🚀 Test d'upload...")
        
        # Upload via SMA
        with open("test_upload.txt", "rb") as f:
            files = {"file": ("test_upload.txt", f, "text/plain")}
            response = requests.post("http://localhost:8000/upload-document", files=files)
        
        print(f"📊 Statut: {response.status_code}")
        print(f"📄 Réponse: {response.text}")
        
        if response.status_code == 200:
            print("✅ Upload réussi!")
            return True
        else:
            print("❌ Upload échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        # Nettoyer
        if os.path.exists("test_upload.txt"):
            os.remove("test_upload.txt")

if __name__ == "__main__":
    test_upload() 