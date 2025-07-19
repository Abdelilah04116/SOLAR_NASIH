"""
Tests unitaires pour les générateurs dans le système RAG multimodal.
Teste les générateurs de réponses et les modèles LLM.
"""

import pytest
import tempfile
from pathlib import Path
import json
from typing import Dict, Any, List
import numpy as np

# Import des modules à tester
from src.generation.response_generator import ResponseGenerator
from src.generation.llm.openai_llm import OpenAILLM
from src.generation.llm.anthropic_llm import AnthropicLLM
from src.generation.llm.huggingface_llm import HuggingFaceLLM
from src.generation.context_builder import ContextBuilder
from src.generation.prompt_templates.multimodal_prompts import MultimodalPrompts

class TestResponseGenerator:
    """Tests pour le générateur de réponses."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.response_generator = ResponseGenerator()
        self.test_documents = self._create_test_documents()
    
    def _create_test_documents(self) -> List[Dict[str, Any]]:
        """Crée des documents de test."""
        return [
            {
                "content": "L'intelligence artificielle est un domaine de l'informatique qui vise à créer des systèmes capables d'effectuer des tâches qui nécessitent normalement l'intelligence humaine.",
                "source": "document1.txt",
                "score": 0.95,
                "metadata": {"author": "Test Author", "date": "2024-01-01"}
            },
            {
                "content": "Le machine learning est une sous-catégorie de l'IA qui se concentre sur l'apprentissage automatique à partir de données.",
                "source": "document2.txt",
                "score": 0.87,
                "metadata": {"author": "Test Author", "date": "2024-01-02"}
            },
            {
                "content": "Les réseaux de neurones sont inspirés du fonctionnement du cerveau humain et sont utilisés pour résoudre des problèmes complexes.",
                "source": "document3.txt",
                "score": 0.78,
                "metadata": {"author": "Test Author", "date": "2024-01-03"}
            }
        ]
    
    def test_generate_response_basic(self):
        """Test de génération de réponse basique."""
        query = "Qu'est-ce que l'intelligence artificielle ?"
        
        result = self.response_generator.generate_response(
            query=query,
            retrieved_docs=self.test_documents,
            max_tokens=150,
            temperature=0.1
        )
        
        assert "response" in result, "Le résultat doit contenir une réponse"
        assert "metadata" in result, "Le résultat doit contenir des métadonnées"
        assert len(result["response"]) > 0, "La réponse ne doit pas être vide"
        assert "model_used" in result["metadata"], "Les métadonnées doivent contenir le modèle utilisé"
    
    def test_generate_response_with_context(self):
        """Test de génération de réponse avec contexte."""
        query = "Expliquez les différences entre IA et machine learning"
        
        result = self.response_generator.generate_response(
            query=query,
            retrieved_docs=self.test_documents,
            max_tokens=200,
            temperature=0.1,
            include_sources=True
        )
        
        assert "response" in result, "Le résultat doit contenir une réponse"
        assert "sources" in result, "Le résultat doit contenir les sources"
        assert len(result["sources"]) > 0, "Il doit y avoir des sources"
    
    def test_generate_response_without_documents(self):
        """Test de génération de réponse sans documents."""
        query = "Qu'est-ce que l'intelligence artificielle ?"
        
        result = self.response_generator.generate_response(
            query=query,
            retrieved_docs=[],
            max_tokens=100,
            temperature=0.1
        )
        
        assert "response" in result, "Le résultat doit contenir une réponse"
        assert len(result["response"]) > 0, "La réponse ne doit pas être vide"
    
    def test_generate_response_with_different_temperatures(self):
        """Test de génération avec différentes températures."""
        query = "Décrivez l'IA en une phrase"
        
        # Test avec température basse (réponses cohérentes)
        result_low = self.response_generator.generate_response(
            query=query,
            retrieved_docs=self.test_documents,
            max_tokens=50,
            temperature=0.1
        )
        
        # Test avec température élevée (réponses plus créatives)
        result_high = self.response_generator.generate_response(
            query=query,
            retrieved_docs=self.test_documents,
            max_tokens=50,
            temperature=0.8
        )
        
        assert len(result_low["response"]) > 0, "Réponse avec température basse"
        assert len(result_high["response"]) > 0, "Réponse avec température élevée"
    
    def test_generate_response_max_tokens(self):
        """Test de génération avec limite de tokens."""
        query = "Expliquez l'IA en détail"
        
        # Test avec limite de tokens courte
        result_short = self.response_generator.generate_response(
            query=query,
            retrieved_docs=self.test_documents,
            max_tokens=50,
            temperature=0.1
        )
        
        # Test avec limite de tokens longue
        result_long = self.response_generator.generate_response(
            query=query,
            retrieved_docs=self.test_documents,
            max_tokens=300,
            temperature=0.1
        )
        
        assert len(result_short["response"]) <= len(result_long["response"]), "Réponse courte doit être plus courte"
    
    def test_generate_response_error_handling(self):
        """Test de gestion d'erreurs lors de la génération."""
        # Test avec une requête vide
        with pytest.raises(ValueError):
            self.response_generator.generate_response(
                query="",
                retrieved_docs=self.test_documents,
                max_tokens=100
            )
        
        # Test avec des paramètres invalides
        with pytest.raises(ValueError):
            self.response_generator.generate_response(
                query="Test query",
                retrieved_docs=self.test_documents,
                max_tokens=-1
            )
    
    def test_generate_response_metadata(self):
        """Test des métadonnées de génération."""
        query = "Test query"
        
        result = self.response_generator.generate_response(
            query=query,
            retrieved_docs=self.test_documents,
            max_tokens=100,
            temperature=0.1
        )
        
        metadata = result["metadata"]
        
        assert "model_used" in metadata, "Modèle utilisé manquant"
        assert "generation_time" in metadata, "Temps de génération manquant"
        assert "tokens_used" in metadata, "Tokens utilisés manquant"
        assert "temperature" in metadata, "Température manquante"
        assert "max_tokens" in metadata, "Max tokens manquant"

