
import logging
import time
from typing import List, Dict, Any, Optional
import json

logger = logging.getLogger(__name__)

class GeminiProvider:
    """Provider pour Google Gemini 2.0 gratuit"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash-exp"):
        self.api_key = api_key
        self.model = model
        
        try:
            import google.generativeai as genai
            
            # Configuration de l'API
            genai.configure(api_key=api_key)
            
            # Initialisation du modèle
            self.client = genai.GenerativeModel(model)
            
            # Test de connexion
            test_response = self.client.generate_content("Hello")
            if test_response:
                logger.info(f"✅ Gemini provider initialized with model: {model}")
            else:
                raise Exception("Failed to get test response")
                
        except ImportError:
            logger.error("❌ Google GenerativeAI library not installed")
            logger.info("💡 Install with: pip install google-generativeai")
            raise
        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}")
            raise
    
    def generate_response(self, 
                         prompt: str, 
                         max_tokens: int = 1000, 
                         temperature: float = 0.1) -> str:
        """Génère une réponse avec Gemini"""
        try:
            # Configuration de génération
            generation_config = {
                'temperature': temperature,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': max_tokens,
            }
            
            # Génération
            response = self.client.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if response.text:
                return response.text.strip()
            else:
                raise Exception("Empty response from Gemini")
                
        except Exception as e:
            logger.error(f"❌ Gemini generation failed: {e}")
            raise
    
    def generate_with_context(self, 
                             query: str, 
                             context: List[Dict[str, Any]],
                             max_tokens: int = 1000,
                             temperature: float = 0.1,
                             system_prompt: Optional[str] = None) -> str:
        """Génère une réponse avec contexte formaté"""
        try:
            # Formater le prompt avec contexte
            formatted_prompt = self._format_prompt_with_context(query, context, system_prompt)
            
            # Générer la réponse
            return self.generate_response(
                prompt=formatted_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
        except Exception as e:
            logger.error(f"❌ Context generation failed: {e}")
            raise
    
    def _format_prompt_with_context(self, 
                                   query: str, 
                                   context: List[Dict[str, Any]], 
                                   system_prompt: Optional[str] = None) -> str:
        """Formate le prompt avec le contexte"""
        
        if not context:
            return query
        
        # Construire le contexte
        context_parts = []
        for i, item in enumerate(context, 1):
            source = item.get('source', 'Source inconnue')
            content = item.get('content', '')
            doc_type = item.get('metadata', {}).get('doc_type', 'texte')
            score = item.get('score', 0.0)
            
            context_parts.append(
                f"📄 **Document {i}** ({doc_type.upper()}) - Pertinence: {score:.2f}\n"
                f"**Source:** {source}\n"
                f"**Contenu:** {content}\n"
            )
        
        context_text = "\n".join(context_parts)
        
        # Prompt système par défaut
        default_system = """Tu es un assistant IA expert qui analyse des documents pour répondre aux questions.
        
RÈGLES IMPORTANTES:
- Utilise UNIQUEMENT les informations fournies dans les documents
- Si les documents ne contiennent pas assez d'informations, dis-le clairement
- Cite tes sources en mentionnant le numéro du document
- Structure ta réponse de manière claire et logique
- Reste factuel et précis"""
        
        system_instruction = system_prompt or default_system
        
        # Prompt final
        final_prompt = f"""{system_instruction}

## DOCUMENTS À ANALYSER:

{context_text}

## QUESTION:
{query}

## RÉPONSE:
Basé sur l'analyse des documents fournis, voici ma réponse détaillée:"""
        
        return final_prompt

    def generate(self, prompt, context=None, max_tokens=1000, temperature=0.1, system_prompt=None):
        # Construit le prompt complet avec contexte si besoin
        if context is not None:
            return self.generate_with_context(
                query=prompt,
                context=context,
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt=system_prompt
            )
        else:
            return self.generate_response(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )