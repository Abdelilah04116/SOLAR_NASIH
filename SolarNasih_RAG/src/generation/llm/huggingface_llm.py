import logging
from typing import List, Dict, Any, Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

logger = logging.getLogger(__name__)

class HuggingFaceLLM:
    """Hugging Face transformers language model interface."""
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
            self.model.to(self.device)
            
            # Add padding token if not present
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            # Create text generation pipeline
            self.generator = pipeline(
                "text-generation",
                model=self.model,
                tokenizer=self.tokenizer,
                device=0 if self.device == "cuda" else -1
            )
            
            logger.info(f"HuggingFace LLM initialized with model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {str(e)}")
            raise
    
    def generate(self,
                prompt: str,
                context: List[Dict[str, Any]],
                max_tokens: int = 1000,
                temperature: float = 0.1,
                system_prompt: Optional[str] = None) -> str:
        """Generate response using HuggingFace model."""
        try:
            # Format prompt with context
            formatted_prompt = self._format_prompt_with_context(prompt, context, system_prompt)
            
            # Generate response
            outputs = self.generator(
                formatted_prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
            
            # Extract generated text
            generated_text = outputs[0]['generated_text']
            
            # Remove the input prompt from the generated text
            if generated_text.startswith(formatted_prompt):
                response = generated_text[len(formatted_prompt):].strip()
            else:
                response = generated_text.strip()
            
            return response
            
        except Exception as e:
            logger.error(f"HuggingFace generation failed: {str(e)}")
            raise
    
    def _format_prompt_with_context(self, 
                                   prompt: str, 
                                   context: List[Dict[str, Any]], 
                                   system_prompt: Optional[str] = None) -> str:
        """Format prompt with retrieved context."""
        parts = []
        
        if system_prompt:
            parts.append(f"System: {system_prompt}")
        
        if context:
            parts.append("Context:")
            for item in context:
                content = item.get('content', '')[:500]  # Truncate for token limits
                source = item.get('source', 'Unknown')
                parts.append(f"- {content} (Source: {source})")
        
        parts.append(f"Question: {prompt}")
        parts.append("Answer:")