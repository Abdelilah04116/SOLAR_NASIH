"""
Module complet des agents Solar Nasih SMA
Tous les 11 agents spécialisés sont maintenant implémentés
"""

from .base_agent import BaseAgent
from .task_divider import TaskDividerAgent
from .technical_advisor import TechnicalAdvisorAgent
from .energy_simulator import EnergySimulatorAgent
from .voice_processor import VoiceProcessorAgent
from .multilingual_detector import MultilingualDetectorAgent
from .regulatory_assistant import RegulatoryAssistantAgent
from .educational_agent import EducationalAgent
from .commercial_assistant import CommercialAssistantAgent
from .certification_assistant import CertificationAssistantAgent
from .document_generator import DocumentGeneratorAgent
from .document_indexer import DocumentIndexerAgent

__all__ = [
    'BaseAgent',
    'TaskDividerAgent',
    'TechnicalAdvisorAgent', 
    'EnergySimulatorAgent',
    'VoiceProcessorAgent',
    'MultilingualDetectorAgent',
    'RegulatoryAssistantAgent',
    'EducationalAgent',
    'CommercialAssistantAgent',
    'CertificationAssistantAgent',
    'DocumentGeneratorAgent',
    'DocumentIndexerAgent'
]