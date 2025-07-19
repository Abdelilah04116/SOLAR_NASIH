import logging
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from src.retrieval.search_engine import SearchEngine
from src.retrieval.retrievers.vector_retriever import VectorRetriever
from src.retrieval.retrievers.keyword_retriever import KeywordRetriever
from src.vectorization.vector_store import VectorStore
from src.vectorization.embeddings.multimodal_embeddings import MultimodalEmbeddings
from src.generation.response_generator import ResponseGenerator
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize components
vector_store = VectorStore(settings.qdrant_url, settings.qdrant_api_key)
embeddings = MultimodalEmbeddings()
vector_retriever = VectorRetriever(vector_store, embeddings)
keyword_retriever = KeywordRetriever()
search_engine = SearchEngine(vector_retriever, keyword_retriever)
response_generator = ResponseGenerator()

class SearchRequest(BaseModel):
    query: str
    method: str = "hybrid"  # vector, keyword, hybrid
    top_k: int = 5
    doc_type: Optional[str] = None
    use_reranking: bool = True
    score_threshold: Optional[float] = None
    generate_response: bool = True

class MultimodalSearchRequest(BaseModel):
    text_query: Optional[str] = None
    image_query: Optional[str] = None
    top_k: int = 5
    use_reranking: bool = True
    generate_response: bool = True

@router.post("/")
async def search(request: SearchRequest) -> Dict[str, Any]:
    """General search endpoint."""
    try:
        # Perform search
        results = search_engine.search(
            query=request.query,
            method=request.method,
            top_k=request.top_k,
            doc_type=request.doc_type,
            use_reranking=request.use_reranking,
            score_threshold=request.score_threshold
        )
        
        response_data = {
            "query": request.query,
            "method": request.method,
            "results": results,
            "total_results": len(results)
        }
        
        # Generate response if requested
        if request.generate_response and results:
            try:
                generated_response = response_generator.generate_response(
                    query=request.query,
                    retrieved_docs=results
                )
                response_data["generated_response"] = generated_response
            except Exception as e:
                logger.warning(f"Response generation failed: {str(e)}")
                response_data["generation_error"] = str(e)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.post("/multimodal")
async def multimodal_search(request: MultimodalSearchRequest) -> Dict[str, Any]:
    """Multimodal search endpoint."""
    try:
        if not request.text_query and not request.image_query:
            raise HTTPException(status_code=400, detail="At least one query type must be provided")
        
        # Perform multimodal search
        results = search_engine.multimodal_search(
            text_query=request.text_query,
            image_query=request.image_query,
            top_k=request.top_k,
            use_reranking=request.use_reranking
        )
        
        response_data = {
            "text_query": request.text_query,
            "image_query": request.image_query,
            "results": results,
            "total_results": len(results)
        }
        
        # Generate response if requested
        if request.generate_response and results:
            try:
                generated_response = response_generator.generate_response(
                    query=request.text_query or request.image_query or "Multimodal query",
                    retrieved_docs=results,
                    template_type="multimodal_rag"
                )
                response_data["generated_response"] = generated_response
            except Exception as e:
                logger.warning(f"Response generation failed: {str(e)}")
                response_data["generation_error"] = str(e)
        
        return response_data
        
    except Exception as e:
        logger.error(f"Multimodal search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Multimodal search failed: {str(e)}")

@router.get("/similar")
async def search_similar(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(5, description="Number of results"),
    doc_type: Optional[str] = Query(None, description="Document type filter")
) -> Dict[str, Any]:
    """Simple similarity search endpoint."""
    try:
        results = vector_retriever.retrieve(
            query=query,
            top_k=top_k,
            doc_type=doc_type
        )
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results)
        }
        
    except Exception as e:
        logger.error(f"Similarity search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Similarity search failed: {str(e)}")

