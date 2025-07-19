import re
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """Clean and normalize text input"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep accents
    text = re.sub(r'[^\w\sàáâäçéèêëïîôöùûüÿ\-\.]', '', text)
    
    return text.strip()

def extract_keywords(text: str) -> List[str]:
    """Extract keywords from text"""
    # Simple keyword extraction
    words = text.lower().split()
    
    # Filter common words
    stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'et', 'ou', 'mais', 'pour', 'avec'}
    
    keywords = [word for word in words if len(word) > 3 and word not in stop_words]
    
    return keywords[:10]  # Limit to 10 keywords

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"{amount:,.2f} €".replace(',', ' ')

def calculate_confidence_score(indicators: Dict[str, Any]) -> float:
    """Calculate confidence score based on various indicators"""
    score = 0.5  # Base score
    
    # Adjust based on indicators
    if indicators.get('keyword_matches', 0) > 2:
        score += 0.2
    
    if indicators.get('has_numbers', False):
        score += 0.1
    
    if indicators.get('response_length', 0) > 100:
        score += 0.1
    
    # Cap at 1.0
    return min(score, 1.0)