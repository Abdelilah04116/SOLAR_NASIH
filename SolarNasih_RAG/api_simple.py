import logging
import sys
import os
import tempfile
import shutil
import uuid
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== MODÈLES PYDANTIC =====

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    method: str = Field("hybrid", description="Search method")
    top_k: int = Field(5, ge=1, le=50, description="Number of results")
    doc_type: Optional[str] = Field(None, description="Document type filter")
    generate_response: bool = Field(True, description="Generate AI response")

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

# ===== APPLICATION FASTAPI =====

app = FastAPI(
    title="RAG Multimodal System",
    description="A multimodal RAG system supporting text, image, audio, and video content",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== ROUTES =====

@app.get("/")
async def root():
    """Route racine"""
    return {
        "message": "RAG Multimodal System API",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health/"
    }

@app.get("/health/")
async def health_check():
    """Vérification de santé"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "RAG Multimodal System"
    }

@app.get("/health/detailed")
async def detailed_health_check():
    """Vérification de santé détaillée"""
    try:
        system_metrics = {
            "status": "operational",
            "features": {
                "upload": True,
                "search": True,
                "documentation": True
            },
            "endpoints": [
                "/", "/health/", "/upload/file", "/search/", "/docs"
            ]
        }
        
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "service": "RAG Multimodal System",
            "system_metrics": system_metrics
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Health check failed")

@app.post("/upload/file", response_model=UploadResponse)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload d'un fichier"""
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        upload_id = str(uuid.uuid4())
        
        # En mode démo, on simule juste l'upload
        logger.info(f"📤 File uploaded: {file.filename} (Demo mode)")
        
        # Sauvegarder le fichier si nécessaire
        upload_dir = Path("data/raw")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return UploadResponse(
            message="File uploaded successfully",
            upload_id=upload_id,
            files=[file.filename],
            status="completed"
        )
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/upload/files", response_model=UploadResponse)
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
    """Upload de plusieurs fichiers"""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        upload_id = str(uuid.uuid4())
        uploaded_files = []
        
        upload_dir = Path("data/raw")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        for file in files:
            if not file.filename:
                continue
                
            file_path = upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            uploaded_files.append(file.filename)
            logger.info(f"📤 File uploaded: {file.filename}")
        
        return UploadResponse(
            message=f"Successfully uploaded {len(uploaded_files)} files",
            upload_id=upload_id,
            files=uploaded_files,
            status="completed"
        )
        
    except Exception as e:
        logger.error(f"Multiple file upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.post("/search/", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """Recherche dans les documents"""
    try:
        # Mode démo - génère des résultats réalistes
        demo_results = []
        
        # Simuler différents types de résultats
        result_templates = [
            {
                "content": f"Document sur l'intelligence artificielle contenant des informations pertinentes pour '{request.query}'. Ce document couvre les aspects techniques et les applications pratiques.",
                "doc_type": "text",
                "source": "ai_guide.pdf"
            },
            {
                "content": f"Présentation PowerPoint avec des diagrammes expliquant '{request.query}'. Contient des schémas détaillés et des exemples concrets.",
                "doc_type": "image", 
                "source": "presentation.pptx"
            },
            {
                "content": f"Transcription d'une conférence audio sur le sujet '{request.query}'. L'expert explique les concepts clés avec des exemples pratiques.",
                "doc_type": "audio",
                "source": "conference.mp3"
            }
        ]
        
        for i in range(min(request.top_k, len(result_templates))):
            template = result_templates[i]
            demo_results.append(
                DocumentResult(
                    content=template["content"],
                    metadata={
                        "doc_type": template["doc_type"],
                        "source": template["source"],
                        "chunk_id": i,
                        "method": request.method,
                        "timestamp": time.time()
                    },
                    score=0.95 - (i * 0.1),
                    source=template["source"],
                    doc_type=template["doc_type"]
                )
            )
        
        response_data = SearchResponse(
            query=request.query,
            method=request.method,
            results=demo_results,
            total_results=len(demo_results)
        )
        
        # Générer une réponse IA simulée
        if request.generate_response and demo_results:
            response_data.generated_response = {
                "response": f"""Basé sur l'analyse de {len(demo_results)} documents pertinents, voici une réponse synthétique à votre question sur '{request.query}':

Les documents analysés montrent que ce sujet est bien documenté dans notre base de connaissances. Les informations trouvées couvrent les aspects théoriques et pratiques, avec des exemples concrets et des recommandations d'experts.

Points clés identifiés:
• Concepts fondamentaux clairement expliqués
• Applications pratiques avec exemples
• Recommandations d'experts du domaine
• Ressources complémentaires disponibles

Cette réponse est générée en mode démo. En production, elle serait créée par un LLM analysant le contenu réel des documents trouvés.""",
                "metadata": {
                    "sources_count": len(demo_results),
                    "method": request.method,
                    "confidence": 0.87,
                    "mode": "demo"
                }
            }
        
        logger.info(f"🔍 Search completed: '{request.query}' -> {len(demo_results)} results")
        return response_data
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/search/multimodal")
async def multimodal_search(
    text_query: Optional[str] = None,
    image_query: Optional[str] = None,
    top_k: int = 5
):
    """Recherche multimodale"""
    if not text_query and not image_query:
        raise HTTPException(status_code=400, detail="At least one query type required")
    
    query = text_query or image_query or "multimodal search"
    
    request = SearchRequest(
        query=f"Multimodal: {query}",
        method="multimodal",
        top_k=top_k,
        generate_response=True
    )
    
    return await search_documents(request)

@app.get("/search/similar")
async def search_similar(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, description="Number of results")
):
    """Recherche de similarité"""
    request = SearchRequest(
        query=query,
        method="vector",
        top_k=top_k,
        generate_response=False
    )
    return await search_documents(request)

@app.post("/index/file")
async def index_file_manually(filename: str):
    """Indexer manuellement un fichier déjà uploadé"""
    try:
        # Chercher le fichier dans le dossier data/raw
        file_path = Path("data/raw") / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail=f"File {filename} not found")
        
        # Simuler l'indexation (en mode démo)
        logger.info(f"Manually indexing file: {filename}")
        
        # En mode démo, on simule juste le traitement
        return {
            "message": f"File {filename} indexed successfully",
            "filename": filename,
            "status": "completed",
            "mode": "demo"
        }
        
    except Exception as e:
        logger.error(f"Manual indexing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

@app.get("/status")
async def get_system_status():
    """Statut détaillé du système"""
    return {
        "system": "RAG Multimodal",
        "version": "1.0.0",
        "status": "operational",
        "mode": "demo",
        "features": {
            "document_upload": True,
            "multimodal_search": True,
            "ai_responses": True,
            "api_documentation": True
        },
        "endpoints": {
            "root": "/",
            "health": "/health/",
            "upload_single": "/upload/file",
            "upload_multiple": "/upload/files",
            "search": "/search/",
            "search_multimodal": "/search/multimodal",
            "search_similar": "/search/similar",
            "status": "/status",
            "documentation": "/docs"
        },
        "statistics": {
            "uptime": "Running",
            "requests_served": "Available in production mode"
        }
    }

# ===== GESTION DES ERREURS =====

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "message": "Internal server error",
            "detail": str(exc),
            "suggestion": "Check logs for more details"
        }
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

# ===== ÉVÉNEMENTS =====

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 RAG Multimodal System API started")
    
    # Créer les répertoires nécessaires
    directories = ["data/raw", "data/processed", "logs"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    logger.info("✅ System ready!")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 RAG Multimodal System shutdown")

# ===== POINT D'ENTRÉE =====

if __name__ == "__main__":
    print("🚀 RAG Multimodal API")
    print("📍 URL: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("💡 Mode: Démo fonctionnel")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )