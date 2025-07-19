"""
Tests unitaires pour les extracteurs dans le système RAG multimodal.
Teste les extracteurs de texte, image, audio et vidéo.
"""

import pytest
import tempfile
from pathlib import Path
import json
from typing import Dict, Any, List

# Import des modules à tester
from src.ingestion.extractors.text_extractor import TextExtractor
from src.ingestion.extractors.image_extractor import ImageExtractor
from src.ingestion.extractors.audio_extractor import AudioExtractor
from src.ingestion.extractors.video_extractor import VideoExtractor

class TestTextExtractor:
    """Tests pour l'extracteur de texte."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.text_extractor = TextExtractor()
        self.test_files = self._create_test_files()
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        for file_path in self.test_files.values():
            if file_path.exists():
                file_path.unlink()
    
    def _create_test_files(self) -> Dict[str, Path]:
        """Crée des fichiers de test."""
        test_files = {}
        
        # Fichier texte simple
        txt_content = "Ceci est un fichier texte de test.\nIl contient plusieurs lignes.\nPour tester l'extracteur."
        txt_file = Path(tempfile.mktemp(suffix='.txt'))
        txt_file.write_text(txt_content, encoding='utf-8')
        test_files['txt'] = txt_file
        
        # Fichier JSON
        json_content = {
            "title": "Document JSON",
            "content": "Contenu du document JSON",
            "metadata": {
                "author": "Test Author",
                "date": "2024-01-01"
            }
        }
        json_file = Path(tempfile.mktemp(suffix='.json'))
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_content, f, ensure_ascii=False, indent=2)
        test_files['json'] = json_file
        
        # Fichier CSV
        csv_content = "nom,age,ville\nJean,25,Paris\nMarie,30,Lyon\nPierre,35,Marseille"
        csv_file = Path(tempfile.mktemp(suffix='.csv'))
        csv_file.write_text(csv_content, encoding='utf-8')
        test_files['csv'] = csv_file
        
        return test_files
    
    def test_extract_txt_file(self):
        """Test d'extraction d'un fichier TXT."""
        result = self.text_extractor.extract(str(self.test_files['txt']))
        
        assert "content" in result, "Le résultat doit contenir le contenu"
        assert "metadata" in result, "Le résultat doit contenir les métadonnées"
        assert "Ceci est un fichier texte de test" in result["content"], "Le contenu doit être extrait"
        assert result["metadata"]["file_type"] == "text", "Le type de fichier doit être correct"
    
    def test_extract_json_file(self):
        """Test d'extraction d'un fichier JSON."""
        result = self.text_extractor.extract(str(self.test_files['json']))
        
        assert "content" in result, "Le résultat doit contenir le contenu"
        assert "metadata" in result, "Le résultat doit contenir les métadonnées"
        assert "Document JSON" in result["content"], "Le contenu JSON doit être extrait"
        assert result["metadata"]["file_type"] == "json", "Le type de fichier doit être correct"
    
    def test_extract_csv_file(self):
        """Test d'extraction d'un fichier CSV."""
        result = self.text_extractor.extract(str(self.test_files['csv']))
        
        assert "content" in result, "Le résultat doit contenir le contenu"
        assert "metadata" in result, "Le résultat doit contenir les métadonnées"
        assert "Jean,25,Paris" in result["content"], "Le contenu CSV doit être extrait"
        assert result["metadata"]["file_type"] == "csv", "Le type de fichier doit être correct"
    
    def test_extract_invalid_file(self):
        """Test d'extraction d'un fichier invalide."""
        with pytest.raises(FileNotFoundError):
            self.text_extractor.extract("invalid/path/file.txt")
    
    def test_extract_empty_file(self):
        """Test d'extraction d'un fichier vide."""
        empty_file = Path(tempfile.mktemp(suffix='.txt'))
        empty_file.write_text("", encoding='utf-8')
        
        try:
            result = self.text_extractor.extract(str(empty_file))
            assert "content" in result, "Le résultat doit contenir le contenu"
            assert result["content"] == "", "Le contenu doit être vide"
        finally:
            empty_file.unlink()
    
    def test_extract_large_file(self):
        """Test d'extraction d'un fichier volumineux."""
        large_content = "Ligne de test. " * 1000  # ~15KB
        large_file = Path(tempfile.mktemp(suffix='.txt'))
        large_file.write_text(large_content, encoding='utf-8')
        
        try:
            result = self.text_extractor.extract(str(large_file))
            assert "content" in result, "Le résultat doit contenir le contenu"
            assert len(result["content"]) > 0, "Le contenu ne doit pas être vide"
        finally:
            large_file.unlink()
    
    def test_extract_with_encoding(self):
        """Test d'extraction avec différents encodages."""
        # Test avec UTF-8
        utf8_content = "Contenu avec accents: éàèùç"
        utf8_file = Path(tempfile.mktemp(suffix='.txt'))
        utf8_file.write_text(utf8_content, encoding='utf-8')
        
        try:
            result = self.text_extractor.extract(str(utf8_file))
            assert "éàèùç" in result["content"], "Les caractères spéciaux doivent être préservés"
        finally:
            utf8_file.unlink()

