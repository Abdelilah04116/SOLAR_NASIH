"""
Tests unitaires pour les retrievers dans le système RAG multimodal.
Teste les différents types de retrievers (vectoriel, keyword, hybride).
"""

import pytest
import numpy as np
from typing import List, Dict, Any
import tempfile
from pathlib import Path

# Import des modules à tester
from src.retrieval.retrievers.vector_retriever import VectorRetriever
from src.retrieval.retrievers.keyword_retriever import KeywordRetriever
from src.retrieval.retrievers.hybrid_retriever import HybridRetriever
from src.retrieval.search_engine import SearchEngine

class TestVectorRetriever:
    """Tests pour le retriever vectoriel."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.vector_retriever = VectorRetriever()
        self.test_documents = self._create_test_documents()
        self.test_embeddings = self._create_test_embeddings()
    
    def _create_test_documents(self) -> List[Dict[str, Any]]:
        """Crée des documents de test."""
        return [
            {
                "id": "doc1",
                "content": "L'intelligence artificielle est un domaine fascinant.",
                "source": "document1.txt",
                "metadata": {"author": "Test Author", "date": "2024-01-01"}
            },
            {
                "id": "doc2",
                "content": "Le machine learning utilise des algorithmes pour apprendre.",
                "source": "document2.txt",
                "metadata": {"author": "Test Author", "date": "2024-01-02"}
            },
            {
                "id": "doc3",
                "content": "Les réseaux de neurones sont inspirés du cerveau humain.",
                "source": "document3.txt",
                "metadata": {"author": "Test Author", "date": "2024-01-03"}
            },
            {
                "id": "doc4",
                "content": "La cuisine française est réputée dans le monde entier.",
                "source": "document4.txt",
                "metadata": {"author": "Test Author", "date": "2024-01-04"}
            }
        ]
    
    def _create_test_embeddings(self) -> Dict[str, np.ndarray]:
        """Crée des embeddings de test."""
        # Création d'embeddings simulés
        embeddings = {}
        for i, doc in enumerate(self.test_documents):
            # Embedding simulé basé sur l'index
            embedding = np.random.rand(384)  # Dimension simulée
            embedding = embedding / np.linalg.norm(embedding)  # Normalisation
            embeddings[doc["id"]] = embedding
        return embeddings
    
    def test_vector_retriever_initialization(self):
        """Test d'initialisation du retriever vectoriel."""
        assert self.vector_retriever is not None, "Le retriever vectoriel doit être initialisé"
    
    def test_vector_retriever_search(self):
        """Test de recherche vectorielle."""
        query = "intelligence artificielle"
        query_embedding = np.random.rand(384)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        results = self.vector_retriever.search(
            query_embedding=query_embedding,
            documents=self.test_documents,
            embeddings=self.test_embeddings,
            top_k=3
        )
        
        assert len(results) <= 3, "Le nombre de résultats doit respecter top_k"
        assert all("score" in result for result in results), "Chaque résultat doit avoir un score"
        assert all("content" in result for result in results), "Chaque résultat doit avoir un contenu"
    
    def test_vector_retriever_similarity_calculation(self):
        """Test de calcul de similarité vectorielle."""
        # Test avec des vecteurs identiques
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([1, 0, 0])
        similarity = self.vector_retriever._calculate_similarity(vec1, vec2)
        assert abs(similarity - 1.0) < 1e-6, "Vecteurs identiques doivent avoir une similarité de 1"
        
        # Test avec des vecteurs orthogonaux
        vec3 = np.array([0, 1, 0])
        similarity = self.vector_retriever._calculate_similarity(vec1, vec3)
        assert abs(similarity - 0.0) < 1e-6, "Vecteurs orthogonaux doivent avoir une similarité de 0"
    
    def test_vector_retriever_ranking(self):
        """Test de classement des résultats."""
        query_embedding = np.random.rand(384)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        results = self.vector_retriever.search(
            query_embedding=query_embedding,
            documents=self.test_documents,
            embeddings=self.test_embeddings,
            top_k=4
        )
        
        # Vérification que les résultats sont triés par score décroissant
        scores = [result["score"] for result in results]
        assert scores == sorted(scores, reverse=True), "Les résultats doivent être triés par score décroissant"
    
    def test_vector_retriever_empty_results(self):
        """Test de recherche avec résultats vides."""
        query_embedding = np.random.rand(384)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        results = self.vector_retriever.search(
            query_embedding=query_embedding,
            documents=[],
            embeddings={},
            top_k=3
        )
        
        assert len(results) == 0, "La recherche avec documents vides doit retourner une liste vide"
    
    def test_vector_retriever_threshold_filtering(self):
        """Test de filtrage par seuil de similarité."""
        query_embedding = np.random.rand(384)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        results = self.vector_retriever.search(
            query_embedding=query_embedding,
            documents=self.test_documents,
            embeddings=self.test_embeddings,
            top_k=10,
            threshold=0.5
        )
        
        # Vérification que tous les résultats respectent le seuil
        for result in results:
            assert result["score"] >= 0.5, "Tous les résultats doivent respecter le seuil de similarité"

