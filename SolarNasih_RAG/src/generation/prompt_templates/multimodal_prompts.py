import logging
from typing import Dict, List, Any, Optional
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

class MultimodalPrompts:
    """
    Load and render multimodal prompt templates for RAG (Retrieval-Augmented Generation).
    Supports text, image, audio, and video-specific prompts.
    """

    def __init__(self, templates_file: Optional[str] = None):
        self.templates = self._load_templates(templates_file)

    def _load_templates(self, templates_file: Optional[str] = None) -> Dict[str, str]:
        """Load prompt templates from YAML file or use defaults."""
        if templates_file and Path(templates_file).exists():
            try:
                with open(templates_file, 'r') as f:
                    return yaml.load(f, Loader=yaml.SafeLoader)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load templates file '{templates_file}': {str(e)}")

        # Default fallback templates
        logger.info("ℹ️ Using built-in default templates.")
        return {
            "general_rag": """Based on the following context, please answer the question comprehensively and accurately.

Context Sources:
{context}

Question: {question}

Instructions:
- Use only the information provided in the context
- If the context doesn't contain sufficient information, state that clearly
- Cite relevant sources when possible
- Provide a detailed and well-structured answer""",

            "multimodal_rag": """I have gathered information from multiple sources including text documents, images, audio, and video. Please provide a comprehensive answer based on all available context.

Context Information:
{context}

Question: {question}

Instructions:
- Synthesize information from all modalities (text, image, audio, video)
- Clearly indicate which sources support your statements
- If certain modalities don't contain relevant information, mention that
- Provide a coherent and complete response""",

            "image_focused": """Based on the following visual content and related information, please answer the question.

Visual Content:
{context}

Question: {question}

Instructions:
- Focus on visual elements and image descriptions
- Relate visual content to the question
- If text sources are also available, integrate them with visual information
- Describe relevant visual details that support your answer""",

            "audio_focused": """Based on the following audio transcriptions and related content, please answer the question.

Audio Content:
{context}

Question: {question}

Instructions:
- Focus on spoken content and audio information
- Consider temporal aspects of audio content
- If multiple audio sources are available, synthesize them appropriately
- Mention any audio-specific insights (speaker identification, tone, etc.)""",

            "video_focused": """Based on the following video content (including both visual and audio elements), please answer the question.

Video Content:
{context}

Question: {question}

Instructions:
- Consider both visual scenes and audio transcription
- Pay attention to temporal sequence of events
- Integrate visual and audio information coherently
- Mention specific timestamps or scenes when relevant""",

            "comparison": """Compare and analyze the following sources to answer the question.

Sources to Compare:
{context}

Question: {question}

Instructions:
- Identify similarities and differences between sources
- Highlight conflicting information if present
- Provide a balanced analysis
- Draw conclusions based on the comparison""",

            "summary": """Provide a comprehensive summary based on the following sources.

Sources:
{context}

Summary Request: {question}

Instructions:
- Create a coherent summary that captures key information
- Organize information logically
- Maintain important details while being concise
- Include information from all relevant sources"""
        }

    def get_prompt(self, 
                   template_name: str,
                   question: str,
                   context: List[Dict[str, Any]],
                   **kwargs) -> str:
        """Generate a prompt using the specified template."""
        try:
            template = self.templates.get(template_name)
            if not template:
                logger.warning(f"⚠️ Template '{template_name}' not found. Using 'general_rag' as fallback.")
                template = self.templates["general_rag"]

            formatted_context = self._format_context(context, template_name)

            prompt = template.format(
                context=formatted_context,
                question=question,
                **kwargs
            )
            return prompt

        except Exception as e:
            logger.error(f"❌ Prompt generation failed for template '{template_name}': {str(e)}")
            raise

    def _format_context(self, context: List[Dict[str, Any]], template_name: str) -> str:
        """Format context depending on document type and template."""
        if not context:
            return "No context available."

        formatted_parts = []

        for i, item in enumerate(context, 1):
            content = item.get('content', '')
            metadata = item.get('metadata', {})
            source = item.get('source', 'Unknown')
            doc_type = metadata.get('doc_type', 'text')
            score = item.get('score', 0.0)

            if template_name == "multimodal_rag":
                header = f"[Source {i} - {doc_type.upper()}] (Relevance: {score:.2f})"
                formatted_parts.append(f"{header}\nSource: {source}\nContent: {content}")

            elif template_name == "image_focused" and doc_type == 'image':
                caption = metadata.get('caption', 'No caption available')
                header = f"[Image {i}] {source}"
                formatted_parts.append(f"{header}\nDescription: {caption}\nContent: {content}")

            elif template_name == "audio_focused" and doc_type == 'audio':
                duration = metadata.get('duration', 'Unknown')
                language = metadata.get('language', 'Unknown')
                header = f"[Audio {i}] {source} (Duration: {duration}s, Language: {language})"
                formatted_parts.append(f"{header}\nTranscription: {content}")

            elif template_name == "video_focused" and doc_type == 'video':
                duration = metadata.get('duration', 'Unknown')
                header = f"[Video {i}] {source} (Duration: {duration}s)"
                scenes = metadata.get('descriptions', [])
                audio_transcript = metadata.get('audio', {}).get('transcription', '')
                video_content = f"Visual scenes: {'; '.join(scenes)}\n"
                if audio_transcript:
                    video_content += f"Audio transcription: {audio_transcript}"
                formatted_parts.append(f"{header}\n{video_content}")

            else:
                header = f"[Source {i}] {source}"
                formatted_parts.append(f"{header}\n{content}")

        return "\n\n".join(formatted_parts)

    def get_system_prompt(self, template_name: str) -> str:
        """Return the system prompt associated with the template."""
        system_prompts = {
            "general_rag": "You are a helpful assistant that answers questions based on provided context. Always cite your sources and be precise.",
            "multimodal_rag": "You are an expert assistant capable of analyzing and synthesizing information from multiple modalities including text, images, audio, and video. Provide comprehensive answers that leverage all available information types.",
            "image_focused": "You are a visual content analyst. Focus on interpreting and describing visual information while connecting it to the user's question.",
            "audio_focused": "You are an audio content specialist. Analyze spoken content, considering temporal aspects and audio-specific features.",
            "video_focused": "You are a video content analyst capable of understanding both visual and audio elements of video content in their temporal context.",
            "comparison": "You are an analytical assistant specialized in comparing and contrasting information from multiple sources.",
            "summary": "You are a summarization expert capable of creating coherent, comprehensive summaries from diverse sources."
        }

        return system_prompts.get(template_name, system_prompts["general_rag"])
