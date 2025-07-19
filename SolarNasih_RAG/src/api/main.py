# ===== src/api/main.py (VERSION COMPLÈTE) =====
import logging
import sys
import os
import tempfile
import shutil
import uuid
import time
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

# Configuration du chemin Python
root_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(root_path))

# Imports FastAPI
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn

# Imports pour le système
try:
    # Configuration
    from config.settings import settings
    
    # Composants d'ingestion
    from src.ingestion.preprocessor import Preprocessor
    
    # Composants de vectorisation
    from src.vectorization.indexer import Indexer
    from src.vectorization.vector_store import VectorStore
    from src.vectorization.embeddings.multimodal_embeddings import MultimodalEmbeddings
    
    # Composants de recherche
    from src.retrieval.retrievers.vector_retriever import VectorRetriever
    from src.retrieval.retrievers.keyword_retriever import KeywordRetriever
    from src.retrieval.search_engine import SearchEngine
    
    # Composants de génération
    from src.generation.response_generator import ResponseGenerator
    
    FULL_SYSTEM_AVAILABLE = True
    
except ImportError as e:
    import traceback
    print(f"⚠️ Import warning: {e}")
    print("🔍 Stack trace complète:")
    traceback.print_exc()
    print("🔄 Falling back to basic mode...")
    FULL_SYSTEM_AVAILABLE = False

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ===== MODÈLES PYDANTIC =====

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    method: str = Field("hybrid", description="Search method: vector, keyword, or hybrid")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")
    doc_type: Optional[str] = Field(None, description="Filter by document type")
    use_reranking: bool = Field(True, description="Whether to use reranking")
    score_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum relevance score")
    generate_response: bool = Field(True, description="Whether to generate a response")

class MultimodalSearchRequest(BaseModel):
    text_query: Optional[str] = Field(None, description="Text search query")
    image_query: Optional[str] = Field(None, description="Image search query")
    top_k: int = Field(5, ge=1, le=50, description="Number of results to return")
    use_reranking: bool = Field(True, description="Whether to use reranking")
    generate_response: bool = Field(True, description="Whether to generate a response")

class DocumentResult(BaseModel):
    content: str
    metadata: Dict[str, Any]
    score: float
    source: str
    doc_type: str

class SearchResponse(BaseModel):
    query: str
    method: str
    results: List[DocumentResult]
    total_results: int
    generated_response: Optional[Dict[str, Any]] = None

class UploadResponse(BaseModel):
    message: str
    upload_id: str
    files: List[str]
    status: str

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    service: str
    system_metrics: Optional[Dict[str, Any]] = None

# ===== APPLICATION FASTAPI =====