class TestKeywordRetriever:
    """Tests pour le retriever par mots-clés."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.keyword_retriever = KeywordRetriever()
        self.test_documents = [
            {
                "id": "doc1",
                "content": "L'intelligence artificielle est un domaine fascinant.",
                "source": "document1.txt"
            },
            {
                "id": "doc2",
                "content": "Le machine learning utilise des algorithmes pour apprendre.",
                "source": "document2.txt"
            },
            {
                "id": "doc3",
                "content": "Les réseaux de neurones sont inspirés du cerveau humain.",
                "source": "document3.txt"
            }
        ]
    
    def test_keyword_retriever_initialization(self):
        """Test d'initialisation du retriever par mots-clés."""
        assert self.keyword_retriever is not None, "Le retriever par mots-clés doit être initialisé"
    
    def test_keyword_retriever_search(self):
        """Test de recherche par mots-clés."""
        query = "intelligence artificielle"
        
        results = self.keyword_retriever.search(
            query=query,
            documents=self.test_documents,
            top_k=3
        )
        
        assert len(results) <= 3, "Le nombre de résultats doit respecter top_k"
        assert all("score" in result for result in results), "Chaque résultat doit avoir un score"
        assert all("content" in result for result in results), "Chaque résultat doit avoir un contenu"
    
    def test_keyword_retriever_exact_match(self):
        """Test de correspondance exacte."""
        query = "intelligence artificielle"
        
        results = self.keyword_retriever.search(
            query=query,
            documents=self.test_documents,
            top_k=3
        )
        
        # Le document contenant "intelligence artificielle" devrait être trouvé
        found = any("intelligence artificielle" in result["content"] for result in results)
        assert found, "Le document avec correspondance exacte devrait être trouvé"
    
    def test_keyword_retriever_partial_match(self):
        """Test de correspondance partielle."""
        query = "machine"
        
        results = self.keyword_retriever.search(
            query=query,
            documents=self.test_documents,
            top_k=3
        )
        
        # Le document contenant "machine learning" devrait être trouvé
        found = any("machine learning" in result["content"] for result in results)
        assert found, "Le document avec correspondance partielle devrait être trouvé"
    
    def test_keyword_retriever_case_insensitive(self):
        """Test de recherche insensible à la casse."""
        query = "INTELLIGENCE ARTIFICIELLE"
        
        results = self.keyword_retriever.search(
            query=query,
            documents=self.test_documents,
            top_k=3
        )
        
        # Le document devrait être trouvé malgré la différence de casse
        found = any("intelligence artificielle" in result["content"].lower() for result in results)
        assert found, "La recherche devrait être insensible à la casse"
    
    def test_keyword_retriever_no_match(self):
        """Test de recherche sans correspondance."""
        query = "cuisine française"
        
        results = self.keyword_retriever.search(
            query=query,
            documents=self.test_documents,
            top_k=3
        )
        
        # Aucun document ne devrait correspondre
        assert len(results) == 0, "Aucun résultat ne devrait être trouvé pour cette requête"
    
    def test_keyword_retriever_ranking(self):
        """Test de classement des résultats par mots-clés."""
        query = "intelligence machine"
        
        results = self.keyword_retriever.search(
            query=query,
            documents=self.test_documents,
            top_k=3
        )
        
        # Vérification que les résultats sont triés par score décroissant
        scores = [result["score"] for result in results]
        assert scores == sorted(scores, reverse=True), "Les résultats doivent être triés par score décroissant"