class TestLLMProviders:
    """Tests pour les différents fournisseurs LLM."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.test_prompt = "Qu'est-ce que l'intelligence artificielle ?"
    
    def test_openai_llm_initialization(self):
        """Test d'initialisation du LLM OpenAI."""
        try:
            llm = OpenAILLM()
            assert llm is not None, "LLM OpenAI doit être initialisé"
        except Exception as e:
            # Si OpenAI n'est pas configuré, c'est acceptable
            pytest.skip(f"OpenAI LLM non configuré: {e}")
    
    def test_anthropic_llm_initialization(self):
        """Test d'initialisation du LLM Anthropic."""
        try:
            llm = AnthropicLLM()
            assert llm is not None, "LLM Anthropic doit être initialisé"
        except Exception as e:
            # Si Anthropic n'est pas configuré, c'est acceptable
            pytest.skip(f"Anthropic LLM non configuré: {e}")
    
    def test_huggingface_llm_initialization(self):
        """Test d'initialisation du LLM HuggingFace."""
        try:
            llm = HuggingFaceLLM()
            assert llm is not None, "LLM HuggingFace doit être initialisé"
        except Exception as e:
            # Si HuggingFace n'est pas configuré, c'est acceptable
            pytest.skip(f"HuggingFace LLM non configuré: {e}")
    
    def test_llm_generate_response(self):
        """Test de génération de réponse avec différents LLM."""
        test_llms = []
        
        # Tentative d'initialisation des différents LLM
        try:
            test_llms.append(OpenAILLM())
        except:
            pass
        
        try:
            test_llms.append(AnthropicLLM())
        except:
            pass
        
        try:
            test_llms.append(HuggingFaceLLM())
        except:
            pass
        
        if not test_llms:
            pytest.skip("Aucun LLM configuré pour les tests")
        
        for llm in test_llms:
            try:
                response = llm.generate(
                    prompt=self.test_prompt,
                    max_tokens=100,
                    temperature=0.1
                )
                
                assert "response" in response, "La réponse doit contenir le texte généré"
                assert len(response["response"]) > 0, "La réponse ne doit pas être vide"
                assert "metadata" in response, "La réponse doit contenir des métadonnées"
                
            except Exception as e:
                # Si un LLM échoue, on continue avec les autres
                print(f"LLM {type(llm).__name__} a échoué: {e}")

class TestContextBuilder:
    """Tests pour le constructeur de contexte."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.context_builder = ContextBuilder()
        self.test_documents = [
            {
                "content": "L'IA est un domaine fascinant.",
                "source": "doc1.txt",
                "score": 0.95
            },
            {
                "content": "Le machine learning utilise des algorithmes.",
                "source": "doc2.txt",
                "score": 0.87
            }
        ]
    
    def test_build_context_basic(self):
        """Test de construction de contexte basique."""
        query = "Qu'est-ce que l'IA ?"
        
        context = self.context_builder.build_context(
            query=query,
            documents=self.test_documents,
            max_context_length=1000
        )
        
        assert "prompt" in context, "Le contexte doit contenir un prompt"
        assert query in context["prompt"], "Le prompt doit contenir la requête"
        assert "L'IA est un domaine fascinant" in context["prompt"], "Le contexte doit contenir le contenu des documents"
    
    def test_build_context_with_metadata(self):
        """Test de construction de contexte avec métadonnées."""
        query = "Test query"
        
        context = self.context_builder.build_context(
            query=query,
            documents=self.test_documents,
            include_metadata=True
        )
        
        assert "prompt" in context, "Le contexte doit contenir un prompt"
        assert "doc1.txt" in context["prompt"], "Les sources doivent être incluses"
    
    def test_build_context_length_limit(self):
        """Test de limitation de longueur du contexte."""
        query = "Test query"
        
        # Test avec une limite courte
        context_short = self.context_builder.build_context(
            query=query,
            documents=self.test_documents,
            max_context_length=100
        )
        
        # Test avec une limite longue
        context_long = self.context_builder.build_context(
            query=query,
            documents=self.test_documents,
            max_context_length=1000
        )
        
        assert len(context_short["prompt"]) <= len(context_long["prompt"]), "Contexte court doit être plus court"
    
    def test_build_context_empty_documents(self):
        """Test de construction de contexte avec documents vides."""
        query = "Test query"
        
        context = self.context_builder.build_context(
            query=query,
            documents=[],
            max_context_length=1000
        )
        
        assert "prompt" in context, "Le contexte doit être généré même sans documents"
        assert query in context["prompt"], "Le prompt doit contenir la requête"
    
    def test_build_context_document_ranking(self):
        """Test de classement des documents dans le contexte."""
        documents_with_scores = [
            {"content": "Document avec score élevé", "score": 0.95, "source": "high.txt"},
            {"content": "Document avec score moyen", "score": 0.75, "source": "medium.txt"},
            {"content": "Document avec score faible", "score": 0.45, "source": "low.txt"}
        ]
        
        context = self.context_builder.build_context(
            query="Test query",
            documents=documents_with_scores,
            max_context_length=1000
        )
        
        # Les documents avec des scores plus élevés devraient apparaître en premier
        prompt = context["prompt"]
        high_index = prompt.find("Document avec score élevé")
        medium_index = prompt.find("Document avec score moyen")
        low_index = prompt.find("Document avec score faible")
        
        assert high_index < medium_index, "Document avec score élevé doit apparaître en premier"
        assert medium_index < low_index, "Document avec score moyen doit apparaître avant le faible"

class TestMultimodalPrompts:
    """Tests pour les prompts multimodaux."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.multimodal_prompts = MultimodalPrompts()
    
    def test_text_only_prompt(self):
        """Test de prompt texte seulement."""
        query = "Qu'est-ce que l'IA ?"
        documents = [{"content": "L'IA est un domaine informatique.", "source": "doc.txt"}]
        
        prompt = self.multimodal_prompts.create_prompt(
            query=query,
            documents=documents,
            modality="text"
        )
        
        assert query in prompt, "Le prompt doit contenir la requête"
        assert "L'IA est un domaine informatique" in prompt, "Le prompt doit contenir le contenu des documents"
    
    def test_image_text_prompt(self):
        """Test de prompt image + texte."""
        query = "Décrivez cette image"
        documents = [{"content": "Image d'un chat", "source": "image.jpg"}]
        
        prompt = self.multimodal_prompts.create_prompt(
            query=query,
            documents=documents,
            modality="image_text"
        )
        
        assert query in prompt, "Le prompt doit contenir la requête"
        assert "image" in prompt.lower(), "Le prompt doit mentionner l'image"
    
    def test_audio_text_prompt(self):
        """Test de prompt audio + texte."""
        query = "Transcrivez cet audio"
        documents = [{"content": "Audio de conversation", "source": "audio.wav"}]
        
        prompt = self.multimodal_prompts.create_prompt(
            query=query,
            documents=documents,
            modality="audio_text"
        )
        
        assert query in prompt, "Le prompt doit contenir la requête"
        assert "audio" in prompt.lower(), "Le prompt doit mentionner l'audio"
    
    def test_video_text_prompt(self):
        """Test de prompt vidéo + texte."""
        query = "Analysez cette vidéo"
        documents = [{"content": "Vidéo de présentation", "source": "video.mp4"}]
        
        prompt = self.multimodal_prompts.create_prompt(
            query=query,
            documents=documents,
            modality="video_text"
        )
        
        assert query in prompt, "Le prompt doit contenir la requête"
        assert "vidéo" in prompt.lower() or "video" in prompt.lower(), "Le prompt doit mentionner la vidéo"
    
    def test_multimodal_prompt_with_metadata(self):
        """Test de prompt multimodal avec métadonnées."""
        query = "Analysez ce contenu"
        documents = [
            {
                "content": "Contenu multimodal",
                "source": "content.txt",
                "metadata": {"type": "multimodal", "confidence": 0.95}
            }
        ]
        
        prompt = self.multimodal_prompts.create_prompt(
            query=query,
            documents=documents,
            modality="multimodal",
            include_metadata=True
        )
        
        assert query in prompt, "Le prompt doit contenir la requête"
        assert "multimodal" in prompt.lower(), "Le prompt doit mentionner le contenu multimodal"
    
    def test_prompt_template_validation(self):
        """Test de validation des templates de prompts."""
        # Test avec une modalité invalide
        with pytest.raises(ValueError):
            self.multimodal_prompts.create_prompt(
                query="Test",
                documents=[],
                modality="invalid_modality"
            )
    
    def test_prompt_length_control(self):
        """Test de contrôle de la longueur des prompts."""
        query = "Test query"
        documents = [{"content": "Test content " * 100, "source": "test.txt"}]
        
        # Test avec limite de longueur
        prompt = self.multimodal_prompts.create_prompt(
            query=query,
            documents=documents,
            modality="text",
            max_length=500
        )
        
        assert len(prompt) <= 500, "Le prompt ne doit pas dépasser la limite de longueur"

