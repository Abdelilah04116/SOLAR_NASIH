from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import logging
import traceback
from pathlib import Path
import uvicorn
import json
import os
from datetime import datetime

# Imports locaux
from models.schemas import *
from graph.workflow import SolarNasihWorkflow
from services.rag_service import RAGService
from services.voice_service import VoiceService
from utils.validators import validate_api_keys, sanitize_user_input
from config.settings import settings
from agents.multilingual_detector import MultilingualDetectorAgent
from httpx import AsyncClient

# Création des dossiers nécessaires AVANT la configuration du logging
os.makedirs('logs', exist_ok=True)
os.makedirs('static/audio', exist_ok=True)
os.makedirs('static/documents', exist_ok=True)

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/solar_nasih.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialisation de l'application
app = FastAPI(
    title="Solar Nasih - Système Multi-Agent",
    description="Système multi-agent intelligent pour conseil en énergie solaire",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir les fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

# Variables globales pour les services
workflow = None
rag_service = None
voice_service = None

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage de l'application"""
    global workflow, rag_service, voice_service
    
    try:
        logger.info("Demarrage Solar Nasih SMA...")
        
        # Vérification des clés API
        api_status = validate_api_keys()
        if not all(api_status.values()):
            logger.warning("⚠️ Certaines clés API manquent ou sont invalides")
            logger.warning(f"Statut APIs: {api_status}")
        
        # Initialisation des services
        logger.info("Initialisation des services...")
        workflow = SolarNasihWorkflow()
        rag_service = RAGService()
        voice_service = VoiceService()
        
        # Test de santé des services
        rag_health = await rag_service.health_check()
        logger.info(f"📊 Statut RAG: {rag_health['status']}")
        
        # Vérification du workflow
        workflow_status = workflow.get_workflow_status()
        logger.info(f"🤖 Agents chargés: {workflow_status['agents_loaded']}")
        
        logger.info("✅ Solar Nasih SMA démarré avec succès!")
        
    except Exception as e:
        logger.error(f"Erreur lors du démarrage: {e}")
        logger.error(traceback.format_exc())
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Nettoyage à l'arrêt de l'application"""
    logger.info("🛑 Arrêt Solar Nasih SMA...")

# Middleware pour logging des requêtes
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = datetime.now()
    
    # Log de la requête
    logger.info(f"📨 {request.method} {request.url.path} - IP: {request.client.host}")
    
    response = await call_next(request)
    
    # Log de la réponse
    process_time = (datetime.now() - start_time).total_seconds()
    logger.info(f"📤 {response.status_code} - Temps: {process_time:.3f}s")
    
    return response

# Dépendance pour vérifier l'initialisation des services
async def get_workflow():
    if workflow is None:
        raise HTTPException(status_code=503, detail="Service non initialisé")
    return workflow

async def get_rag_service():
    if rag_service is None:
        raise HTTPException(status_code=503, detail="Service RAG non initialisé")
    return rag_service

async def get_voice_service():
    if voice_service is None:
        raise HTTPException(status_code=503, detail="Service vocal non initialisé")
    return voice_service

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    workflow_service: SolarNasihWorkflow = Depends(get_workflow)
):
    """
    Point d'entrée principal pour les conversations
    """
    try:
        # Sanitisation de l'entrée utilisateur
        sanitized_message = sanitize_user_input(request.message)
        if not sanitized_message.strip():
            raise HTTPException(status_code=400, detail="Message vide ou invalide")
        logger.info(f"💬 Chat: {sanitized_message[:100]}...")
        
        # Utilisation directe du TaskDividerAgent au lieu du workflow complexe
        try:
            from agents.task_divider import TaskDividerAgent
            from models.schemas import AgentState
            
            # Création de l'état pour l'agent
            agent_state = AgentState(
                current_message=sanitized_message,
                detected_language="fr",
                user_intent="",
                agent_route=AgentType.TASK_DIVIDER,
                context=request.context or {},
                response="",
                confidence=0.0,
                sources=[],
                processing_history=[]
            )
            
            # Récupération du mapping des agents depuis le workflow
            agents_map = workflow_service.agents
            
            # Appel direct du TaskDividerAgent
            task_divider = TaskDividerAgent()
            result = await task_divider.process(agent_state, agents_map)
            
            # Extraction de la réponse
            response_text = result.get("response", "")
            agent_used = result.get("agent_used", "task_divider")
            confidence = result.get("confidence", 0.7)
            sources = result.get("sources", [])
            agent_responses = result.get("agent_responses", [])
            
            logger.info(f"🤖 Agent principal utilisé: {agent_used} - Confiance: {confidence}")
            logger.info(f"📝 Réponse générée: {response_text[:100]}...")
            
            # Création de la réponse structurée
            response_dict = {
                "message": response_text,
                "agent_used": agent_used,
                "confidence": confidence,
                "sources": sources
            }
            
            # Ajout de la propriété agent_responses si disponible
            if agent_responses:
                response_dict["agent_responses"] = agent_responses
            
            return response_dict
            
        except Exception as agent_error:
            logger.error(f"Erreur avec TaskDividerAgent: {agent_error}")
            # Fallback vers le workflow original
            result = await workflow_service.run(sanitized_message, request.context)
            
            # Extraction de la réponse avec gestion d'erreur
            response_text = ""
            if isinstance(result, dict):
                response_text = result.get("response") or result.get("message") or ""
                if not response_text and "error" in result:
                    response_text = f"Erreur: {result['error']}"
                if not response_text:
                    response_text = "Je n'ai pas pu traiter votre demande. Pouvez-vous reformuler votre question ?"
            else:
                response_text = str(result) if result else "Aucune réponse générée"
            
            # Création de la réponse structurée
            response = ChatResponse(
                message=response_text,
                agent_used=result.get("agent_used", "task_divider") if isinstance(result, dict) else "task_divider",
                confidence=result.get("confidence", 0.8) if isinstance(result, dict) else 0.5,
                sources=result.get("sources", []) if isinstance(result, dict) else []
            )
            
            logger.info(f"🤖 Agent utilisé (fallback): {response.agent_used} - Confiance: {response.confidence}")
            logger.info(f"📝 Réponse générée (fallback): {response_text[:100]}...")
            
            # Ajout de la propriété agent_responses si disponible
            response_dict = response.dict()
            if isinstance(result, dict) and "agent_responses" in result:
                response_dict["agent_responses"] = result["agent_responses"]
            
            return response_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur chat: {e}")
        logger.error(traceback.format_exc())
        
        # Retourne toujours une réponse structurée même en cas d'erreur
        return {
            "message": f"Erreur lors du traitement: {str(e)}",
            "agent_used": "task_divider",
            "confidence": 0.0,
            "sources": []
        }

@app.post("/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    rag_service_dep: RAGService = Depends(get_rag_service)
):
    """
    Upload et indexation de documents (Active l'endpoint RAG existant)
    """
    try:
        logger.info(f"📄 Upload document: {file.filename}")
        logger.info(f"📋 Content-Type: {file.content_type}")
        
        # Validation du fichier
        from utils.validators import validate_file_upload
        # Lire le contenu pour obtenir la taille réelle
        content = await file.read()
        file_size = len(content)
        # Remettre le curseur au début pour que le service RAG puisse lire le fichier
        await file.seek(0)
        
        logger.info(f"📏 Taille fichier: {file_size} bytes")
        validation = validate_file_upload(file.filename, file.content_type, file_size)
        
        if not validation['valid']:
            logger.error(f"❌ Validation échouée pour {file.filename}: {validation['errors']}")
            raise HTTPException(status_code=400, detail=f"Fichier invalide: {validation['errors']}")
        
        logger.info(f"✅ Validation réussie pour {file.filename} (taille: {file_size} bytes)")
        
        # Appel au service RAG existant
        result = await rag_service_dep.index_document(file)
        
        logger.info(f"✅ Document indexé: {result}")
        
        return {
            "message": "Document indexé avec succès",
            "document_id": result,
            "filename": file.filename,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-chat")
async def voice_chat(
    audio_file: UploadFile = File(...),
    workflow_service: SolarNasihWorkflow = Depends(get_workflow),
    voice_service_dep: VoiceService = Depends(get_voice_service)
):
    """
    Traitement des requêtes vocales
    """
    try:
        logger.info(f"🎤 Traitement vocal: {audio_file.filename}")
        
        # Validation du fichier audio
        validation = voice_service_dep.validate_audio_file(audio_file)
        if not validation['valid']:
            raise HTTPException(status_code=400, detail=f"Fichier audio invalide: {validation['errors']}")
        
        # Traitement vocal via l'agent spécialisé
        result = await workflow_service.run_voice_processing(audio_file)
        
        logger.info("✅ Traitement vocal terminé")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur vocal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/simulate-energy")
async def simulate_energy(
    request: EnergySimulationRequest,
    workflow_service: SolarNasihWorkflow = Depends(get_workflow)
):
    """
    Simulation énergétique
    """
    try:
        logger.info(f"⚡ Simulation énergétique: {request.surface_toit}m² - {request.localisation}")
        
        result = await workflow_service.run_energy_simulation(request.dict())
        
        logger.info("✅ Simulation terminée")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur simulation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-document")
async def generate_document(
    request: DocumentGenerationRequest,
    background_tasks: BackgroundTasks,
    workflow_service: SolarNasihWorkflow = Depends(get_workflow)
):
    """
    Génération de documents
    """
    try:
        logger.info(f"📋 Génération document: {request.document_type}")
        
        result = await workflow_service.run_document_generation(request.dict())
        
        # Ajout d'une tâche de nettoyage en arrière-plan si nécessaire
        if result.get('document_url'):
            background_tasks.add_task(cleanup_temp_files, result['document_url'])
        
        logger.info("✅ Document généré")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur génération: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """
    Vérification de l'état du système
    """
    try:
        health_status = {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "services": {}
        }
        
        # Vérification des services
        if workflow:
            workflow_status = workflow.get_workflow_status()
            health_status["services"]["workflow"] = {
                "status": "running",
                "agents_loaded": workflow_status.get("agents_loaded", 0)
            }
        
        if rag_service:
            rag_health = await rag_service.health_check()
            health_status["services"]["rag"] = rag_health
        
        # Vérification des APIs externes
        api_status = validate_api_keys()
        health_status["services"]["apis"] = api_status
        
        return health_status
        
    except Exception as e:
        logger.error(f"❌ Erreur health check: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/agents")
async def list_agents(workflow_service: SolarNasihWorkflow = Depends(get_workflow)):
    """
    Liste des agents disponibles
    """
    try:
        status = workflow_service.get_workflow_status()
        return {
            "agents": status.get("available_agents", []),
            "total": status.get("agents_loaded", 0),
            "workflow_compiled": status.get("workflow_compiled", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents(rag_service_dep: RAGService = Depends(get_rag_service)):
    """
    Liste des documents indexés
    """
    try:
        documents = await rag_service_dep.list_documents()
        return {"documents": documents, "total": len(documents)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    rag_service_dep: RAGService = Depends(get_rag_service)
):
    """
    Suppression d'un document
    """
    try:
        success = await rag_service_dep.delete_document(document_id)
        if success:
            return {"message": "Document supprimé avec succès"}
        else:
            raise HTTPException(status_code=404, detail="Document non trouvé")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """
    Page d'accueil avec informations système
    """
    return {
        "name": "Solar Nasih - Système Multi-Agent",
        "version": "1.0.0",
        "description": "Système multi-agent intelligent pour conseil en énergie solaire",
        "endpoints": {
            "chat": "/chat",
            "voice": "/voice-chat", 
            "simulation": "/simulate-energy",
            "documents": "/generate-document",
            "upload": "/upload-document",
            "health": "/health",
            "docs": "/docs"
        },
        "status": "operational"
    }

# Gestionnaire d'exceptions global
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"❌ Exception non gérée: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erreur interne du serveur",
            "detail": str(exc) if settings.DEBUG else "Une erreur inattendue s'est produite",
            "timestamp": datetime.now().isoformat()
        }
    )

# Fonction utilitaire pour nettoyage
async def cleanup_temp_files(file_path: str):
    """Nettoie les fichiers temporaires après un délai"""
    import asyncio
    await asyncio.sleep(3600)  # Attendre 1 heure
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"🗑️ Fichier temporaire supprimé: {file_path}")
    except Exception as e:
        logger.warning(f"⚠️ Impossible de supprimer {file_path}: {e}")

async def query_rag_service(query: str, method: str = "hybrid", top_k: int = 5):
    """Appelle l'API RAG pour une requête de recherche."""
    async with AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/search/",
            json={"query": query, "method": method, "top_k": top_k}
        )
        response.raise_for_status()
        return response.json()

@app.post("/query")
async def query_endpoint(request: ChatRequest):
    """Orchestre la requête SMA -> RAG et retourne la réponse à l'utilisateur."""
    rag_response = await query_rag_service(request.message)
    # Ici, tu peux enrichir la réponse ou la traiter via des agents SMA si besoin
    return rag_response

if __name__ == "__main__":
    # Configuration selon l'environnement
    debug_mode = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=debug_mode,
        log_level="info" if not debug_mode else "debug"
    )