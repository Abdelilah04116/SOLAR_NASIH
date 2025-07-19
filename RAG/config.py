"""
Configuration pour la pipeline RAG multimodal
"""
import os
from dataclasses import dataclass
from typing import List, Dict, Any
from pathlib import Path

@dataclass
class ChunkingConfig:
    """Configuration pour le chunking"""
    text_chunk_size: int = 1000
    text_chunk_overlap: int = 200
    table_chunk_size: int = 5000
    image_chunk_size: int = 2000
    
    # Paramètres de découpage de texte
    prefer_sentence_boundaries: bool = True
    min_chunk_size: int = 100

@dataclass
class EmbeddingConfig:
    """Configuration pour les embeddings"""
    text_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    image_model_name: str = "openai/clip-vit-base-patch32"
    
    # Paramètres d'embedding
    normalize_embeddings: bool = True
    batch_size: int = 32
    device: str = "auto"  # auto, cpu, cuda

@dataclass
class VectorStoreConfig:
    """Configuration pour le stockage vectoriel"""
    store_type: str = "chroma"  # chroma, faiss
    store_path: str = "./vector_store"
    collection_name: str = "multimodal_rag"
    
    # Paramètres spécifiques à ChromaDB
    chromadb_host: str = "localhost"
    chromadb_port: int = 8000
    
    # Paramètres spécifiques à FAISS (peuvent rester pour compatibilité)
    faiss_index_type: str = "flat"  # flat, ivf, hnsw
    faiss_metric: str = "L2"  # L2, IP

@dataclass
class ParsingConfig:
    """Configuration pour le parsing"""
    supported_formats: List[str] = None
    
    # Paramètres PDF
    extract_images: bool = True
    extract_tables: bool = True
    extract_text: bool = True
    
    # Qualité d'image
    image_dpi: int = 150
    image_format: str = "PNG"
    
    # Paramètres de tableau
    table_detection_threshold: float = 0.8
    
    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = [".pdf"]

@dataclass
class QuestionGenerationConfig:
    """Configuration pour la génération de questions"""
    max_questions_per_chunk: int = 3
    min_question_length: int = 10
    max_question_length: int = 200
    
    # Modèle pour la génération de questions
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Templates de questions
    use_default_templates: bool = True
    custom_templates: Dict[str, List[str]] = None

@dataclass
class RAGPipelineConfig:
    """Configuration principale de la pipeline"""
    chunking: ChunkingConfig = None
    embedding: EmbeddingConfig = None
    vector_store: VectorStoreConfig = None
    parsing: ParsingConfig = None
    question_generation: QuestionGenerationConfig = None
    
    # Paramètres généraux
    log_level: str = "INFO"
    max_workers: int = 4
    cache_embeddings: bool = True
    
    # Répertoires
    temp_dir: str = "./temp"
    logs_dir: str = "./logs"
    
    def __post_init__(self):
        if self.chunking is None:
            self.chunking = ChunkingConfig()
        if self.embedding is None:
            self.embedding = EmbeddingConfig()
        if self.vector_store is None:
            self.vector_store = VectorStoreConfig()
        if self.parsing is None:
            self.parsing = ParsingConfig()
        if self.question_generation is None:
            self.question_generation = QuestionGenerationConfig()
        
        # Créer les répertoires si nécessaire
        Path(self.temp_dir).mkdir(exist_ok=True)
        Path(self.logs_dir).mkdir(exist_ok=True)
        Path(self.vector_store.store_path).mkdir(exist_ok=True)

# Configuration par défaut
DEFAULT_CONFIG = RAGPipelineConfig()

def load_config_from_env() -> RAGPipelineConfig:
    """Charge la configuration depuis les variables d'environnement"""
    config = RAGPipelineConfig()
    
    # Chunking
    config.chunking.text_chunk_size = int(os.getenv("TEXT_CHUNK_SIZE", 1000))
    config.chunking.text_chunk_overlap = int(os.getenv("TEXT_CHUNK_OVERLAP", 200))
    
    # Embedding
    config.embedding.text_model_name = os.getenv("TEXT_MODEL_NAME", 
                                                 "sentence-transformers/all-MiniLM-L6-v2")
    config.embedding.image_model_name = os.getenv("IMAGE_MODEL_NAME", 
                                                  "openai/clip-vit-base-patch32")
    
    # Vector store
    config.vector_store.store_type = os.getenv("VECTOR_STORE_TYPE", "chroma")
    config.vector_store.store_path = os.getenv("VECTOR_STORE_PATH", "./vector_store")
    config.vector_store.chromadb_host = os.getenv("CHROMADB_HOST", "localhost")
    config.vector_store.chromadb_port = int(os.getenv("CHROMADB_PORT", 8000))
    
    # Logging
    config.log_level = os.getenv("LOG_LEVEL", "INFO")
    
    return config

def save_config_to_file(config: RAGPipelineConfig, file_path: str):
    """Sauvegarde la configuration dans un fichier JSON"""
    import json
    from dataclasses import asdict
    
    config_dict = asdict(config)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)

def load_config_from_file(file_path: str) -> RAGPipelineConfig:
    """Charge la configuration depuis un fichier JSON"""
    import json
    
    with open(file_path, 'r', encoding='utf-8') as f:
        config_dict = json.load(f)
    
    # Reconstruction des objets de configuration
    config = RAGPipelineConfig(
        chunking=ChunkingConfig(**config_dict.get('chunking', {})),
        embedding=EmbeddingConfig(**config_dict.get('embedding', {})),
        vector_store=VectorStoreConfig(**config_dict.get('vector_store', {})),
        parsing=ParsingConfig(**config_dict.get('parsing', {})),
        question_generation=QuestionGenerationConfig(**config_dict.get('question_generation', {}))
    )
    
    # Paramètres généraux
    config.log_level = config_dict.get('log_level', 'INFO')
    config.max_workers = config_dict.get('max_workers', 4)
    config.cache_embeddings = config_dict.get('cache_embeddings', True)
    config.temp_dir = config_dict.get('temp_dir', './temp')
    config.logs_dir = config_dict.get('logs_dir', './logs')
    
    return config