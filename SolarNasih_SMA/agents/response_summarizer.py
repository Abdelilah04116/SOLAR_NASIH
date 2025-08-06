from typing import Dict, Any, List
from langchain.tools import Tool
from agents.base_agent import BaseAgent
from models.schemas import AgentType
from services.gemini_service import GeminiService
import re
import logging

logger = logging.getLogger(__name__)

class ResponseSummarizerAgent(BaseAgent):
    """
    Agent Résumeur de Réponses - Transforme les réponses des agents en format structuré
    """
    
    def __init__(self):
        super().__init__(
            agent_type=AgentType.RESPONSE_SUMMARIZER,
            description="Agent qui résume et structure les réponses des autres agents"
        )
        self.gemini_service = GeminiService()
    
    def _init_tools(self) -> List[Tool]:
        """Initialise les outils du résumeur"""
        return [
            Tool(
                name="summarize_response",
                description="Résume et structure une réponse",
                func=self._summarize_response
            ),
            Tool(
                name="extract_key_points",
                description="Extrait les points clés d'une réponse",
                func=self._extract_key_points
            ),
            Tool(
                name="format_chatgpt_style",
                description="Formate la réponse en style ChatGPT",
                func=self._format_chatgpt_style
            )
        ]
    
    def _get_system_prompt(self) -> str:
        """Prompt système pour le résumeur de réponses"""
        return """
        Tu es l'Agent Formateur de Réponses du système Solar Nasih.
        
        Ton rôle est de formater les réponses des agents spécialisés en style structuré et professionnel, similaire à ChatGPT.
        
        **IMPORTANT : Ne résume PAS le contenu, formate-le seulement !**
        
        **Format de sortie souhaité :**
        1. **Titre contextuel** (gras, basé sur la question)
        2. **Points clés** (extraction des données importantes)
        3. **Contenu original** (le contenu complet des agents)
        
        **Règles de formatage :**
        - Garder TOUT le contenu original
        - Ajouter seulement un titre et des points clés
        - Extraire les points clés pour faciliter la lecture
        - Utiliser UN SEUL saut de ligne entre sections
        - Éviter les sauts de ligne multiples
        - Langage clair et professionnel
        
        **Exemple de format :**
        **Réponse à votre question sur l'énergie solaire.**

        **Points clés :**
        • [Extraction automatique des données importantes]

        **Contenu détaillé :**
        [Contenu complet des agents sans modification]
        """
    
    def _summarize_response(self, response: str) -> str:
        """Résume une réponse en format structuré"""
        try:
            if not response or len(response.strip()) < 10:
                return "Aucune information disponible pour générer un résumé."
            
            # Utiliser Gemini pour générer le résumé
            llm = self.gemini_service.get_llm()
            
            prompt = f"""
            Tu es un expert en résumé de contenu technique sur l'énergie solaire.
            
            Voici une réponse d'un agent spécialisé :
            {response}
            
            Transforme cette réponse en format structuré avec :
            1. **Résumé en une phrase** (gras, maximum 150 mots)
            2. **Points clés** (3-5 points maximum, liste à puces)
            3. **Détails techniques** (paragraphe court si nécessaire)
            4. **Recommandations** (si applicable)
            
            Utilise un langage clair, professionnel et accessible.
            """
            
            result = llm.invoke(prompt)
            return result.content if hasattr(result, 'content') else str(result)
            
        except Exception as e:
            logger.error(f"Erreur lors du résumé: {e}")
            return self._fallback_summarize(response)
    
    def _extract_key_points(self, response: str) -> str:
        """Extrait les points clés d'une réponse SANS couper"""
        try:
            # Extraction automatique des points clés
            lines = response.split('\n')
            key_points = []
            
            # Chercher les lignes avec des données importantes
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Détecter les lignes avec des données chiffrées
                if any(keyword in line.lower() for keyword in ['kwh', 'kwc', '€', 'ans', 'production', 'coût', 'prix', 'économie']):
                    key_points.append(line)
                elif len(line) > 10 and len(line) < 100 and not line.startswith('*'):
                    key_points.append(line)
            
            # Limiter à 5 points maximum pour l'affichage
            if len(key_points) > 5:
                key_points = key_points[:5]
            
            if key_points:
                return "**Points clés :**\n" + "\n".join([f"• {point}" for point in key_points])
            else:
                return "**Informations principales :**\n" + "Contenu complet disponible ci-dessous"
                
        except Exception as e:
            logger.error(f"Erreur extraction points clés: {e}")
            return "**Informations :**\n" + "Contenu complet disponible ci-dessous"
    
    def _format_chatgpt_style(self, response: str) -> str:
        """Formate la réponse en style ChatGPT SANS couper"""
        try:
            # Nettoyer la réponse
            cleaned_response = self._clean_response(response)
            
            # Générer un résumé automatique
            summary = self._generate_auto_summary(cleaned_response)
            
            # Extraire les points clés
            key_points = self._extract_key_points(cleaned_response)
            
            # Formater en style ChatGPT avec TOUT le contenu
            formatted_response = f"**{summary}**\n\n{key_points}\n\n**Contenu détaillé :**\n{cleaned_response}"
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Erreur formatage ChatGPT: {e}")
            return response
    
    def _clean_response(self, response: str) -> str:
        """Nettoie la réponse des métadonnées SANS couper le contenu"""
        if not response:
            return ""
        
        # Supprimer les métadonnées et émojis
        lines = response.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Ignorer SEULEMENT les lignes avec métadonnées système
            if any(skip in line.lower() for skip in [
                "confiance:", "similarité:", "score:", "agent:", "base de connaissances",
                "🟢", "🟡", "🔴", "📚", "🤖", "🔍", "**analyse de votre demande**"
            ]):
                continue
            
            # NE PAS ignorer les lignes techniques - elles font partie du contenu
            cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _generate_auto_summary(self, response: str) -> str:
        """Génère un résumé automatique"""
        try:
            # Extraire les informations principales
            lines = response.split('\n')
            summary_parts = []
            
            for line in lines[:3]:  # Prendre les 3 premières lignes utiles
                if any(keyword in line.lower() for keyword in ['kwh', 'kwc', '€', 'ans', 'production', 'coût', 'prix']):
                    summary_parts.append(line)
            
            if summary_parts:
                return summary_parts[0][:100] + "..."
            else:
                return "Informations sur l'énergie solaire disponibles."
                
        except Exception as e:
            logger.error(f"Erreur génération résumé auto: {e}")
            return "Résumé de la réponse généré."
    
    def _fallback_summarize(self, response: str) -> str:
        """Résumé de fallback si Gemini échoue SANS couper"""
        try:
            # Résumé simple basé sur les mots-clés
            response_lower = response.lower()
            
            if 'kwh' in response_lower and 'kwc' in response_lower:
                return f"**Simulation énergétique générée.**\n\n**Points clés :**\n• Données de production et consommation calculées\n• Estimation des économies réalisées\n• Analyse de rentabilité incluse\n\n**Contenu détaillé :**\n{response}"
            
            elif '€' in response_lower or 'prix' in response_lower:
                return f"**Informations financières fournies.**\n\n**Points clés :**\n• Estimation des coûts d'installation\n• Calcul des aides disponibles\n• Analyse de rentabilité\n\n**Contenu détaillé :**\n{response}"
            
            else:
                return f"**Réponse technique générée.**\n\n**Points clés :**\n• Informations spécialisées fournies\n• Recommandations techniques incluses\n• Données actualisées\n\n**Contenu détaillé :**\n{response}"
                
        except Exception as e:
            logger.error(f"Erreur fallback: {e}")
            return response
    
    async def process(self, state) -> Dict[str, Any]:
        """Méthode principale de traitement - formate et structure la réponse"""
        try:
            original_response = state.current_message
            user_question = state.context.get("user_question", "")
            
            # Vérifier si c'est une réponse longue (quiz, documents, guides)
            is_long_response = (
                len(original_response) > 5000 or 
                "Question" in original_response and original_response.count("Question") > 10 or
                "═══" in original_response or  # Documents avec séparateurs
                "MAINTENANCE" in original_response or  # Guides de maintenance
                "FORMATION" in original_response or    # Documents de formation
                "DEVIS" in original_response or        # Devis détaillés
                "CONTRAT" in original_response         # Contrats complets
            )
            
            if is_long_response:
                # Pour les réponses longues, utiliser le formatage local SANS Gemini
                logger.info("Long response detected, using local formatting without Gemini")
                formatted_response = self._format_chatgpt_style_with_context(original_response, user_question)
            else:
                # Pour les réponses courtes, utiliser Gemini
                formatted_response = self._summarize_response_with_context(original_response, user_question)
                
                # Si le formatage échoue, utiliser le formatage automatique
                if "Aucune information disponible" in formatted_response:
                    formatted_response = self._format_chatgpt_style_with_context(original_response, user_question)
            
            return {
                "response": formatted_response,
                "original_response": original_response,
                "agent_used": "response_formatter",
                "confidence": 0.9,
                "sources": ["Solar Nasih Response Formatter"],
                "processing_info": {
                    "formatted": True,
                    "format": "chatgpt_style",
                    "word_count": len(formatted_response.split()),
                    "user_question": user_question,
                    "content_preserved": True,
                    "long_response": is_long_response
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur dans l'agent formateur: {e}")
            return {
                "response": f"Erreur lors du formatage: {str(e)}",
                "original_response": state.current_message,
                "agent_used": "response_formatter",
                "confidence": 0.0,
                "error": str(e),
                "sources": ["Solar Nasih Response Formatter"]
            }
    
    def _summarize_response_with_context(self, response: str, user_question: str) -> str:
        """Formate une réponse en tenant compte de la question de l'utilisateur"""
        try:
            if not response or len(response.strip()) < 10:
                return "Aucune information disponible."
            
            # Utiliser Gemini pour formater la réponse avec contexte
            llm = self.gemini_service.get_llm()
            
            prompt = f"""
            Tu es un expert en formatage de contenu technique sur l'énergie solaire.
            
            Question de l'utilisateur : {user_question}
            
            Réponse d'un agent spécialisé :
            {response}
            
            **IMPORTANT : Ne résume PAS le contenu, formate-le seulement !**
            **CRITIQUE : Garder TOUT le contenu original, ne rien couper !**
            
            Transforme cette réponse en format structuré :
            1. **Titre contextuel** (gras, basé sur la question) - maximum 100 mots
            2. **Points clés** (extraction des données importantes) - 3-5 points maximum
            3. **Contenu détaillé** (le contenu original COMPLET sans aucune modification)
            
            **Règles STRICTES :**
            - Garder TOUT le contenu original sans aucune coupure
            - Ne pas résumer, ne pas tronquer, ne pas omettre
            - Ajouter seulement un titre et des points clés
            - Utiliser UN SEUL saut de ligne entre sections
            - Éviter les sauts de ligne multiples
            - Format : **Titre**\n\n**Points clés :**\n• Point 1\n• Point 2\n\n**Contenu détaillé :**\n[Contenu original COMPLET]
            
            **EXEMPLE :** Si l'agent a généré 30 questions, afficher les 30 questions complètes.
            """
            
            result = llm.invoke(prompt)
            return result.content if hasattr(result, 'content') else str(result)
            
        except Exception as e:
            logger.error(f"Erreur lors du formatage avec contexte: {e}")
            return self._format_chatgpt_style_with_context(response, user_question)
    
    def _format_chatgpt_style_with_context(self, response: str, user_question: str) -> str:
        """Formate la réponse en style ChatGPT en tenant compte de la question SANS couper"""
        try:
            # Nettoyer la réponse
            cleaned_response = self._clean_response(response)
            
            # Générer un titre contextuel
            title = self._generate_contextual_title(cleaned_response, user_question)
            
            # Pour les documents structurés, préserver le formatage original
            if any(marker in cleaned_response for marker in ["═══", "MAINTENANCE", "FORMATION", "DEVIS", "CONTRAT"]):
                # Document structuré - préserver le formatage
                formatted_response = f"**{title}**\n\n{cleaned_response}"
            else:
                # Contenu standard - extraire les points clés
                key_points = self._extract_key_points(cleaned_response)
                formatted_response = f"**{title}**\n\n{key_points}\n\n**Contenu détaillé :**\n{cleaned_response}"
            
            return formatted_response
            
        except Exception as e:
            logger.error(f"Erreur formatage ChatGPT avec contexte: {e}")
            return response
    
    def _generate_contextual_summary(self, response: str, user_question: str) -> str:
        """Génère un résumé automatique lié à la question"""
        try:
            # Analyser la question pour comprendre le contexte
            question_lower = user_question.lower()
            
            # Détecter le type de question
            if any(word in question_lower for word in ['roi', 'retour', 'amortissement', 'rentabilité']):
                return "Analyse de rentabilité et retour sur investissement de votre installation solaire."
            elif any(word in question_lower for word in ['production', 'kwh', 'kwc', 'énergie']):
                return "Simulation de production énergétique de votre installation photovoltaïque."
            elif any(word in question_lower for word in ['prix', 'coût', '€', 'devis', 'tarif']):
                return "Estimation des coûts et tarifs pour votre projet solaire."
            elif any(word in question_lower for word in ['aide', 'subvention', 'prime', 'financement']):
                return "Informations sur les aides et subventions disponibles."
            elif any(word in question_lower for word in ['installation', 'panneau', 'onduleur', 'technique']):
                return "Conseils techniques pour votre installation photovoltaïque."
            else:
                # Résumé générique basé sur le contenu
                lines = response.split('\n')
                summary_parts = []
                
                for line in lines[:3]:
                    if any(keyword in line.lower() for keyword in ['kwh', 'kwc', '€', 'ans', 'production', 'coût', 'prix']):
                        summary_parts.append(line)
                
                if summary_parts:
                    return summary_parts[0][:100] + "..."
                else:
                    return "Informations sur l'énergie solaire en réponse à votre question."
                
        except Exception as e:
            logger.error(f"Erreur génération résumé contextuel: {e}")
            return "Résumé de la réponse généré."
    
    def _generate_contextual_title(self, response: str, user_question: str) -> str:
        """Génère un titre contextuel basé sur la question"""
        try:
            # Analyser la question pour comprendre le contexte
            question_lower = user_question.lower()
            
            # Détecter le type de question
            if any(word in question_lower for word in ['roi', 'retour', 'amortissement', 'rentabilité']):
                return "Analyse de rentabilité de votre installation solaire"
            elif any(word in question_lower for word in ['production', 'kwh', 'kwc', 'énergie']):
                return "Simulation de production énergétique de votre installation photovoltaïque"
            elif any(word in question_lower for word in ['prix', 'coût', '€', 'devis', 'tarif']):
                return "Estimation des coûts et tarifs pour votre projet solaire"
            elif any(word in question_lower for word in ['aide', 'subvention', 'prime', 'financement']):
                return "Informations sur les aides et subventions disponibles"
            elif any(word in question_lower for word in ['installation', 'panneau', 'onduleur', 'technique']):
                return "Conseils techniques pour votre installation photovoltaïque"
            elif any(word in question_lower for word in ['quiz', 'question', 'test']):
                return "Quiz et questions sur l'énergie solaire"
            else:
                return "Réponse à votre question sur l'énergie solaire"
                
        except Exception as e:
            logger.error(f"Erreur génération titre contextuel: {e}")
            return "Informations sur l'énergie solaire"
    
    def _fallback_summarize_with_context(self, response: str, user_question: str) -> str:
        """Formatage de fallback avec contexte si Gemini échoue SANS couper"""
        try:
            # Analyser la question pour adapter le titre
            question_lower = user_question.lower()
            
            if 'roi' in question_lower or 'retour' in question_lower:
                title = "Analyse de rentabilité de votre installation solaire"
            elif 'production' in question_lower or 'kwh' in question_lower:
                title = "Simulation de production énergétique"
            elif 'prix' in question_lower or 'coût' in question_lower:
                title = "Estimation des coûts d'installation"
            elif 'quiz' in question_lower or 'question' in question_lower:
                title = "Quiz et questions sur l'énergie solaire"
            else:
                title = "Réponse à votre question sur l'énergie solaire"
            
            # Extraire les points clés
            key_points = self._extract_key_points(response)
            
            return f"**{title}**\n\n{key_points}\n\n**Contenu détaillé :**\n{response}"
                
        except Exception as e:
            logger.error(f"Erreur fallback avec contexte: {e}")
            return response
    
    def can_handle(self, user_input: str, context: Dict[str, Any] = None) -> float:
        """L'agent résumeur peut traiter toutes les réponses"""
        return 1.0 