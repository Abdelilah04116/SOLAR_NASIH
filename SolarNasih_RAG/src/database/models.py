from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class Document(Base):
    """Document model for metadata storage."""
    __tablename__ = "documents"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String)
    doc_type = Column(String, nullable=False)
    
    # Processing status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    chunks_count = Column(Integer, default=0)
    
    # Metadata
    metadata = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class ProcessingJob(Base):
    """Processing job tracking."""
    __tablename__ = "processing_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    upload_id = Column(String, nullable=False)
    document_id = Column(String, nullable=False)
    
    status = Column(String, default="queued")  # queued, running, completed, failed
    progress = Column(Float, default=0.0)
    error_message = Column(Text)
    
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

class SearchLog(Base):
    """Search query logging."""
    __tablename__ = "search_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    query = Column(Text, nullable=False)
    method = Column(String, nullable=False)
    results_count = Column(Integer, default=0)
    response_time = Column(Float)
    
    # User tracking (if implemented)
    user_id = Column(String)
    
    created_at = Column(DateTime, server_default=func.now())

