import logging
from typing import List, Dict, Any, Optional, Union
from .llm.openai_llm import OpenAILLM
from .llm.anthropic_llm import AnthropicLLM
from .llm.huggingface_llm import HuggingFaceLLM
from .llm.gemini_provider import GeminiProvider
from .prompt_templates.multimodal_prompts import MultimodalPrompts
from .context_builder import ContextBuilder
from config.settings import settings

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Main response generator for RAG system."""
    
    def __init__(self, 
                 #llm_provider: str = "openai",
                 llm_provider: str = "gemini",
                 model_name: Optional[str] = None,
                 use_context_builder: bool = True):
        
        self.llm_provider = llm_provider
        self.prompt_templates = MultimodalPrompts()
        
        if use_context_builder:
            self.context_builder = ContextBuilder()
        else:
            self.context_builder = None
        
        # Initialize LLM
        self.llm = self._initialize_llm(llm_provider, model_name)
        
        logger.info(f"Response generator initialized with {llm_provider}")
    
    def _initialize_llm(self, provider: str, model_name: Optional[str]) -> Union[OpenAILLM, AnthropicLLM, HuggingFaceLLM, GeminiProvider]:
        """Initialize the specified LLM provider."""
        try:
            if provider == "openai":
                if not settings.openai_api_key:
                    raise ValueError("OpenAI API key not configured")
                model = model_name or settings.default_llm_model
                return OpenAILLM(settings.openai_api_key, model)
                
            elif provider == "anthropic":
                if not settings.anthropic_api_key:
                    raise ValueError("Anthropic API key not configured")
                model = model_name or "claude-3-sonnet-20240229"
                return AnthropicLLM(settings.anthropic_api_key, model)
                
            elif provider == "huggingface":
                model = model_name or "microsoft/DialoGPT-medium"
                return HuggingFaceLLM(model)
        
            elif provider == "gemini":
                if not settings.gemini_api_key:
                    raise ValueError("Gemini API key not configured")
                model = model_name or "gemini-2.0-flash-exp"
                return GeminiProvider(settings.gemini_api_key, model)
                
            else:
                raise ValueError(f"Unsupported LLM provider: {provider}")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {str(e)}")
            raise
    
    def generate_response(self,
                         query: str,
                         retrieved_docs: List[Dict[str, Any]],
                         template_type: str = "general_rag",
                         max_tokens: int = 1000,
                         temperature: float = 0.1,
                         **kwargs) -> Dict[str, Any]:
        """Generate response from query and retrieved documents."""
        try:
            # Build context
            if self.context_builder:
                context_docs = self.context_builder.build_context(retrieved_docs, query)
            else:
                context_docs = retrieved_docs
            
            # Determine appropriate template type based on document types
            if template_type == "auto":
                template_type = self._determine_template_type(context_docs)
            
            # Generate prompt
            prompt = self.prompt_templates.get_prompt(
                template_type, query, context_docs, **kwargs
            )
            
            # Get system prompt
            system_prompt = self.prompt_templates.get_system_prompt(template_type)
            
            # Generate response
            response_text = self.llm.generate(
                prompt=prompt,
                context=context_docs,
                max_tokens=max_tokens,
                temperature=temperature,
                system_prompt=system_prompt
            )
            
            # Prepare response metadata
            response_metadata = {
                'template_type': template_type,
                'llm_provider': self.llm_provider,
                'context_length': len(context_docs),
                'sources_used': [doc.get('source', 'Unknown') for doc in context_docs],
                'document_types': list(set(doc.get('metadata', {}).get('doc_type', 'text') for doc in context_docs)),
                'generation_params': {
                    'max_tokens': max_tokens,
                    'temperature': temperature
                }
            }
            
            return {
                'response': response_text,
                'metadata': response_metadata,
                'context': context_docs,
                'query': query
            }
            
        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            raise
    
    def _determine_template_type(self, context_docs: List[Dict[str, Any]]) -> str:
        """Automatically determine the best template type based on context."""
        if not context_docs:
            return "general_rag"
        
        # Count document types
        doc_types = [doc.get('metadata', {}).get('doc_type', 'text') for doc in context_docs]
        type_counts = {}
        for doc_type in doc_types:
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        # Determine dominant type
        total_docs = len(context_docs)
        
        # If mostly one type
        for doc_type, count in type_counts.items():
            if count / total_docs >= 0.7:  # 70% or more of one type
                if doc_type == 'image':
                    return "image_focused"
                elif doc_type == 'audio':
                    return "audio_focused"
                elif doc_type == 'video':
                    return "video_focused"
        
        # If multiple types (multimodal)
        if len(type_counts) > 1:
            return "multimodal_rag"
        
        # Default to general RAG
        return "general_rag"
    
    def generate_multimodal_response(self,
                                   query: str,
                                   text_docs: List[Dict[str, Any]] = None,
                                   image_docs: List[Dict[str, Any]] = None,
                                   audio_docs: List[Dict[str, Any]] = None,
                                   video_docs: List[Dict[str, Any]] = None,
                                   **kwargs) -> Dict[str, Any]:
        """Generate response specifically for multimodal content."""
        try:
            # Combine all documents
            all_docs = []
            if text_docs:
                all_docs.extend(text_docs)
            if image_docs:
                all_docs.extend(image_docs)
            if audio_docs:
                all_docs.extend(audio_docs)
            if video_docs:
                all_docs.extend(video_docs)
            
            # Sort by relevance score
            all_docs.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return self.generate_response(
                query=query,
                retrieved_docs=all_docs,
                template_type="multimodal_rag",
                **kwargs
            )
            
        except Exception as e:
            logger.error(f"Multimodal response generation failed: {str(e)}")
            raise