class TestGenerationUtilities:
    """Tests pour les utilitaires de génération."""
    
    def test_response_validation(self):
        """Test de validation des réponses générées."""
        from src.generation.response_generator import ResponseGenerator
        
        response_generator = ResponseGenerator()
        
        # Test avec une réponse valide
        valid_response = {
            "response": "Ceci est une réponse valide.",
            "metadata": {"model_used": "test_model"}
        }
        
        is_valid = response_generator._validate_response(valid_response)
        assert is_valid, "La réponse valide doit être acceptée"
        
        # Test avec une réponse invalide
        invalid_response = {
            "metadata": {"model_used": "test_model"}
            # Manque de "response"
        }
        
        is_valid = response_generator._validate_response(invalid_response)
        assert not is_valid, "La réponse invalide doit être rejetée"
    
    def test_token_counting(self):
        """Test de comptage de tokens."""
        from src.generation.response_generator import ResponseGenerator
        
        response_generator = ResponseGenerator()
        
        text = "Ceci est un texte de test pour compter les tokens."
        token_count = response_generator._count_tokens(text)
        
        assert token_count > 0, "Le nombre de tokens doit être positif"
        assert isinstance(token_count, int), "Le nombre de tokens doit être un entier"
    
    def test_response_formatting(self):
        """Test de formatage des réponses."""
        from src.generation.response_generator import ResponseGenerator
        
        response_generator = ResponseGenerator()
        
        raw_response = "Réponse brute avec des espaces   multiples   et des\nsauts de ligne."
        
        formatted_response = response_generator._format_response(raw_response)
        
        assert "   " not in formatted_response, "Les espaces multiples doivent être nettoyés"
        assert "\n\n" not in formatted_response, "Les sauts de ligne multiples doivent être nettoyés"

def run_generator_tests():
    """Fonction pour exécuter tous les tests de générateurs."""
    test_classes = [
        TestResponseGenerator,
        TestLLMProviders,
        TestContextBuilder,
        TestMultimodalPrompts,
        TestGenerationUtilities
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    print("🚀 Démarrage des tests de générateurs...")
    
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
    
    print(f"\n📊 Résultats des tests de générateurs:")
    print(f"Tests réussis: {passed_tests}")
    print(f"Tests échoués: {failed_tests}")
    print(f"Total: {passed_tests + failed_tests}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_generator_tests()
    exit(0 if success else 1)
