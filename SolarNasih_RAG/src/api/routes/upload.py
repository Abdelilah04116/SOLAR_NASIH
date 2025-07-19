import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from typing import List, Dict, Any
import tempfile
import shutil
from pathlib import Path
import uuid

from src.ingestion.preprocessor import Preprocessor
from src.vectorization.indexer import Indexer
from config.settings import settings

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize components
preprocessor = Preprocessor()
indexer = Indexer()

@router.post("/file")
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
) -> Dict[str, Any]:
    """Upload and process a single file."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = Path(tmp_file.name)
        
        # Generate unique ID for this upload
        upload_id = str(uuid.uuid4())
        
        # Process file in background
        background_tasks.add_task(
            process_and_index_file,
            tmp_path,
            file.filename,
            upload_id
        )
        
        return {
            "message": "File uploaded successfully",
            "upload_id": upload_id,
            "filename": file.filename,
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.post("/files")
async def upload_files(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
) -> Dict[str, Any]:
    """Upload and process multiple files."""
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        upload_id = str(uuid.uuid4())
        uploaded_files = []
        
        for file in files:
            if not file.filename:
                continue
                
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = Path(tmp_file.name)
            
            uploaded_files.append({
                "filename": file.filename,
                "temp_path": tmp_path
            })
        
        # Process files in background
        background_tasks.add_task(
            process_and_index_files,
            uploaded_files,
            upload_id
        )
        
        return {
            "message": f"Successfully uploaded {len(uploaded_files)} files",
            "upload_id": upload_id,
            "files": [f["filename"] for f in uploaded_files],
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Multiple file upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

async def process_and_index_file(file_path: Path, filename: str, upload_id: str):
    """Background task to process and index a single file."""
    try:
        logger.info(f"Processing file: {filename} (Upload ID: {upload_id})")
        
        # Process document
        chunks = preprocessor.process_document(file_path)
        
        # Index chunks
        success = indexer.index_chunks(chunks)
        
        if success:
            logger.info(f"Successfully indexed {len(chunks)} chunks from {filename}")
        else:
            logger.error(f"Failed to index file: {filename}")
        
        # Cleanup temporary file
        file_path.unlink()
        
    except Exception as e:
        logger.error(f"Background processing failed for {filename}: {str(e)}")
        # Cleanup on error
        if file_path.exists():
            file_path.unlink()

async def process_and_index_files(uploaded_files: List[Dict[str, Any]], upload_id: str):
    """Background task to process and index multiple files."""
    try:
        logger.info(f"Processing {len(uploaded_files)} files (Upload ID: {upload_id})")
        
        all_chunks = []
        
        for file_info in uploaded_files:
            try:
                file_path = file_info["temp_path"]
                filename = file_info["filename"]
                
                # Process document
                chunks = preprocessor.process_document(file_path)
                all_chunks.extend(chunks)
                
                logger.info(f"Processed {filename}: {len(chunks)} chunks")
                
                # Cleanup temporary file
                file_path.unlink()
                
            except Exception as e:
                logger.error(f"Failed to process {file_info['filename']}: {str(e)}")
                continue
        
        # Index all chunks
        if all_chunks:
            success = indexer.index_chunks(all_chunks)
            if success:
                logger.info(f"Successfully indexed {len(all_chunks)} total chunks")
            else:
                logger.error("Failed to index chunks")
        
    except Exception as e:
        logger.error(f"Background batch processing failed: {str(e)}")

