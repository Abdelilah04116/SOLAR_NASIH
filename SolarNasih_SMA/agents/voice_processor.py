from typing import Dict, Any, List
from langchain.tools import Tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType
from services.gemini_service import GeminiService
from services.tavily_service import TavilyService
import speech_recognition as sr
from gtts import gTTS
import io
import tempfile
import os
import subprocess
import re
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# AGENT DE TRAITEMENT VOCAL
# =============================================================================

class VoiceProcessorAgent(BaseAgent):
    """
    Agent de Traitement Vocal - Conversion speech-to-text et text-to-speech
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.VOICE_PROCESSOR,
            description="Agent de traitement vocal pour interactions audio"
        )
        self.recognizer = sr.Recognizer()
        
        # Configuration des langues supportées
        self.supported_languages = {
            "fr": {
                "name": "Français",
                "code": "fr-FR",
                "keywords": ["bonjour", "merci", "s'il vous plaît", "comment", "pourquoi", "quand", "où", "qui", "quoi"],
                "solar_terms": ["panneau", "solaire", "photovoltaïque", "énergie", "installation", "puissance", "kwh", "kwc"]
            },
            "en": {
                "name": "English",
                "code": "en-US",
                "keywords": ["hello", "thank you", "please", "how", "why", "when", "where", "who", "what"],
                "solar_terms": ["panel", "solar", "photovoltaic", "energy", "installation", "power", "kwh", "kwp"]
            },
            "ar": {
                "name": "العربية",
                "code": "ar-SA",
                "keywords": ["مرحبا", "شكرا", "من فضلك", "كيف", "لماذا", "متى", "أين", "من", "ماذا"],
                "solar_terms": ["لوحة", "شمسية", "كهروضوئية", "طاقة", "تركيب", "قوة", "كيلوواط"]
            },
            "darija": {
                "name": "Darija",
                "code": "ar-MA",
                "keywords": ["سلام", "شكرا", "عافاك", "كيفاش", "علاش", "فين", "شكون", "شنو", "فاش"],
                "solar_terms": ["طابلة", "شمسية", "كهرباء", "طاقة", "تركيب", "قوة", "كيلوواط"]
            }
        }
    
    def _init_tools(self) -> List[Tool]:
        return [
            Tool(
                name="transcribe_audio",
                description="Transcrit l'audio en texte",
                func=self._transcribe_audio
            ),
            Tool(
                name="generate_audio_response",
                description="Génère une réponse audio",
                func=self._generate_audio_response
            ),
            Tool(
                name="detect_voice_language",
                description="Détecte la langue parlée",
                func=self._detect_voice_language
            ),
            Tool(
                name="convert_audio_format",
                description="Convertit le format audio avec ffmpeg",
                func=self._convert_audio_format
            )
        ]
    
    def _get_system_prompt(self) -> str:
        return """
        Tu es l'Agent de Traitement Vocal du système Solar Nasih.
        
        Tes fonctions:
        - Transcription audio vers texte
        - Génération de réponses vocales
        - Détection de langue parlée (Français, Anglais, Arabe, Darija)
        - Conversion audio avec ffmpeg
        - Optimisation pour l'interaction vocale
        
        Langues supportées:
        - Français (fr)
        - Anglais (en)
        - Arabe (ar)
        - Darija (darija)
        
        Adapte tes réponses pour l'oral: phrases courtes et claires.
        """
    
    def _convert_audio_format(self, input_file: str, output_format: str = "wav") -> str:
        """Convertit le format audio avec ffmpeg"""
        try:
            # Vérifier que ffmpeg est disponible
            if not self._check_ffmpeg():
                return "Erreur: ffmpeg non disponible"
            
            # Créer le nom du fichier de sortie
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}.{output_format}"
            
            # Commande ffmpeg pour conversion
            cmd = [
                "ffmpeg", "-i", input_file,
                "-acodec", "pcm_s16le",  # Codec audio
                "-ar", "16000",          # Taux d'échantillonnage
                "-ac", "1",              # Mono
                "-y",                    # Écraser si existe
                output_file
            ]
            
            # Exécuter la conversion
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return f"Conversion réussie: {output_file}"
            else:
                return f"Erreur conversion: {result.stderr}"
                
        except Exception as e:
            logger.error(f"Erreur conversion audio: {e}")
            return f"Erreur conversion audio: {str(e)}"
    
    def _check_ffmpeg(self) -> bool:
        """Vérifie si ffmpeg est disponible"""
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False
    
    def _transcribe_audio(self, audio_file_path: str) -> str:
        """Transcrit l'audio en texte avec détection automatique de langue"""
        try:
            # Convertir l'audio en format compatible si nécessaire
            if not audio_file_path.endswith('.wav'):
                audio_file_path = self._convert_audio_format(audio_file_path, "wav")
            
            # Détecter la langue d'abord
            detected_lang = self._detect_voice_language(audio_file_path)
            
            # Configuration du recognizer selon la langue
            if detected_lang in self.supported_languages:
                lang_code = self.supported_languages[detected_lang]["code"]
            else:
                lang_code = "fr-FR"  # Défaut français
            
            # Transcription avec la langue détectée
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
                
                # Essayer d'abord avec la langue détectée
                try:
                    text = self.recognizer.recognize_google(audio, language=lang_code)
                    return text
                except sr.UnknownValueError:
                    # Si échec, essayer avec reconnaissance automatique
                    try:
                        text = self.recognizer.recognize_google(audio)
                        return text
                    except sr.UnknownValueError:
                        return "Impossible de transcrire l'audio"
                except sr.RequestError as e:
                    return f"Erreur service reconnaissance: {str(e)}"
                    
        except Exception as e:
            logger.error(f"Erreur transcription: {e}")
            return f"Erreur de transcription: {str(e)}"
    
    def _generate_audio_response(self, text: str, language: str = "fr") -> str:
        """Génère une réponse audio dans la langue spécifiée"""
        try:
            # Mapping des langues pour gTTS
            lang_mapping = {
                "fr": "fr",
                "en": "en",
                "ar": "ar",
                "darija": "ar"  # Darija utilise l'arabe pour gTTS
            }
            
            gtts_lang = lang_mapping.get(language, "fr")
            
            # Générer l'audio
            tts = gTTS(text=text, lang=gtts_lang, slow=False)
            
            # Créer le dossier audio s'il n'existe pas
            os.makedirs("static/audio", exist_ok=True)
            
            # Nom du fichier avec timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"response_{language}_{timestamp}.mp3"
            filepath = f"static/audio/{filename}"
            
            # Sauvegarder le fichier audio
            tts.save(filepath)
            
            return f"/static/audio/{filename}"
            
        except Exception as e:
            logger.error(f"Erreur génération audio: {e}")
            return f"Erreur génération audio: {str(e)}"
    
    def _detect_voice_language(self, audio_file_path: str) -> str:
        """Détecte la langue parlée dans l'audio"""
        try:
            # Convertir en format compatible si nécessaire
            if not audio_file_path.endswith('.wav'):
                audio_file_path = self._convert_audio_format(audio_file_path, "wav")
            
            # Transcription avec reconnaissance automatique de langue
            with sr.AudioFile(audio_file_path) as source:
                audio = self.recognizer.record(source)
                
                # Essayer avec reconnaissance automatique
                try:
                    text = self.recognizer.recognize_google(audio)
                    
                    # Analyser le texte pour détecter la langue
                    detected_lang = self._analyze_text_language(text)
                    return detected_lang
                    
                except sr.UnknownValueError:
                    # Si pas de transcription possible, essayer différentes langues
                    return self._try_multiple_languages(audio)
                except sr.RequestError:
                    return "fr"  # Défaut français
                    
        except Exception as e:
            logger.error(f"Erreur détection langue: {e}")
            return "fr"  # Défaut français
    
    def _analyze_text_language(self, text: str) -> str:
        """Analyse le texte pour détecter la langue"""
        text_lower = text.lower()
        
        # Calculer les scores pour chaque langue
        scores = {}
        
        for lang_code, lang_data in self.supported_languages.items():
            score = 0
            
            # Points pour les mots-clés généraux
            keyword_matches = sum(1 for word in lang_data["keywords"] if word in text_lower)
            score += keyword_matches * 2
            
            # Points pour les termes solaires
            solar_matches = sum(1 for word in lang_data["solar_terms"] if word in text_lower)
            score += solar_matches * 3
            
            # Points pour les patterns spécifiques
            if lang_code == "darija":
                # Patterns spécifiques au darija
                darija_patterns = ["كيفاش", "علاش", "فين", "شكون", "شنو", "فاش", "عافاك"]
                darija_matches = sum(1 for pattern in darija_patterns if pattern in text_lower)
                score += darija_matches * 4
            elif lang_code == "ar":
                # Patterns arabes (mais pas darija)
                arabic_patterns = ["كيف", "لماذا", "أين", "من", "ماذا", "متى"]
                arabic_matches = sum(1 for pattern in arabic_patterns if pattern in text_lower)
                score += arabic_matches * 3
            
            scores[lang_code] = score
        
        # Retourner la langue avec le meilleur score
        if scores:
            best_lang = max(scores.items(), key=lambda x: x[1])
            if best_lang[1] > 0:
                return best_lang[0]
        
        return "fr"  # Défaut français
    
    def _try_multiple_languages(self, audio) -> str:
        """Essaie de transcrire avec différentes langues"""
        languages_to_try = ["fr-FR", "en-US", "ar-SA"]
        
        for lang_code in languages_to_try:
            try:
                text = self.recognizer.recognize_google(audio, language=lang_code)
                if text.strip():
                    # Analyser le texte transcrit
                    return self._analyze_text_language(text)
            except:
                continue
        
        return "fr"  # Défaut français
    
    async def process(self, state) -> Dict[str, Any]:
        """Méthode requise par BaseAgent - traite une requête vocale"""
        try:
            # Utiliser la langue détectée par le workflow ou détecter si pas disponible
            detected_language = getattr(state, 'detected_language', None)
            if not detected_language:
                detected_language = "fr"  # Défaut français
            
            # Analyse du type de demande
            message_lower = state.current_message.lower()
            
            if "transcrire" in message_lower or "audio" in message_lower:
                # Simulation de transcription (en production, utiliser un vrai fichier audio)
                result = self._transcribe_audio("audio_sample.wav")
            elif "générer" in message_lower or "audio" in message_lower:
                # Génération de réponse audio
                result = self._generate_audio_response(state.current_message, detected_language)
            elif "détecter" in message_lower or "langue" in message_lower:
                # Détection de langue
                result = self._detect_voice_language("audio_sample.wav")
            else:
                # Traitement vocal par défaut
                result = f"Traitement vocal en {detected_language}: {state.current_message}"
            
            return {
                "response": result,
                "agent_used": "voice_processor",
                "confidence": 0.8,
                "detected_language": detected_language,
                "sources": ["Solar Nasih Voice Processing"]
            }
            
        except Exception as e:
            return {
                "response": f"Erreur dans le traitement vocal: {str(e)}",
                "agent_used": "voice_processor",
                "confidence": 0.3,
                "error": str(e),
                "sources": ["Solar Nasih Voice Processing"]
            }
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        voice_indicators = ["audio", "vocal", "parler", "écouter", "micro", "transcrire", "générer audio"]
        return 0.9 if any(ind in user_input.lower() for ind in voice_indicators) else 0.1

