"""
Tests unitaires pour les embeddings dans le système RAG multimodal.
Teste les différents types d'embeddings (texte, image, audio, multimodal).
"""

import pytest
import numpy as np
from typing import List, Dict, Any
import tempfile
from pathlib import Path
import json

# Import des modules à tester
from src.vectorization.embeddings.text_embeddings import TextEmbeddings
from src.vectorization.embeddings.image_embeddings import ImageEmbeddings
from src.vectorization.embeddings.audio_embeddings import AudioEmbeddings
from src.vectorization.embeddings.multimodal_embeddings import MultimodalEmbeddings

class TestTextEmbeddings:
    """Tests pour les embeddings de texte."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.text_embeddings = TextEmbeddings()
        self.test_texts = [
            "L'intelligence artificielle est un domaine fascinant.",
            "Le machine learning utilise des algorithmes pour apprendre.",
            "Les réseaux de neurones sont inspirés du cerveau humain."
        ]
    
    def test_text_embedding_generation(self):
        """Test de génération d'embeddings de texte."""
        for text in self.test_texts:
            embedding = self.text_embeddings.generate_embedding(text)
            
            assert isinstance(embedding, np.ndarray), "L'embedding doit être un numpy array"
            assert embedding.ndim == 1, "L'embedding doit être un vecteur 1D"
            assert embedding.shape[0] > 0, "L'embedding ne doit pas être vide"
    
    def test_text_embedding_dimensions(self):
        """Test des dimensions des embeddings de texte."""
        text = "Test embedding dimensions"
        embedding = self.text_embeddings.generate_embedding(text)
        
        # Vérification que la dimension est cohérente
        expected_dim = self.text_embeddings.get_embedding_dimension()
        assert embedding.shape[0] == expected_dim, f"Dimension attendue: {expected_dim}, obtenue: {embedding.shape[0]}"
    
    def test_text_embedding_similarity(self):
        """Test de similarité entre embeddings de texte."""
        text1 = "L'intelligence artificielle"
        text2 = "L'IA"
        text3 = "La cuisine française"
        
        emb1 = self.text_embeddings.generate_embedding(text1)
        emb2 = self.text_embeddings.generate_embedding(text2)
        emb3 = self.text_embeddings.generate_embedding(text3)
        
        # Calcul des similarités
        sim_1_2 = self.text_embeddings.cosine_similarity(emb1, emb2)
        sim_1_3 = self.text_embeddings.cosine_similarity(emb1, emb3)
        
        # Les textes similaires devraient avoir une similarité plus élevée
        assert sim_1_2 > sim_1_3, "Les textes similaires devraient avoir une similarité plus élevée"
        assert 0 <= sim_1_2 <= 1, "La similarité doit être entre 0 et 1"
        assert 0 <= sim_1_3 <= 1, "La similarité doit être entre 0 et 1"
    
    def test_text_embedding_batch(self):
        """Test de génération d'embeddings en lot."""
        embeddings = self.text_embeddings.generate_embeddings_batch(self.test_texts)
        
        assert len(embeddings) == len(self.test_texts), "Nombre d'embeddings incorrect"
        assert all(isinstance(emb, np.ndarray) for emb in embeddings), "Tous les embeddings doivent être des numpy arrays"
    
    def test_text_embedding_normalization(self):
        """Test de normalisation des embeddings."""
        text = "Test normalization"
        embedding = self.text_embeddings.generate_embedding(text)
        
        # Vérification que l'embedding est normalisé (norme = 1)
        norm = np.linalg.norm(embedding)
        assert abs(norm - 1.0) < 1e-6, f"L'embedding doit être normalisé, norme: {norm}"
    
    def test_text_embedding_empty_input(self):
        """Test avec une entrée vide."""
        with pytest.raises(ValueError):
            self.text_embeddings.generate_embedding("")
    
    def test_text_embedding_large_input(self):
        """Test avec un texte volumineux."""
        large_text = "Test. " * 1000
        embedding = self.text_embeddings.generate_embedding(large_text)
        
        assert isinstance(embedding, np.ndarray), "L'embedding doit être généré même pour un texte volumineux"
        assert embedding.shape[0] > 0, "L'embedding ne doit pas être vide"

