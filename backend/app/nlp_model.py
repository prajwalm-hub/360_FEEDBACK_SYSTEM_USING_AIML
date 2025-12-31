from __future__ import annotations
import logging
from typing import Dict, List, Any, Optional
from functools import lru_cache
import hashlib

from .config import settings
from .sentiment_adjuster import get_sentiment_adjuster
from .cache import get_cache

logger = logging.getLogger(__name__)

# Initialize cache
nlp_cache = get_cache(redis_url=None)  # Set redis_url from env if available


class NLPModel:
    def __init__(self):
        self.enabled = settings.NLP_ENABLED
        self._sentiment_pipe = None
        self._english_sentiment_pipe = None  # Cardiff RoBERTa for English
        self._muril_sentiment_pipe = None  # IndicBERT for Indian languages
        self._zero_shot_pipe = None
        self._ner_pipe = None
        self._spacy_nlp = None
        self._phrase_matcher = None
        self._gazetteers = None
        self._device = -1  # CPU by default

    def _ensure_loaded(self):
        if not self.enabled:
            return
            
        # Determine device
        if settings.USE_GPU:
            try:
                import torch
                self._device = 0 if torch.cuda.is_available() else -1
                logger.info(f"Using device: {'GPU' if self._device == 0 else 'CPU'}")
            except ImportError:
                logger.warning("torch not available, using CPU")
                self._device = -1
        
        # Load sentiment model
        if self._sentiment_pipe is None:
            from transformers import pipeline  # type: ignore
            try:
                logger.info(f"Loading sentiment model: {settings.SENTIMENT_MODEL}")
                self._sentiment_pipe = pipeline(
                    "sentiment-analysis",
                    model=settings.SENTIMENT_MODEL,
                    device=self._device,
                    max_length=settings.MAX_LENGTH,
                    truncation=True,
                )
                logger.info("Sentiment model loaded successfully")
            except Exception as e:
                logger.exception("Failed to load sentiment model: %s", e)
                self.enabled = False
                return
        
        # Load zero-shot model (only if enabled)
        if self._zero_shot_pipe is None and settings.ZERO_SHOT_ENABLED:
            from transformers import pipeline  # type: ignore
            try:
                logger.info(f"Loading zero-shot model: {settings.ZERO_SHOT_MODEL}")
                self._zero_shot_pipe = pipeline(
                    "zero-shot-classification",
                    model=settings.ZERO_SHOT_MODEL,
                    device=self._device,
                    max_length=settings.MAX_LENGTH,
                    truncation=True,
                    
                )
                logger.info("Zero-shot model loaded successfully")
            except Exception as e:
                logger.exception("Failed to load zero-shot model: %s", e)
        
        # Load NER model
        if self._ner_pipe is None and settings.NER_ENABLED:
            from transformers import pipeline  # type: ignore
            try:
                logger.info(f"Loading NER model: {settings.NER_MODEL}")
                self._ner_pipe = pipeline(
                    "ner",
                    model=settings.NER_MODEL,
                    device=self._device,
                    aggregation_strategy="simple",
                    
                )
                logger.info("NER model loaded successfully")
            except Exception as e:
                logger.exception("Failed to load NER model: %s", e)
        
        # Load spaCy and gazetteers (optional - only if installed)
        if self._spacy_nlp is None:
            try:
                import spacy  # type: ignore
                from spacy.matcher import PhraseMatcher  # type: ignore
                from .resources import gazetteers

                logger.info("Loading spaCy model: en_core_web_sm")
                self._spacy_nlp = spacy.load("en_core_web_sm")
                self._phrase_matcher = PhraseMatcher(self._spacy_nlp.vocab, attr="LOWER")
                self._gazetteers = gazetteers

                # Add gazetteer patterns
                def add_list(name: str, items: List[str]):
                    patterns = [self._spacy_nlp.make_doc(x) for x in items]
                    self._phrase_matcher.add(name, patterns)

                add_list("STATE", gazetteers.STATES_UTS)
                add_list("MINISTRY", gazetteers.MINISTRIES)
                add_list("SCHEME", gazetteers.SCHEMES)
                add_list("OFFICIAL", gazetteers.OFFICIALS)
                add_list("CITY", gazetteers.MAJOR_CITIES)
                
                logger.info("spaCy and gazetteers loaded successfully")
            except ImportError:
                logger.warning("spaCy not installed - entity extraction will be limited")
                self._spacy_nlp = False  # Mark as unavailable
            except Exception as e:
                logger.warning("Failed to init spaCy/gazetteers: %s - continuing without it", e)
                self._spacy_nlp = False
    
    def _ensure_muril_sentiment(self):
        """Load IndicBERT-based sentiment model for Indian languages (lazy loading)."""
        if self._muril_sentiment_pipe is not None:
            return
        
        # Check if IndicBERT sentiment is enabled
        if not settings.INDICBERT_SENTIMENT_ENABLED:
            logger.info("IndicBERT sentiment is disabled in config")
            self._muril_sentiment_pipe = False
            return
        
        try:
            from transformers import pipeline
            import torch
            
            # Use IndicBERT fine-tuned for sentiment
            indicbert_model = settings.INDICBERT_FINETUNED_MODEL
            
            logger.info(f"Loading IndicBERT sentiment model: {indicbert_model}")
            self._muril_sentiment_pipe = pipeline(
                "sentiment-analysis",
                model=indicbert_model,
                device=self._device,
                max_length=settings.MAX_LENGTH,
                truncation=True,
                use_fast=False
            )
            logger.info("IndicBERT sentiment model loaded successfully")
        except Exception as e:
            logger.exception("Failed to load IndicBERT sentiment model: %s", e)
            # Set to False to prevent retry
            self._muril_sentiment_pipe = False
    
    def _ensure_english_sentiment(self):
        """Load Cardiff RoBERTa sentiment model for English (lazy loading)."""
        if self._english_sentiment_pipe is not None:
            return
        
        try:
            from transformers import pipeline
            
            # Use Cardiff RoBERTa for English sentiment
            english_model = settings.ENGLISH_SENTIMENT_MODEL
            
            logger.info(f"Loading English sentiment model: {english_model}")
            self._english_sentiment_pipe = pipeline(
                "sentiment-analysis",
                model=english_model,
                device=self._device,
                max_length=settings.MAX_LENGTH,
                truncation=True,
                
            )
            logger.info("English sentiment model (Cardiff RoBERTa) loaded successfully")
        except Exception as e:
            logger.exception("Failed to load English sentiment model: %s", e)
            # Set to False to prevent retry
            self._english_sentiment_pipe = False
    
    def _normalize_sentiment_output(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize sentiment output from different models to consistent format.
        Handles 5-star ratings (1-5 stars) and converts to positive/negative/neutral.
        
        Args:
            raw_output: Raw model output with 'label' and 'score'
        
        Returns:
            Normalized output with 'label' (positive/negative/neutral) and 'score'
        """
        label = raw_output.get('label', '')
        score = raw_output.get('score', 0.5)
        
        # Check if it's a star rating (1-5 stars)
        if 'star' in label.lower():
            # Extract star number
            if '5 star' in label.lower() or '4 star' in label.lower():
                return {'label': 'positive', 'score': score}
            elif '1 star' in label.lower() or '2 star' in label.lower():
                return {'label': 'negative', 'score': score}
            else:  # 3 stars
                return {'label': 'neutral', 'score': score}
        
        # Already in correct format
        return raw_output
    
    def _convert_to_polarity(self, label: str, score: float) -> float:
        """
        Convert sentiment label and confidence score to polarity scale [-1, +1].
        
        Args:
            label: Sentiment label (positive, negative, neutral)
            score: Model confidence score (0-1)
        
        Returns:
            Polarity score from -1 (strongly negative) to +1 (strongly positive)
        """
        label_lower = label.lower()
        
        if label_lower in ['positive', 'pos']:
            # Positive: score ranges from 0 to +1
            # If score=1.0 (100% confident) → polarity=+1.0
            # If score=0.5 (50% confident) → polarity=+0.5
            return score
        elif label_lower in ['negative', 'neg']:
            # Negative: score ranges from 0 to -1
            # If score=1.0 (100% confident) → polarity=-1.0
            # If score=0.5 (50% confident) → polarity=-0.5
            return -score
        else:  # neutral
            # Neutral: close to 0
            # Map neutral confidence to a small range around 0
            return 0.0
    
    def analyze(self, text: str, language: Optional[str] = None) -> Dict[str, Any]:
        """
        Run sentiment, topic classification, and entity extraction.
        
        Args:
            text: Text to analyze
            language: Language code (hi, ta, te, etc.) for language-specific models
        """
        result: Dict[str, Any] = {
            "sentiment": None,
            "topics": [],
            "entities": [],
        }
        if not text:
            return result

        # PERFORMANCE: Check cache first
        cached_sentiment = nlp_cache.get_sentiment(text)
        if cached_sentiment:
            logger.info("[CACHE HIT] Using cached sentiment analysis")
            result["sentiment"] = cached_sentiment
            # Still need to do topics/entities if enabled
            # But skip expensive sentiment analysis
            self._ensure_loaded()
        else:
            self._ensure_loaded()

        # ========================================
        # HYBRID SENTIMENT ANALYSIS
        # ========================================
        # English -> Cardiff RoBERTa (best for English news)
        # Indian languages (hi, kn, ta, te, bn, gu, mr, pa, ml, or, ur) -> IndicBERT
        # Other/Unknown -> XLM-RoBERTa (fallback)
        
        indian_languages = ['hi', 'kn', 'ta', 'te', 'bn', 'gu', 'mr', 'pa', 'ml', 'or', 'ur', 'as']
        use_english_model = language and language == 'en'
        use_indicbert = language and language in indian_languages
        
        raw_sentiment = None
        
        # Route 1: English articles -> Cardiff RoBERTa
        if use_english_model:
            self._ensure_english_sentiment()
            if self._english_sentiment_pipe and self._english_sentiment_pipe is not False:
                try:
                    logger.info(f"[SENTIMENT] Using Cardiff RoBERTa for English")
                    logger.debug(f"[SENTIMENT] Input text: {text[:200]}...")
                    out = self._english_sentiment_pipe(text[:settings.MAX_LENGTH])
                    if isinstance(out, list) and out:
                        raw_sentiment = out[0]
                        logger.info(f"[SENTIMENT] Cardiff RoBERTa output: {raw_sentiment}")
                except Exception as e:
                    logger.exception(f"Cardiff RoBERTa sentiment failed: {e}, falling back to XLM-RoBERTa")
                    use_english_model = False
        
        # Route 2: Indian languages -> IndicBERT
        elif use_indicbert:
            self._ensure_muril_sentiment()
            if self._muril_sentiment_pipe and self._muril_sentiment_pipe is not False:
                try:
                    logger.info(f"[SENTIMENT] Using IndicBERT for {language}")
                    logger.debug(f"[SENTIMENT] Input text: {text[:200]}...")
                    out = self._muril_sentiment_pipe(text[:settings.MAX_LENGTH])
                    if isinstance(out, list) and out:
                        raw_sentiment = out[0]
                        logger.info(f"[SENTIMENT] IndicBERT output: {raw_sentiment}")
                except Exception as e:
                    logger.exception(f"IndicBERT sentiment inference failed: {e}, falling back to XLM-RoBERTa")
                    use_indicbert = False
        
        # Route 3: Fallback to multilingual model if specialized models not used/failed
        if raw_sentiment is None and self._sentiment_pipe is not None:
            try:
                logger.info(f"[SENTIMENT] Using multilingual model (fallback) for {language or 'unknown'}")
                logger.debug(f"[SENTIMENT] Input text: {text[:200]}...")
                out = self._sentiment_pipe(text[:settings.MAX_LENGTH])
                if isinstance(out, list) and out:
                    raw_sentiment = out[0]
                    # Convert 5-star rating to positive/negative/neutral if needed
                    raw_sentiment = self._normalize_sentiment_output(raw_sentiment)
                    logger.info(f"[SENTIMENT] Multilingual model output: {raw_sentiment}")
            except Exception as e:
                logger.exception(f"Sentiment inference failed: {e}")
        
        # Apply rule-based sentiment adjuster if enabled
        if raw_sentiment and settings.RULE_BASED_ADJUSTER_ENABLED:
            try:
                adjuster = get_sentiment_adjuster(settings.SENTIMENT_BOOST_THRESHOLD)
                adjustment_result = adjuster.adjust_sentiment(
                    text,
                    raw_sentiment.get('label', 'neutral').lower(),
                    raw_sentiment.get('score', 0.5)
                )
                
                # Convert to polarity scale [-1, +1]
                adjusted_polarity = self._convert_to_polarity(
                    adjustment_result['adjusted_label'],
                    adjustment_result['adjusted_score']
                )
                original_polarity = self._convert_to_polarity(
                    adjustment_result['original_label'],
                    adjustment_result['original_score']
                )
                
                # Update result with adjusted sentiment including polarity
                result["sentiment"] = {
                    'label': adjustment_result['adjusted_label'],
                    'score': adjustment_result['adjusted_score'],
                    'polarity': round(adjusted_polarity, 3),  # -1 to +1 scale
                    'original_label': adjustment_result['original_label'],
                    'original_score': adjustment_result['original_score'],
                    'original_polarity': round(original_polarity, 3),
                    'adjustment_reason': adjustment_result.get('adjustment_reason', ''),
                }
                logger.info(f"[SENTIMENT] Rule-Adjusted: {adjustment_result['original_label']}({adjustment_result['original_score']:.3f}) → {adjustment_result['adjusted_label']}({adjustment_result['adjusted_score']:.3f})")
                logger.debug(f"[SENTIMENT] Full result: {result['sentiment']}")
            except Exception:
                logger.exception("Sentiment adjustment failed, using raw sentiment")
                # Fallback: convert raw sentiment to polarity
                if raw_sentiment:
                    polarity = self._convert_to_polarity(
                        raw_sentiment.get('label', 'neutral'),
                        raw_sentiment.get('score', 0.5)
                    )
                    raw_sentiment['polarity'] = round(polarity, 3)
                result["sentiment"] = raw_sentiment
        else:
            # No adjustment, just convert raw sentiment to polarity
            if raw_sentiment:
                polarity = self._convert_to_polarity(
                    raw_sentiment.get('label', 'neutral'),
                    raw_sentiment.get('score', 0.5)
                )
                raw_sentiment['polarity'] = round(polarity, 3)
                logger.info(f"[SENTIMENT] Final (no adjustment): {raw_sentiment.get('label')}({raw_sentiment.get('score'):.3f}) polarity={polarity:.3f}")
            result["sentiment"] = raw_sentiment
        
        # PERFORMANCE: Cache the sentiment result
        if result["sentiment"] and not cached_sentiment:
            nlp_cache.set_sentiment(text, result["sentiment"])

        # Zero-shot topic classification
        if self._zero_shot_pipe is not None:
            try:
                zs = self._zero_shot_pipe(
                    text[:settings.MAX_LENGTH],
                    candidate_labels=settings.TOPIC_LABELS,
                    multi_label=True,
                )
                labels = zs.get("labels", [])
                scores = zs.get("scores", [])
                # Keep labels with score > 0.35
                topics = [l for l, s in zip(labels, scores) if s >= 0.35]
                result["topics"] = topics[:5]
                logger.debug(f"Topics: {result['topics']}")
            except Exception:
                logger.exception("Zero-shot topic inference failed")

        # Named Entity Recognition via Transformers
        entities_map: Dict[str, Dict[str, Any]] = {}
        
        if self._ner_pipe is not None:
            try:
                ner_results = self._ner_pipe(text[:settings.MAX_LENGTH])
                for ent in ner_results:
                    entity_text = ent.get("word", "")
                    entity_key = entity_text.lower().strip()
                    if entity_key and entity_key not in entities_map:
                        entities_map[entity_key] = {
                            "text": entity_text,
                            "label": ent.get("entity_group", "UNKNOWN"),
                            "start": ent.get("start"),
                            "end": ent.get("end"),
                            "confidence": float(ent.get("score", 0.0)),
                            "type": "transformer_ner",
                        }
                logger.debug(f"Transformer NER found {len(ner_results)} entities")
            except Exception:
                logger.exception("Transformer NER failed")

        # Entities via spaCy (optional)
        if self._spacy_nlp and self._spacy_nlp is not False:
            try:
                doc = self._spacy_nlp(text)
                for ent in doc.ents:
                    entity_key = ent.text.lower().strip()
                    if entity_key and entity_key not in entities_map:
                        entities_map[entity_key] = {
                            "text": ent.text,
                            "label": ent.label_,
                            "start": ent.start_char,
                            "end": ent.end_char,
                            "confidence": 0.9,
                            "type": "spacy_ner",
                        }
                
                # Gazetteer phrase matches
                if self._phrase_matcher is not None:
                    matches = self._phrase_matcher(doc)
                    for mid, start, end in matches:
                        span = doc[start:end]
                        entity_key = span.text.lower().strip()
                        entities_map[entity_key] = {
                            "text": span.text,
                            "label": self._spacy_nlp.vocab.strings[mid],
                            "start": span.start_char,
                            "end": span.end_char,
                            "confidence": 1.0,
                            "type": "gazetteer",
                        }
                logger.debug(f"spaCy/Gazetteer found {len(entities_map)} total entities")
            except Exception:
                logger.exception("spaCy/gazetteer entity extraction failed")

        result["entities"] = list(entities_map.values())
        
        # Normalize regional entity variations (convert regional names to English)
        if language and language != 'en':
            result["entities"] = self._normalize_regional_entities(result["entities"], language)
        
        return result
    
    def analyze_batch(self, texts: List[str], languages: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        PERFORMANCE: Batch analyze multiple texts for 4x speedup
        
        Args:
            texts: List of texts to analyze
            languages: Optional list of language codes (same length as texts)
        
        Returns:
            List of analysis results
        """
        if not texts:
            return []
        
        if languages is None:
            languages = [None] * len(texts)
        
        results = []
        
        # Check cache for all texts first
        cached_results = []
        uncached_indices = []
        uncached_texts = []
        uncached_langs = []
        
        for i, (text, lang) in enumerate(zip(texts, languages)):
            cached = nlp_cache.get_sentiment(text)
            if cached:
                cached_results.append((i, cached))
            else:
                uncached_indices.append(i)
                uncached_texts.append(text)
                uncached_langs.append(lang)
        
        logger.info(f"[BATCH] Cache: {len(cached_results)} hits, {len(uncached_texts)} misses")
        
        # Batch process uncached texts
        batch_sentiments = []
        if uncached_texts:
            self._ensure_loaded()
            
            # Batch sentiment analysis
            try:
                # Truncate all texts
                truncated = [t[:settings.MAX_LENGTH] for t in uncached_texts]
                
                # Determine which model to use based on languages
                english_count = sum(1 for lang in uncached_langs if lang == 'en')
                indian_count = sum(1 for lang in uncached_langs if lang in ['hi', 'kn', 'ta', 'te', 'bn', 'gu', 'mr', 'pa', 'ml', 'or', 'ur', 'as'])
                
                # Use the most common model for batch processing
                if english_count > len(uncached_texts) / 2:
                    self._ensure_english_sentiment()
                    if self._english_sentiment_pipe and self._english_sentiment_pipe is not False:
                        logger.info(f"[BATCH] Processing {len(uncached_texts)} texts with Cardiff RoBERTa")
                        batch_sentiments = self._english_sentiment_pipe(truncated)
                elif indian_count > len(uncached_texts) / 2:
                    self._ensure_muril_sentiment()
                    if self._muril_sentiment_pipe and self._muril_sentiment_pipe is not False:
                        logger.info(f"[BATCH] Processing {len(uncached_texts)} texts with IndicBERT")
                        batch_sentiments = self._muril_sentiment_pipe(truncated)
                
                # Fallback to multilingual
                if not batch_sentiments and self._sentiment_pipe:
                    logger.info(f"[BATCH] Processing {len(uncached_texts)} texts with multilingual model")
                    batch_sentiments = self._sentiment_pipe(truncated)
                
                # Cache results
                for text, sentiment in zip(uncached_texts, batch_sentiments):
                    if sentiment:
                        # Normalize and add polarity
                        normalized = self._normalize_sentiment_output(sentiment)
                        polarity = self._convert_to_polarity(
                            normalized.get('label', 'neutral'),
                            normalized.get('score', 0.5)
                        )
                        normalized['polarity'] = round(polarity, 3)
                        nlp_cache.set_sentiment(text, normalized)
            
            except Exception as e:
                logger.exception(f"[BATCH] Batch sentiment analysis failed: {e}")
                # Fallback to individual analysis
                batch_sentiments = [None] * len(uncached_texts)
        
        # Combine cached and newly analyzed results
        all_results = [None] * len(texts)
        
        # Fill in cached results
        for idx, cached in cached_results:
            all_results[idx] = {
                "sentiment": cached,
                "topics": [],
                "entities": [],
            }
        
        # Fill in batch processed results
        for idx, uncached_idx in enumerate(uncached_indices):
            sentiment = batch_sentiments[idx] if idx < len(batch_sentiments) else None
            if sentiment:
                normalized = self._normalize_sentiment_output(sentiment)
                polarity = self._convert_to_polarity(
                    normalized.get('label', 'neutral'),
                    normalized.get('score', 0.5)
                )
                normalized['polarity'] = round(polarity, 3)
            all_results[uncached_idx] = {
                "sentiment": sentiment or None,
                "topics": [],
                "entities": [],
            }
        
        return all_results
    
    def _normalize_regional_entities(self, entities: List[Dict[str, Any]], language: str) -> List[Dict[str, Any]]:
        """Normalize regional language entity names to English equivalents."""
        try:
            from .resources import gazetteers
            normalized = []
            
            for entity in entities:
                text = entity.get('text', '')
                # Check if entity text has a regional variation mapping
                if text in gazetteers.REGIONAL_VARIATIONS:
                    # Add normalized English name
                    entity['normalized_text'] = gazetteers.REGIONAL_VARIATIONS[text]
                    logger.debug(f"Normalized '{text}' → '{entity['normalized_text']}'")
                normalized.append(entity)
            
            return normalized
        except Exception as e:
            logger.exception(f"Regional entity normalization failed: {e}")
            return entities
    
    def analyze_batch(self, texts: List[str], languages: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Batch processing for better performance."""
        if languages:
            return [self.analyze(text, language=lang) for text, lang in zip(texts, languages)]
        return [self.analyze(text) for text in texts]
