import logging
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)

async def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Simple authentication (extend for production use)."""
    # For development, we'll skip authentication
    # In production, implement proper JWT validation here
    
    if not credentials:
        # For now, allow unauthenticated access
        return {"user_id": "anonymous", "permissions": ["read", "write"]}
    
    # Validate token (placeholder)
    token = credentials.credentials
    
    if token == "demo-token":
        return {"user_id": "demo_user", "permissions": ["read", "write"]}
    
    # For production, implement proper JWT validation
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
