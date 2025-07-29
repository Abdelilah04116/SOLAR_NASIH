#!/usr/bin/env python3
"""
Test d'upload de fichier JSON
"""

import requests
import json
import os

def test_json_upload():
    """Test d'upload d'un fichier JSON"""
    
    # Créer un fichier JSON de test
    test_data = {
        "name": "Test Contact Page",
        "type": "contact",
        "data": {
            "email": "test@example.com",
            "phone": "+33123456789",
            "address": "123 Test Street"
        },
        "metadata": {
            "created": "2024-01-01",
            "version": "1.0"
        }
    }
    
    with open("test_contact.json", "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2)
    
    try:
        print("🚀 Test d'upload JSON...")
        
        # Upload via SMA
        with open("test_contact.json", "rb") as f:
            files = {"file": ("test_contact.json", f, "application/json")}
            response = requests.post("http://localhost:8000/upload-document", files=files)
        
        print(f"📊 Statut: {response.status_code}")
        print(f"📄 Réponse: {response.text}")
        
        if response.status_code == 200:
            print("✅ Upload JSON réussi!")
            return True
        else:
            print("❌ Upload JSON échoué")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    finally:
        # Nettoyer
        if os.path.exists("test_contact.json"):
            os.remove("test_contact.json")

if __name__ == "__main__":
    test_json_upload() 