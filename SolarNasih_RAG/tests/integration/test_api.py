"""
Tests d'intégration pour l'API RAG multimodal.
Teste les endpoints, les réponses et les interactions complètes.
"""

import pytest
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, List
import logging

# Configuration du logging pour les tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestRAGAPI:
    """Tests d'intégration pour l'API RAG."""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.test_documents = []
    
    def setup_method(self):
        """Configuration avant chaque test."""
        # Vérification que l'API est accessible
        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code != 200:
                pytest.skip("API non accessible")
        except requests.exceptions.ConnectionError:
            pytest.skip("API non accessible")
    
    def test_health_check(self):
        """Test du health check de l'API."""
        response = self.session.get(f"{self.base_url}/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["success", "error"]
    
    def test_health_check_detailed(self):
        """Test du health check détaillé."""
        response = self.session.get(f"{self.base_url}/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "components" in data
        assert "dependencies" in data
    
    def test_search_endpoint(self):
        """Test de l'endpoint de recherche."""
        query = "test query"
        payload = {
            "query": query,
            "search_type": "hybrid",
            "top_k": 5
        }
        
        response = self.session.post(f"{self.base_url}/search", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "query" in data
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_search_with_filters(self):
        """Test de la recherche avec filtres."""
        query = "test query"
        payload = {
            "query": query,
            "search_type": "semantic",
            "top_k": 3,
            "filters": {
                "document_type": "text"
            }
        }
        
        response = self.session.post(f"{self.base_url}/search", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["success", "error"]
    
    def test_generate_endpoint(self):
        """Test de l'endpoint de génération."""
        query = "What is RAG?"
        payload = {
            "query": query,
            "max_tokens": 100,
            "temperature": 0.1
        }
        
        response = self.session.post(f"{self.base_url}/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "query" in data
        assert "response" in data
    
    def test_upload_endpoint(self):
        """Test de l'endpoint d'upload."""
        # Création d'un fichier de test temporaire
        test_file = Path("test_document.txt")
        test_content = "This is a test document for RAG system."
        
        try:
            test_file.write_text(test_content)
            
            payload = {
                "file_path": str(test_file),
                "document_type": "text",
                "chunk_size": 500
            }
            
            response = self.session.post(f"{self.base_url}/upload", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "file_path" in data
            
        finally:
            # Nettoyage du fichier de test
            if test_file.exists():
                test_file.unlink()
    
    def test_multimodal_search(self):
        """Test de la recherche multimodale."""
        payload = {
            "text_query": "test query",
            "top_k": 5,
            "fusion_strategy": "weighted"
        }
        
        response = self.session.post(f"{self.base_url}/search/multimodal", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "fused_results" in data
    
    def test_batch_search(self):
        """Test de la recherche par lot."""
        queries = ["query 1", "query 2", "query 3"]
        payload = {
            "queries": queries,
            "search_type": "hybrid",
            "top_k": 3
        }
        
        response = self.session.post(f"{self.base_url}/search/batch", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "total_queries" in data
        assert "results" in data
        assert len(data["results"]) == len(queries)
    
    def test_statistics_endpoint(self):
        """Test de l'endpoint de statistiques."""
        response = self.session.get(f"{self.base_url}/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "total_documents" in data
        assert "total_chunks" in data
    
    def test_api_info(self):
        """Test de l'endpoint d'informations API."""
        response = self.session.get(f"{self.base_url}/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data
    
    def test_error_handling(self):
        """Test de la gestion des erreurs."""
        # Test avec une requête invalide
        payload = {
            "query": "",  # Requête vide
            "search_type": "invalid_type"
        }
        
        response = self.session.post(f"{self.base_url}/search", json=payload)
        
        # L'API devrait retourner une erreur 422 (Validation Error) ou 400 (Bad Request)
        assert response.status_code in [400, 422]
    
    def test_rate_limiting(self):
        """Test de la limitation de taux."""
        # Envoi de plusieurs requêtes rapides
        for i in range(10):
            payload = {
                "query": f"test query {i}",
                "search_type": "semantic",
                "top_k": 1
            }
            
            response = self.session.post(f"{self.base_url}/search", json=payload)
            
            # Si le rate limiting est activé, on devrait avoir une erreur 429
            if response.status_code == 429:
                break
        
        # Au moins une requête devrait réussir
        assert any(response.status_code == 200 for _ in range(10))
    
    def test_search_performance(self):
        """Test de performance de la recherche."""
        query = "performance test query"
        payload = {
            "query": query,
            "search_type": "hybrid",
            "top_k": 10
        }
        
        start_time = time.time()
        response = self.session.post(f"{self.base_url}/search", json=payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 5.0  # La recherche ne devrait pas prendre plus de 5 secondes
        
        data = response.json()
        if "search_time" in data:
            assert data["search_time"] < 5.0
    
    def test_generation_performance(self):
        """Test de performance de la génération."""
        query = "What is the difference between RAG and traditional search?"
        payload = {
            "query": query,
            "max_tokens": 200,
            "temperature": 0.1
        }
        
        start_time = time.time()
        response = self.session.post(f"{self.base_url}/generate", json=payload)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 30.0  # La génération ne devrait pas prendre plus de 30 secondes
        
        data = response.json()
        if "generation_time" in data:
            assert data["generation_time"] < 30.0
    
    def test_concurrent_requests(self):
        """Test de requêtes concurrentes."""
        import threading
        
        results = []
        errors = []
        
        def make_request(query_id):
            try:
                payload = {
                    "query": f"concurrent query {query_id}",
                    "search_type": "semantic",
                    "top_k": 3
                }
                
                response = self.session.post(f"{self.base_url}/search", json=payload)
                results.append(response.status_code)
                
            except Exception as e:
                errors.append(str(e))
        
        # Création de threads pour les requêtes concurrentes
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Attente de la fin de tous les threads
        for thread in threads:
            thread.join()
        
        # Vérification des résultats
        assert len(errors) == 0, f"Erreurs lors des requêtes concurrentes: {errors}"
        assert len(results) == 5, "Toutes les requêtes devraient être terminées"
        assert all(status == 200 for status in results), "Toutes les requêtes devraient réussir"
    
    def test_search_result_structure(self):
        """Test de la structure des résultats de recherche."""
        query = "test structure query"
        payload = {
            "query": query,
            "search_type": "hybrid",
            "top_k": 3
        }
        
        response = self.session.post(f"{self.base_url}/search", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérification de la structure de base
        assert "status" in data
        assert "query" in data
        assert "results" in data
        assert "total_results" in data
        assert "search_time" in data
        
        # Vérification de la structure des résultats
        if data["results"]:
            result = data["results"][0]
            assert "content" in result
            assert "source" in result
            assert "score" in result
            assert isinstance(result["score"], (int, float))
            assert 0 <= result["score"] <= 1
    
    def test_generation_result_structure(self):
        """Test de la structure des résultats de génération."""
        query = "What is artificial intelligence?"
        payload = {
            "query": query,
            "max_tokens": 150,
            "temperature": 0.1
        }
        
        response = self.session.post(f"{self.base_url}/generate", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Vérification de la structure de base
        assert "status" in data
        assert "query" in data
        assert "response" in data
        assert "sources" in data
        assert "generation_time" in data
        
        # Vérification du contenu de la réponse
        if data["status"] == "success":
            assert len(data["response"]) > 0
            assert isinstance(data["sources"], list)

def run_integration_tests():
    """Fonction pour exécuter tous les tests d'intégration."""
    test_instance = TestRAGAPI()
    
    # Liste des méthodes de test
    test_methods = [
        test_instance.test_health_check,
        test_instance.test_health_check_detailed,
        test_instance.test_search_endpoint,
        test_instance.test_search_with_filters,
        test_instance.test_generate_endpoint,
        test_instance.test_upload_endpoint,
        test_instance.test_multimodal_search,
        test_instance.test_batch_search,
        test_instance.test_statistics_endpoint,
        test_instance.test_api_info,
        test_instance.test_error_handling,
        test_instance.test_rate_limiting,
        test_instance.test_search_performance,
        test_instance.test_generation_performance,
        test_instance.test_concurrent_requests,
        test_instance.test_search_result_structure,
        test_instance.test_generation_result_structure
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    print("🚀 Démarrage des tests d'intégration...")
    
    for test_method in test_methods:
        try:
            test_method()
            print(f"✅ {test_method.__name__}: PASSED")
            passed_tests += 1
        except Exception as e:
            print(f"❌ {test_method.__name__}: FAILED - {str(e)}")
            failed_tests += 1
    
    print(f"\n📊 Résultats des tests:")
    print(f"Tests réussis: {passed_tests}")
    print(f"Tests échoués: {failed_tests}")
    print(f"Total: {passed_tests + failed_tests}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_integration_tests()
    exit(0 if success else 1)