class TestHybridRetriever:
    """Tests pour le retriever hybride."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.hybrid_retriever = HybridRetriever()
        self.test_documents = [
            {
                "id": "doc1",
                "content": "L'intelligence artificielle est un domaine fascinant.",
                "source": "document1.txt"
            },
            {
                "id": "doc2",
                "content": "Le machine learning utilise des algorithmes pour apprendre.",
                "source": "document2.txt"
            },
            {
                "id": "doc3",
                "content": "Les réseaux de neurones sont inspirés du cerveau humain.",
                "source": "document3.txt"
            }
        ]
        self.test_embeddings = {
            "doc1": np.random.rand(384),
            "doc2": np.random.rand(384),
            "doc3": np.random.rand(384)
        }
    
    def test_hybrid_retriever_initialization(self):
        """Test d'initialisation du retriever hybride."""
        assert self.hybrid_retriever is not None, "Le retriever hybride doit être initialisé"
    
    def test_hybrid_retriever_search(self):
        """Test de recherche hybride."""
        query = "intelligence artificielle"
        query_embedding = np.random.rand(384)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        results = self.hybrid_retriever.search(
            query=query,
            query_embedding=query_embedding,
            documents=self.test_documents,
            embeddings=self.test_embeddings,
            top_k=3
        )
        
        assert len(results) <= 3, "Le nombre de résultats doit respecter top_k"
        assert all("score" in result for result in results), "Chaque résultat doit avoir un score"
        assert all("content" in result for result in results), "Chaque résultat doit avoir un contenu"
    
    def test_hybrid_retriever_fusion_strategies(self):
        """Test des stratégies de fusion."""
        query = "intelligence artificielle"
        query_embedding = np.random.rand(384)
        query_embedding = query_embedding / np.linalg.norm(query_embedding)
        
        # Test avec fusion pondérée
        results_weighted = self.hybrid_retriever.search(
            query=query,
            query_embedding=query_embedding,
            documents=self.test_documents,
            embeddings=self.test_embeddings,
            top_k=3,
            fusion_strategy="weighted"
        )
        
        # Test avec fusion par score maximum
        results_max = self.hybrid_retriever.search(
            query=query,
            query_embedding=query_embedding,
            documents=self.test_documents,
            embeddings=self.test_embeddings,
            top_k=3,
            fusion_strategy="max"
        )
        
        assert len(results_weighted) > 0, "Recherche avec fusion pondérée"
        assert len(results_max) > 0, "Recherche avec fusion par maximum"
    
    def test_hybrid_retriever_score_fusion(self):
        """Test de fusion des scores."""
        vector_scores = {"doc1": 0.9, "doc2": 0.7, "doc3": 0.5}
        keyword_scores = {"doc1": 0.8, "doc2": 0.9, "doc3": 0.3}
        
        # Test fusion pondérée
        fused_scores = self.hybrid_retriever._fuse_scores(
            vector_scores, keyword_scores, strategy="weighted", weights=[0.6, 0.4]
        )
        
        assert "doc1" in fused_scores, "Le document doc1 doit être dans les scores fusionnés"
        assert "doc2" in fused_scores, "Le document doc2 doit être dans les scores fusionnés"
        assert "doc3" in fused_scores, "Le document doc3 doit être dans les scores fusionnés"
        
        # Test fusion par maximum
        fused_scores_max = self.hybrid_retriever._fuse_scores(
            vector_scores, keyword_scores, strategy="max"
        )
        
        assert len(fused_scores_max) == len(vector_scores), "Tous les documents doivent avoir un score fusionné"
    
    def test_hybrid_retriever_weights_validation(self):
        """Test de validation des poids de fusion."""
        vector_scores = {"doc1": 0.9}
        keyword_scores = {"doc1": 0.8}
        
        # Test avec des poids valides
        try:
            self.hybrid_retriever._fuse_scores(
                vector_scores, keyword_scores, strategy="weighted", weights=[0.6, 0.4]
            )
        except ValueError:
            pytest.fail("Fusion avec poids valides ne devrait pas lever d'exception")
        
        # Test avec des poids invalides
        with pytest.raises(ValueError):
            self.hybrid_retriever._fuse_scores(
                vector_scores, keyword_scores, strategy="weighted", weights=[0.6, 0.6]  # Somme > 1
            )

