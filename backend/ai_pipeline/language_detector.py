"""
Language Detection Module
Detects language and script from text using multiple strategies
"""

import logging
from typing import Dict, Any

import langdetect
from langdetect import detect, detect_langs

logger = logging.getLogger(__name__)


class LanguageDetector:
    """
    Multi-strategy language detection for Indian regional languages
    """
    
    # ISO 639-1 language codes to script mapping
    LANGUAGE_SCRIPTS = {
        'en': 'Latin',
        'hi': 'Devanagari',
        'kn': 'Kannada',
        'ta': 'Tamil',
        'te': 'Telugu',
        'ml': 'Malayalam',
        'bn': 'Bengali',
        'gu': 'Gujarati',
        'pa': 'Gurmukhi',
        'mr': 'Devanagari',
        'or': 'Odia',
        'as': 'Bengali',
        'ur': 'Arabic'
    }
    
    def __init__(self):
        """Initialize language detector"""
        # Set seed for consistent results
        langdetect.DetectorFactory.seed = 0
    
    def detect_script(self, text: str) -> str:
        """
        Detect script/writing system from text
        
        Args:
            text: Input text
            
        Returns:
            Script name
        """
        if not text:
            return 'unknown'
        
        # Unicode ranges for Indian scripts
        scripts_ranges = {
            'Devanagari': (0x0900, 0x097F),
            'Bengali': (0x0980, 0x09FF),
            'Gurmukhi': (0x0A00, 0x0A7F),
            'Gujarati': (0x0A80, 0x0AFF),
            'Odia': (0x0B00, 0x0B7F),
            'Tamil': (0x0B80, 0x0BFF),
            'Telugu': (0x0C00, 0x0C7F),
            'Kannada': (0x0C80, 0x0CFF),
            'Malayalam': (0x0D00, 0x0D7F),
            'Arabic': (0x0600, 0x06FF),
            'Latin': (0x0041, 0x007A)
        }
        
        script_counts = {script: 0 for script in scripts_ranges}
        
        for char in text:
            code_point = ord(char)
            for script, (start, end) in scripts_ranges.items():
                if start <= code_point <= end:
                    script_counts[script] += 1
                    break
        
        # Return script with highest count
        if max(script_counts.values()) > 0:
            return max(script_counts, key=script_counts.get)
        
        return 'unknown'
    
    def detect(self, text: str) -> Dict[str, Any]:
        """
        Detect language and script from text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with language code, script, and confidence
        """
        if not text or len(text.strip()) < 10:
            return {
                'code': 'unknown',
                'script': 'unknown',
                'confidence': 0.0
            }
        
        try:
            # Detect language using langdetect
            lang_probs = detect_langs(text)
            
            if lang_probs:
                top_lang = lang_probs[0]
                lang_code = top_lang.lang
                confidence = top_lang.prob
                
                # Get script
                script = self.LANGUAGE_SCRIPTS.get(lang_code)
                
                # If script not in mapping, detect from text
                if not script:
                    script = self.detect_script(text)
                
                return {
                    'code': lang_code,
                    'script': script,
                    'confidence': confidence,
                    'all_probabilities': [
                        {'code': lp.lang, 'prob': lp.prob} 
                        for lp in lang_probs[:3]
                    ]
                }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
        
        # Fallback: try to detect script only
        script = self.detect_script(text)
        return {
            'code': 'unknown',
            'script': script,
            'confidence': 0.0
        }


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    detector = LanguageDetector()
    
    # Test with various languages
    tests = [
        ("This is English text", "en"),
        ("यह हिंदी पाठ है", "hi"),
        ("ಇದು ಕನ್ನಡ ಪಠ್ಯ", "kn"),
        ("இது தமிழ் உரை", "ta"),
    ]
    
    for text, expected in tests:
        result = detector.detect(text)
        print(f"\nText: {text}")
        print(f"Detected: {result['code']} (expected: {expected})")
        print(f"Script: {result['script']}")
        print(f"Confidence: {result['confidence']:.2f}")
