import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator
import logging

logger = logging.getLogger(__name__)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate French phone number"""
    # Remove spaces and special characters
    clean_phone = re.sub(r'[\s\-\.]', '', phone)
    
    # French phone patterns
    patterns = [
        r'^0[1-9]\d{8}',  # 10 digits starting with 0
        r'^\+33[1-9]\d{8}',  # International format
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def validate_postal_code(postal_code: str) -> bool:
    """Validate French postal code"""
    pattern = r'^[0-9]{5}'
    return bool(re.match(pattern, postal_code))

def validate_power_range(power_kwc: float) -> bool:
    """Validate solar installation power range"""
    return 0.1 <= power_kwc <= 1000.0  # Reasonable range in kWc

def validate_roof_area(area_m2: float) -> bool:
    """Validate roof area"""
    return 1.0 <= area_m2 <= 10000.0  # Reasonable range in m²

def validate_inclination(inclination: float) -> bool:
    """Validate roof inclination"""
    return 0.0 <= inclination <= 90.0  # Degrees

def validate_orientation(orientation: str) -> bool:
    """Validate roof orientation"""
    valid_orientations = [
        'nord', 'nord-est', 'est', 'sud-est', 
        'sud', 'sud-ouest', 'ouest', 'nord-ouest'
    ]
    return orientation.lower() in valid_orientations

def validate_energy_consumption(consumption_kwh: float) -> bool:
    """Validate annual energy consumption"""
    return 100.0 <= consumption_kwh <= 100000.0  # Reasonable range

class ProjectValidator(BaseModel):
    """Validator for solar project data"""
    
    power_kwc: float
    roof_area_m2: float
    inclination: float
    orientation: str
    annual_consumption: float
    
    @validator('power_kwc')
    def validate_power(cls, v):
        if not validate_power_range(v):
            raise ValueError('Power must be between 0.1 and 1000 kWc')
        return v
    
    @validator('roof_area_m2')
    def validate_area(cls, v):
        if not validate_roof_area(v):
            raise ValueError('Roof area must be between 1 and 10000 m²')
        return v
    
    @validator('inclination')
    def validate_incl(cls, v):
        if not validate_inclination(v):
            raise ValueError('Inclination must be between 0 and 90 degrees')
        return v
    
    @validator('orientation')
    def validate_orient(cls, v):
        if not validate_orientation(v):
            raise ValueError('Invalid orientation')
        return v
    
    @validator('annual_consumption')
    def validate_consumption(cls, v):
        if not validate_energy_consumption(v):
            raise ValueError('Consumption must be between 100 and 100000 kWh/year')
        return v

def sanitize_user_input(user_input: str) -> str:
    """Sanitize user input to prevent injection attacks"""
    if not user_input:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\';\\]', '', user_input)
    
    # Limit length
    sanitized = sanitized[:1000]
    
    return sanitized.strip()

def validate_file_upload(filename: str, content_type: str, file_size: int) -> Dict[str, Any]:
    """Validate file upload parameters"""
    result = {
        'valid': True,
        'errors': []
    }
    
    # Check file size (max 10MB)
    if file_size > 10 * 1024 * 1024:
        result['valid'] = False
        result['errors'].append('File too large (max 10MB)')
    
    # Check file extension
    allowed_extensions = ['.pdf', '.docx', '.txt', '.md', '.xlsx', '.json', '.csv', '.xml', '.html', '.htm']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        result['valid'] = False
        result['errors'].append(f'File type not allowed: {filename}')
    
    # Check content type (plus permissif)
    allowed_types = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/markdown',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv',
        'application/msword',
        'application/vnd.ms-excel',
        'application/json',
        'text/html',
        'text/xml',
        'application/xml',
        'application/octet-stream'  # Pour les fichiers binaires génériques
    ]
    
    # Si le content_type n'est pas dans la liste, on vérifie l'extension
    if content_type not in allowed_types:
        # Vérifier si c'est un type de texte générique ou JSON
        if (not content_type.startswith('text/') and 
            not content_type.startswith('application/json') and 
            content_type != 'application/octet-stream'):
            result['valid'] = False
            result['errors'].append(f'Content type not allowed: {content_type}')
        else:
            logger.info(f"✅ Content type accepté: {content_type}")
    
    return result

def validate_api_keys() -> Dict[str, bool]:
    """Validate API keys format"""
    from config.settings import settings
    
    results = {}
    
    # Gemini API key validation
    gemini_key = settings.GEMINI_API_KEY
    results['gemini'] = bool(gemini_key and len(gemini_key) > 10 and gemini_key != "your_gemini_api_key_here")
    
    # Tavily API key validation  
    tavily_key = settings.TAVILY_API_KEY
    results['tavily'] = bool(tavily_key and len(tavily_key) > 10 and tavily_key != "your_tavily_api_key_here")
    
    return results