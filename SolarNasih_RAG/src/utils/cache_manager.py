"""
Gestionnaire de cache pour optimiser les performances du système RAG multimodal.
Gère le cache des embeddings, des résultats de recherche et des réponses générées.
"""

import logging
import hashlib
import json
import time
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from datetime import datetime, timedelta
import pickle
import threading
from collections import OrderedDict

logger = logging.getLogger(__name__)

class CacheEntry:
    """Représente une entrée dans le cache."""
    
    def __init__(self, key: str, value: Any, ttl: int = 3600):
        self.key = key
        self.value = value
        self.created_at = datetime.now()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        """Vérifie si l'entrée a expiré."""
        return datetime.now() > self.created_at + timedelta(seconds=self.ttl)
    
    def access(self):
        """Marque l'entrée comme accédée."""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit l'entrée en dictionnaire pour la sérialisation."""
        return {
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat(),
            'ttl': self.ttl,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat()
        }

class CacheManager:
    """Gestionnaire de cache principal."""
    
    def __init__(self, 
                 max_size: int = 1000,
                 default_ttl: int = 3600,
                 cache_dir: str = "cache",
                 enable_persistence: bool = True):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache_dir = Path(cache_dir)
        self.enable_persistence = enable_persistence
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        
        # Création du dossier de cache
        if self.enable_persistence:
            self.cache_dir.mkdir(exist_ok=True)
        
        # Chargement du cache persistant
        if self.enable_persistence:
            self._load_persistent_cache()
        
        # Nettoyage périodique
        self._start_cleanup_thread()
        
        logger.info(f"✅ Cache manager initialisé (max_size={max_size}, ttl={default_ttl}s)")
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Génère une clé de cache basée sur les arguments."""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Récupère une valeur du cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                if entry.is_expired():
                    # Suppression de l'entrée expirée
                    del self.cache[key]
                    return default
                
                # Mise à jour de l'accès
                entry.access()
                
                # Déplacement en fin de liste (LRU)
                self.cache.move_to_end(key)
                
                return entry.value
            
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Stocke une valeur dans le cache."""
        with self.lock:
            # Nettoyage si nécessaire
            self._cleanup_if_needed()
            
            # Création de l'entrée
            entry = CacheEntry(key, value, ttl or self.default_ttl)
            
            # Ajout au cache
            self.cache[key] = entry
            
            # Déplacement en fin de liste
            self.cache.move_to_end(key)
            
            return True
    
    def delete(self, key: str) -> bool:
        """Supprime une entrée du cache."""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Vide complètement le cache."""
        with self.lock:
            self.cache.clear()
            if self.enable_persistence:
                self._clear_persistent_cache()
    
    def exists(self, key: str) -> bool:
        """Vérifie si une clé existe dans le cache."""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    del self.cache[key]
                    return False
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques du cache."""
        with self.lock:
            total_entries = len(self.cache)
            expired_entries = sum(1 for entry in self.cache.values() if entry.is_expired())
            valid_entries = total_entries - expired_entries
            
            total_access = sum(entry.access_count for entry in self.cache.values())
            avg_access = total_access / total_entries if total_entries > 0 else 0
            
            return {
                'total_entries': total_entries,
                'valid_entries': valid_entries,
                'expired_entries': expired_entries,
                'max_size': self.max_size,
                'usage_percentage': (total_entries / self.max_size) * 100,
                'total_access_count': total_access,
                'average_access_count': avg_access,
                'cache_hit_rate': self._calculate_hit_rate()
            }
    
    def _calculate_hit_rate(self) -> float:
        """Calcule le taux de succès du cache."""
        # Cette méthode nécessiterait un suivi des accès manqués
        # Pour l'instant, on retourne une estimation basée sur les accès
        total_access = sum(entry.access_count for entry in self.cache.values())
        return min(1.0, total_access / max(len(self.cache), 1))
    
    def _cleanup_if_needed(self):
        """Nettoie le cache si nécessaire."""
        # Suppression des entrées expirées
        expired_keys = [key for key, entry in self.cache.items() if entry.is_expired()]
        for key in expired_keys:
            del self.cache[key]
        
        # Si le cache est encore trop plein, supprime les entrées les moins utilisées
        while len(self.cache) >= self.max_size:
            # Supprime l'entrée la moins récemment utilisée
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
    
    def _start_cleanup_thread(self):
        """Démarre le thread de nettoyage périodique."""
        def cleanup_worker():
            while True:
                try:
                    time.sleep(300)  # Nettoyage toutes les 5 minutes
                    with self.lock:
                        self._cleanup_if_needed()
                except Exception as e:
                    logger.error(f"❌ Erreur dans le thread de nettoyage: {e}")
        
        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
    
    def _load_persistent_cache(self):
        """Charge le cache depuis le stockage persistant."""
        cache_file = self.cache_dir / "cache.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                # Conversion des données en objets CacheEntry
                for key, entry_data in cached_data.items():
                    entry = CacheEntry(
                        key=entry_data['key'],
                        value=entry_data['value'],
                        ttl=entry_data['ttl']
                    )
                    entry.created_at = datetime.fromisoformat(entry_data['created_at'])
                    entry.access_count = entry_data['access_count']
                    entry.last_accessed = datetime.fromisoformat(entry_data['last_accessed'])
                    
                    if not entry.is_expired():
                        self.cache[key] = entry
                
                logger.info(f"✅ Cache chargé depuis {cache_file}")
                
            except Exception as e:
                logger.error(f"❌ Erreur lors du chargement du cache: {e}")
    
    def _save_persistent_cache(self):
        """Sauvegarde le cache vers le stockage persistant."""
        if not self.enable_persistence:
            return
        
        cache_file = self.cache_dir / "cache.pkl"
        try:
            # Conversion des entrées en dictionnaires
            cache_data = {}
            for key, entry in self.cache.items():
                if not entry.is_expired():
                    cache_data[key] = entry.to_dict()
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info(f"✅ Cache sauvegardé vers {cache_file}")
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde du cache: {e}")
    
    def _clear_persistent_cache(self):
        """Efface le cache persistant."""
        cache_file = self.cache_dir / "cache.pkl"
        if cache_file.exists():
            cache_file.unlink()

