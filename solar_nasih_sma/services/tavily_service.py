from typing import List, Dict, Any, Optional
from tavily import TavilyClient
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TavilyService:
    """
    Service pour interagir avec l'API Tavily (recherche web)
    """
    
    def __init__(self):
        self.api_key = settings.TAVILY_API_KEY
        self.max_results = settings.TAVILY_MAX_RESULTS
        
        try:
            self.client = TavilyClient(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Tavily: {e}")
            raise
    
    def search(
        self, 
        query: str, 
        search_depth: str = "basic",
        max_results: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Effectue une recherche web avec Tavily
        
        Args:
            query: La requête de recherche
            search_depth: Profondeur de recherche ("basic" ou "advanced")
            max_results: Nombre maximum de résultats
            
        Returns:
            Liste des résultats de recherche
        """
        
        try:
            max_results = max_results or self.max_results
            
            # Ajout de mots-clés spécifiques au solaire
            enhanced_query = f"{query} énergie solaire photovoltaïque"
            
            response = self.client.search(
                query=enhanced_query,
                search_depth=search_depth,
                max_results=max_results
            )
            
            # Filtrage et formatage des résultats
            return self._process_search_results(response.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche Tavily: {e}")
            return []
    
    def search_solar_regulations(self, region: str = "france") -> List[Dict[str, Any]]:
        """
        Recherche spécifique sur les réglementations solaires
        
        Args:
            region: Région pour la recherche réglementaire
            
        Returns:
            Résultats sur les réglementations
        """
        
        query = f"réglementation photovoltaïque {region} 2024 normes installation"
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=5
            )
            
            return self._process_search_results(response.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche réglementaire: {e}")
            return []
    
    def search_solar_prices(self, location: str = "france") -> List[Dict[str, Any]]:
        """
        Recherche sur les prix du solaire
        
        Args:
            location: Localisation pour la recherche de prix
            
        Returns:
            Résultats sur les prix du solaire
        """
        
        query = f"prix installation photovoltaïque {location} 2024 coût panneau solaire"
        
        try:
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=self.max_results
            )
            
            return self._process_search_results(response.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de prix: {e}")
            return []
    
    def search_solar_incentives(self, region: str = "france") -> List[Dict[str, Any]]:
        """
        Recherche sur les aides et subventions solaires
        
        Args:
            region: Région pour la recherche d'aides
            
        Returns:
            Résultats sur les aides disponibles
        """
        
        query = f"aides subventions photovoltaïque {region} 2024 prime autoconsommation"
        
        try:
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=self.max_results
            )
            
            return self._process_search_results(response.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche d'aides: {e}")
            return []
    
    def search_technical_info(self, topic: str) -> List[Dict[str, Any]]:
        """
        Recherche d'informations techniques spécifiques
        
        Args:
            topic: Sujet technique à rechercher
            
        Returns:
            Résultats techniques
        """
        
        query = f"{topic} photovoltaïque technique installation guide"
        
        try:
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=3
            )
            
            return self._process_search_results(response.get("results", []))
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche technique: {e}")
            return []
    
    def _process_search_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Traite et filtre les résultats de recherche
        
        Args:
            results: Résultats bruts de Tavily
            
        Returns:
            Résultats traités et filtrés
        """
        
        processed_results = []
        
        for result in results:
            # Filtrage des résultats pertinents
            if self._is_relevant_result(result):
                processed_result = {
                    "title": result.get("title", ""),
                    "url": result.get("url", ""),
                    "content": self._clean_content(result.get("content", "")),
                    "score": result.get("score", 0),
                    "published_date": result.get("published_date", ""),
                    "source": self._extract_source(result.get("url", ""))
                }
                processed_results.append(processed_result)
        
        # Tri par score de pertinence
        processed_results.sort(key=lambda x: x["score"], reverse=True)
        
        return processed_results
    
    def _is_relevant_result(self, result: Dict[str, Any]) -> bool:
        """
        Vérifie si un résultat est pertinent pour le solaire
        
        Args:
            result: Résultat à vérifier
            
        Returns:
            True si pertinent, False sinon
        """
        
        # Mots-clés pertinents
        relevant_keywords = [
            "photovoltaïque", "solaire", "panneau", "installation",
            "onduleur", "énergie", "électricité", "autoconsommation",
            "rendement", "watt", "kwh", "rge", "enedis"
        ]
        
        # Mots-clés à éviter
        irrelevant_keywords = [
            "casino", "jeux", "publicité", "spam", "adult"
        ]
        
        content = (result.get("title", "") + " " + result.get("content", "")).lower()
        
        # Vérification des mots-clés pertinents
        has_relevant = any(keyword in content for keyword in relevant_keywords)
        
        # Vérification des mots-clés non pertinents
        has_irrelevant = any(keyword in content for keyword in irrelevant_keywords)
        
        return has_relevant and not has_irrelevant
    
    def _clean_content(self, content: str) -> str:
        """
        Nettoie le contenu des résultats
        
        Args:
            content: Contenu à nettoyer
            
        Returns:
            Contenu nettoyé
        """
        
        if not content:
            return ""
        
        # Limitation de la longueur
        max_length = 500
        if len(content) > max_length:
            content = content[:max_length] + "..."
        
        # Nettoyage basique
        content = content.replace("\n", " ").replace("\t", " ")
        content = " ".join(content.split())  # Supprime les espaces multiples
        
        return content
    
    def _extract_source(self, url: str) -> str:
        """
        Extrait le nom de la source depuis l'URL
        
        Args:
            url: URL du résultat
            
        Returns:
            Nom de la source
        """
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc
            
            # Suppression du www
            if domain.startswith("www."):
                domain = domain[4:]
                
            return domain
            
        except Exception:
            return "Source inconnue"
    
    def validate_api_key(self) -> bool:
        """
        Valide la clé API Tavily
        
        Returns:
            True si la clé est valide, False sinon
        """
        
        try:
            # Test simple de recherche
            test_response = self.client.search(
                query="test",
                max_results=1
            )
            return True
            
        except Exception as e:
            logger.error(f"Clé API Tavily invalide: {e}")
            return False