class TestImageEmbeddings:
    """Tests pour les embeddings d'images."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.image_embeddings = ImageEmbeddings()
        self.test_image_path = self._create_test_image()
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        if hasattr(self, 'test_image_path') and self.test_image_path.exists():
            self.test_image_path.unlink()
    
    def _create_test_image(self) -> Path:
        """Crée une image de test."""
        try:
            from PIL import Image, ImageDraw
            
            # Création d'une image simple
            img = Image.new('RGB', (100, 100), color='white')
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 80, 80], fill='blue')
            
            # Sauvegarde temporaire
            temp_path = Path(tempfile.mktemp(suffix='.png'))
            img.save(temp_path)
            return temp_path
            
        except ImportError:
            # Si PIL n'est pas disponible, créer un fichier factice
            temp_path = Path(tempfile.mktemp(suffix='.png'))
            temp_path.write_bytes(b'fake_image_data')
            return temp_path
    
    def test_image_embedding_generation(self):
        """Test de génération d'embedding d'image."""
        embedding = self.image_embeddings.generate_embedding(str(self.test_image_path))
        
        assert isinstance(embedding, np.ndarray), "L'embedding doit être un numpy array"
        assert embedding.ndim == 1, "L'embedding doit être un vecteur 1D"
        assert embedding.shape[0] > 0, "L'embedding ne doit pas être vide"
    
    def test_image_embedding_dimensions(self):
        """Test des dimensions des embeddings d'image."""
        embedding = self.image_embeddings.generate_embedding(str(self.test_image_path))
        
        expected_dim = self.image_embeddings.get_embedding_dimension()
        assert embedding.shape[0] == expected_dim, f"Dimension attendue: {expected_dim}, obtenue: {embedding.shape[0]}"
    
    def test_image_embedding_invalid_path(self):
        """Test avec un chemin d'image invalide."""
        with pytest.raises(FileNotFoundError):
            self.image_embeddings.generate_embedding("invalid/path/image.jpg")
    
    def test_image_embedding_batch(self):
        """Test de génération d'embeddings d'images en lot."""
        image_paths = [str(self.test_image_path)] * 3
        embeddings = self.image_embeddings.generate_embeddings_batch(image_paths)
        
        assert len(embeddings) == len(image_paths), "Nombre d'embeddings incorrect"
        assert all(isinstance(emb, np.ndarray) for emb in embeddings), "Tous les embeddings doivent être des numpy arrays"

class TestAudioEmbeddings:
    """Tests pour les embeddings audio."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.audio_embeddings = AudioEmbeddings()
        self.test_audio_path = self._create_test_audio()
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        if hasattr(self, 'test_audio_path') and self.test_audio_path.exists():
            self.test_audio_path.unlink()
    
    def _create_test_audio(self) -> Path:
        """Crée un fichier audio de test."""
        try:
            import wave
            import struct
            
            # Création d'un fichier WAV simple
            temp_path = Path(tempfile.mktemp(suffix='.wav'))
            
            with wave.open(str(temp_path), 'w') as wav_file:
                wav_file.setnchannels(1)  # Mono
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(44100)  # 44.1kHz
                
                # Génération d'un signal simple
                frames = []
                for i in range(4410):  # 0.1 seconde
                    value = int(32767 * 0.1 * np.sin(2 * np.pi * 440 * i / 44100))
                    frames.append(struct.pack('<h', value))
                
                wav_file.writeframes(b''.join(frames))
            
            return temp_path
            
        except ImportError:
            # Si wave n'est pas disponible, créer un fichier factice
            temp_path = Path(tempfile.mktemp(suffix='.wav'))
            temp_path.write_bytes(b'fake_audio_data')
            return temp_path
    
    def test_audio_embedding_generation(self):
        """Test de génération d'embedding audio."""
        embedding = self.audio_embeddings.generate_embedding(str(self.test_audio_path))
        
        assert isinstance(embedding, np.ndarray), "L'embedding doit être un numpy array"
        assert embedding.ndim == 1, "L'embedding doit être un vecteur 1D"
        assert embedding.shape[0] > 0, "L'embedding ne doit pas être vide"
    
    def test_audio_embedding_dimensions(self):
        """Test des dimensions des embeddings audio."""
        embedding = self.audio_embeddings.generate_embedding(str(self.test_audio_path))
        
        expected_dim = self.audio_embeddings.get_embedding_dimension()
        assert embedding.shape[0] == expected_dim, f"Dimension attendue: {expected_dim}, obtenue: {embedding.shape[0]}"
    
    def test_audio_embedding_invalid_path(self):
        """Test avec un chemin audio invalide."""
        with pytest.raises(FileNotFoundError):
            self.audio_embeddings.generate_embedding("invalid/path/audio.wav")

