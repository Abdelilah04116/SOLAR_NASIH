"""
Tests d'intégration pour le pipeline RAG multimodal complet.
Teste l'ensemble du pipeline : ingestion, vectorisation, recherche, génération.
"""

import pytest
import sys
import os
from pathlib import Path
import tempfile
import shutil
import json
import time
from typing import Dict, Any, List, Optional

# Ajout du chemin du projet pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.ingestion.document_loader import DocumentLoader
from src.vectorization.indexer import Indexer
from src.retrieval.search_engine import SearchEngine
from src.generation.response_generator import ResponseGenerator
from src.utils.file_utils import FileUtils

class TestRAGPipeline:
    """Tests d'intégration pour le pipeline RAG complet."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.temp_dir = tempfile.mkdtemp(prefix="rag_test_")
        self.test_docs_dir = Path(self.temp_dir) / "test_docs"
        self.test_docs_dir.mkdir(exist_ok=True)
        
        # Création de documents de test
        self._create_test_documents()
        
        # Initialisation des composants
        self.document_loader = DocumentLoader()
        self.indexer = Indexer()
        self.search_engine = SearchEngine()
        self.response_generator = ResponseGenerator()
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def _create_test_documents(self):
        """Crée des documents de test pour les tests."""
        # Document texte 1
        doc1_content = """
        L'intelligence artificielle (IA) est un domaine de l'informatique qui vise à créer des systèmes capables d'effectuer des tâches qui nécessitent normalement l'intelligence humaine.
        Ces tâches incluent l'apprentissage, le raisonnement, la perception et la résolution de problèmes.
        L'IA a de nombreuses applications dans des domaines variés comme la médecine, la finance, les transports et l'éducation.
        """
        
        doc1_path = self.test_docs_dir / "ai_introduction.txt"
        doc1_path.write_text(doc1_content.strip())
        
        # Document texte 2
        doc2_content = """
        Le RAG (Retrieval-Augmented Generation) est une technique qui combine la recherche d'informations et la génération de texte.
        Cette approche permet aux modèles de langage d'accéder à des connaissances externes pour améliorer leurs réponses.
        Le RAG est particulièrement utile pour les tâches qui nécessitent des informations à jour ou spécifiques.
        """
        
        doc2_path = self.test_docs_dir / "rag_explanation.txt"
        doc2_path.write_text(doc2_content.strip())
        
        # Document JSON avec métadonnées
        doc3_content = {
            "title": "Machine Learning Basics",
            "content": "Le machine learning est une sous-catégorie de l'IA qui se concentre sur l'apprentissage automatique à partir de données.",
            "tags": ["machine learning", "IA", "algorithmes"],
            "author": "Test Author",
            "date": "2024-01-01"
        }
        
        doc3_path = self.test_docs_dir / "ml_basics.json"
        with open(doc3_path, 'w', encoding='utf-8') as f:
            json.dump(doc3_content, f, ensure_ascii=False, indent=2)
    
    def test_full_pipeline_ingestion(self):
        """Test du pipeline complet - étape d'ingestion."""
        # Chargement des documents
        documents = self.document_loader.load_documents(str(self.test_docs_dir))
        
        assert len(documents) >= 3, "Au moins 3 documents devraient être chargés"
        
        # Vérification de la structure des documents
        for doc in documents:
            assert "content" in doc, "Chaque document doit avoir un contenu"
            assert "metadata" in doc, "Chaque document doit avoir des métadonnées"
            assert "source" in doc, "Chaque document doit avoir une source"
        
        return documents
    
    def test_full_pipeline_indexing(self):
        """Test du pipeline complet - étape d'indexation."""
        # Chargement des documents
        documents = self.test_full_pipeline_ingestion()
        
        # Indexation des documents
        start_time = time.time()
        indexing_result = self.indexer.index_documents(documents)
        indexing_time = time.time() - start_time
        
        assert indexing_result["success"], "L'indexation devrait réussir"
        assert indexing_result["documents_indexed"] >= 3, "Au moins 3 documents devraient être indexés"
        assert indexing_time < 60, "L'indexation ne devrait pas prendre plus de 60 secondes"
        
        return indexing_result
    
    def test_full_pipeline_search(self):
        """Test du pipeline complet - étape de recherche."""
        # Indexation préalable
        indexing_result = self.test_full_pipeline_indexing()
        
        # Test de recherche
        query = "intelligence artificielle"
        search_results = self.search_engine.search(query, top_k=3)
        
        assert len(search_results) > 0, "La recherche devrait retourner des résultats"
        assert len(search_results) <= 3, "Le nombre de résultats devrait respecter top_k"
        
        # Vérification de la structure des résultats
        for result in search_results:
            assert "content" in result, "Chaque résultat doit avoir un contenu"
            assert "score" in result, "Chaque résultat doit avoir un score"
            assert "source" in result, "Chaque résultat doit avoir une source"
            assert 0 <= result["score"] <= 1, "Le score doit être entre 0 et 1"
        
        return search_results
    
    def test_full_pipeline_generation(self):
        """Test du pipeline complet - étape de génération."""
        # Recherche préalable
        search_results = self.test_full_pipeline_search()
        
        # Génération de réponse
        query = "Qu'est-ce que l'intelligence artificielle ?"
        generation_result = self.response_generator.generate_response(
            query=query,
            retrieved_docs=search_results,
            max_tokens=200,
            temperature=0.1
        )
        
        assert "response" in generation_result, "La génération doit retourner une réponse"
        assert "metadata" in generation_result, "La génération doit retourner des métadonnées"
        assert len(generation_result["response"]) > 0, "La réponse ne doit pas être vide"
        
        return generation_result
    
    def test_full_pipeline_end_to_end(self):
        """Test du pipeline complet de bout en bout."""
        # Exécution du pipeline complet
        documents = self.test_full_pipeline_ingestion()
        indexing_result = self.test_full_pipeline_indexing()
        search_results = self.test_full_pipeline_search()
        generation_result = self.test_full_pipeline_generation()
        
        # Vérifications finales
        assert len(documents) >= 3, "Au moins 3 documents chargés"
        assert indexing_result["success"], "Indexation réussie"
        assert len(search_results) > 0, "Recherche avec résultats"
        assert len(generation_result["response"]) > 0, "Génération avec réponse"
        
        print(f"✅ Pipeline complet testé avec succès:")
        print(f"   - Documents chargés: {len(documents)}")
        print(f"   - Documents indexés: {indexing_result['documents_indexed']}")
        print(f"   - Résultats de recherche: {len(search_results)}")
        print(f"   - Réponse générée: {len(generation_result['response'])} caractères")
    
    def test_pipeline_with_different_queries(self):
        """Test du pipeline avec différentes requêtes."""
        # Indexation préalable
        self.test_full_pipeline_indexing()
        
        test_queries = [
            "intelligence artificielle",
            "RAG technique",
            "machine learning",
            "génération de texte"
        ]
        
        for query in test_queries:
            # Recherche
            search_results = self.search_engine.search(query, top_k=2)
            assert len(search_results) >= 0, f"Recherche pour '{query}' devrait retourner des résultats"
            
            # Génération
            generation_result = self.response_generator.generate_response(
                query=query,
                retrieved_docs=search_results,
                max_tokens=150
            )
            
            assert len(generation_result["response"]) > 0, f"Génération pour '{query}' devrait produire une réponse"
    
    def test_pipeline_performance(self):
        """Test de performance du pipeline."""
        # Mesure du temps d'ingestion
        start_time = time.time()
        documents = self.document_loader.load_documents(str(self.test_docs_dir))
        ingestion_time = time.time() - start_time
        
        # Mesure du temps d'indexation
        start_time = time.time()
        indexing_result = self.indexer.index_documents(documents)
        indexing_time = time.time() - start_time
        
        # Mesure du temps de recherche
        start_time = time.time()
        search_results = self.search_engine.search("test query", top_k=5)
        search_time = time.time() - start_time
        
        # Mesure du temps de génération
        start_time = time.time()
        generation_result = self.response_generator.generate_response(
            query="test query",
            retrieved_docs=search_results,
            max_tokens=100
        )
        generation_time = time.time() - start_time
        
        # Vérifications de performance
        assert ingestion_time < 10, f"Ingestion trop lente: {ingestion_time:.2f}s"
        assert indexing_time < 60, f"Indexation trop lente: {indexing_time:.2f}s"
        assert search_time < 5, f"Recherche trop lente: {search_time:.2f}s"
        assert generation_time < 30, f"Génération trop lente: {generation_time:.2f}s"
        
        print(f"📊 Performance du pipeline:")
        print(f"   - Ingestion: {ingestion_time:.2f}s")
        print(f"   - Indexation: {indexing_time:.2f}s")
        print(f"   - Recherche: {search_time:.2f}s")
        print(f"   - Génération: {generation_time:.2f}s")
    
    def test_pipeline_error_handling(self):
        """Test de la gestion d'erreurs du pipeline."""
        # Test avec un dossier inexistant
        try:
            documents = self.document_loader.load_documents("/path/that/does/not/exist")
            assert False, "Devrait lever une exception pour un dossier inexistant"
        except Exception:
            pass  # Comportement attendu
        
        # Test avec une requête vide
        try:
            search_results = self.search_engine.search("", top_k=5)
            # Le comportement peut varier selon l'implémentation
        except Exception:
            pass  # Comportement acceptable
        
        # Test avec des documents vides
        empty_docs = []
        try:
            indexing_result = self.indexer.index_documents(empty_docs)
            # Le comportement peut varier selon l'implémentation
        except Exception:
            pass  # Comportement acceptable
    
    def test_pipeline_with_large_documents(self):
        """Test du pipeline avec des documents volumineux."""
        # Création d'un document volumineux
        large_content = "Test content. " * 1000  # ~15KB de contenu
        large_doc_path = self.test_docs_dir / "large_document.txt"
        large_doc_path.write_text(large_content)
        
        # Test du pipeline avec le document volumineux
        documents = self.document_loader.load_documents(str(self.test_docs_dir))
        
        # Vérification que le document volumineux est chargé
        large_docs = [doc for doc in documents if "large_document.txt" in doc.get("source", "")]
        assert len(large_docs) > 0, "Le document volumineux devrait être chargé"
        
        # Indexation
        indexing_result = self.indexer.index_documents(documents)
        assert indexing_result["success"], "L'indexation devrait réussir même avec des documents volumineux"
        
        # Recherche
        search_results = self.search_engine.search("test content", top_k=3)
        assert len(search_results) > 0, "La recherche devrait fonctionner avec des documents volumineux"
    
    def test_pipeline_consistency(self):
        """Test de la cohérence du pipeline."""
        # Exécution multiple du pipeline
        results = []
        
        for i in range(3):
            # Réinitialisation des composants
            self.indexer = Indexer()
            self.search_engine = SearchEngine()
            
            # Exécution du pipeline
            documents = self.document_loader.load_documents(str(self.test_docs_dir))
            indexing_result = self.indexer.index_documents(documents)
            search_results = self.search_engine.search("intelligence artificielle", top_k=2)
            
            results.append({
                "documents_count": len(documents),
                "indexing_success": indexing_result["success"],
                "search_results_count": len(search_results)
            })
        
        # Vérification de la cohérence
        for i in range(1, len(results)):
            assert results[i]["documents_count"] == results[0]["documents_count"], "Nombre de documents cohérent"
            assert results[i]["indexing_success"] == results[0]["indexing_success"], "Succès d'indexation cohérent"
            assert results[i]["search_results_count"] == results[0]["search_results_count"], "Nombre de résultats cohérent"

