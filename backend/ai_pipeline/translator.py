"""
Translation Module
Uses MultilingualProcessor for IndicTrans2 and Google Translate fallback
"""

import logging
from typing import Optional
import sys
from pathlib import Path

# Add app directory to path to import language_processor
sys.path.insert(0, str(Path(__file__).parent.parent / 'app'))

logger = logging.getLogger(__name__)


class IndianLanguageTranslator:
    """
    Indian language translator using MultilingualProcessor
    Supports IndicTrans2 with Google Translate fallback
    """
    
    def __init__(self, use_gpu: bool = False):
        """Initialize translator"""
        self.use_gpu = use_gpu
        self._processor = None
        logger.info("IndianLanguageTranslator initialized")
    
    @property
    def processor(self):
        """Lazy load MultilingualProcessor"""
        if self._processor is None:
            try:
                from language_processor import MultilingualProcessor
                self._processor = MultilingualProcessor()
                logger.info("MultilingualProcessor loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load MultilingualProcessor: {e}")
                self._processor = False
        return self._processor if self._processor is not False else None
    
    def translate(
        self, 
        text: str, 
        source_lang: str, 
        target_lang: str = 'en'
    ) -> Optional[str]:
        """
        Translate text using MultilingualProcessor
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
            
        Returns:
            Translated text or None
        """
        if not text or source_lang == target_lang:
            return text
        
        if not self.processor:
            logger.warning("MultilingualProcessor not available, translation skipped")
            return None
        
        try:
            translated = self.processor.translate_to_english(text, source_lang)
            if translated:
                logger.debug(f"Translation successful: {source_lang} -> {target_lang}")
                return translated
            else:
                logger.warning(f"Translation returned None for {source_lang} -> {target_lang}")
                return None
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return None


class EntityExtractor:
    """
    Stub for entity extraction
    Real implementation would use XLM-RoBERTa or IndicNER
    """
    
    def __init__(self, use_gpu: bool = False):
        """Initialize entity extractor"""
        self.use_gpu = use_gpu
        logger.warning("Entity extraction stub initialized")
    
    def extract(self, text: str, language: str = 'en') -> list:
        """
        Extract entities (stub implementation)
        
        Args:
            text: Text to analyze
            language: Language code
            
        Returns:
            List of entities
        """
        logger.debug(f"Entity extraction stub for {language}")
        return []  # Return empty list for now