class TestMultimodalEmbeddings:
    """Tests pour les embeddings multimodaux."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.multimodal_embeddings = MultimodalEmbeddings()
        self.test_text = "Description d'une image"
        self.test_image_path = self._create_test_image()
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        if hasattr(self, 'test_image_path') and self.test_image_path.exists():
            self.test_image_path.unlink()
    
    def _create_test_image(self) -> Path:
        """Crée une image de test."""
        try:
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (100, 100), color='white')
            draw = ImageDraw.Draw(img)
            draw.rectangle([20, 20, 80, 80], fill='red')
            
            temp_path = Path(tempfile.mktemp(suffix='.png'))
            img.save(temp_path)
            return temp_path
            
        except ImportError:
            temp_path = Path(tempfile.mktemp(suffix='.png'))
            temp_path.write_bytes(b'fake_image_data')
            return temp_path
    
    def test_multimodal_embedding_generation(self):
        """Test de génération d'embedding multimodal."""
        embedding = self.multimodal_embeddings.generate_multimodal_embedding(
            text=self.test_text,
            image_path=str(self.test_image_path)
        )
        
        assert isinstance(embedding, np.ndarray), "L'embedding doit être un numpy array"
        assert embedding.ndim == 1, "L'embedding doit être un vecteur 1D"
        assert embedding.shape[0] > 0, "L'embedding ne doit pas être vide"
    
    def test_multimodal_embedding_text_only(self):
        """Test d'embedding multimodal avec texte seulement."""
        embedding = self.multimodal_embeddings.generate_multimodal_embedding(
            text=self.test_text
        )
        
        assert isinstance(embedding, np.ndarray), "L'embedding doit être un numpy array"
        assert embedding.shape[0] > 0, "L'embedding ne doit pas être vide"
    
    def test_multimodal_embedding_image_only(self):
        """Test d'embedding multimodal avec image seulement."""
        embedding = self.multimodal_embeddings.generate_multimodal_embedding(
            image_path=str(self.test_image_path)
        )
        
        assert isinstance(embedding, np.ndarray), "L'embedding doit être un numpy array"
        assert embedding.shape[0] > 0, "L'embedding ne doit pas être vide"
    
    def test_multimodal_embedding_fusion(self):
        """Test de fusion des embeddings multimodaux."""
        text_embedding = np.random.rand(384)  # Embedding texte simulé
        image_embedding = np.random.rand(512)  # Embedding image simulé
        
        fused_embedding = self.multimodal_embeddings.fuse_embeddings(
            text_embedding, image_embedding
        )
        
        assert isinstance(fused_embedding, np.ndarray), "L'embedding fusionné doit être un numpy array"
        assert fused_embedding.shape[0] > 0, "L'embedding fusionné ne doit pas être vide"
    
    def test_multimodal_embedding_similarity(self):
        """Test de similarité entre embeddings multimodaux."""
        # Création d'embeddings de test
        emb1 = self.multimodal_embeddings.generate_multimodal_embedding(
            text="Chat noir sur fond blanc",
            image_path=str(self.test_image_path)
        )
        
        emb2 = self.multimodal_embeddings.generate_multimodal_embedding(
            text="Chat noir sur fond blanc",
            image_path=str(self.test_image_path)
        )
        
        emb3 = self.multimodal_embeddings.generate_multimodal_embedding(
            text="Voiture rouge",
            image_path=str(self.test_image_path)
        )
        
        # Calcul des similarités
        sim_1_2 = self.multimodal_embeddings.cosine_similarity(emb1, emb2)
        sim_1_3 = self.multimodal_embeddings.cosine_similarity(emb1, emb3)
        
        # Les embeddings identiques devraient avoir une similarité plus élevée
        assert sim_1_2 >= sim_1_3, "Les embeddings identiques devraient avoir une similarité plus élevée"
        assert 0 <= sim_1_2 <= 1, "La similarité doit être entre 0 et 1"
        assert 0 <= sim_1_3 <= 1, "La similarité doit être entre 0 et 1"

