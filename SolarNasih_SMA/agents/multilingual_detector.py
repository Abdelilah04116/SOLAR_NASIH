"""
Agent de Détection Multilingue - Solar Nasih SMA
Détecte et traite plusieurs langues pour l'assistance solaire
"""

from typing import Dict, Any, List, Optional
import re
import logging
import google.generativeai as genai
from datetime import datetime
from agents.base_agent import BaseAgent, AgentType, Tool

logger = logging.getLogger(__name__)

class MultilingualDetectorAgent(BaseAgent):
    """
    Agent de détection multilingue - détecte la langue des messages utilisateurs
    """
    def __init__(self):
        super().__init__(
            agent_type=AgentType.MULTILINGUAL_DETECTOR,
            description="Détecte la langue des messages utilisateurs"
        )

    def _init_tools(self) -> List[Tool]:
        # À compléter avec les outils spécifiques si besoin
        return []

    def _get_system_prompt(self) -> str:
        return """
        Tu es l'agent de détection multilingue du système Solar Nasih.
        Ta tâche est d'identifier la langue du message utilisateur et de fournir cette information aux autres agents.
        """

class MultilingualDetectorAgent:
    """
    Agent de Détection Multilingue - Détecte et traite plusieurs langues
    """
    
    def __init__(self, gemini_api_key: str = None):
        self.agent_type = "multilingual_detector"
        self.description = "Agent de détection et traitement multilingue pour l'énergie solaire"
        
        # Configuration Gemini pour traduction
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')
        else:
            self.gemini_model = None
        
        # Langues supportées avec leurs codes et noms
        self.supported_languages = {
            "fr": {
                "name": "Français",
                "native_name": "Français",
                "indicators": ["le", "la", "les", "un", "une", "des", "et", "ou", "mais", "pour", "avec", "dans", "sur", "par", "sans", "sous"],
                "solar_terms": ["photovoltaïque", "solaire", "panneau", "onduleur", "électricité", "énergie", "installation"]
            },
            "en": {
                "name": "English",
                "native_name": "English", 
                "indicators": ["the", "and", "is", "are", "was", "were", "with", "for", "but", "or", "in", "on", "at", "by"],
                "solar_terms": ["photovoltaic", "solar", "panel", "inverter", "electricity", "energy", "installation"]
            },
            "es": {
                "name": "Español",
                "native_name": "Español",
                "indicators": ["el", "la", "los", "las", "un", "una", "y", "o", "pero", "para", "con", "en", "por", "sin"],
                "solar_terms": ["fotovoltaico", "solar", "panel", "inversor", "electricidad", "energía", "instalación"]
            },
            "de": {
                "name": "Deutsch",
                "native_name": "Deutsch",
                "indicators": ["der", "die", "das", "und", "ist", "sind", "mit", "für", "aber", "oder", "in", "auf", "von"],
                "solar_terms": ["photovoltaik", "solar", "panel", "wechselrichter", "strom", "energie", "installation"]
            },
            "it": {
                "name": "Italiano", 
                "native_name": "Italiano",
                "indicators": ["il", "la", "i", "le", "un", "una", "e", "o", "ma", "per", "con", "in", "su", "da"],
                "solar_terms": ["fotovoltaico", "solare", "pannello", "inverter", "elettricità", "energia", "installazione"]
            }
        }
        
        # Réponses types par langue pour l'énergie solaire
        self.solar_responses = {
            "fr": {
                "welcome": "🌞 Bonjour ! Je suis votre assistant en énergie solaire. Comment puis-je vous aider ?",
                "general_info": """
L'énergie solaire photovoltaïque convertit la lumière du soleil en électricité.

✅ Avantages principaux :
• Énergie renouvelable et gratuite
• Réduction de la facture électrique
• Impact environnemental positif
• Autonomie énergétique

💡 Sujets que je peux traiter :
• Prix et financement
• Simulation de production
• Conseils techniques
• Réglementation
• Démarches administratives
                """,
                "pricing": "En France, une installation photovoltaïque coûte entre 2000€ et 3000€ par kWc installé.",
                "simulation": "La production solaire en France varie de 1000 à 1400 kWh par kWc installé selon la région."
            },
            "en": {
                "welcome": "🌞 Hello! I'm your solar energy assistant. How can I help you?",
                "general_info": """
Solar photovoltaic energy converts sunlight into electricity.

✅ Main advantages:
• Renewable and free energy
• Electricity bill reduction
• Positive environmental impact
• Energy independence

💡 Topics I can help with:
• Pricing and financing
• Production simulation
• Technical advice
• Regulations
• Administrative procedures
                """,
                "pricing": "In France, a photovoltaic installation costs between €2000 and €3000 per kWp installed.",
                "simulation": "Solar production in France varies from 1000 to 1400 kWh per kWp installed depending on the region."
            },
            "es": {
                "welcome": "🌞 ¡Hola! Soy tu asistente de energía solar. ¿Cómo puedo ayudarte?",
                "general_info": """
La energía solar fotovoltaica convierte la luz solar en electricidad.

✅ Principales ventajas:
• Energía renovable y gratuita
• Reducción de la factura eléctrica
• Impacto ambiental positivo
• Independencia energética

💡 Temas que puedo tratar:
• Precios y financiación
• Simulación de producción
• Consejos técnicos
• Regulaciones
• Trámites administrativos
                """,
                "pricing": "En Francia, una instalación fotovoltaica cuesta entre 2000€ y 3000€ por kWp instalado.",
                "simulation": "La producción solar en Francia varía de 1000 a 1400 kWh por kWp instalado según la región."
            },
            "de": {
                "welcome": "🌞 Hallo! Ich bin Ihr Solarenergie-Assistent. Wie kann ich Ihnen helfen?",
                "general_info": """
Solare Photovoltaik wandelt Sonnenlicht in Elektrizität um.

✅ Hauptvorteile:
• Erneuerbare und kostenlose Energie
• Reduzierung der Stromrechnung
• Positive Umweltauswirkungen
• Energieunabhängigkeit

💡 Themen, bei denen ich helfen kann:
• Preise und Finanzierung
• Produktionssimulation
• Technische Beratung
• Vorschriften
• Verwaltungsverfahren
                """,
                "pricing": "In Frankreich kostet eine Photovoltaikanlage zwischen 2000€ und 3000€ pro installiertem kWp.",
                "simulation": "Die Solarproduktion in Frankreich variiert je nach Region zwischen 1000 und 1400 kWh pro installiertem kWp."
            },
            "it": {
                "welcome": "🌞 Ciao! Sono il tuo assistente per l'energia solare. Come posso aiutarti?",
                "general_info": """
L'energia solare fotovoltaica converte la luce solare in elettricità.

✅ Principali vantaggi:
• Energia rinnovabile e gratuita
• Riduzione della bolletta elettrica
• Impatto ambientale positivo
• Indipendenza energetica

💡 Argomenti che posso trattare:
• Prezzi e finanziamenti
• Simulazione di produzione
• Consigli tecnici
• Regolamentazioni
• Procedure amministrative
                """,
                "pricing": "In Francia, un impianto fotovoltaico costa tra 2000€ e 3000€ per kWp installato.",
                "simulation": "La produzione solare in Francia varia da 1000 a 1400 kWh per kWp installato a seconda della regione."
            }
        }
        
        # Statistiques d'utilisation
        self.stats = {
            "detections": 0,
            "translations": 0,
            "languages_detected": {},
            "last_detection": None
        }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Détecte la langue d'un texte avec score de confiance
        
        Args:
            text: Texte à analyser
            
        Returns:
            Dictionnaire avec langue détectée et score de confiance
        """
        
        if not text or len(text.strip()) < 3:
            return {"language": "fr", "confidence": 0.3, "method": "default"}
        
        text_lower = text.lower().strip()
        
        # Suppression de la ponctuation pour l'analyse
        text_clean = re.sub(r'[^\w\s]', ' ', text_lower)
        words = text_clean.split()
        
        if len(words) == 0:
            return {"language": "fr", "confidence": 0.3, "method": "default"}
        
        # Calcul des scores pour chaque langue
        language_scores = {}
        
        for lang_code, lang_data in self.supported_languages.items():
            score = 0
            total_indicators = len(lang_data["indicators"])
            
            # Points pour les indicateurs de langue (mots courants)
            indicator_matches = sum(1 for word in words if word in lang_data["indicators"])
            indicator_score = (indicator_matches / len(words)) * 0.7
            
            # Points pour les termes spécialisés en solaire
            solar_matches = sum(1 for word in words if any(term in word for term in lang_data["solar_terms"]))
            solar_score = (solar_matches / len(words)) * 0.3
            
            # Score total
            language_scores[lang_code] = indicator_score + solar_score
        
        # Langue avec le meilleur score
        detected_lang = max(language_scores.items(), key=lambda x: x[1])
        language = detected_lang[0]
        confidence = min(detected_lang[1] * 2, 1.0)  # Normalisation
        
        # Si confiance trop faible, analyse avec patterns spécifiques
        if confidence < 0.4:
            language, confidence = self._detect_with_patterns(text_lower)
        
        # Mise à jour des statistiques
        self.stats["detections"] += 1
        self.stats["languages_detected"][language] = self.stats["languages_detected"].get(language, 0) + 1
        self.stats["last_detection"] = datetime.now().isoformat()
        
        return {
            "language": language,
            "confidence": confidence,
            "method": "statistical_analysis",
            "alternatives": dict(sorted(language_scores.items(), key=lambda x: x[1], reverse=True)[:3])
        }
    
    def _detect_with_patterns(self, text: str) -> tuple:
        """
        Détection avec patterns spécifiques quand l'analyse statistique échoue
        
        Args:
            text: Texte à analyser
            
        Returns:
            Tuple (langue, confiance)
        """
        
        # Patterns spécifiques par langue
        patterns = {
            "en": [
                r"\b(what|how|when|where|why|who)\b",
                r"\b(solar panel|photovoltaic|electricity bill)\b",
                r"\b(installation|cost|price|energy)\b"
            ],
            "es": [
                r"\b(qué|cómo|cuándo|dónde|por qué|quién)\b",
                r"\b(panel solar|fotovoltaico|factura eléctrica)\b",
                r"\b(instalación|costo|precio|energía)\b"
            ],
            "de": [
                r"\b(was|wie|wann|wo|warum|wer)\b",
                r"\b(solarmodul|photovoltaik|stromrechnung)\b",
                r"\b(installation|kosten|preis|energie)\b"
            ],
            "it": [
                r"\b(cosa|come|quando|dove|perché|chi)\b",
                r"\b(pannello solare|fotovoltaico|bolletta elettrica)\b",
                r"\b(installazione|costo|prezzo|energia)\b"
            ]
        }
        
        for lang, pattern_list in patterns.items():
            matches = sum(len(re.findall(pattern, text)) for pattern in pattern_list)
            if matches > 0:
                confidence = min(matches * 0.3, 0.8)
                return lang, confidence
        
        # Défaut français
        return "fr", 0.5
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str = "fr") -> Dict[str, Any]:
        """
        Traduit un texte d'une langue vers une autre
        
        Args:
            text: Texte à traduire
            source_lang: Langue source
            target_lang: Langue cible (défaut: français)
            
        Returns:
            Dictionnaire avec traduction et métadonnées
        """
        
        if source_lang == target_lang:
            return {
                "translated_text": text,
                "source_language": source_lang,
                "target_language": target_lang,
                "method": "no_translation_needed"
            }
        
        try:
            if self.gemini_model:
                # Traduction avec Gemini
                prompt = f"""
                Traduis ce texte de {self.supported_languages[source_lang]['name']} vers {self.supported_languages[target_lang]['name']}.
                Conserve le contexte technique lié à l'énergie solaire.
                
                Texte à traduire: "{text}"
                
                Réponse: traduction uniquement, sans explication.
                """
                
                response = self.gemini_model.generate_content(prompt)
                translated_text = response.text.strip()
                
                self.stats["translations"] += 1
                
                return {
                    "translated_text": translated_text,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "method": "gemini_translation",
                    "confidence": 0.85
                }
            
            else:
                # Traduction de base (mots-clés uniquement)
                return self._basic_translation(text, source_lang, target_lang)
                
        except Exception as e:
            logger.error(f"Erreur traduction: {e}")
            return self._basic_translation(text, source_lang, target_lang)
    
    def _basic_translation(self, text: str, source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Traduction basique des termes solaires courants
        
        Args:
            text: Texte à traduire
            source_lang: Langue source
            target_lang: Langue cible
            
        Returns:
            Traduction basique
        """
        
        # Dictionnaire de traduction des termes solaires
        solar_translations = {
            ("en", "fr"): {
                "solar panel": "panneau solaire",
                "photovoltaic": "photovoltaïque", 
                "inverter": "onduleur",
                "installation": "installation",
                "electricity": "électricité",
                "energy": "énergie",
                "cost": "coût",
                "price": "prix"
            },
            ("es", "fr"): {
                "panel solar": "panneau solaire",
                "fotovoltaico": "photovoltaïque",
                "inversor": "onduleur",
                "instalación": "installation",
                "electricidad": "électricité",
                "energía": "énergie",
                "costo": "coût",
                "precio": "prix"
            },
            ("de", "fr"): {
                "solarmodul": "panneau solaire",
                "photovoltaik": "photovoltaïque",
                "wechselrichter": "onduleur",
                "installation": "installation",
                "strom": "électricité",
                "energie": "énergie",
                "kosten": "coût",
                "preis": "prix"
            },
            ("it", "fr"): {
                "pannello solare": "panneau solaire",
                "fotovoltaico": "photovoltaïque",
                "inverter": "onduleur",
                "installazione": "installation",
                "elettricità": "électricité",
                "energia": "énergie",
                "costo": "coût",
                "prezzo": "prix"
            }
        }
        
        translation_dict = solar_translations.get((source_lang, target_lang), {})
        
        translated_text = text
        for source_term, target_term in translation_dict.items():
            translated_text = re.sub(
                r'\b' + re.escape(source_term) + r'\b', 
                target_term, 
                translated_text, 
                flags=re.IGNORECASE
            )
        
        return {
            "translated_text": translated_text,
            "source_language": source_lang,
            "target_language": target_lang,
            "method": "basic_dictionary",
            "confidence": 0.6
        }
    
    def get_solar_response(self, language: str, topic: str = "general_info") -> str:
        """
        Retourne une réponse pré-définie en énergie solaire dans la langue demandée
        
        Args:
            language: Code de langue
            topic: Sujet de la réponse
            
        Returns:
            Réponse dans la langue demandée
        """
        
        if language not in self.solar_responses:
            language = "fr"  # Défaut français
        
        if topic not in self.solar_responses[language]:
            topic = "general_info"  # Défaut informations générales
        
        return self.solar_responses[language][topic]
    
    def adapt_response_to_language(self, response: str, target_language: str) -> str:
        """
        Adapte une réponse française vers une autre langue
        
        Args:
            response: Réponse en français
            target_language: Langue cible
            
        Returns:
            Réponse adaptée
        """
        
        if target_language == "fr":
            return response
        
        # Si autre langue, retourner réponse pré-définie ou traduction basique
        if target_language in self.solar_responses:
            return self.solar_responses[target_language]["general_info"]
        
        return f"[Response in {target_language}] {response}"
    
    async def process_multilingual_request(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Traite une requête multilingue complète
        
        Args:
            message: Message utilisateur
            context: Contexte optionnel
            
        Returns:
            Réponse avec détection et traitement multilingue
        """
        
        try:
            # 1. Détection de langue
            detection_result = self.detect_language(message)
            detected_lang = detection_result["language"]
            
            # 2. Traduction vers français si nécessaire
            if detected_lang != "fr":
                translation_result = await self.translate_text(message, detected_lang, "fr")
                translated_message = translation_result["translated_text"]
            else:
                translated_message = message
                translation_result = None
            
            # 3. Analyse du contenu pour déterminer la réponse appropriée
            topic = self._analyze_solar_topic(translated_message)
            
            # 4. Génération de réponse en français
            if detected_lang == "fr":
                response = self.get_solar_response("fr", topic)
            else:
                # Réponse dans la langue détectée
                response = self.get_solar_response(detected_lang, topic)
            
            # 5. Résultat complet
            result = {
                "response": response,
                "agent_used": "multilingual_detector",
                "confidence": detection_result["confidence"],
                "detected_language": detected_lang,
                "language_confidence": detection_result["confidence"],
                "original_message": message,
                "translated_message": translated_message if translation_result else None,
                "topic_detected": topic,
                "sources": [f"Solar Nasih Knowledge Base ({self.supported_languages[detected_lang]['native_name']})"]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur traitement multilingue: {e}")
            return {
                "response": self.get_solar_response("fr", "general_info"),
                "agent_used": "multilingual_detector",
                "confidence": 0.5,
                "detected_language": "fr",
                "error": str(e),
                "sources": ["Solar Nasih Knowledge Base"]
            }
    
    def _analyze_solar_topic(self, message: str) -> str:
        """
        Analyse le sujet principal d'un message lié à l'énergie solaire
        
        Args:
            message: Message à analyser
            
        Returns:
            Sujet détecté
        """
        
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["prix", "coût", "tarif", "budget", "financement"]):
            return "pricing"
        elif any(word in message_lower for word in ["simulation", "calcul", "production", "économie"]):
            return "simulation"
        elif any(word in message_lower for word in ["bonjour", "hello", "hola", "ciao", "guten tag"]):
            return "welcome"
        else:
            return "general_info"
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Retourne les statistiques d'utilisation de l'agent
        
        Returns:
            Statistiques détaillées
        """
        
        return {
            "agent_type": self.agent_type,
            "supported_languages": list(self.supported_languages.keys()),
            "statistics": self.stats,
            "capabilities": [
                "Language detection",
                "Text translation", 
                "Multilingual solar responses",
                "Cultural adaptation"
            ]
        }
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        """
        Évalue si l'agent peut traiter la requête
        
        Args:
            user_input: Entrée utilisateur
            context: Contexte optionnel
            
        Returns:
            Score de confiance (0-1)
        """
        
        detection_result = self.detect_language(user_input)
        detected_lang = detection_result["language"]
        confidence = detection_result["confidence"]
        
        # Score élevé si langue non française détectée avec confiance
        if detected_lang != "fr" and confidence > 0.6:
            return 0.9
        
        # Score moyen si indices multilingues
        multilingual_indicators = ["translate", "english", "español", "deutsch", "italiano"]
        if any(indicator in user_input.lower() for indicator in multilingual_indicators):
            return 0.7
        
        # Score faible pour français standard
        return 0.3