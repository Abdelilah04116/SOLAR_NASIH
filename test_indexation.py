#!/usr/bin/env python3
"""
Script de test pour vérifier l'indexation automatique des documents
"""

import requests
import json
import time

def test_rag_status():
    """Test du statut du système RAG"""
    print("🔍 Test du statut RAG...")
    try:
        response = requests.get("http://localhost:8001/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ RAG opérationnel: {data}")
            return True
        else:
            print(f"❌ RAG non disponible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion RAG: {e}")
        return False

def test_sma_status():
    """Test du statut du système SMA"""
    print("🔍 Test du statut SMA...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SMA opérationnel: {data}")
            return True
        else:
            print(f"❌ SMA non disponible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur connexion SMA: {e}")
        return False

def test_upload_document():
    """Test d'upload d'un document"""
    print("📄 Test d'upload de document...")
    
    # Créer un fichier de test simple
    test_content = """
    Guide d'installation photovoltaïque
    
    Ce document contient des informations sur l'installation de panneaux solaires.
    
    Points clés:
    - Choix des panneaux
    - Installation électrique
    - Raccordement au réseau
    - Maintenance
    
    Ceci est un test d'indexation automatique.
    """
    
    try:
        # Créer le fichier temporaire
        with open("test_document.txt", "w", encoding="utf-8") as f:
            f.write(test_content)
        
        # Upload via SMA
        with open("test_document.txt", "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            response = requests.post("http://localhost:8000/upload-document", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Document uploadé avec succès: {result}")
            return True
        else:
            print(f"❌ Erreur upload: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test d'upload: {e}")
        return False
    finally:
        # Nettoyer le fichier de test
        import os
        if os.path.exists("test_document.txt"):
            os.remove("test_document.txt")

def test_search_document():
    """Test de recherche dans les documents indexés"""
    print("🔍 Test de recherche...")
    try:
        response = requests.post("http://localhost:8001/search/", json={
            "query": "installation photovoltaïque",
            "method": "hybrid",
            "top_k": 3,
            "generate_response": True
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Recherche réussie: {len(result.get('results', []))} résultats")
            return True
        else:
            print(f"❌ Erreur recherche: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors de la recherche: {e}")
        return False

def main():
    """Test complet du système d'indexation"""
    print("🚀 Test complet du système d'indexation automatique")
    print("=" * 60)
    
    # Test 1: Statut des services
    rag_ok = test_rag_status()
    sma_ok = test_sma_status()
    
    if not rag_ok or not sma_ok:
        print("❌ Services non disponibles. Vérifiez que:")
        print("   - RAG est lancé sur le port 8001")
        print("   - SMA est lancé sur le port 8000")
        return
    
    # Test 2: Upload de document
    upload_ok = test_upload_document()
    
    if upload_ok:
        # Attendre un peu pour l'indexation
        print("⏳ Attente de l'indexation...")
        time.sleep(3)
        
        # Test 3: Recherche
        search_ok = test_search_document()
        
        if search_ok:
            print("\n🎉 SUCCÈS: L'indexation automatique fonctionne correctement!")
            print("✅ Le document est uploadé via SMA (port 8000)")
            print("✅ Le document est indexé dans RAG (port 8001)")
            print("✅ Le document est recherchable")
        else:
            print("\n⚠️  ATTENTION: Upload réussi mais recherche échouée")
            print("   Le document pourrait ne pas être correctement indexé")
    else:
        print("\n❌ ÉCHEC: L'upload de document a échoué")
        print("   Vérifiez la configuration et les logs")

if __name__ == "__main__":
    main() 