class TestEmbeddingUtilities:
    """Tests pour les utilitaires d'embeddings."""
    
    def test_cosine_similarity(self):
        """Test du calcul de similarité cosinus."""
        from src.vectorization.embeddings.text_embeddings import TextEmbeddings
        
        text_embeddings = TextEmbeddings()
        
        # Vecteurs de test
        vec1 = np.array([1, 0, 0])
        vec2 = np.array([1, 0, 0])
        vec3 = np.array([0, 1, 0])
        
        # Calcul des similarités
        sim_1_2 = text_embeddings.cosine_similarity(vec1, vec2)
        sim_1_3 = text_embeddings.cosine_similarity(vec1, vec3)
        
        assert sim_1_2 == 1.0, "Vecteurs identiques devraient avoir une similarité de 1"
        assert sim_1_3 == 0.0, "Vecteurs orthogonaux devraient avoir une similarité de 0"
    
    def test_embedding_normalization(self):
        """Test de normalisation d'embedding."""
        from src.vectorization.embeddings.text_embeddings import TextEmbeddings
        
        text_embeddings = TextEmbeddings()
        
        # Vecteur non normalisé
        vec = np.array([3, 4, 0])
        normalized_vec = text_embeddings.normalize_embedding(vec)
        
        # Vérification de la normalisation
        norm = np.linalg.norm(normalized_vec)
        assert abs(norm - 1.0) < 1e-6, f"Vecteur normalisé devrait avoir une norme de 1, obtenue: {norm}"
    
    def test_embedding_dimensions_consistency(self):
        """Test de cohérence des dimensions d'embeddings."""
        text_embeddings = TextEmbeddings()
        image_embeddings = ImageEmbeddings()
        audio_embeddings = AudioEmbeddings()
        multimodal_embeddings = MultimodalEmbeddings()
        
        # Vérification que les dimensions sont cohérentes
        text_dim = text_embeddings.get_embedding_dimension()
        image_dim = image_embeddings.get_embedding_dimension()
        audio_dim = audio_embeddings.get_embedding_dimension()
        multimodal_dim = multimodal_embeddings.get_embedding_dimension()
        
        assert text_dim > 0, "Dimension d'embedding texte doit être positive"
        assert image_dim > 0, "Dimension d'embedding image doit être positive"
        assert audio_dim > 0, "Dimension d'embedding audio doit être positive"
        assert multimodal_dim > 0, "Dimension d'embedding multimodal doit être positive"

def run_embedding_tests():
    """Fonction pour exécuter tous les tests d'embeddings."""
    test_classes = [
        TestTextEmbeddings,
        TestImageEmbeddings,
        TestAudioEmbeddings,
        TestMultimodalEmbeddings,
        TestEmbeddingUtilities
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    print("🚀 Démarrage des tests d'embeddings...")
    
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
    
    print(f"\n📊 Résultats des tests d'embeddings:")
    print(f"Tests réussis: {passed_tests}")
    print(f"Tests échoués: {failed_tests}")
    print(f"Total: {passed_tests + failed_tests}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_embedding_tests()
    exit(0 if success else 1)