app = FastAPI(
    title="RAG Multimodal System",
    description="A comprehensive multimodal RAG system supporting text, image, audio, and video content",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifiez les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== INITIALISATION DES COMPOSANTS =====

# Variables globales pour les composants
preprocessor = None
indexer = None
search_engine = None
response_generator = None

def initialize_components():
    """Initialise les composants du système si disponibles"""
    global preprocessor, indexer, search_engine, response_generator
    
    if not FULL_SYSTEM_AVAILABLE:
        logger.warning("Full system not available, running in basic mode")
        return
    
    try:
        # Initialiser les composants
        preprocessor = Preprocessor()
        indexer = Indexer()
        
        # Composants de recherche
        vector_store = VectorStore(settings.qdrant_url, settings.qdrant_api_key)
        embeddings = MultimodalEmbeddings()
        vector_retriever = VectorRetriever(vector_store, embeddings)
        keyword_retriever = KeywordRetriever()
        search_engine = SearchEngine(vector_retriever, keyword_retriever)
        
        # Générateur de réponses
        response_generator = ResponseGenerator()
        
        logger.info("✅ All components initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Component initialization failed: {str(e)}")
        # Continuer en mode dégradé

# ===== ROUTES DE SANTÉ =====

@app.get("/", response_model=Dict[str, str])
async def root():
    """Route racine"""
    return {
        "message": "RAG Multimodal System API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health/", response_model=HealthResponse)
async def health_check():
    """Vérification de santé basique"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        service="RAG Multimodal System"
    )

@app.get("/health/detailed", response_model=HealthResponse)
async def detailed_health_check():
    """Vérification de santé détaillée avec métriques système"""
    try:
        import psutil
        
        # Métriques système
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('.')
        
        system_metrics = {
            "cpu_percent": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "components": {
                "full_system": FULL_SYSTEM_AVAILABLE,
                "preprocessor": preprocessor is not None,
                "search_engine": search_engine is not None,
                "response_generator": response_generator is not None
            }
        }
        
        return HealthResponse(
            status="healthy",
            timestamp=time.time(),
            service="RAG Multimodal System",
            system_metrics=system_metrics
        )
        
    except ImportError:
        # psutil non disponible
        return HealthResponse(
            status="healthy",
            timestamp=time.time(),
            service="RAG Multimodal System",
            system_metrics={
                "components": {
                    "full_system": FULL_SYSTEM_AVAILABLE,
                    "preprocessor": preprocessor is not None,
                    "search_engine": search_engine is not None,
                    "response_generator": response_generator is not None
                }
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

# ===== ROUTES D'UPLOAD =====

async def process_and_index_file(file_path: Path, filename: str, upload_id: str):
    """Tâche en arrière-plan pour traiter et indexer un fichier"""
    try:
        if not FULL_SYSTEM_AVAILABLE or not preprocessor or not indexer:
            logger.warning(f"System not fully available, skipping processing of {filename}")
            return
        
        logger.info(f"Processing file: {filename} (Upload ID: {upload_id})")
        
        # Traiter le document
        chunks = preprocessor.process_document(file_path)
        
        # Indexer les chunks
        success = indexer.index_chunks(chunks)
        
        if success:
            logger.info(f"Successfully indexed {len(chunks)} chunks from {filename}")
        else:
            logger.error(f"Failed to index file: {filename}")
        
    except Exception as e:
        logger.error(f"Background processing failed for {filename}: {str(e)}")
    finally:
        # Nettoyer le fichier temporaire
        if file_path.exists():
            file_path.unlink()

@app.post("/upload/file", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload et traitement d'un fichier unique"""
    try:
        # Validation
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Créer un fichier temporaire
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = Path(tmp_file.name)
        
        # Générer un ID unique
        upload_id = str(uuid.uuid4())
        
        # Traiter en arrière-plan
        background_tasks.add_task(
            process_and_index_file,
            tmp_path,
            file.filename,
            upload_id
        )
        
        return UploadResponse(
            message="File uploaded successfully",
            upload_id=upload_id,
            files=[file.filename],
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/upload/files", response_model=UploadResponse)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Upload et traitement de plusieurs fichiers"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        upload_id = str(uuid.uuid4())
        uploaded_files = []
        
        for file in files:
            if not file.filename:
                continue
                
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = Path(tmp_file.name)
            
            # Traiter en arrière-plan
            background_tasks.add_task(
                process_and_index_file,
                tmp_path,
                file.filename,
                upload_id
            )
            
            uploaded_files.append(file.filename)
        
        return UploadResponse(
            message=f"Successfully uploaded {len(uploaded_files)} files",
            upload_id=upload_id,
            files=uploaded_files,
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"Multiple file upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ===== ROUTES DE RECHERCHE =====

@app.post("/search/", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Recherche générale dans les documents"""
    try:
        if not FULL_SYSTEM_AVAILABLE or not search_engine:
            # Mode démo sans recherche réelle
            demo_results = [
                DocumentResult(
                    content=f"Résultat démo pour la requête: {request.query}",
                    metadata={
                        "doc_type": "text",
                        "source": "demo.txt",
                        "chunk_id": 0
                    },
                    score=0.95,
                    source="demo.txt",
                    doc_type="text"
                )
            ]
            
            return SearchResponse(
                query=request.query,
                method=request.method,
                results=demo_results,
                total_results=len(demo_results),
                generated_response={
                    "response": f"Réponse démo basée sur la requête: {request.query}",
                    "metadata": {"mode": "demo"}
                } if request.generate_response else None
            )
        
        # Effectuer la recherche
        results = search_engine.search(
            query=request.query,
            method=request.method,
            top_k=request.top_k,
            doc_type=request.doc_type,
            use_reranking=request.use_reranking,
            score_threshold=request.score_threshold
        )
        
        # Convertir en format de réponse
        formatted_results = [
            DocumentResult(
                content=result["content"],
                metadata=result["metadata"],
                score=result["score"],
                source=result["source"],
                doc_type=result["metadata"].get("doc_type", "unknown")
            )
            for result in results
        ]
        
        response_data = SearchResponse(
            query=request.query,
            method=request.method,
            results=formatted_results,
            total_results=len(formatted_results)
        )
        
        # Générer une réponse si demandé
        if request.generate_response and results and response_generator:
            try:
                generated_response = response_generator.generate_response(
                    query=request.query,
                    retrieved_docs=results
                )
                response_data.generated_response = generated_response
            except Exception as e:
                logger.warning(f"Response generation failed: {str(e)}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search/multimodal", response_model=SearchResponse)
async def multimodal_search(request: MultimodalSearchRequest):
    """Recherche multimodale"""
    try:
        if not request.text_query and not request.image_query:
            raise HTTPException(
                status_code=400, 
                detail="At least one query type must be provided"
            )
        
        if not FULL_SYSTEM_AVAILABLE or not search_engine:
            # Mode démo
            demo_results = [
                DocumentResult(
                    content=f"Résultat multimodal démo: {request.text_query or request.image_query}",
                    metadata={
                        "doc_type": "multimodal",
                        "source": "demo_multimodal.txt"
                    },
                    score=0.92,
                    source="demo_multimodal.txt",
                    doc_type="multimodal"
                )
            ]
            
            return SearchResponse(
                query=request.text_query or request.image_query or "multimodal query",
                method="multimodal",
                results=demo_results,
                total_results=len(demo_results)
            )
        
        # Recherche multimodale réelle
        results = search_engine.multimodal_search(
            text_query=request.text_query,
            image_query=request.image_query,
            top_k=request.top_k,
            use_reranking=request.use_reranking
        )
        
        formatted_results = [
            DocumentResult(
                content=result["content"],
                metadata=result["metadata"],
                score=result["score"],
                source=result["source"],
                doc_type=result["metadata"].get("doc_type", "unknown")
            )
            for result in results
        ]
        
        response_data = SearchResponse(
            query=request.text_query or request.image_query or "multimodal query",
            method="multimodal",
            results=formatted_results,
            total_results=len(formatted_results)
        )
        
        # Générer une réponse
        if request.generate_response and results and response_generator:
            try:
                generated_response = response_generator.generate_response(
                    query=request.text_query or request.image_query or "Multimodal query",
                    retrieved_docs=results,
                    template_type="multimodal_rag"
                )
                response_data.generated_response = generated_response
            except Exception as e:
                logger.warning(f"Response generation failed: {str(e)}")
        
        return response_data
        
    except Exception as e:
        logger.error(f"Multimodal search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Multimodal search failed: {str(e)}")

@app.get("/search/similar")
async def search_similar(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, description="Number of results"),
    doc_type: Optional[str] = Query(None, description="Document type filter")
):
    """Recherche de similarité simple"""
    try:
        search_request = SearchRequest(
            query=query,
            method="vector",
            top_k=top_k,
            doc_type=doc_type,
            generate_response=False
        )
        
        return await search_documents(search_request)
        
    except Exception as e:
        logger.error(f"Similarity search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Similarity search failed: {str(e)}")

# ===== ROUTES UTILITAIRES =====

@app.get("/status")
async def get_system_status():
    """Statut détaillé du système"""
    return {
        "system": "RAG Multimodal",
        "version": "1.0.0",
        "status": "operational",
        "full_system_available": FULL_SYSTEM_AVAILABLE,
        "components": {
            "preprocessor": preprocessor is not None,
            "indexer": indexer is not None,
            "search_engine": search_engine is not None,
            "response_generator": response_generator is not None
        },
        "endpoints": {
            "health": "/health/",
            "upload": "/upload/file",
            "search": "/search/",
            "docs": "/docs"
        }
    }

@app.get("/docs-info")
async def get_docs_info():
    """Informations sur la documentation"""
    return {
        "documentation_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json"
    }

@app.post("/index/file")
async def index_file_manually(filename: str):
    """Indexer manuellement un fichier déjà uploadé"""
    try:
        # Chercher le fichier dans le dossier data/raw
        file_path = Path("data/raw") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        # En mode basic, on simule l'indexation
        if not FULL_SYSTEM_AVAILABLE or not preprocessor or not indexer:
            logger.warning(f"System not fully available, simulating indexing of {filename}")
            return {
                "message": f"File {filename} indexed successfully (demo mode)",
                "filename": filename,
                "status": "completed",
                "mode": "demo"
            }
        
        # Traitement réel si le système est disponible
        logger.info(f"Manually indexing file: {filename}")
        
        # Traiter le document
        chunks = preprocessor.process_document(file_path)
        
        # Indexer les chunks
        success = indexer.index_chunks(chunks)
        
        if success:
            return {
                "message": f"File {filename} indexed successfully",
                "filename": filename,
                "status": "completed",
                "chunks_indexed": len(chunks)
            }
        else:
            raise HTTPException(status_code=500, detail="Indexing failed")
        
    except Exception as e:
        logger.error(f"Manual indexing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

# ===== GESTION DES ERREURS =====

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Gestionnaire global d'exceptions"""
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Gestionnaire d'exceptions HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

# ===== ÉVÉNEMENTS DE L'APPLICATION =====

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    logger.info("🚀 Starting RAG Multimodal System")
    
    # Créer les répertoires nécessaires
    directories = [
        "data/raw", "data/processed", "data/cache",
        "models/embeddings", "models/llm", "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Initialiser les composants
    initialize_components()
    
    logger.info("✅ RAG Multimodal System started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt"""
    logger.info("🛑 Shutting down RAG Multimodal System")

# ===== POINT D'ENTRÉE =====

if __name__ == "__main__":
    # Configuration par défaut si settings n'est pas disponible
    host = "0.0.0.0"
    port = 8000
    debug = True
    
    try:
        if FULL_SYSTEM_AVAILABLE:
            host = settings.api_host
            port = settings.api_port
            debug = settings.debug
    except:
        pass
    
    print(f"🚀 Launching RAG Multimodal API on http://{host}:{port}")
    print(f"📚 Documentation available at http://{host}:{port}/docs")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )