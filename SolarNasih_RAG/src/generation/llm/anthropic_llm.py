import logging
from typing import List, Dict, Any, Optional
import anthropic

logger = logging.getLogger(__name__)

class AnthropicLLM:
    """Anthropic Claude language model interface."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
        logger.info(f"Anthropic LLM initialized with model: {model}")
    
    def generate(self,
                prompt: str,
                context: List[Dict[str, Any]],
                max_tokens: int = 1000,
                temperature: float = 0.1,
                system_prompt: Optional[str] = None) -> str:
        """Generate response using Anthropic API."""
        try:
            # Format prompt with context
            formatted_prompt = self._format_prompt_with_context(prompt, context)
            
            # Generate response
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt or "You are a helpful assistant that answers questions based on provided context.",
                messages=[
                    {"role": "user", "content": formatted_prompt}
                ]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {str(e)}")
            raise
    
    def _format_prompt_with_context(self, prompt: str, context: List[Dict[str, Any]]) -> str:
        """Format prompt with retrieved context."""
        if not context:
            return prompt
        
        context_parts = []
        for i, item in enumerate(context, 1):
            source = item.get('source', 'Unknown')
            content = item.get('content', '')
            doc_type = item.get('metadata', {}).get('doc_type', 'text')
            
            context_parts.append(f"[Source {i} - {doc_type}]: {source}\n{content}")
        
        context_text = "\n\n".join(context_parts)
        
        formatted_prompt = f"""I have the following context information:

{context_text}

Based on this context, please answer: {prompt}

Instructions:
- Use only the information provided in the context
- If the context doesn't contain sufficient information, please state that clearly
- Cite the relevant sources when possible
- Provide a comprehensive and accurate answer"""
        
        return formatted_prompt
