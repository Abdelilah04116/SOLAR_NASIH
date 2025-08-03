"""
Agent de Détection Multilingue - Solar Nasih SMA
Détecte et traite plusieurs langues pour l'assistance solaire
Supporte: Français, Darija, Arabe, Tamazight, Anglais
"""

from typing import Dict, Any, List, Optional
import re
import logging
from datetime import datetime
from agents.base_agent import BaseAgent
from models.schemas import AgentType
from services.gemini_service import GeminiService
from services.tavily_service import TavilyService

logger = logging.getLogger(__name__)

class MultilingualDetectorAgent(BaseAgent):
    """
    Agent de Détection Multilingue - Détecte et traite plusieurs langues
    Supporte: Français, Darija, Arabe, Tamazight, Anglais
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.MULTILINGUAL_DETECTOR,
            description="Agent de détection et traitement multilingue pour l'énergie solaire"
        )
        
        # Services
        self.gemini_service = GeminiService()
        self.tavily_service = TavilyService()
        
        # Langues supportées avec leurs codes et noms
        self.supported_languages = {
            "fr": {
                "name": "Français",
                "native_name": "Français",
                "indicators": ["le", "la", "les", "un", "une", "des", "et", "ou", "mais", "pour", "avec", "dans", "sur", "par", "sans", "sous", "je", "tu", "il", "elle", "nous", "vous", "ils", "elles"],
                "solar_terms": ["photovoltaïque", "solaire", "panneau", "onduleur", "électricité", "énergie", "installation", "kwh", "kwc"]
            },
            "darija": {
                "name": "Darija",
                "native_name": "الدارجة",
                "indicators": ["كيفاش", "علاش", "فين", "شكون", "شنو", "فاش", "عافاك", "سلام", "شكرا", "بزاف", "واش", "كاين", "ماكاينش", "عندي", "عندك", "عندو"],
                "solar_terms": ["طابلة", "شمسية", "كهرباء", "طاقة", "تركيب", "قوة", "كيلوواط", "شمس", "ضوء"]
            },
            "ar": {
                "name": "Arabe",
                "native_name": "العربية",
                "indicators": ["كيف", "لماذا", "أين", "من", "ماذا", "متى", "هذا", "هذه", "التي", "الذي", "عندي", "عندك", "عنده", "نحن", "أنتم", "هم"],
                "solar_terms": ["لوحة", "شمسية", "كهروضوئية", "طاقة", "تركيب", "قوة", "كيلوواط", "شمس", "ضوء", "كهرباء"]
            },
            "tamazight": {
                "name": "Tamazight",
                "native_name": "ⵜⴰⵎⴰⵣⵉⵖⵜ",
                "indicators": ["ⵎⴰⵏ", "ⵎⴰⵏⵉ", "ⵎⴰⵏⵉⵎ", "ⵎⴰⵏⵉⵎⵏ", "ⵎⴰⵏⵉⵎⵏⵉ", "ⵎⴰⵏⵉⵎⵏⵉⵏ", "ⵎⴰⵏⵉⵎⵏⵉⵏⵉ", "ⵎⴰⵏⵉⵎⵏⵉⵏⵉⵏ", "ⵎⴰⵏⵉⵎⵏⵉⵏⵉⵏⵉ", "ⵎⴰⵏⵉⵎⵏⵉⵏⵉⵏⵉⵏ"],
                "solar_terms": ["ⵜⴰⵏⵙⵔⵉⵏ", "ⵜⴰⵏⵙⵔⵉⵏⵜ", "ⵜⴰⵏⵙⵔⵉⵏⵜⵉ", "ⵜⴰⵏⵙⵔⵉⵏⵜⵉⵏ", "ⵜⴰⵏⵙⵔⵉⵏⵜⵉⵏⵉ", "ⵜⴰⵏⵙⵔⵉⵏⵜⵉⵏⵉⵏ", "ⵜⴰⵏⵙⵔⵉⵏⵜⵉⵏⵉⵏⵉ", "ⵜⴰⵏⵙⵔⵉⵏⵜⵉⵏⵉⵏⵉⵏ", "ⵜⴰⵏⵙⵔⵉⵏⵜⵉⵏⵉⵏⵉⵏⵉ", "ⵜⴰⵏⵙⵔⵉⵏⵜⵉⵏⵉⵏⵉⵏⵉⵏ"]
            },
            "en": {
                "name": "English",
                "native_name": "English", 
                "indicators": ["the", "and", "is", "are", "was", "were", "with", "for", "but", "or", "in", "on", "at", "by", "I", "you", "he", "she", "it", "we", "they"],
                "solar_terms": ["photovoltaic", "solar", "panel", "inverter", "electricity", "energy", "installation", "kwh", "kwp"]
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
            "darija": {
                "welcome": "🌞 السلام عليكم ! أنا مساعدكم في الطاقة الشمسية. كيفاش نقدر نخدمكم ؟",
                "general_info": """
الطاقة الشمسية الكهروضوئية تحول ضوء الشمس إلى كهرباء.

✅ المزايا الرئيسية :
• طاقة متجددة ومجانية
• تقليل فاتورة الكهرباء
• تأثير إيجابي على البيئة
• استقلالية طاقية

💡 المواضيع التي يمكنني معالجتها :
• الأسعار والتمويل
• محاكاة الإنتاج
• النصائح التقنية
• التنظيمات
• الإجراءات الإدارية
                """,
                "pricing": "في فرنسا، تكلفة التركيب الكهروضوئي بين 2000 و 3000 يورو لكل كيلوواط ذروة.",
                "simulation": "الإنتاج الشمسي في فرنسا يتراوح من 1000 إلى 1400 كيلوواط ساعة لكل كيلوواط ذروة حسب المنطقة."
            },
            "ar": {
                "welcome": "🌞 مرحباً ! أنا مساعدك في الطاقة الشمسية. كيف يمكنني مساعدتك ؟",
                "general_info": """
الطاقة الشمسية الكهروضوئية تحول ضوء الشمس إلى كهرباء.

✅ المزايا الرئيسية :
• طاقة متجددة ومجانية
• تقليل فاتورة الكهرباء
• تأثير إيجابي على البيئة
• استقلالية طاقية

💡 المواضيع التي يمكنني معالجتها :
• الأسعار والتمويل
• محاكاة الإنتاج
• النصائح التقنية
• التنظيمات
• الإجراءات الإدارية
                """,
                "pricing": "في فرنسا، تكلفة التركيب الكهروضوئي بين 2000 و 3000 يورو لكل كيلوواط ذروة.",
                "simulation": "الإنتاج الشمسي في فرنسا يتراوح من 1000 إلى 1400 كيلوواط ساعة لكل كيلوواط ذروة حسب المنطقة."
            },
            "tamazight": {
                "welcome": "🌞 ⴰⵣⵍⵎ ⵎⵍⵉⴽ ! ⵏⴽ ⴰⵙⵙⵉⵙⵜⴰⵏ ⵏⵏⵉⵎ ⴰⵏ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ. ⵎⴰⵏ ⵉⵍⵍⴰ ⵏⵙⵙⵉⵔ ⴰⵖ ?",
                "general_info": """
ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵍⵉⵏⵙⵔⵉ ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵙ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ.

