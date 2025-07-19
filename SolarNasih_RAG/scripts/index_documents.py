import logging
import sys
import os
from pathlib import Path
import argparse
import time

# Ajouter le dossier racine au PYTHONPATH
script_dir = Path(__file__).parent
project_root = script_dir.parent
sys.path.insert(0, str(project_root))

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/indexing.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Vérifie que les dépendances nécessaires sont disponibles"""
    missing_deps = []
    
    try:
        from src.ingestion.preprocessor import Preprocessor
    except ImportError as e:
        missing_deps.append(f"Preprocessor: {e}")
    
    try:
        from src.vectorization.indexer import Indexer
    except ImportError as e:
        missing_deps.append(f"Indexer: {e}")
    
    if missing_deps:
        logger.error("❌ Missing dependencies:")
        for dep in missing_deps:
            logger.error(f"   - {dep}")
        return False
    
    return True

def check_qdrant_connection():
    """Vérifie la connexion à Qdrant"""
    try:
        import requests
        response = requests.get("http://localhost:6333/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Qdrant is running")
            return True
        else:
            logger.warning(f"⚠️ Qdrant health check failed: {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"⚠️ Cannot connect to Qdrant: {e}")
        return False

def find_documents(directory_path: Path, extensions: list = None) -> list:
    """Trouve tous les documents supportés dans un répertoire"""
    if extensions is None:
        extensions = ['.txt', '.pdf', '.jpg', '.jpeg', '.png', '.mp3', '.wav', '.mp4', '.avi']
    
    found_files = []
    
    if not directory_path.exists():
        logger.error(f"❌ Directory does not exist: {directory_path}")
        return found_files
    
    logger.info(f"🔍 Scanning directory: {directory_path}")
    
    for extension in extensions:
        files = list(directory_path.rglob(f"*{extension}"))
        found_files.extend(files)
        if files:
            logger.info(f"   Found {len(files)} {extension} files")
    
    logger.info(f"📊 Total files found: {len(found_files)}")
    return found_files

def index_directory(directory_path: str, dry_run: bool = False):
    """Indexe tous les documents dans un répertoire"""
    
    print("🚀 Document Indexing System")
    print("=" * 50)
    
    directory = Path(directory_path)
    
    # Vérifications préliminaires
    logger.info("🔍 Performing preliminary checks...")
    
    if not check_dependencies():
        logger.error("❌ Cannot proceed without required dependencies")
        return False
    
    qdrant_available = check_qdrant_connection()
    
    # Créer les répertoires de logs si nécessaire
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Trouver les documents
    files_to_process = find_documents(directory)
    
    if not files_to_process:
        logger.warning("⚠️ No supported documents found")
        return False
    
    if dry_run:
        logger.info("🔬 DRY RUN MODE - No actual processing will occur")
        for file_path in files_to_process:
            logger.info(f"   Would process: {file_path}")
        return True
    
    # Initialiser les composants
    logger.info("⚡ Initializing components...")
    
    try:
        from src.ingestion.preprocessor import Preprocessor
        from src.vectorization.indexer import Indexer
        
        preprocessor = Preprocessor()
        logger.info("✅ Preprocessor initialized")
        
        if qdrant_available:
            indexer = Indexer()
            logger.info("✅ Indexer initialized")
        else:
            logger.warning("⚠️ Qdrant not available - will process without indexing")
            indexer = None
            
    except Exception as e:
        logger.error(f"❌ Component initialization failed: {e}")
        return False
    
    # Traitement des documents
    logger.info(f"📚 Processing {len(files_to_process)} documents...")
    
    successful_files = 0
    failed_files = 0
    total_chunks = 0
    
    start_time = time.time()
    
    for i, file_path in enumerate(files_to_process, 1):
        try:
            logger.info(f"📄 [{i}/{len(files_to_process)}] Processing: {file_path.name}")
            
            # Traiter le document
            chunks = preprocessor.process_document(file_path)
            
            if chunks:
                logger.info(f"   ✅ Created {len(chunks)} chunks")
                total_chunks += len(chunks)
                
                # Indexer si possible
                if indexer:
                    try:
                        success = indexer.index_chunks(chunks)
                        if success:
                            logger.info(f"   ✅ Indexed {len(chunks)} chunks")
                        else:
                            logger.warning(f"   ⚠️ Indexing failed for {file_path.name}")
                    except Exception as e:
                        logger.warning(f"   ⚠️ Indexing error: {e}")
                
                successful_files += 1
            else:
                logger.warning(f"   ⚠️ No chunks created for {file_path.name}")
                failed_files += 1
                
        except Exception as e:
            logger.error(f"   ❌ Processing failed for {file_path.name}: {e}")
            failed_files += 1
        
        # Afficher le progrès
        progress = (i / len(files_to_process)) * 100
        logger.info(f"   📊 Progress: {progress:.1f}%")
    
    # Résumé final
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 50)
    print("📊 INDEXING SUMMARY")
    print("=" * 50)
    print(f"✅ Successful files: {successful_files}")
    print(f"❌ Failed files: {failed_files}")
    print(f"📦 Total chunks created: {total_chunks}")
    print(f"⏱️ Total time: {duration:.2f} seconds")
    print(f"📈 Average time per file: {duration/len(files_to_process):.2f} seconds")
    
    if indexer:
        print(f"🗄️ Documents indexed in Qdrant")
    else:
        print(f"⚠️ Documents processed but not indexed (Qdrant unavailable)")
    
    return successful_files > 0

def main():
    """Point d'entrée principal avec gestion d'arguments"""
    parser = argparse.ArgumentParser(
        description="Index documents for RAG multimodal system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/index_documents.py data/raw
  python scripts/index_documents.py data/raw --dry-run
  python scripts/index_documents.py /path/to/documents --extensions .pdf .txt
        """
    )
    
    parser.add_argument(
        'directory',
        help='Directory containing documents to index'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be processed without actually doing it'
    )
    
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.txt', '.pdf', '.jpg', '.jpeg', '.png', '.mp3', '.wav', '.mp4', '.avi'],
        help='File extensions to process (default: all supported)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configuration du logging selon la verbosité
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Vérifier que le répertoire existe
    directory_path = Path(args.directory)
    if not directory_path.exists():
        print(f"❌ Error: Directory '{args.directory}' does not exist")
        print(f"💡 Available directories in current path:")
        for item in Path('.').iterdir():
            if item.is_dir():
                print(f"   📁 {item}")
        sys.exit(1)
    
    # Lancer l'indexation
    try:
        success = index_directory(args.directory, args.dry_run)
        if success:
            print("\n🎉 Indexing completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Indexing failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Indexing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()