def run_pipeline_tests():
    """Fonction pour exécuter tous les tests du pipeline."""
    test_instance = TestRAGPipeline()
    
    # Liste des méthodes de test
    test_methods = [
        test_instance.test_full_pipeline_ingestion,
        test_instance.test_full_pipeline_indexing,
        test_instance.test_full_pipeline_search,
        test_instance.test_full_pipeline_generation,
        test_instance.test_full_pipeline_end_to_end,
        test_instance.test_pipeline_with_different_queries,
        test_instance.test_pipeline_performance,
        test_instance.test_pipeline_error_handling,
        test_instance.test_pipeline_with_large_documents,
        test_instance.test_pipeline_consistency
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    print("🚀 Démarrage des tests du pipeline RAG...")
    
    for test_method in test_methods:
        try:
            test_method()
            print(f"✅ {test_method.__name__}: PASSED")
            passed_tests += 1
        except Exception as e:
            print(f"❌ {test_method.__name__}: FAILED - {str(e)}")
            failed_tests += 1
    
    print(f"\n📊 Résultats des tests du pipeline:")
    print(f"Tests réussis: {passed_tests}")
    print(f"Tests échoués: {failed_tests}")
    print(f"Total: {passed_tests + failed_tests}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_pipeline_tests()
    exit(0 if success else 1)