class EmbeddingCache:
    """Cache spécialisé pour les embeddings."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.prefix = "embedding_"
    
    def get_embedding(self, text: str, model_name: str) -> Optional[List[float]]:
        """Récupère un embedding du cache."""
        key = self._generate_key(text, model_name)
        return self.cache_manager.get(key)
    
    def set_embedding(self, text: str, model_name: str, embedding: List[float], ttl: int = 86400):
        """Stocke un embedding dans le cache."""
        key = self._generate_key(text, model_name)
        self.cache_manager.set(key, embedding, ttl)
    
    def _generate_key(self, text: str, model_name: str) -> str:
        """Génère une clé pour un embedding."""
        key_data = f"{self.prefix}{model_name}_{hashlib.md5(text.encode()).hexdigest()}"
        return key_data

class SearchCache:
    """Cache spécialisé pour les résultats de recherche."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        self.prefix = "search_"
    
    def get_search_results(self, query: str, search_type: str, top_k: int) -> Optional[List[Dict[str, Any]]]:
        """Récupère des résultats de recherche du cache."""
        key = self._generate_key(query, search_type, top_k)
        return self.cache_manager.get(key)
    
    def set_search_results(self, query: str, search_type: str, top_k: int, results: List[Dict[str, Any]], ttl: int = 1800):
        """Stocke des résultats de recherche dans le cache."""
        key = self._generate_key(query, search_type, top_k)
        self.cache_manager.set(key, results, ttl)
    
    def _generate_key(self, query: str, search_type: str, top_k: int) -> str:
        """Génère une clé pour des résultats de recherche."""
        key_data = f"{self.prefix}{search_type}_{top_k}_{hashlib.md5(query.encode()).hexdigest()}"
        return key_data

# Instance globale du cache manager
_cache_manager: Optional[CacheManager] = None

def get_cache_manager() -> CacheManager:
    """Récupère l'instance globale du cache manager."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager

def get_embedding_cache() -> EmbeddingCache:
    """Récupère l'instance du cache d'embeddings."""
    return EmbeddingCache(get_cache_manager())

def get_search_cache() -> SearchCache:
    """Récupère l'instance du cache de recherche."""
    return SearchCache(get_cache_manager())
