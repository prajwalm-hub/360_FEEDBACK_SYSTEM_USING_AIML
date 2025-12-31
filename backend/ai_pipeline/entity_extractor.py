"""
Entity Extraction Module Stub
"""

import logging
logger = logging.getLogger(__name__)

class EntityExtractor:
    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu
        logger.warning("Entity extraction stub initialized")
    
    def extract(self, text: str, language: str = 'en') -> list:
        return []
