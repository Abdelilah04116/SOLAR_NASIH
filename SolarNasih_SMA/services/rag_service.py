from typing import Dict, Any, List, Optional
from fastapi import UploadFile
import httpx
from config.settings import settings
import logging
import requests

logger = logging.getLogger(__name__)

RAG_API_URL = "http://localhost:8001"  # adapte le port si besoin

class RAGService:
    """
    Interface avec le système RAG existant
    """
    
    def __init__(self, base_url=RAG_API_URL):
        self.base_url = base_url
        self.similarity_threshold = settings.RAG_SIMILARITY_THRESHOLD
        
    async def query(
        self, 
        query: str, 
        language: str = "fr", 
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Interroge le système RAG existant
        
        Args:
            query: Question à poser au RAG
            language: Langue de la requête
            max_results: Nombre maximum de résultats
            
        Returns:
            Réponse du système RAG
        """
        
        try:
            async with httpx.AsyncClient() as client:
                # Appel à l'endpoint RAG correct /search/
                response = await client.post(
                    f"{self.base_url}/search/",
                    json={
                        "query": query,
                        "method": "hybrid",
                        "top_k": max_results,
                        "generate_response": True
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    rag_data = response.json()
                    
                    # Transformation de la réponse pour correspondre au format attendu
                    return {
                        "answer": rag_data.get("generated_response", {}).get("response", ""),
                        "confidence": rag_data.get("generated_response", {}).get("confidence", 0.8),
                        "sources": [result.get("source", "") for result in rag_data.get("results", [])],
                        "similarity_score": rag_data.get("results", [{}])[0].get("score", 0.0) if rag_data.get("results") else 0.0,
                        "total_results": rag_data.get("total_results", 0)
                    }
                else:
                    logger.error(f"Erreur RAG: {response.status_code} - {response.text}")
                    return self._fallback_response(query)
                    
        except httpx.RequestError as e:
            logger.error(f"Erreur de connexion RAG: {e}")
            return self._fallback_response(query)
        
        except Exception as e:
            logger.error(f"Erreur lors de la requête RAG: {e}")
            return self._fallback_response(query)
    
    async def index_document(self, file: UploadFile) -> str:
        """
        Indexe un document dans le système RAG
        
        Args:
            file: Fichier à indexer
            
        Returns:
            ID du document indexé
        """
        
        try:
            async with httpx.AsyncClient() as client:
                # Préparation du fichier pour l'upload
                files = {"file": (file.filename, await file.read(), file.content_type)}
                
                # Appel à l'endpoint d'indexation RAG correct
                response = await client.post(
                    f"{self.base_url}/upload/file",
                    files=files,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("upload_id", "unknown")
                else:
                    logger.error(f"Erreur indexation RAG: {response.status_code}")
                    raise Exception(f"Erreur lors de l'indexation: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Erreur lors de l'indexation: {e}")
            raise
    
    async def get_document_info(self, document_id: str) -> Dict[str, Any]:
        """
        Récupère les informations d'un document
        
        Args:
            document_id: ID du document
            
        Returns:
            Informations du document
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/status",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": "Document non trouvé"}
                    
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du document: {e}")
            return {"error": str(e)}
    
    async def list_documents(self) -> List[Dict[str, Any]]:
        """
        Liste tous les documents indexés
        
        Returns:
            Liste des documents
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/status",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data.get("documents", [])
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Erreur lors de la liste des documents: {e}")
            return []
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Supprime un document du système RAG
        
        Args:
            document_id: ID du document à supprimer
            
        Returns:
            True si suppression réussie, False sinon
        """
        
        try:
            # Le système RAG actuel ne supporte pas la suppression
            logger.warning("Suppression de document non supportée par le système RAG actuel")
            return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du document: {e}")
            return False
    
    async def search_similar(
        self, 
        text: str, 
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recherche de documents similaires
        
        Args:
            text: Texte de référence
            limit: Nombre de résultats
            
        Returns:
            Documents similaires
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/similar",
                    params={
                        "query": text,
                        "top_k": limit
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    return response.json().get("results", [])
                else:
                    return []
                    
        except Exception as e:
            logger.error(f"Erreur lors de la recherche similaire: {e}")
            return []
    
    def _fallback_response(self, query: str) -> Dict[str, Any]:
        """
        Réponse de fallback quand le RAG n'est pas disponible
        """
        query_lower = query.lower()

        if any(word in query_lower for word in ["prix", "coût", "tarif"]):
            answer = "Le coût d'une installation photovoltaïque varie généralement entre 9 000€ et 18 000€ pour une maison individuelle, selon la puissance et la qualité des équipements."
        elif any(word in query_lower for word in ["production", "rendement"]):
            answer = "Une installation photovoltaïque de 3 kWc produit en moyenne 3 500 à 4 500 kWh par an en France, selon la région et l'orientation."
        elif any(word in query_lower for word in ["aide", "subvention", "prime"]):
            answer = "Plusieurs aides existent : prime à l'autoconsommation, taux de TVA réduit, crédit d'impôt dans certains cas, et aides locales variables selon les régions."
        elif any(word in query_lower for word in ["installation", "étapes"]):
            answer = "L'installation comprend : étude de faisabilité, démarches administratives, pose des panneaux, raccordement électrique, et mise en service par Enedis."
        elif any(word in query_lower for word in ["solar nasih", "rôle", "role", "fonction", "mission", "qui es-tu", "qui etes-vous", "présente-toi", "présentez-vous"]):
            answer = (
                "Solar Nasih est un assistant intelligent multi-agent dédié à l'énergie solaire. "
                "Il accompagne les utilisateurs dans la compréhension, la simulation, la réglementation, la certification, le financement et la gestion de projets solaires. "
                "Il répond à vos questions, vous guide dans vos démarches et vous aide à optimiser vos projets photovoltaïques."
            )
        else:
            answer = (
                "Je n'ai pas pu accéder à ma base de connaissances, mais voici ce que je peux vous dire :\n"
                "Solar Nasih est un assistant intelligent dédié à l'énergie solaire. Posez-moi des questions sur l'installation, la réglementation, la simulation, la certification ou le financement, et je vous aiderai au mieux !"
            )
        return {
            "answer": answer,
            "confidence": 0.6,
            "sources": ["Connaissances de base Solar Nasih"],
            "fallback": True
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Vérifie la santé du système RAG
        
        Returns:
            Statut de santé du système RAG
        """
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health/",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    health_data = response.json()
                    return {
                        "status": "healthy",
                        "endpoint": self.base_url,
                        "response_time": response.elapsed.total_seconds(),
                        "rag_status": health_data
                    }
                else:
                    return {
                        "status": "unhealthy",
                        "endpoint": self.base_url,
                        "error": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "status": "unhealthy",
                "endpoint": self.base_url,
                "error": str(e)
            }