class TestSearchEngine:
    """Tests pour le moteur de recherche principal."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.search_engine = SearchEngine()
        self.test_documents = [
            {
                "id": "doc1",
                "content": "L'intelligence artificielle est un domaine fascinant.",
                "source": "document1.txt"
            },
            {
                "id": "doc2",
                "content": "Le machine learning utilise des algorithmes pour apprendre.",
                "source": "document2.txt"
            },
            {
                "id": "doc3",
                "content": "Les réseaux de neurones sont inspirés du cerveau humain.",
                "source": "document3.txt"
            }
        ]
    
    def test_search_engine_initialization(self):
        """Test d'initialisation du moteur de recherche."""
        assert self.search_engine is not None, "Le moteur de recherche doit être initialisé"
    
    def test_search_engine_semantic_search(self):
        """Test de recherche sémantique."""
        query = "intelligence artificielle"
        
        results = self.search_engine.search(
            query=query,
            search_type="semantic",
            top_k=3
        )
        
        assert len(results) <= 3, "Le nombre de résultats doit respecter top_k"
        assert all("score" in result for result in results), "Chaque résultat doit avoir un score"
    
    def test_search_engine_keyword_search(self):
        """Test de recherche par mots-clés."""
        query = "machine learning"
        
        results = self.search_engine.search(
            query=query,
            search_type="keyword",
            top_k=3
        )
        
        assert len(results) <= 3, "Le nombre de résultats doit respecter top_k"
        assert all("score" in result for result in results), "Chaque résultat doit avoir un score"
    
    def test_search_engine_hybrid_search(self):
        """Test de recherche hybride."""
        query = "intelligence artificielle"
        
        results = self.search_engine.search(
            query=query,
            search_type="hybrid",
            top_k=3
        )
        
        assert len(results) <= 3, "Le nombre de résultats doit respecter top_k"
        assert all("score" in result for result in results), "Chaque résultat doit avoir un score"
    
    def test_search_engine_invalid_search_type(self):
        """Test de recherche avec type invalide."""
        query = "test query"
        
        with pytest.raises(ValueError):
            self.search_engine.search(
                query=query,
                search_type="invalid_type",
                top_k=3
            )
    
    def test_search_engine_filters(self):
        """Test de recherche avec filtres."""
        query = "intelligence"
        
        filters = {
            "source": "document1.txt"
        }
        
        results = self.search_engine.search(
            query=query,
            search_type="keyword",
            top_k=3,
            filters=filters
        )
        
        # Vérification que tous les résultats respectent le filtre
        for result in results:
            assert result["source"] == "document1.txt", "Tous les résultats doivent respecter le filtre"
    
    def test_search_engine_threshold_filtering(self):
        """Test de filtrage par seuil."""
        query = "intelligence"
        
        results = self.search_engine.search(
            query=query,
            search_type="semantic",
            top_k=10,
            threshold=0.5
        )
        
        # Vérification que tous les résultats respectent le seuil
        for result in results:
            assert result["score"] >= 0.5, "Tous les résultats doivent respecter le seuil"

class TestRetrieverUtilities:
    """Tests pour les utilitaires des retrievers."""
    
    def test_document_preprocessing(self):
        """Test de prétraitement des documents."""
        from src.retrieval.retrievers.vector_retriever import VectorRetriever
        
        vector_retriever = VectorRetriever()
        
        raw_document = "  Document avec   espaces   multiples  \n\n  "
        processed_document = vector_retriever._preprocess_document(raw_document)
        
        assert processed_document == "Document avec espaces multiples", "Le document doit être prétraité"
    
    def test_score_normalization(self):
        """Test de normalisation des scores."""
        from src.retrieval.retrievers.vector_retriever import VectorRetriever
        
        vector_retriever = VectorRetriever()
        
        scores = [0.1, 0.5, 0.9, 0.3]
        normalized_scores = vector_retriever._normalize_scores(scores)
        
        assert len(normalized_scores) == len(scores), "Le nombre de scores doit être préservé"
        assert all(0 <= score <= 1 for score in normalized_scores), "Tous les scores doivent être entre 0 et 1"
    
    def test_result_formatting(self):
        """Test de formatage des résultats."""
        from src.retrieval.retrievers.vector_retriever import VectorRetriever
        
        vector_retriever = VectorRetriever()
        
        raw_results = [
            {"id": "doc1", "content": "Test content", "score": 0.9},
            {"id": "doc2", "content": "Another content", "score": 0.7}
        ]
        
        formatted_results = vector_retriever._format_results(raw_results)
        
        assert len(formatted_results) == len(raw_results), "Le nombre de résultats doit être préservé"
        assert all("score" in result for result in formatted_results), "Tous les résultats doivent avoir un score"
        assert all("content" in result for result in formatted_results), "Tous les résultats doivent avoir un contenu"

def run_retriever_tests():
    """Fonction pour exécuter tous les tests de retrievers."""
    test_classes = [
        TestVectorRetriever,
        TestKeywordRetriever,
        TestHybridRetriever,
        TestSearchEngine,
        TestRetrieverUtilities
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    print("🚀 Démarrage des tests de retrievers...")
    
    for test_class in test_classes:
        test_instance = test_class()
        
        # Récupération de toutes les méthodes de test
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for method_name in test_methods:
            try:
                method = getattr(test_instance, method_name)
                method()
                print(f"✅ {test_class.__name__}.{method_name}: PASSED")
                passed_tests += 1
            except Exception as e:
                print(f"❌ {test_class.__name__}.{method_name}: FAILED - {str(e)}")
                failed_tests += 1
    
    print(f"\n📊 Résultats des tests de retrievers:")
    print(f"Tests réussis: {passed_tests}")
    print(f"Tests échoués: {failed_tests}")
    print(f"Total: {passed_tests + failed_tests}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_retriever_tests()
    exit(0 if success else 1)
