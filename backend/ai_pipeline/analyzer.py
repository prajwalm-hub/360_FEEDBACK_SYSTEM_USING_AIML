"""
Comprehensive NLP Analyzer
Integrates language detection, translation, sentiment analysis, and entity extraction
Specialized for Indian regional languages and Government of India content
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NLPAnalyzer:
    """
    Main NLP pipeline orchestrator for multilingual Indian news analysis
    Combines multiple AI models for comprehensive text understanding
    """
    
    def __init__(
        self,
        use_indic_models: bool = True,
        use_translation: bool = True,
        use_gpu: bool = False
    ):
        """
        Initialize NLP analyzer with required components
        
        Args:
            use_indic_models: Use Indian language-specific models (IndicBERT, MuRIL)
            use_translation: Enable IndicTrans2 translation
            use_gpu: Use GPU acceleration if available
        """
        self.use_indic_models = use_indic_models
        self.use_translation = use_translation
        self.use_gpu = use_gpu
        
        # Lazy loading of components
        self._language_detector = None
        self._sentiment_analyzer = None
        self._translator = None
        self._entity_extractor = None
        
        logger.info(
            f"NLP Analyzer initialized "
            f"(Indic models: {use_indic_models}, Translation: {use_translation}, GPU: {use_gpu})"
        )
    
    @property
    def language_detector(self):
        """Lazy load language detector"""
        if self._language_detector is None:
            from .language_detector import LanguageDetector
            self._language_detector = LanguageDetector()
        return self._language_detector
    
    @property
    def sentiment_analyzer(self):
        """Lazy load sentiment analyzer"""
        if self._sentiment_analyzer is None:
            from .sentiment_analyzer import SentimentAnalyzer
            self._sentiment_analyzer = SentimentAnalyzer(
                use_indic_models=self.use_indic_models,
                use_gpu=self.use_gpu
            )
        return self._sentiment_analyzer
    
    @property
    def translator(self):
        """Lazy load translator"""
        if self._translator is None and self.use_translation:
            from .translator import IndianLanguageTranslator
            self._translator = IndianLanguageTranslator(use_gpu=self.use_gpu)
        return self._translator
    
    @property
    def entity_extractor(self):
        """Lazy load entity extractor"""
        if self._entity_extractor is None:
            from .entity_extractor import EntityExtractor
            self._entity_extractor = EntityExtractor(use_gpu=self.use_gpu)
        return self._entity_extractor
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language and script of text
        
        Args:
            text: Input text
            
        Returns:
            Dict with language code, script, confidence
        """
        try:
            return self.language_detector.detect(text)
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {'code': 'unknown', 'script': 'unknown', 'confidence': 0.0}
    
    def translate_to_english(self, text: str, source_lang: str) -> Optional[str]:
        """
        Translate Indian language text to English
        
        Args:
            text: Text to translate
            source_lang: Source language code (hi, kn, ta, etc.)
            
        Returns:
            Translated English text or None
        """
        if not self.use_translation or not self.translator:
            return None
        
        try:
            return self.translator.translate(text, source_lang, 'en')
        except Exception as e:
            logger.error(f"Translation failed ({source_lang} -> en): {e}")
            return None
    
    def analyze_sentiment(
        self, 
        text: str, 
        language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of text
        Uses language-specific models when available
        
        Args:
            text: Text to analyze
            language: Language code
            
        Returns:
            Dict with sentiment label and score
        """
        try:
            return self.sentiment_analyzer.analyze(text, language)
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {'label': 'neutral', 'score': 0.0, 'scores': {}}
    
    def extract_entities(
        self, 
        text: str,
        language: str = 'en'
    ) -> List[Dict[str, Any]]:
        """
        Extract named entities from text
        
        Args:
            text: Text to analyze
            language: Language code
            
        Returns:
            List of entity dictionaries
        """
        try:
            return self.entity_extractor.extract(text, language)
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    def analyze_article(
        self, 
        article: Dict[str, Any],
        extract_entities: bool = True
    ) -> Dict[str, Any]:
        """
        Complete NLP analysis pipeline for a news article
        
        Args:
            article: Article dictionary with title, content, etc.
            extract_entities: Whether to extract named entities
            
        Returns:
            Enhanced article with NLP results
        """
        title = article.get('title', '')
        content = article.get('content', '') or article.get('summary', '')
        declared_language = article.get('language', 'en')
        
        full_text = f"{title}\n\n{content}"
        
        if not full_text.strip():
            logger.warning("Empty article text for NLP analysis")
            return article
        
        # 1. Detect language and script
        lang_result = self.detect_language(full_text)
        detected_lang = lang_result.get('code', declared_language)
        detected_script = lang_result.get('script', '')
        lang_confidence = lang_result.get('confidence', 0.0)
        
        article['detected_language'] = detected_lang
        article['detected_script'] = detected_script
        article['language_confidence'] = lang_confidence
        
        # Use detected language if different and confidence is high
        analysis_lang = detected_lang if lang_confidence > 0.85 else declared_language
        
        # 2. Translate to English if needed (HTML will be cleaned in translate_to_english)
        text_for_analysis = full_text
        if analysis_lang != 'en' and self.use_translation:
            translated = self.translate_to_english(full_text, analysis_lang)
            if translated:
                article['translated_title'] = self.translate_to_english(title, analysis_lang)
                article['translated_summary'] = self.translate_to_english(
                    content[:500], analysis_lang
                )
                text_for_analysis = translated
                logger.info(f"Translated {analysis_lang} article to English")
        
        # 3. Sentiment analysis (on original or translated text)
        sentiment_result = self.analyze_sentiment(text_for_analysis, analysis_lang)
        article['sentiment_label'] = sentiment_result.get('label', 'neutral')
        article['sentiment_score'] = sentiment_result.get('score', 0.0)
        article['sentiment_scores'] = sentiment_result.get('scores', {})
        
        # 3.5. PIB Alert System - Check for negative sentiment
        try:
            from app.config import settings
            from app.pib_alerts import send_pib_alert
            
            # Trigger alert if negative sentiment detected with high confidence
            if (settings.ALERT_ENABLED and 
                article['sentiment_label'] == 'negative' and 
                article['sentiment_score'] >= settings.ALERT_NEGATIVE_THRESHOLD):
                
                # Get article details for alert
                article_id = article.get('id', '')
                article_title = article.get('title', 'Untitled')
                article_summary = article.get('summary', '') or article.get('content', '')[:500]
                article_link = article.get('url', '')
                
                # Send PIB alert (runs in background)
                if article_id:  # Only send if article has been saved with an ID
                    logger.info(
                        f"🚨 Negative news detected! Triggering PIB alert for: {article_title[:50]}... "
                        f"(score: {article['sentiment_score']:.2f})"
                    )
                    send_pib_alert(
                        article_title=article_title,
                        article_summary=article_summary,
                        article_link=article_link,
                        language=analysis_lang,
                        sentiment_score=article['sentiment_score'],
                        article_id=article_id,
                    )
        except Exception as e:
            logger.exception(f"Failed to send PIB alert: {e}")
        
        # 4. Entity extraction (optional, more resource-intensive)
        if extract_entities:
            entities = self.extract_entities(text_for_analysis, analysis_lang)
            article['entities'] = entities
            
            # Extract entity types for easier filtering
            article['entity_types'] = list(set(e.get('type', '') for e in entities))
        
        # 5. Government relevance classification (using existing filters)
        try:
            from app.goi_filter import classify_goi_relevance
            goi_result = classify_goi_relevance(full_text, analysis_lang)
            article['is_goi'] = goi_result.get('is_goi', False)
            article['relevance_score'] = goi_result.get('score', 0.0)
            article['goi_ministries'] = goi_result.get('ministries', [])
            article['goi_schemes'] = goi_result.get('schemes', [])
            article['goi_matched_terms'] = goi_result.get('matched_terms', [])
        except Exception as e:
            logger.debug(f"GoI relevance classification unavailable: {e}")
        
        article['nlp_analyzed_at'] = datetime.utcnow()
        
        logger.info(
            f"NLP analysis complete: {title[:50]}... "
            f"(lang: {detected_lang}, sentiment: {article['sentiment_label']})"
        )
        
        return article
    
    def batch_analyze(
        self, 
        articles: List[Dict[str, Any]],
        batch_size: int = 16,
        extract_entities: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple articles in batches
        
        Args:
            articles: List of article dictionaries
            batch_size: Number of articles to process at once
            extract_entities: Whether to extract entities (slower)
            
        Returns:
            List of analyzed articles
        """
        analyzed = []
        total = len(articles)
        
        logger.info(f"Starting batch NLP analysis for {total} articles")
        
        for i in range(0, total, batch_size):
            batch = articles[i:i + batch_size]
            
            for article in batch:
                try:
                    analyzed_article = self.analyze_article(
                        article, 
                        extract_entities=extract_entities
                    )
                    analyzed.append(analyzed_article)
                except Exception as e:
                    logger.error(f"Failed to analyze article: {e}")
                    analyzed.append(article)  # Add original
            
            logger.info(f"Processed {min(i + batch_size, total)}/{total} articles")
        
        logger.info(f"Batch analysis complete: {len(analyzed)} articles")
        return analyzed
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages
        
        Returns:
            List of language codes
        """
        return [
            'en', 'hi', 'kn', 'ta', 'te', 'ml', 'bn', 
            'gu', 'pa', 'mr', 'or', 'as', 'ur'
        ]
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get analyzer statistics
        
        Returns:
            Dictionary with stats
        """
        return {
            'supported_languages': len(self.get_supported_languages()),
            'languages': self.get_supported_languages(),
            'translation_enabled': self.use_translation,
            'indic_models_enabled': self.use_indic_models,
            'gpu_enabled': self.use_gpu,
            'components': {
                'language_detector': self._language_detector is not None,
                'sentiment_analyzer': self._sentiment_analyzer is not None,
                'translator': self._translator is not None,
                'entity_extractor': self._entity_extractor is not None
            }
        }


if __name__ == '__main__':
    # Test NLP analyzer
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    analyzer = NLPAnalyzer(
        use_indic_models=True,
        use_translation=False,  # Disable for quick test
        use_gpu=False
    )
    
    test_article = {
        'title': 'Government announces new education policy',
        'content': 'The government has announced a comprehensive new education policy focusing on digital literacy and skill development.',
        'language': 'en'
    }
    
    result = analyzer.analyze_article(test_article, extract_entities=False)
    
    print(f"\nAnalysis Results:")
    print(f"Language: {result.get('detected_language')}")
    print(f"Sentiment: {result.get('sentiment_label')} ({result.get('sentiment_score'):.2f})")
    print(f"GoI Relevant: {result.get('is_goi', False)}")
