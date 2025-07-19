import logging
from typing import List, Dict, Any, Optional
import openai
from openai import OpenAI

logger = logging.getLogger(__name__)

class OpenAILLM:
    """OpenAI language model interface."""
    
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        logger.info(f"OpenAI LLM initialized with model: {model}")
    
    def generate(self,
                prompt: str,
                context: List[Dict[str, Any]],
                max_tokens: int = 1000,
                temperature: float = 0.1,
                system_prompt: Optional[str] = None) -> str:
        """Generate response using OpenAI API."""
        try:
            # Prepare messages
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            # Add context and prompt
            user_message = self._format_prompt_with_context(prompt, context)
            messages.append({"role": "user", "content": user_message})
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise
    
    def _format_prompt_with_context(self, prompt: str, context: List[Dict[str, Any]]) -> str:
        """Format prompt with retrieved context."""
        if not context:
            return prompt
        
        context_text = "\n\n".join([
            f"Source: {item.get('source', 'Unknown')}\n"
            f"Content: {item.get('content', '')}"
            for item in context
        ])
        
        formatted_prompt = f"""Based on the following context, please answer the question.

Context:
{context_text}

Question: {prompt}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to answer the question, please mention that."""
        
        return formatted_prompt