✅ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵍⵉⵏⵙⵔⵉ :
• ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ
• ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ
• ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ
• ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ
                """,
                "pricing": "ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ.",
                "simulation": "ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ ⵉⵙⵙⵉⵔ ⵉⵎⵙⵙⵉ ⵏ ⵙⵉⵎⵙ."
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
            }
        }
    
    def _init_tools(self) -> List:
        """Initialise les outils de l'agent"""
        return []
    
    def _get_system_prompt(self) -> str:
        """Prompt système de l'agent multilingue"""
        return """
        Tu es l'Agent de Détection Multilingue du système Solar Nasih.
        
        Tes responsabilités :
        1. Détecter automatiquement la langue de l'utilisateur
        2. Traduire les réponses dans la langue de l'utilisateur
        3. Adapter le contenu selon la culture et les habitudes linguistiques
        4. Supporter : Français, Darija, Arabe, Tamazight, Anglais
        
        Langues supportées :
        - Français (fr) : Langue principale du système
        - Darija (darija) : Arabe dialectal marocain
        - Arabe (ar) : Arabe standard
        - Tamazight (tamazight) : Langue berbère
        - Anglais (en) : Langue internationale
        
        Tu dois toujours détecter la langue et traduire la réponse finale.
        """
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Détecte la langue du texte avec plusieurs méthodes"""
        try:
            text_lower = text.lower().strip()
            
            if not text_lower:
                return {"language": "fr", "confidence": 0.5, "method": "default"}
            
            # Méthode 1: Détection par patterns
            pattern_result = self._detect_with_patterns(text_lower)
            
            # Méthode 2: Détection par caractères
            char_result = self._detect_with_characters(text_lower)
            
            # Combiner les résultats
            combined_lang = self._combine_detection_results(pattern_result, char_result)
            
            logger.info(f"Langue détectée: {combined_lang['language']} (confiance: {combined_lang['confidence']})")
            
            return combined_lang
            
        except Exception as e:
            logger.error(f"Erreur détection langue: {e}")
            return {"language": "fr", "confidence": 0.3, "method": "fallback", "error": str(e)}
    
    def _detect_with_patterns(self, text: str) -> Dict[str, Any]:
        """Détecte la langue par analyse des mots-clés"""
        scores = {}
        
        for lang_code, lang_data in self.supported_languages.items():
            score = 0
            
            # Points pour les mots-clés généraux
            for indicator in lang_data["indicators"]:
                if indicator in text:
                    score += 2
            
            # Points pour les termes solaires
            for term in lang_data["solar_terms"]:
                if term in text:
                    score += 3
            
            # Points bonus pour patterns spécifiques
            if lang_code == "darija":
                darija_patterns = ["كيفاش", "علاش", "فين", "شكون", "شنو", "فاش", "عافاك", "واش", "كاين", "ماكاينش"]
                for pattern in darija_patterns:
                    if pattern in text:
                        score += 4
            elif lang_code == "ar":
                arabic_patterns = ["كيف", "لماذا", "أين", "من", "ماذا", "متى", "هذا", "هذه"]
                for pattern in arabic_patterns:
                    if pattern in text:
                        score += 3
            elif lang_code == "tamazight":
                tamazight_patterns = ["ⵎⴰⵏ", "ⵎⴰⵏⵉ", "ⵎⴰⵏⵉⵎ", "ⵎⴰⵏⵉⵎⵏ", "ⵎⴰⵏⵉⵎⵏⵉ"]
                for pattern in tamazight_patterns:
                    if pattern in text:
                        score += 4
            
            scores[lang_code] = score
        
        # Retourner la langue avec le meilleur score
        if scores:
            best_lang = max(scores.items(), key=lambda x: x[1])
            confidence = min(best_lang[1] / 10, 0.95)  # Normaliser la confiance
            return {
                "language": best_lang[0] if best_lang[1] > 0 else "fr",
                "confidence": confidence,
                "method": "patterns"
            }
        
        return {"language": "fr", "confidence": 0.3, "method": "patterns"}
    
    def _detect_with_characters(self, text: str) -> Dict[str, Any]:
        """Détecte la langue par analyse des caractères"""
        # Compter les caractères arabes
        arabic_chars = len(re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', text))
        
        # Compter les caractères tamazight
        tamazight_chars = len(re.findall(r'[\u2D30-\u2D7F]', text))
        
        # Compter les caractères latins
        latin_chars = len(re.findall(r'[a-zA-Z]', text))
        
        total_chars = len(text)
        
        if total_chars == 0:
            return {"language": "fr", "confidence": 0.3, "method": "characters"}
        
        # Calculer les pourcentages
        arabic_ratio = arabic_chars / total_chars
        tamazight_ratio = tamazight_chars / total_chars
        latin_ratio = latin_chars / total_chars
        
        # Détecter la langue dominante
        if arabic_ratio > 0.3:
            # Distinguer entre arabe et darija (basé sur des patterns spécifiques)
            darija_indicators = ["كيفاش", "علاش", "فين", "شكون", "شنو", "فاش", "عافاك", "واش", "كاين", "ماكاينش"]
            if any(indicator in text for indicator in darija_indicators):
                return {"language": "darija", "confidence": min(arabic_ratio + 0.2, 0.9), "method": "characters"}
            else:
                return {"language": "ar", "confidence": min(arabic_ratio + 0.1, 0.9), "method": "characters"}
        elif tamazight_ratio > 0.2:
            return {"language": "tamazight", "confidence": min(tamazight_ratio + 0.3, 0.9), "method": "characters"}
        elif latin_ratio > 0.5:
            # Distinguer français et anglais
            english_indicators = ["the", "and", "is", "are", "was", "were", "with", "for", "but", "or"]
            french_indicators = ["le", "la", "les", "un", "une", "des", "et", "ou", "mais", "pour"]
            
            english_score = sum(1 for indicator in english_indicators if indicator in text)
            french_score = sum(1 for indicator in french_indicators if indicator in text)
            
            if english_score > french_score:
                return {"language": "en", "confidence": min(latin_ratio + 0.1, 0.9), "method": "characters"}
            else:
                return {"language": "fr", "confidence": min(latin_ratio + 0.1, 0.9), "method": "characters"}
        
        return {"language": "fr", "confidence": 0.3, "method": "characters"}
    
    def _combine_detection_results(self, pattern_result: Dict, char_result: Dict) -> Dict[str, Any]:
        """Combine les résultats des différentes méthodes de détection"""
        pattern_lang = pattern_result["language"]
        char_lang = char_result["language"]
        pattern_conf = pattern_result["confidence"]
        char_conf = char_result["confidence"]
        
        # Si les deux méthodes donnent le même résultat
        if pattern_lang == char_lang:
            combined_confidence = (pattern_conf + char_conf) / 2
            return {
                "language": pattern_lang,
                "confidence": combined_confidence,
                "method": "combined"
            }
        
        # Si les résultats diffèrent, prendre celui avec la plus haute confiance
        if pattern_conf > char_conf:
            return pattern_result
        else:
            return char_result
    
    async def translate_text(self, text: str, source_lang: str, target_lang: str = "fr") -> Dict[str, Any]:
        """Traduit le texte d'une langue vers une autre"""
        try:
            if source_lang == target_lang:
                return {
                    "translated_text": text,
                    "source_language": source_lang,
                    "target_language": target_lang,
                    "confidence": 1.0
                }
            
            # Utiliser Gemini pour la traduction
            llm = self.gemini_service.get_llm()
            
            prompt = f"""
            Traduis le texte suivant de {source_lang} vers {target_lang}.
            Conserve le sens et le style du texte original.
            
            Texte à traduire: {text}
            
            Traduction en {target_lang}:
            """
            
            response = await llm.ainvoke(prompt)
            translated_text = response.content if hasattr(response, 'content') else str(response)
            
            return {
                "translated_text": translated_text,
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Erreur traduction: {e}")
            return {
                "translated_text": text,  # Retourner le texte original en cas d'erreur
                "source_language": source_lang,
                "target_language": target_lang,
                "confidence": 0.3,
                "error": str(e)
            }
    
    def get_solar_response(self, language: str, topic: str = "general_info") -> str:
        """Récupère une réponse prédéfinie dans la langue spécifiée"""
        if language in self.solar_responses and topic in self.solar_responses[language]:
            return self.solar_responses[language][topic]
        else:
            # Fallback vers français
            return self.solar_responses["fr"].get(topic, "Information non disponible")
    
    async def process(self, state) -> Dict[str, Any]:
        """Méthode principale de traitement - détecte la langue et traduit la réponse"""
        try:
            user_message = state.current_message
            
            # 1. Détecter la langue de l'utilisateur
            detection_result = self.detect_language(user_message)
            detected_language = detection_result["language"]
            confidence = detection_result["confidence"]
            
            logger.info(f"Langue détectée: {detected_language} (confiance: {confidence})")
            
            # 2. Analyser le contenu pour déterminer le type de réponse
            topic = self._analyze_solar_topic(user_message)
            
            # 3. Générer la réponse dans la langue détectée
            if detected_language in self.solar_responses:
                response = self.get_solar_response(detected_language, topic)
            else:
                # Fallback vers français
                response = self.get_solar_response("fr", topic)
            
            # 4. Si la langue détectée n'est pas le français, traduire la réponse
            if detected_language != "fr":
                translation_result = await self.translate_text(response, "fr", detected_language)
                response = translation_result["translated_text"]
            
            return {
                "response": response,
                "detected_language": detected_language,
                "confidence": confidence,
                "agent_used": "multilingual_detector",
                "sources": ["Solar Nasih Multilingual Detection"],
                "translation_info": {
                    "original_language": "fr",
                    "target_language": detected_language,
                    "translation_confidence": confidence
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur dans l'agent multilingue: {e}")
            return {
                "response": f"Erreur dans le traitement multilingue: {str(e)}",
                "detected_language": "fr",
                "confidence": 0.0,
                "agent_used": "multilingual_detector",
                "error": str(e),
                "sources": ["Solar Nasih Multilingual Detection"]
            }
    
    def _analyze_solar_topic(self, message: str) -> str:
        """Analyse le message pour déterminer le sujet solaire"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["prix", "coût", "tarif", "price", "cost", "سعر", "ثمن", "ⵙⵉⵔ"]):
            return "pricing"
        elif any(word in message_lower for word in ["simulation", "production", "kwh", "kwc", "محاكاة", "إنتاج", "ⵉⵙⵙⵉⵔ"]):
            return "simulation"
        elif any(word in message_lower for word in ["bonjour", "salut", "hello", "مرحبا", "سلام", "ⴰⵣⵍⵎ"]):
            return "welcome"
        else:
            return "general_info"
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        """Détermine si l'agent peut traiter la requête"""
        # L'agent multilingue peut traiter toutes les requêtes
        # mais avec une priorité plus élevée pour les langues non-françaises
        text_lower = user_input.lower()
        
        # Détecter si le texte contient des caractères non-latins
        has_arabic = bool(re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', text_lower))
        has_tamazight = bool(re.search(r'[\u2D30-\u2D7F]', text_lower))
        
        if has_arabic or has_tamazight:
            return 0.9  # Haute priorité pour les langues non-latines
        
        # Vérifier les mots-clés spécifiques
        multilingual_indicators = [
            "كيفاش", "علاش", "فين", "شكون", "شنو", "فاش", "عافاك",  # Darija
            "كيف", "لماذا", "أين", "من", "ماذا", "متى",  # Arabe
            "ⵎⴰⵏ", "ⵎⴰⵏⵉ", "ⵎⴰⵏⵉⵎ",  # Tamazight
            "the", "and", "is", "are", "was", "were"  # Anglais
        ]
        
        if any(indicator in text_lower for indicator in multilingual_indicators):
            return 0.8
        
        return 0.3  # Priorité normale pour le français 