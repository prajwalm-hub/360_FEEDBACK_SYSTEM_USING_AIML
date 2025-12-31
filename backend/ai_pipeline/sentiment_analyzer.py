"""
Sentiment Analysis Module
Multi-strategy sentiment analysis for Indian regional languages
Uses XLM-RoBERTa for multilingual support and MuRIL for Indian languages
"""

import logging
from typing import Dict, Any, Optional

import torch
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    pipeline
)

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Multilingual sentiment analyzer with special support for Indian languages
    """
    
    # Supported models
    MODELS = {
        'multilingual': 'cardiffnlp/twitter-xlm-roberta-base-sentiment',
        'indic': 'l3cube-pune/mbert-base-indian-sentiment'
    }
    
    # Indian languages that work better with Indic models
    INDIC_LANGUAGES = {'hi', 'kn', 'ta', 'te', 'ml', 'bn', 'gu', 'pa', 'mr', 'or', 'as'}
    
    def __init__(self, use_indic_models: bool = True, use_gpu: bool = False):
        """
        Initialize sentiment analyzer
        
        Args:
            use_indic_models: Use MuRIL model for Indian languages
            use_gpu: Use GPU if available
        """
        self.use_indic_models = use_indic_models
        self.device = 0 if use_gpu and torch.cuda.is_available() else -1
        
        # Lazy loading
        self._multilingual_pipeline = None
        self._indic_pipeline = None
        
        logger.info(
            f"Sentiment analyzer initialized "
            f"(Indic: {use_indic_models}, GPU: {use_gpu}, Device: {self.device})"
        )
    
    @property
    def multilingual_pipeline(self):
        """Lazy load multilingual sentiment pipeline"""
        if self._multilingual_pipeline is None:
            try:
                logger.info(f"Loading multilingual sentiment model...")
                self._multilingual_pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.MODELS['multilingual'],
                    device=self.device,
                    top_k=None
                )
                logger.info("Multilingual model loaded")
            except Exception as e:
                logger.error(f"Failed to load multilingual model: {e}")
                self._multilingual_pipeline = None
        return self._multilingual_pipeline
    
    @property
    def indic_pipeline(self):
        """Lazy load Indic sentiment pipeline"""
        if self._indic_pipeline is None and self.use_indic_models:
            try:
                logger.info(f"Loading Indic sentiment model...")
                self._indic_pipeline = pipeline(
                    "sentiment-analysis",
                    model=self.MODELS['indic'],
                    device=self.device,
                    top_k=None
                )
                logger.info("Indic model loaded")
            except Exception as e:
                logger.error(f"Failed to load Indic model: {e}")
                self._indic_pipeline = None
        return self._indic_pipeline
    
    def _normalize_label(self, label: str) -> str:
        """
        Normalize sentiment label to standard format
        
        Args:
            label: Raw model output label
            
        Returns:
            Normalized label (positive, negative, neutral)
        """
        label_lower = label.lower()
        
        if 'pos' in label_lower or label_lower == 'label_2':
            return 'positive'
        elif 'neg' in label_lower or label_lower == 'label_0':
            return 'negative'
        else:
            return 'neutral'
    
    def analyze(self, text: str, language: str = 'en') -> Dict[str, Any]:
        """
        Analyze sentiment of text with MANDATORY fallback (always returns a result)
        
        Args:
            text: Text to analyze
            language: Language code
            
        Returns:
            Dictionary with sentiment label, score, and detailed scores (NEVER None)
        """
        if not text or len(text.strip()) < 5:
            return {
                'label': 'neutral',
                'score': 0.5,
                'scores': {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
            }
        
        # Truncate very long texts
        if len(text) > 512:
            text = text[:512]
        
        # Try Method 1: Indic model for Indian languages
        use_indic = (
            self.use_indic_models and 
            language in self.INDIC_LANGUAGES and
            self.indic_pipeline is not None
        )
        
        if use_indic:
            try:
                logger.debug(f"Trying Indic model for {language}")
                results = self.indic_pipeline(text)
                if results and results[0]:
                    scores_dict = {}
                    for item in results[0]:
                        normalized_label = self._normalize_label(item['label'])
                        scores_dict[normalized_label] = item['score']
                    
                    # Ensure all labels present
                    for label in ['positive', 'negative', 'neutral']:
                        if label not in scores_dict:
                            scores_dict[label] = 0.0
                    
                    primary_label = max(scores_dict, key=scores_dict.get)
                    primary_score = scores_dict[primary_label]
                    
                    logger.info(f"✓ Indic sentiment analysis successful for {language}")
                    return {
                        'label': primary_label,
                        'score': primary_score,
                        'scores': scores_dict
                    }
            except Exception as e:
                logger.warning(f"Indic model failed for {language}: {str(e)[:100]}")
        
        # Try Method 2: Multilingual model (XLM-RoBERTa)
        try:
            logger.debug(f"Trying multilingual model for {language}")
            if self.multilingual_pipeline is not None:
                results = self.multilingual_pipeline(text)
                if results and results[0]:
                    scores_dict = {}
                    for item in results[0]:
                        normalized_label = self._normalize_label(item['label'])
                        scores_dict[normalized_label] = item['score']
                    
                    # Ensure all labels present
                    for label in ['positive', 'negative', 'neutral']:
                        if label not in scores_dict:
                            scores_dict[label] = 0.0
                    
                    primary_label = max(scores_dict, key=scores_dict.get)
                    primary_score = scores_dict[primary_label]
                    
                    logger.info(f"✓ Multilingual sentiment analysis successful for {language}")
                    return {
                        'label': primary_label,
                        'score': primary_score,
                        'scores': scores_dict
                    }
        except Exception as e:
            logger.warning(f"Multilingual model failed for {language}: {str(e)[:100]}")
        
        # MANDATORY Fallback: Keyword-based sentiment (ALWAYS returns a result)
        logger.info(f"✓ Using keyword-based sentiment fallback for {language}")
        return self._fallback_sentiment(text)
    
    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Simple keyword-based fallback sentiment analysis
        
        Args:
            text: Text to analyze
            
        Returns:
            Basic sentiment result
        """
        text_lower = text.lower()
        
        # Simple keyword lists
        positive_words = [
            'good', 'great', 'excellent', 'positive', 'success', 'achievement',
            'improvement', 'growth', 'progress', 'benefit', 'advantage'
        ]
        negative_words = [
            'bad', 'poor', 'negative', 'failure', 'problem', 'crisis',
            'decline', 'concern', 'issue', 'risk', 'threat'
        ]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            label = 'positive'
            score = min(0.5 + (pos_count * 0.1), 0.9)
        elif neg_count > pos_count:
            label = 'negative'
            score = min(0.5 + (neg_count * 0.1), 0.9)
        else:
            label = 'neutral'
            score = 0.6
        
        return {
            'label': label,
            'score': score,
            'scores': {
                'positive': pos_count * 0.1,
                'negative': neg_count * 0.1,
                'neutral': 0.6
            }
        }
    
    def batch_analyze(
        self, 
        texts: list[str],
        language: str = 'en'
    ) -> list[Dict[str, Any]]:
        """
        Analyze sentiment for multiple texts
        
        Args:
            texts: List of texts
            language: Language code
            
        Returns:
            List of sentiment results
        """
        return [self.analyze(text, language) for text in texts]


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    analyzer = SentimentAnalyzer(use_indic_models=False, use_gpu=False)
    
    tests = [
        ("This is a great achievement for the government", "en"),
        ("The policy has failed to address key concerns", "en"),
        ("The minister announced new regulations today", "en"),
    ]
    
    for text, lang in tests:
        result = analyzer.analyze(text, lang)
        print(f"\nText: {text}")
        print(f"Sentiment: {result['label']} (score: {result['score']:.2f})")
        print(f"Scores: {result['scores']}")
