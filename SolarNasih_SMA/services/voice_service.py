from typing import Dict, Any, Optional, Tuple
import speech_recognition as sr
from gtts import gTTS
import tempfile
import os
from io import BytesIO
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class VoiceService:
    """
    Service de traitement vocal pour Solar Nasih
    """
    
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.supported_languages = {
            'fr': 'fr-FR',
            'en': 'en-US',
            'es': 'es-ES',
            'de': 'de-DE',
            'it': 'it-IT'
        }
        
        # Configuration du recognizer
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = 30
    
    async def transcribe_audio(
        self, 
        audio_file: UploadFile, 
        language: str = 'fr'
    ) -> Dict[str, Any]:
        """
        Transcrit un fichier audio en texte
        
        Args:
            audio_file: Fichier audio uploadé
            language: Langue de transcription
            
        Returns:
            Résultat de transcription avec confiance
        """
        
        try:
            # Lecture du fichier audio
            audio_data = await audio_file.read()
            
            # Sauvegarde temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                # Transcription avec speech_recognition
                with sr.AudioFile(temp_file_path) as source:
                    # Ajustement du bruit ambiant
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    # Enregistrement de l'audio
                    audio = self.recognizer.record(source)
                
                # Transcription
                lang_code = self.supported_languages.get(language, 'fr-FR')
                
                try:
                    # Essai avec Google Speech Recognition
                    text = self.recognizer.recognize_google(audio, language=lang_code)
                    confidence = 0.8  # Google ne retourne pas de score de confiance
                    
                except sr.UnknownValueError:
                    # Essai avec reconnaissance offline si disponible
                    try:
                        text = self.recognizer.recognize_sphinx(audio)
                        confidence = 0.6
                    except:
                        text = ""
                        confidence = 0.0
                
                except sr.RequestError as e:
                    logger.error(f"Erreur API Google Speech: {e}")
                    text = ""
                    confidence = 0.0
                
                return {
                    'transcribed_text': text,
                    'confidence': confidence,
                    'detected_language': language,
                    'duration_seconds': len(audio_data) / (16000 * 2),  # Estimation
                    'success': bool(text)
                }
                
            finally:
                # Nettoyage du fichier temporaire
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Erreur lors de la transcription: {e}")
            return {
                'transcribed_text': "",
                'confidence': 0.0,
                'detected_language': language,
                'duration_seconds': 0,
                'success': False,
                'error': str(e)
            }
    
    async def generate_speech(
        self, 
        text: str, 
        language: str = 'fr',
        slow: bool = False
    ) -> Tuple[bytes, str]:
        """
        Génère un fichier audio à partir de texte
        
        Args:
            text: Texte à synthétiser
            language: Langue de synthèse
            slow: Vitesse de lecture lente
            
        Returns:
            Tuple (données audio, nom fichier)
        """
        
        try:
            # Limitation de la longueur du texte
            if len(text) > 1000:
                text = text[:1000] + "..."
            
            # Configuration gTTS
            lang_code = language if language in ['fr', 'en', 'es', 'de', 'it'] else 'fr'
            
            # Génération avec gTTS
            tts = gTTS(text=text, lang=lang_code, slow=slow)
            
            # Sauvegarde en mémoire
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Génération du nom de fichier
            filename = f"response_{hash(text)}.mp3"
            
            return audio_buffer.getvalue(), filename
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération audio: {e}")
            # Retour d'un fichier vide en cas d'erreur
            return b'', 'error.mp3'
    
    def detect_language_from_audio(self, audio_data: bytes) -> str:
        """
        Détecte la langue parlée dans l'audio
        
        Args:
            audio_data: Données audio
            
        Returns:
            Code langue détecté
        """
        
        try:
            # Sauvegarde temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            try:
                with sr.AudioFile(temp_file_path) as source:
                    audio = self.recognizer.record(source)
                
                # Essai de transcription dans différentes langues
                languages_to_try = ['fr-FR', 'en-US', 'es-ES', 'de-DE', 'it-IT']
                
                for lang in languages_to_try:
                    try:
                        text = self.recognizer.recognize_google(audio, language=lang)
                        if text:
                            return lang[:2]  # Retourne le code à 2 lettres
                    except:
                        continue
                
                return 'fr'  # Défaut en français
                
            finally:
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Erreur détection langue: {e}")
            return 'fr'
    
    def validate_audio_file(self, audio_file: UploadFile) -> Dict[str, Any]:
        """
        Valide un fichier audio uploadé
        
        Args:
            audio_file: Fichier à valider
            
        Returns:
            Résultat de validation
        """
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Vérification du type de fichier
        allowed_types = [
            'audio/wav', 'audio/wave', 'audio/x-wav',
            'audio/mpeg', 'audio/mp3',
            'audio/ogg', 'audio/webm',
            'audio/flac', 'audio/x-flac'
        ]
        
        if audio_file.content_type not in allowed_types:
            result['valid'] = False
            result['errors'].append(f"Type de fichier non supporté: {audio_file.content_type}")
        
        # Vérification de l'extension
        allowed_extensions = ['.wav', '.mp3', '.ogg', '.webm', '.flac']
        if not any(audio_file.filename.lower().endswith(ext) for ext in allowed_extensions):
            result['warnings'].append("Extension de fichier inhabituelle")
        
        # Vérification de la taille (max 25MB)
        if hasattr(audio_file, 'size') and audio_file.size > 25 * 1024 * 1024:
            result['valid'] = False
            result['errors'].append("Fichier trop volumineux (max 25MB)")
        
        return result
    
    def optimize_audio_for_recognition(self, audio_data: bytes) -> bytes:
        """
        Optimise l'audio pour améliorer la reconnaissance
        
        Args:
            audio_data: Données audio originales
            
        Returns:
            Données audio optimisées
        """
        
        try:
            # En production, utiliser des bibliothèques comme pydub
            # pour normaliser le volume, réduire le bruit, etc.
            
            # Pour cette implémentation, on retourne l'audio tel quel
            return audio_data
            
        except Exception as e:
            logger.error(f"Erreur optimisation audio: {e}")
            return audio_data
    
    def get_voice_commands_help(self, language: str = 'fr') -> Dict[str, str]:
        """
        Retourne l'aide sur les commandes vocales
        
        Args:
            language: Langue pour l'aide
            
        Returns:
            Dictionnaire des commandes et descriptions
        """
        
        if language == 'fr':
            return {
                "calcule": "Demande de simulation énergétique",
                "prix": "Information sur les coûts",
                "installation": "Conseils techniques d'installation",
                "aide": "Informations sur les aides financières",
                "réglementation": "Questions réglementaires",
                "formation": "Informations sur les formations",
                "document": "Génération de documents"
            }
        
        elif language == 'en':
            return {
                "calculate": "Energy simulation request",
                "price": "Cost information",
                "installation": "Technical installation advice",
                "help": "Financial aid information",
                "regulation": "Regulatory questions",
                "training": "Training information",
                "document": "Document generation"
            }
        
        else:
            return self.get_voice_commands_help('fr')  # Défaut en français
    
    def extract_voice_intent(self, transcribed_text: str) -> Dict[str, Any]:
        """
        Extrait l'intention à partir du texte transcrit
        
        Args:
            transcribed_text: Texte transcrit
            
        Returns:
            Intention détectée avec métadonnées
        """
        
        text_lower = transcribed_text.lower()
        
        # Patterns d'intention pour la voix
        intentions = {
            'simulation': ['calcule', 'simule', 'estime', 'combien produit'],
            'prix': ['prix', 'coût', 'coûte', 'tarif', 'budget'],
            'technique': ['comment installer', 'installation', 'technique', 'problème'],
            'aide': ['aide', 'subvention', 'prime', 'financement'],
            'info': ['qu\'est-ce que', 'explique', 'définition', 'c\'est quoi']
        }
        
        detected_intent = 'info'  # Défaut
        confidence = 0.5
        
        for intent, patterns in intentions.items():
            matches = sum(1 for pattern in patterns if pattern in text_lower)
            if matches > 0:
                detected_intent = intent
                confidence = min(0.8, 0.4 + matches * 0.2)
                break
        
        return {
            'intent': detected_intent,
            'confidence': confidence,
            'keywords': [word for word in text_lower.split() if len(word) > 3],
            'original_text': transcribed_text
        }