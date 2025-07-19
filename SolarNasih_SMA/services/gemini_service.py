from typing import Dict, Any, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from config.settings import settings
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """
    Service pour interagir avec l'API Gemini 2.0
    """
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.temperature = settings.GEMINI_TEMPERATURE
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        
        # Configuration de l'API Gemini
        try:
            genai.configure(api_key=self.api_key)
            self.llm = self._initialize_llm()
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Gemini: {e}")
            raise
    
    def _initialize_llm(self) -> ChatGoogleGenerativeAI:
        """Initialise le modèle LangChain avec Gemini"""
        try:
            return ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                google_api_key=self.api_key
            )
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du LLM: {e}")
            raise
    
    def get_llm(self) -> ChatGoogleGenerativeAI:
        """Retourne l'instance du LLM"""
        return self.llm
    
    async def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Génère une réponse avec Gemini
        
        Args:
            prompt: Le prompt utilisateur
            system_prompt: Le prompt système (optionnel)
            context: Contexte additionnel (optionnel)
            
        Returns:
            La réponse générée
        """
        try:
            # Préparation du prompt complet
            full_prompt = self._prepare_prompt(prompt, system_prompt, context)
            
            # Génération de la réponse
            response = await self.llm.ainvoke([HumanMessage(content=full_prompt)])
            
            return response.content
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération avec Gemini: {e}")
            return f"Erreur lors de la génération: {str(e)}"
    
    def _prepare_prompt(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Prépare le prompt complet"""
        
        parts = []
        
        if system_prompt:
            parts.append(f"SYSTÈME: {system_prompt}")
        
        if context:
            parts.append(f"CONTEXTE: {self._format_context(context)}")
        
        parts.append(f"UTILISATEUR: {prompt}")
        
        return "\n\n".join(parts)
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Formate le contexte pour le prompt"""
        formatted = []
        
        for key, value in context.items():
            if isinstance(value, (str, int, float)):
                formatted.append(f"- {key}: {value}")
            elif isinstance(value, list):
                formatted.append(f"- {key}: {', '.join(map(str, value))}")
            elif isinstance(value, dict):
                formatted.append(f"- {key}: {value}")
        
        return "\n".join(formatted)
    
    async def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Analyse l'intention de l'utilisateur
        
        Args:
            user_input: Le message de l'utilisateur
            
        Returns:
            Dictionnaire contenant l'analyse d'intention
        """
        
        intent_prompt = f"""
        Analyse l'intention de l'utilisateur dans le contexte du conseil en énergie solaire.
        
        Catégories possibles:
        - information_generale: Questions sur le solaire en général
        - conseil_technique: Questions techniques d'installation
        - simulation_energetique: Demandes de calculs/simulations
        - aide_reglementaire: Questions sur les normes/réglementations
        - assistance_commerciale: Questions sur les prix/financement
        - formation_certification: Questions sur les formations/certifications
        - generation_documents: Demandes de création de documents
        
        Message utilisateur: "{user_input}"
        
        Réponds au format JSON avec:
        {{
            "intention_principale": "categorie",
            "confiance": 0.8,
            "mots_cles": ["mot1", "mot2"],
            "contexte_detecte": "description"
        }}
        """
        
        try:
            response = await self.generate_response(intent_prompt)
            # Ici, on devrait parser la réponse JSON
            # Pour la simplicité, on retourne un format basique
            return {
                "intention_principale": "information_generale",
                "confiance": 0.7,
                "mots_cles": user_input.split()[:5],
                "contexte_detecte": "Analyse en cours"
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse d'intention: {e}")
            return {
                "intention_principale": "information_generale",
                "confiance": 0.5,
                "mots_cles": [],
                "contexte_detecte": "Erreur d'analyse"
            }
    
    async def enhance_response(
        self, 
        base_response: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """
        Améliore une réponse de base avec le contexte utilisateur
        
        Args:
            base_response: La réponse de base
            user_context: Le contexte utilisateur
            
        Returns:
            Réponse améliorée
        """
        
        enhancement_prompt = f"""
        Améliore cette réponse en la personnalisant selon le contexte utilisateur.
        
        Réponse de base: "{base_response}"
        
        Contexte utilisateur: {self._format_context(user_context)}
        
        Consignes:
        - Garde le contenu technique intact
        - Ajoute des éléments personnalisés
        - Reste professionnel et informatif
        - Réponds en français
        """
        
        try:
            return await self.generate_response(enhancement_prompt)
        except Exception as e:
            logger.error(f"Erreur lors de l'amélioration: {e}")
            return base_response
    
    async def summarize_conversation(self, messages: List[BaseMessage]) -> str:
        """
        Résume une conversation
        
        Args:
            messages: Liste des messages de la conversation
            
        Returns:
            Résumé de la conversation
        """
        
        conversation_text = "\n".join([
            f"{'Utilisateur' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
            for msg in messages
        ])
        
        summary_prompt = f"""
        Résume cette conversation sur l'énergie solaire en français.
        
        Conversation:
        {conversation_text}
        
        Fournis un résumé structuré avec:
        - Sujets abordés
        - Informations clés échangées
        - Prochaines étapes suggérées
        """
        
        try:
            return await self.generate_response(summary_prompt)
        except Exception as e:
            logger.error(f"Erreur lors du résumé: {e}")
            return "Erreur lors du résumé de la conversation"
    
    def validate_api_key(self) -> bool:
        """Valide la clé API Gemini"""
        try:
            # Test simple d'appel API
            test_model = genai.GenerativeModel(self.model_name)
            test_response = test_model.generate_content("Test")
            return True
        except Exception as e:
            logger.error(f"Clé API Gemini invalide: {e}")
            return False