class TestImageExtractor:
    """Tests pour l'extracteur d'images."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.image_extractor = ImageExtractor()
        self.test_image = self._create_test_image()
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        if hasattr(self, 'test_image') and self.test_image.exists():
            self.test_image.unlink()
    
    def _create_test_image(self) -> Path:
        """Crée une image de test."""
        try:
            from PIL import Image, ImageDraw
            
            # Création d'une image simple
            img = Image.new('RGB', (200, 200), color='white')
            draw = ImageDraw.Draw(img)
            draw.rectangle([50, 50, 150, 150], fill='blue')
            draw.text((60, 60), "Test Image", fill='black')
            
            # Sauvegarde temporaire
            temp_path = Path(tempfile.mktemp(suffix='.png'))
            img.save(temp_path)
            return temp_path
            
        except ImportError:
            # Si PIL n'est pas disponible, créer un fichier factice
            temp_path = Path(tempfile.mktemp(suffix='.png'))
            temp_path.write_bytes(b'fake_image_data')
            return temp_path
    
    def test_extract_image(self):
        """Test d'extraction d'une image."""
        result = self.image_extractor.extract(str(self.test_image))
        
        assert "content" in result, "Le résultat doit contenir le contenu"
        assert "metadata" in result, "Le résultat doit contenir les métadonnées"
        assert result["metadata"]["file_type"] == "image", "Le type de fichier doit être correct"
        assert "width" in result["metadata"], "Les métadonnées doivent contenir la largeur"
        assert "height" in result["metadata"], "Les métadonnées doivent contenir la hauteur"
    
    def test_extract_image_metadata(self):
        """Test d'extraction des métadonnées d'image."""
        result = self.image_extractor.extract(str(self.test_image))
        metadata = result["metadata"]
        
        assert "width" in metadata, "Largeur manquante"
        assert "height" in metadata, "Hauteur manquante"
        assert "format" in metadata, "Format manquant"
        assert metadata["width"] > 0, "Largeur doit être positive"
        assert metadata["height"] > 0, "Hauteur doit être positive"
    
    def test_extract_invalid_image(self):
        """Test d'extraction d'une image invalide."""
        with pytest.raises(FileNotFoundError):
            self.image_extractor.extract("invalid/path/image.jpg")
    
    def test_extract_corrupted_image(self):
        """Test d'extraction d'une image corrompue."""
        corrupted_file = Path(tempfile.mktemp(suffix='.jpg'))
        corrupted_file.write_bytes(b'corrupted_image_data')
        
        try:
            with pytest.raises(Exception):  # Peut être ValueError, OSError, etc.
                self.image_extractor.extract(str(corrupted_file))
        finally:
            corrupted_file.unlink()

class TestAudioExtractor:
    """Tests pour l'extracteur audio."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.audio_extractor = AudioExtractor()
        self.test_audio = self._create_test_audio()
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        if hasattr(self, 'test_audio') and self.test_audio.exists():
            self.test_audio.unlink()
    
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
    
    def test_extract_audio(self):
        """Test d'extraction d'un fichier audio."""
        result = self.audio_extractor.extract(str(self.test_audio))
        
        assert "content" in result, "Le résultat doit contenir le contenu"
        assert "metadata" in result, "Le résultat doit contenir les métadonnées"
        assert result["metadata"]["file_type"] == "audio", "Le type de fichier doit être correct"
    
    def test_extract_audio_metadata(self):
        """Test d'extraction des métadonnées audio."""
        result = self.audio_extractor.extract(str(self.test_audio))
        metadata = result["metadata"]
        
        assert "duration" in metadata, "Durée manquante"
        assert "sample_rate" in metadata, "Taux d'échantillonnage manquant"
        assert "channels" in metadata, "Nombre de canaux manquant"
        assert metadata["duration"] > 0, "Durée doit être positive"
        assert metadata["sample_rate"] > 0, "Taux d'échantillonnage doit être positif"
    
    def test_extract_invalid_audio(self):
        """Test d'extraction d'un fichier audio invalide."""
        with pytest.raises(FileNotFoundError):
            self.audio_extractor.extract("invalid/path/audio.wav")
    
    def test_extract_audio_transcription(self):
        """Test de transcription audio."""
        result = self.audio_extractor.extract(str(self.test_audio))
        
        # Pour un fichier audio simple, la transcription peut être vide ou contenir du texte
        assert "transcription" in result["metadata"], "Les métadonnées doivent contenir la transcription"
        # La transcription peut être vide pour un fichier audio simple

