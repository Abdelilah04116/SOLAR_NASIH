"""
Validateurs pour le système RAG multimodal.
Gère la validation des entrées, des configurations et des données.
"""

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path
import json
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class Validator:
    """Classe de base pour les validateurs."""
    
    @staticmethod
    def validate_not_empty(value: Any, field_name: str) -> Tuple[bool, str]:
        """Valide qu'une valeur n'est pas vide."""
        if value is None:
            return False, f"Le champ '{field_name}' ne peut pas être null"
        
        if isinstance(value, str) and not value.strip():
            return False, f"Le champ '{field_name}' ne peut pas être vide"
        
        if isinstance(value, (list, dict)) and len(value) == 0:
            return False, f"Le champ '{field_name}' ne peut pas être vide"
        
        return True, "Valeur valide"
    
    @staticmethod
    def validate_string_length(value: str, field_name: str, min_length: int = 1, max_length: int = 1000) -> Tuple[bool, str]:
        """Valide la longueur d'une chaîne."""
        if not isinstance(value, str):
            return False, f"Le champ '{field_name}' doit être une chaîne de caractères"
        
        length = len(value.strip())
        if length < min_length:
            return False, f"Le champ '{field_name}' doit contenir au moins {min_length} caractère(s)"
        
        if length > max_length:
            return False, f"Le champ '{field_name}' ne peut pas dépasser {max_length} caractères"
        
        return True, "Longueur valide"
    
    @staticmethod
    def validate_integer_range(value: Any, field_name: str, min_value: int = 0, max_value: int = 100) -> Tuple[bool, str]:
        """Valide qu'un entier est dans une plage donnée."""
        if not isinstance(value, int):
            return False, f"Le champ '{field_name}' doit être un entier"
        
        if value < min_value:
            return False, f"Le champ '{field_name}' doit être supérieur ou égal à {min_value}"
        
        if value > max_value:
            return False, f"Le champ '{field_name}' doit être inférieur ou égal à {max_value}"
        
        return True, "Valeur dans la plage valide"
    
    @staticmethod
    def validate_float_range(value: Any, field_name: str, min_value: float = 0.0, max_value: float = 1.0) -> Tuple[bool, str]:
        """Valide qu'un float est dans une plage donnée."""
        if not isinstance(value, (int, float)):
            return False, f"Le champ '{field_name}' doit être un nombre"
        
        float_value = float(value)
        if float_value < min_value:
            return False, f"Le champ '{field_name}' doit être supérieur ou égal à {min_value}"
        
        if float_value > max_value:
            return False, f"Le champ '{field_name}' doit être inférieur ou égal à {max_value}"
        
        return True, "Valeur dans la plage valide"
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path], field_name: str = "file_path") -> Tuple[bool, str]:
        """Valide un chemin de fichier."""
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False, f"Le fichier '{field_name}' n'existe pas: {file_path}"
            
            if not path.is_file():
                return False, f"Le chemin '{field_name}' ne pointe pas vers un fichier: {file_path}"
            
            if not path.is_readable():
                return False, f"Le fichier '{field_name}' n'est pas lisible: {file_path}"
            
            return True, "Chemin de fichier valide"
            
        except Exception as e:
            return False, f"Erreur de validation du chemin '{field_name}': {str(e)}"
    
    @staticmethod
    def validate_directory_path(dir_path: Union[str, Path], field_name: str = "directory_path") -> Tuple[bool, str]:
        """Valide un chemin de dossier."""
        try:
            path = Path(dir_path)
            
            if not path.exists():
                return False, f"Le dossier '{field_name}' n'existe pas: {dir_path}"
            
            if not path.is_dir():
                return False, f"Le chemin '{field_name}' ne pointe pas vers un dossier: {dir_path}"
            
            return True, "Chemin de dossier valide"
            
        except Exception as e:
            return False, f"Erreur de validation du chemin '{field_name}': {str(e)}"
    
    @staticmethod
    def validate_url(url: str, field_name: str = "url") -> Tuple[bool, str]:
        """Valide une URL."""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, f"L'URL '{field_name}' n'est pas valide: {url}"
            
            return True, "URL valide"
            
        except Exception as e:
            return False, f"Erreur de validation de l'URL '{field_name}': {str(e)}"
    
    @staticmethod
    def validate_email(email: str, field_name: str = "email") -> Tuple[bool, str]:
        """Valide une adresse email."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, f"L'email '{field_name}' n'est pas valide: {email}"
        
        return True, "Email valide"
    
    @staticmethod
    def validate_json_string(json_str: str, field_name: str = "json_string") -> Tuple[bool, str]:
        """Valide une chaîne JSON."""
        try:
            json.loads(json_str)
            return True, "JSON valide"
        except json.JSONDecodeError as e:
            return False, f"Le JSON '{field_name}' n'est pas valide: {str(e)}"
    
    @staticmethod
    def validate_list_not_empty(value: Any, field_name: str) -> Tuple[bool, str]:
        """Valide qu'une liste n'est pas vide."""
        if not isinstance(value, list):
            return False, f"Le champ '{field_name}' doit être une liste"
        
        if len(value) == 0:
            return False, f"La liste '{field_name}' ne peut pas être vide"
        
        return True, "Liste valide"
    
    @staticmethod
    def validate_dict_not_empty(value: Any, field_name: str) -> Tuple[bool, str]:
        """Valide qu'un dictionnaire n'est pas vide."""
        if not isinstance(value, dict):
            return False, f"Le champ '{field_name}' doit être un dictionnaire"
        
        if len(value) == 0:
            return False, f"Le dictionnaire '{field_name}' ne peut pas être vide"
        
        return True, "Dictionnaire valide"

class SearchValidator(Validator):
    """Validateur spécialisé pour les requêtes de recherche."""
    
    @staticmethod
    def validate_search_query(query: str) -> Tuple[bool, str]:
        """Valide une requête de recherche."""
        # Validation de base
        is_valid, message = SearchValidator.validate_string_length(query, "query", 1, 1000)
        if not is_valid:
            return is_valid, message
        
        # Vérification des caractères dangereux
        dangerous_chars = ['<', '>', '"', "'", '&', ';']
        for char in dangerous_chars:
            if char in query:
                return False, f"La requête contient des caractères dangereux: {char}"
        
        # Vérification de la longueur minimale après nettoyage
        cleaned_query = query.strip()
        if len(cleaned_query) < 2:
            return False, "La requête doit contenir au moins 2 caractères"
        
        return True, "Requête de recherche valide"
    
    @staticmethod
    def validate_search_filters(filters: Dict[str, Any]) -> Tuple[bool, str]:
        """Valide les filtres de recherche."""
        if filters is None:
            return True, "Aucun filtre"
        
        if not isinstance(filters, dict):
            return False, "Les filtres doivent être un dictionnaire"
        
        # Validation des clés de filtre autorisées
        allowed_keys = ['document_type', 'date_range', 'source', 'metadata']
        for key in filters.keys():
            if key not in allowed_keys:
                return False, f"Clé de filtre non autorisée: {key}"
        
        return True, "Filtres valides"
    
    @staticmethod
    def validate_search_type(search_type: str) -> Tuple[bool, str]:
        """Valide le type de recherche."""
        allowed_types = ['semantic', 'keyword', 'hybrid', 'multimodal']
        
        if search_type not in allowed_types:
            return False, f"Type de recherche non supporté: {search_type}. Types autorisés: {allowed_types}"
        
        return True, "Type de recherche valide"

class FileValidator(Validator):
    """Validateur spécialisé pour les fichiers."""
    
    @staticmethod
    def validate_file_extension(file_path: Union[str, Path], allowed_extensions: List[str]) -> Tuple[bool, str]:
        """Valide l'extension d'un fichier."""
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in allowed_extensions:
            return False, f"Extension non autorisée: {extension}. Extensions autorisées: {allowed_extensions}"
        
        return True, "Extension valide"
    
    @staticmethod
    def validate_file_size(file_path: Union[str, Path], max_size_bytes: int) -> Tuple[bool, str]:
        """Valide la taille d'un fichier."""
        path = Path(file_path)
        
        if not path.exists():
            return False, f"Le fichier n'existe pas: {file_path}"
        
        file_size = path.stat().st_size
        
        if file_size > max_size_bytes:
            return False, f"Le fichier est trop volumineux: {file_size} bytes > {max_size_bytes} bytes"
        
        return True, "Taille de fichier valide"
    
    @staticmethod
    def validate_file_content(file_path: Union[str, Path], expected_type: str) -> Tuple[bool, str]:
        """Valide le contenu d'un fichier."""
        path = Path(file_path)
        
        if not path.exists():
            return False, f"Le fichier n'existe pas: {file_path}"
        
        # Lecture des premiers bytes pour vérifier le type
        try:
            with open(path, 'rb') as f:
                header = f.read(512)
            
            # Vérifications basiques selon le type attendu
            if expected_type == 'text':
                try:
                    header.decode('utf-8')
                    return True, "Contenu texte valide"
                except UnicodeDecodeError:
                    return False, "Le fichier ne semble pas être un fichier texte valide"
            
            elif expected_type == 'json':
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        json.load(f)
                    return True, "Contenu JSON valide"
                except json.JSONDecodeError:
                    return False, "Le fichier ne contient pas du JSON valide"
            
            return True, "Contenu valide"
            
        except Exception as e:
            return False, f"Erreur lors de la validation du contenu: {str(e)}"

class ConfigValidator(Validator):
    """Validateur spécialisé pour les configurations."""
    
    @staticmethod
    def validate_api_config(config: Dict[str, Any]) -> Tuple[bool, str]:
        """Valide une configuration d'API."""
        required_fields = ['host', 'port', 'debug']
        
        for field in required_fields:
            if field not in config:
                return False, f"Champ requis manquant dans la config API: {field}"
        
        # Validation du port
        is_valid, message = ConfigValidator.validate_integer_range(
            config['port'], 'port', 1, 65535
        )
        if not is_valid:
            return is_valid, message
        
        # Validation du debug
        if not isinstance(config['debug'], bool):
            return False, "Le champ 'debug' doit être un booléen"
        
        return True, "Configuration API valide"
    
    @staticmethod
    def validate_database_config(config: Dict[str, Any]) -> Tuple[bool, str]:
        """Valide une configuration de base de données."""
        required_fields = ['host', 'port', 'database', 'username']
        
        for field in required_fields:
            if field not in config:
                return False, f"Champ requis manquant dans la config DB: {field}"
        
        # Validation du port
        is_valid, message = ConfigValidator.validate_integer_range(
            config['port'], 'port', 1, 65535
        )
        if not is_valid:
            return is_valid, message
        
        return True, "Configuration base de données valide"
    
    @staticmethod
    def validate_model_config(config: Dict[str, Any]) -> Tuple[bool, str]:
        """Valide une configuration de modèle."""
        required_fields = ['model_name', 'provider', 'max_tokens']
        
        for field in required_fields:
            if field not in config:
                return False, f"Champ requis manquant dans la config modèle: {field}"
        
        # Validation du provider
        allowed_providers = ['openai', 'anthropic', 'huggingface', 'gemini']
        if config['provider'] not in allowed_providers:
            return False, f"Provider non supporté: {config['provider']}"
        
        # Validation des tokens
        is_valid, message = ConfigValidator.validate_integer_range(
            config['max_tokens'], 'max_tokens', 1, 4000
        )
        if not is_valid:
            return is_valid, message
        
        return True, "Configuration modèle valide"

class ResponseValidator(Validator):
    """Validateur spécialisé pour les réponses."""
    
    @staticmethod
    def validate_search_response(response: Dict[str, Any]) -> Tuple[bool, str]:
        """Valide une réponse de recherche."""
        required_fields = ['status', 'query', 'results']
        
        for field in required_fields:
            if field not in response:
                return False, f"Champ requis manquant dans la réponse: {field}"
        
        # Validation du statut
        allowed_statuses = ['success', 'error', 'partial']
        if response['status'] not in allowed_statuses:
            return False, f"Statut non valide: {response['status']}"
        
        # Validation des résultats
        if not isinstance(response['results'], list):
            return False, "Le champ 'results' doit être une liste"
        
        return True, "Réponse de recherche valide"
    
    @staticmethod
    def validate_generation_response(response: Dict[str, Any]) -> Tuple[bool, str]:
        """Valide une réponse de génération."""
        required_fields = ['status', 'query', 'response']
        
        for field in required_fields:
            if field not in response:
                return False, f"Champ requis manquant dans la réponse: {field}"
        
        # Validation du statut
        allowed_statuses = ['success', 'error', 'partial']
        if response['status'] not in allowed_statuses:
            return False, f"Statut non valide: {response['status']}"
        
        # Validation de la réponse générée
        if response['status'] == 'success':
            is_valid, message = ResponseValidator.validate_string_length(
                response['response'], 'response', 1, 10000
            )
            if not is_valid:
                return is_valid, message
        
        return True, "Réponse de génération valide"

# Instance globale des validateurs
_search_validator = SearchValidator()
_file_validator = FileValidator()
_config_validator = ConfigValidator()
_response_validator = ResponseValidator()

def get_search_validator() -> SearchValidator:
    """Récupère l'instance du validateur de recherche."""
    return _search_validator

def get_file_validator() -> FileValidator:
    """Récupère l'instance du validateur de fichiers."""
    return _file_validator

def get_config_validator() -> ConfigValidator:
    """Récupère l'instance du validateur de configuration."""
    return _config_validator

def get_response_validator() -> ResponseValidator:
    """Récupère l'instance du validateur de réponses."""
    return _response_validator
