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
            )
        ]
    
    def _get_system_prompt(self) -> str:
        return """
        Tu es l'Agent de Traitement Vocal du système Solar Nasih.
        
        Tes fonctions:
        - Transcription audio vers texte
        - Génération de réponses vocales
        - Détection de langue parlée
        - Optimisation pour l'interaction vocale
        
        Adapte tes réponses pour l'oral: phrases courtes et claires.
        """
    
    def _transcribe_audio(self, audio_data: str) -> str:
        """Transcrit l'audio en texte"""
        try:
            # Simulation - en production, utiliser speech_recognition
            return "Combien coûte une installation photovoltaïque de 6 kWc ?"
        except Exception as e:
            return f"Erreur de transcription: {str(e)}"
    
    def _generate_audio_response(self, text: str) -> str:
        """Génère une réponse audio"""
        try:
            # Simulation - en production, utiliser gTTS
            tts = gTTS(text=text, lang='fr')
            # Sauvegarder le fichier audio
            return "/audio/response_generated.mp3"
        except Exception as e:
            return f"Erreur génération audio: {str(e)}"
    
    def _detect_voice_language(self, audio_data: str) -> str:
        """Détecte la langue parlée"""
        # Simulation simple
        return "fr"
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        voice_indicators = ["audio", "vocal", "parler", "écouter", "micro"]
        return 0.9 if any(ind in user_input.lower() for ind in voice_indicators) else 0.1