class TestVideoExtractor:
    """Tests pour l'extracteur vidéo."""
    
    def setup_method(self):
        """Configuration avant chaque test."""
        self.video_extractor = VideoExtractor()
        self.test_video = self._create_test_video()
    
    def teardown_method(self):
        """Nettoyage après chaque test."""
        if hasattr(self, 'test_video') and self.test_video.exists():
            self.test_video.unlink()
    
    def _create_test_video(self) -> Path:
        """Crée un fichier vidéo de test."""
        try:
            import cv2
            
            # Création d'une vidéo simple
            temp_path = Path(tempfile.mktemp(suffix='.mp4'))
            
            # Création d'une vidéo avec OpenCV
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(temp_path), fourcc, 20.0, (640, 480))
            
            for i in range(30):  # 30 frames = 1.5 secondes
                frame = np.zeros((480, 640, 3), dtype=np.uint8)
                cv2.putText(frame, f"Frame {i}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                out.write(frame)
            
            out.release()
            return temp_path
            
        except ImportError:
            # Si OpenCV n'est pas disponible, créer un fichier factice
            temp_path = Path(tempfile.mktemp(suffix='.mp4'))
            temp_path.write_bytes(b'fake_video_data')
            return temp_path
    
    def test_extract_video(self):
        """Test d'extraction d'une vidéo."""
        result = self.video_extractor.extract(str(self.test_video))
        
        assert "content" in result, "Le résultat doit contenir le contenu"
        assert "metadata" in result, "Le résultat doit contenir les métadonnées"
        assert result["metadata"]["file_type"] == "video", "Le type de fichier doit être correct"
    
    def test_extract_video_metadata(self):
        """Test d'extraction des métadonnées vidéo."""
        result = self.video_extractor.extract(str(self.test_video))
        metadata = result["metadata"]
        
        assert "duration" in metadata, "Durée manquante"
        assert "width" in metadata, "Largeur manquante"
        assert "height" in metadata, "Hauteur manquante"
        assert "fps" in metadata, "FPS manquant"
        assert metadata["duration"] > 0, "Durée doit être positive"
        assert metadata["width"] > 0, "Largeur doit être positive"
        assert metadata["height"] > 0, "Hauteur doit être positive"
    
    def test_extract_video_frames(self):
        """Test d'extraction des frames vidéo."""
        result = self.video_extractor.extract(str(self.test_video))
        
        assert "frames" in result["metadata"], "Les métadonnées doivent contenir les frames"
        frames = result["metadata"]["frames"]
        assert isinstance(frames, list), "Les frames doivent être une liste"
        assert len(frames) > 0, "Il doit y avoir au moins une frame"
    
    def test_extract_invalid_video(self):
        """Test d'extraction d'une vidéo invalide."""
        with pytest.raises(FileNotFoundError):
            self.video_extractor.extract("invalid/path/video.mp4")

class TestExtractorUtilities:
    """Tests pour les utilitaires des extracteurs."""
    
    def test_file_type_detection(self):
        """Test de détection du type de fichier."""
        from src.ingestion.extractors.text_extractor import TextExtractor
        
        text_extractor = TextExtractor()
        
        # Test avec différents types de fichiers
        test_cases = [
            ("test.txt", "text"),
            ("test.json", "json"),
            ("test.csv", "csv"),
            ("test.md", "markdown"),
            ("test.xml", "xml"),
            ("test.html", "html")
        ]
        
        for filename, expected_type in test_cases:
            detected_type = text_extractor._detect_file_type(filename)
            assert detected_type == expected_type, f"Type détecté incorrect pour {filename}"
    
    def test_metadata_extraction(self):
        """Test d'extraction des métadonnées."""
        from src.ingestion.extractors.text_extractor import TextExtractor
        
        text_extractor = TextExtractor()
        
        # Création d'un fichier de test
        test_file = Path(tempfile.mktemp(suffix='.txt'))
        test_file.write_text("Test content", encoding='utf-8')
        
        try:
            metadata = text_extractor._extract_metadata(test_file)
            
            assert "file_size" in metadata, "Taille de fichier manquante"
            assert "created_time" in metadata, "Temps de création manquant"
            assert "modified_time" in metadata, "Temps de modification manquant"
            assert "file_type" in metadata, "Type de fichier manquant"
            
        finally:
            test_file.unlink()
    
    def test_content_cleaning(self):
        """Test de nettoyage du contenu."""
        from src.ingestion.extractors.text_extractor import TextExtractor
        
        text_extractor = TextExtractor()
        
        # Test avec du contenu contenant des caractères spéciaux
        dirty_content = "  \n\n  Contenu avec   espaces   multiples  \n\n  "
        clean_content = text_extractor._clean_content(dirty_content)
        
        assert clean_content == "Contenu avec espaces multiples", "Le contenu doit être nettoyé"
    
    def test_error_handling(self):
        """Test de gestion d'erreurs."""
        from src.ingestion.extractors.text_extractor import TextExtractor
        
        text_extractor = TextExtractor()
        
        # Test avec un fichier inexistant
        with pytest.raises(FileNotFoundError):
            text_extractor.extract("nonexistent_file.txt")
        
        # Test avec un fichier non lisible
        unreadable_file = Path(tempfile.mktemp(suffix='.txt'))
        unreadable_file.write_text("test", encoding='utf-8')
        unreadable_file.chmod(0o000)  # Rendre le fichier non lisible
        
        try:
            with pytest.raises(PermissionError):
                text_extractor.extract(str(unreadable_file))
        finally:
            unreadable_file.chmod(0o644)  # Restaurer les permissions
            unreadable_file.unlink()

def run_extractor_tests():
    """Fonction pour exécuter tous les tests d'extracteurs."""
    test_classes = [
        TestTextExtractor,
        TestImageExtractor,
        TestAudioExtractor,
        TestVideoExtractor,
        TestExtractorUtilities
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    print("🚀 Démarrage des tests d'extracteurs...")
    
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
    
    print(f"\n📊 Résultats des tests d'extracteurs:")
    print(f"Tests réussis: {passed_tests}")
    print(f"Tests échoués: {failed_tests}")
    print(f"Total: {passed_tests + failed_tests}")
    
    return failed_tests == 0

if __name__ == "__main__":
    success = run_extractor_tests()
    exit(0 if success else 1)
