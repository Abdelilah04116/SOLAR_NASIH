"""
Utilitaires pour la gestion des fichiers dans le système RAG multimodal.
Gère la validation, le nettoyage, la conversion et l'organisation des fichiers.
"""

import logging
import os
import shutil
import hashlib
import mimetypes
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
from datetime import datetime
import json
import zipfile
import tempfile
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class FileUtils:
    """Utilitaires pour la gestion des fichiers."""
    
    # Extensions supportées par type de document
    SUPPORTED_EXTENSIONS = {
        'text': ['.txt', '.md', '.rst', '.csv', '.json', '.xml', '.html', '.htm'],
        'document': ['.pdf', '.docx', '.doc', '.odt', '.rtf'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'],
        'audio': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'],
        'video': ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'],
        'archive': ['.zip', '.rar', '.7z', '.tar', '.gz']
    }
    
    # Taille maximale des fichiers (en bytes)
    MAX_FILE_SIZES = {
        'text': 10 * 1024 * 1024,      # 10 MB
        'document': 50 * 1024 * 1024,   # 50 MB
        'image': 20 * 1024 * 1024,      # 20 MB
        'audio': 100 * 1024 * 1024,     # 100 MB
        'video': 500 * 1024 * 1024,     # 500 MB
        'archive': 200 * 1024 * 1024    # 200 MB
    }
    
    @staticmethod
    def get_file_type(file_path: Union[str, Path]) -> str:
        """Détermine le type de fichier basé sur l'extension."""
        file_path = Path(file_path)
        extension = file_path.suffix.lower()
        
        for file_type, extensions in FileUtils.SUPPORTED_EXTENSIONS.items():
            if extension in extensions:
                return file_type
        
        return 'unknown'
    
    @staticmethod
    def is_supported_file(file_path: Union[str, Path]) -> bool:
        """Vérifie si le fichier est supporté."""
        file_type = FileUtils.get_file_type(file_path)
        return file_type != 'unknown'
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """Récupère la taille d'un fichier."""
        return Path(file_path).stat().st_size
    
    @staticmethod
    def is_file_size_valid(file_path: Union[str, Path]) -> bool:
        """Vérifie si la taille du fichier est dans les limites."""
        file_size = FileUtils.get_file_size(file_path)
        file_type = FileUtils.get_file_type(file_path)
        max_size = FileUtils.MAX_FILE_SIZES.get(file_type, 0)
        return file_size <= max_size
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path], algorithm: str = 'md5') -> str:
        """Calcule le hash d'un fichier."""
        file_path = Path(file_path)
        
        if algorithm == 'md5':
            hash_func = hashlib.md5()
        elif algorithm == 'sha1':
            hash_func = hashlib.sha1()
        elif algorithm == 'sha256':
            hash_func = hashlib.sha256()
        else:
            raise ValueError(f"Algorithme de hash non supporté: {algorithm}")
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def get_file_metadata(file_path: Union[str, Path]) -> Dict[str, Any]:
        """Récupère les métadonnées d'un fichier."""
        file_path = Path(file_path)
        stat = file_path.stat()
        
        metadata = {
            'filename': file_path.name,
            'file_path': str(file_path),
            'file_type': FileUtils.get_file_type(file_path),
            'file_size': stat.st_size,
            'created_time': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'file_hash': FileUtils.get_file_hash(file_path),
            'mime_type': mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        }
        
        return metadata
    
    @staticmethod
    def create_directory_structure(base_path: Union[str, Path], structure: Dict[str, Any]) -> None:
        """Crée une structure de dossiers."""
        base_path = Path(base_path)
        
        for name, content in structure.items():
            path = base_path / name
            
            if isinstance(content, dict):
                # C'est un dossier
                path.mkdir(parents=True, exist_ok=True)
                FileUtils.create_directory_structure(path, content)
            else:
                # C'est un fichier
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(str(content))
    
    @staticmethod
    def safe_copy_file(source: Union[str, Path], destination: Union[str, Path], overwrite: bool = False) -> bool:
        """Copie un fichier de manière sécurisée."""
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            logger.error(f"❌ Fichier source introuvable: {source}")
            return False
        
        if destination.exists() and not overwrite:
            logger.warning(f"⚠️ Fichier de destination existe déjà: {destination}")
            return False
        
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            logger.info(f"✅ Fichier copié: {source} -> {destination}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la copie: {e}")
            return False
    
    @staticmethod
    def safe_move_file(source: Union[str, Path], destination: Union[str, Path], overwrite: bool = False) -> bool:
        """Déplace un fichier de manière sécurisée."""
        source = Path(source)
        destination = Path(destination)
        
        if not source.exists():
            logger.error(f"❌ Fichier source introuvable: {source}")
            return False
        
        if destination.exists() and not overwrite:
            logger.warning(f"⚠️ Fichier de destination existe déjà: {destination}")
            return False
        
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(destination))
            logger.info(f"✅ Fichier déplacé: {source} -> {destination}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors du déplacement: {e}")
            return False
    
    @staticmethod
    def extract_archive(archive_path: Union[str, Path], extract_to: Union[str, Path]) -> List[Path]:
        """Extrait une archive."""
        archive_path = Path(archive_path)
        extract_to = Path(extract_to)
        
        if not archive_path.exists():
            logger.error(f"❌ Archive introuvable: {archive_path}")
            return []
        
        extracted_files = []
        
        try:
            extract_to.mkdir(parents=True, exist_ok=True)
            
            if archive_path.suffix.lower() == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_to)
                    extracted_files = [extract_to / f for f in zip_ref.namelist()]
            
            logger.info(f"✅ Archive extraite: {archive_path} -> {extract_to}")
            return extracted_files
            
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'extraction: {e}")
            return []
    
    @staticmethod
    def clean_filename(filename: str) -> str:
        """Nettoie un nom de fichier pour le rendre sûr."""
        import re
        
        # Supprime les caractères dangereux
        cleaned = re.sub(r'[<>:"/\\|?*]', '_', filename)
        
        # Supprime les espaces multiples
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Supprime les points et underscores multiples
        cleaned = re.sub(r'[._]+', '_', cleaned)
        
        # Supprime les espaces en début et fin
        cleaned = cleaned.strip()
        
        # Limite la longueur
        if len(cleaned) > 255:
            name, ext = os.path.splitext(cleaned)
            cleaned = name[:255-len(ext)] + ext
        
        return cleaned
    
    @staticmethod
    def create_temp_file(prefix: str = "rag_", suffix: str = "", content: Optional[str] = None) -> Path:
        """Crée un fichier temporaire."""
        with tempfile.NamedTemporaryFile(prefix=prefix, suffix=suffix, delete=False) as f:
            temp_path = Path(f.name)
            
            if content:
                f.write(content.encode('utf-8'))
        
        return temp_path
    
    @staticmethod
    def create_temp_directory(prefix: str = "rag_") -> Path:
        """Crée un dossier temporaire."""
        temp_dir = tempfile.mkdtemp(prefix=prefix)
        return Path(temp_dir)
    
    @staticmethod
    def cleanup_temp_files(temp_paths: List[Path]) -> None:
        """Nettoie les fichiers temporaires."""
        for path in temp_paths:
            try:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
                logger.info(f"✅ Fichier temporaire supprimé: {path}")
            except Exception as e:
                logger.warning(f"⚠️ Impossible de supprimer le fichier temporaire {path}: {e}")
    
    @staticmethod
    def find_files_by_pattern(directory: Union[str, Path], pattern: str, recursive: bool = True) -> List[Path]:
        """Trouve des fichiers selon un pattern."""
        directory = Path(directory)
        files = []
        
        if recursive:
            search_pattern = f"**/{pattern}"
        else:
            search_pattern = pattern
        
        try:
            files = list(directory.glob(search_pattern))
            logger.info(f"✅ {len(files)} fichiers trouvés avec le pattern '{pattern}' dans {directory}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de la recherche: {e}")
        
        return files
    
    @staticmethod
    def get_directory_size(directory: Union[str, Path]) -> int:
        """Calcule la taille totale d'un dossier."""
        directory = Path(directory)
        total_size = 0
        
        try:
            for file_path in directory.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
        except Exception as e:
            logger.error(f"❌ Erreur lors du calcul de la taille: {e}")
        
        return total_size
    
    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Formate une taille de fichier en format lisible."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    @staticmethod
    def validate_file_path(file_path: Union[str, Path]) -> Tuple[bool, str]:
        """Valide un chemin de fichier."""
        file_path = Path(file_path)
        
        # Vérifie si le fichier existe
        if not file_path.exists():
            return False, f"Le fichier n'existe pas: {file_path}"
        
        # Vérifie si c'est un fichier (pas un dossier)
        if not file_path.is_file():
            return False, f"Le chemin ne pointe pas vers un fichier: {file_path}"
        
        # Vérifie si le fichier est lisible
        if not os.access(file_path, os.R_OK):
            return False, f"Le fichier n'est pas lisible: {file_path}"
        
        # Vérifie si le fichier est supporté
        if not FileUtils.is_supported_file(file_path):
            return False, f"Type de fichier non supporté: {file_path}"
        
        # Vérifie la taille du fichier
        if not FileUtils.is_file_size_valid(file_path):
            file_size = FileUtils.get_file_size(file_path)
            file_type = FileUtils.get_file_type(file_path)
            max_size = FileUtils.MAX_FILE_SIZES.get(file_type, 0)
            return False, f"Fichier trop volumineux ({FileUtils.format_file_size(file_size)} > {FileUtils.format_file_size(max_size)}): {file_path}"
        
        return True, "Fichier valide"
    
    @staticmethod
    def save_json(data: Dict[str, Any], file_path: Union[str, Path], indent: int = 2) -> bool:
        """Sauvegarde des données en JSON."""
        file_path = Path(file_path)
        
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=indent, ensure_ascii=False)
            logger.info(f"✅ Données JSON sauvegardées: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la sauvegarde JSON: {e}")
            return False
    
    @staticmethod
    def load_json(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Charge des données JSON."""
        file_path = Path(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ Données JSON chargées: {file_path}")
            return data
        except Exception as e:
            logger.error(f"❌ Erreur lors du chargement JSON: {e}")
            return None
