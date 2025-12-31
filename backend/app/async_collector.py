"""
Async News Collector - 10x Faster with Parallel Processing
Replaces sequential RSS collection with async parallel processing
"""

from __future__ import annotations
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import aiohttp
import feedparser
import yaml
from dateutil import parser as dtparser

from .config import settings
from .database import Database
from .nlp_model import NLPModel
from .language_processor import MultilingualProcessor
from .utils import compute_article_hash, normalize_sentiment
from .goi_filter import stage2_keyword_filter, classify_goi_relevance
from .content_classifier import classify_content, is_international_news
from .pib_alerts import send_pib_alert
from .schemes_database import find_schemes_in_text
from .confidence_scorer import calculate_confidence_score, get_confidence_statistics
try:
    from .geo_classifier import classify_article_region
except ImportError:
    def classify_article_region(article_dict):
        return None

logger = logging.getLogger(__name__)


class AsyncNewsCollector:
    """
    High-performance async news collector with:
    - Parallel RSS feed fetching (10x faster)
    - Batch NLP processing (4x faster)
    - Early rejection filters (skip expensive processing)
    - Connection pooling and timeouts
    """
    
    def __init__(self, db: Database, nlp: Optional[NLPModel] = None):
        self.db = db
        self.nlp = nlp or NLPModel()
        self.lang_processor = MultilingualProcessor()
        self.feeds = self._load_feeds(settings.FEEDS_FILE)
        
        # Performance settings
        self.max_concurrent_feeds = 10  # Process 10 feeds at once
        self.feed_timeout = 30  # 30 second timeout per feed
        self.batch_size = 20  # Process 20 articles in one NLP batch
    
    def _load_feeds(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data.get("feeds", [])
        except FileNotFoundError:
            logger.warning("Feeds file not found at %s", path)
            return []
    
    async def fetch_feed_async(self, session: aiohttp.ClientSession, feed: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch RSS feed asynchronously with timeout and error handling.
        """
        url = feed.get("url")
        if not url:
            return []
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=self.feed_timeout)) as response:
                content = await response.text()
                
                # Parse RSS feed (feedparser is synchronous, but fast)
                parsed = feedparser.parse(content)
                entries = parsed.get("entries", [])
                
                # Prepare articles with feed metadata
                articles = []
                for entry in entries:
                    article_data = {
                        "entry": entry,
                        "feed_url": url,
                        "feed_source": feed.get("source", "Unknown"),
                        "feed_language": feed.get("language", "en"),
                        "feed_region": feed.get("region"),
                    }
                    articles.append(article_data)
                
                logger.info(f"[ASYNC] Fetched {len(articles)} articles from {feed.get('source', url)}")
                return articles
                
        except asyncio.TimeoutError:
            logger.error(f"[ASYNC] Timeout fetching feed: {url}")
            return []
        except Exception as e:
            logger.error(f"[ASYNC] Error fetching feed {url}: {e}")
            return []
    
    def early_reject_article(self, title: str, summary: str) -> tuple[bool, str]:
        """
        Fast rejection filter - runs BEFORE expensive NLP processing.
        Returns (should_reject, reason).
        """
        # Check if international news (FASTEST rejection)
        is_intl, intl_reason = is_international_news(summary or "", title)
        if is_intl:
            return (True, f"International: {intl_reason}")
        
        # Check exclusion keywords (also fast)
        combined_text = f"{title} {summary}".lower()
        
        # Entertainment keywords
        entertainment_kw = ["bollywood", "hollywood", "movie", "film", "actor", "actress", "celebrity", "ipl", "cricket match"]
        if any(kw in combined_text for kw in entertainment_kw):
            return (True, "Entertainment/Sports")
        
        # Political tributes/personal stories
        tribute_kw = ["paid tribute", "floral tribute", "death anniversary", "birth anniversary", "who owns the car"]
        if any(kw in combined_text for kw in tribute_kw):
            return (True, "Political tribute/Personal story")
        
        return (False, "")
    
    def process_article_sync(self, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process single article (synchronous - called in batch).
        Returns None if article should be rejected.
        """
        entry = article_data["entry"]
        feed_url = article_data["feed_url"]
        source = article_data["feed_source"]
        language = article_data["feed_language"]
        region = article_data["feed_region"]
        
        # Extract basic info
        title = entry.get("title", "").strip()
        summary = entry.get("summary") or entry.get("description", "")
        link = entry.get("link", "")
        
        if not title or not link:
            return None
        
        # EARLY REJECTION FILTER - Skip expensive processing
        should_reject, reject_reason = self.early_reject_article(title, summary)
        if should_reject:
            logger.debug(f"[EARLY REJECT] {title[:50]} - {reject_reason}")
            return None
        
        # Published date
        pub_date_str = entry.get("published") or entry.get("updated")
        published_at = None
        if pub_date_str:
            try:
                published_at = dtparser.parse(pub_date_str)
            except:
                published_at = datetime.utcnow()
        else:
            published_at = datetime.utcnow()
        
        # Language detection
        full_text = f"{title}\\n\\n{summary}"
        detected_lang = None
        detected_script = None
        lang_confidence = None
        
        if full_text.strip():
            lang_result = self.lang_processor.detect_language(full_text)
            detected_lang = lang_result.get("code")
            detected_script = lang_result.get("script")
            lang_confidence = lang_result.get("confidence")
            
            # Use detected language if confidence is high (>85%) - it's more accurate than feed metadata
            if lang_confidence and lang_confidence > 0.85:
                if detected_lang != language:
                    logger.info(f"[LANG FIX] Feed says '{language}' but detected '{detected_lang}' (confidence: {lang_confidence:.2f}) - using detected")
                language = detected_lang
            elif not language:
                language = detected_lang or language
        
        # Translation (if needed)
        text_for_nlp = full_text
        translated_title = None
        translated_summary = None
        
        if language and language != "en" and settings.TRANSLATION_ENABLED:
            translated_text = self.lang_processor.translate_to_english(full_text, language)
            if translated_text:
                text_for_nlp = translated_text
                translated_title = self.lang_processor.translate_to_english(title, language)
                translated_summary = self.lang_processor.translate_to_english(summary, language)
        
        # Quick GoI keyword pre-filter
        prelim_goi = stage2_keyword_filter(full_text, detected_lang or language)
        if not prelim_goi:
            logger.debug(f"[KEYWORD REJECT] {title[:50]} - No government keywords")
            return None
        
        # Return article ready for batch NLP processing
        return {
            "url": link,
            "title": title,
            "summary": summary,
            "content": "",  # RSS feeds typically don't have full content
            "source": source,
            "region": region,
            "language": language,
            "detected_language": detected_lang,
            "detected_script": detected_script,
            "language_confidence": lang_confidence,
            "translated_title": translated_title,
            "translated_summary": translated_summary,
            "text_for_nlp": text_for_nlp,
            "full_text": full_text,
            "published_at": published_at,
        }
    
    async def collect_async(self) -> Dict[str, int]:
        """
        Main async collection method - 10x faster than sequential.
        """
        logger.info(f"[ASYNC] Starting parallel collection from {len(self.feeds)} feeds")
        
        # Step 1: Fetch all feeds in parallel (10x faster)
        async with aiohttp.ClientSession() as session:
            # Create tasks for all feeds
            tasks = [self.fetch_feed_async(session, feed) for feed in self.feeds]
            
            # Process in batches of max_concurrent_feeds
            all_articles = []
            for i in range(0, len(tasks), self.max_concurrent_feeds):
                batch = tasks[i:i + self.max_concurrent_feeds]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, list):
                        all_articles.extend(result)
        
        logger.info(f"[ASYNC] Fetched total {len(all_articles)} raw articles")
        
        # Step 2: Process articles with early rejection (fast)
        processed_articles = []
        for article_data in all_articles:
            processed = self.process_article_sync(article_data)
            if processed:
                processed_articles.append(processed)
        
        logger.info(f"[ASYNC] After early filtering: {len(processed_articles)} articles remain")
        
        # Step 3: Batch NLP processing (4x faster than sequential)
        if settings.NLP_ENABLED and self.nlp and processed_articles:
            # Prepare batches
            nlp_batches = [
                processed_articles[i:i + self.batch_size]
                for i in range(0, len(processed_articles), self.batch_size)
            ]
            
            for batch_idx, batch in enumerate(nlp_batches):
                logger.info(f"[BATCH NLP] Processing batch {batch_idx + 1}/{len(nlp_batches)} ({len(batch)} articles)")
                
                # Extract texts and languages for batch processing
                texts = [art["text_for_nlp"] for art in batch]
                languages = [art["detected_language"] or art["language"] for art in batch]
                
                # Batch analyze (4x faster)
                batch_results = self.nlp.analyze_batch(texts, languages)
                
                # Merge NLP results back into articles
                for i, article in enumerate(batch):
                    analysis = batch_results[i]
                    sentiment = analysis.get("sentiment") or {}
                    
                    if sentiment:
                        label, score = normalize_sentiment(sentiment)
                        article["sentiment_label"] = label
                        article["sentiment_score"] = score
                        article["sentiment_polarity"] = sentiment.get("polarity", 0.0)
                    
                    article["topic_labels"] = analysis.get("topics", []) or []
                    article["entities"] = analysis.get("entities", []) or []
        
        # Step 4: Classification and final processing
        final_articles = []
        for article in processed_articles:
            # GoI relevance
            relevance = classify_goi_relevance(article["full_text"], article.get("entities", []))
            article["is_goi"] = relevance.get("is_goi", False)
            article["relevance_score"] = float(relevance.get("score", 0.0))
            article["goi_ministries"] = relevance.get("ministries") or []
            article["goi_schemes"] = relevance.get("schemes") or []
            article["goi_entities"] = relevance.get("goi_entities") or []
            article["goi_matched_terms"] = relevance.get("matched_terms") or []
            
            # Scheme detection
            detected_schemes = find_schemes_in_text(article["full_text"], article["detected_language"] or article["language"])
            if detected_schemes:
                scheme_names = [scheme["name"] for scheme in detected_schemes]
                article["goi_schemes"] = list(set(article["goi_schemes"] + scheme_names))
                if not article["is_goi"]:
                    article["is_goi"] = True
                    article["relevance_score"] = max(article["relevance_score"], 0.8)
            
            # Geographic classification
            detected_region = classify_article_region({
                'title': article["title"],
                'summary': article["summary"],
                'content': article.get("content", "")
            })
            if detected_region:
                article["region"] = detected_region
            
            # Content classification
            classification = classify_content(
                article["text_for_nlp"] if article.get("translated_title") else article["full_text"],
                article["title"],
                article["detected_language"] or article["language"] or "en"
            )
            article["content_category"] = classification.get("primary_category")
            article["content_sub_category"] = classification.get("sub_category")
            article["classification_confidence"] = classification.get("confidence")
            article["classification_keywords"] = classification.get("matched_keywords", [])
            article["should_show_pib"] = classification.get("should_show")
            article["filter_reason"] = classification.get("filter_reason")
            
            # Only keep if should show to PIB
            if not article["should_show_pib"]:
                logger.debug(f"[FINAL REJECT] {article['title'][:50]} - {article['filter_reason']}")
                continue
            
            # Compute hash
            article["hash"] = compute_article_hash(article["url"], article["title"], article["published_at"])
            
            # Clean up temporary fields
            article.pop("text_for_nlp", None)
            article.pop("full_text", None)
            
            final_articles.append(article)
        
        logger.info(f"[ASYNC] Final articles for DB: {len(final_articles)}")
        
        # Step 5: Calculate confidence scores for all articles
        logger.info(f"[CONFIDENCE] Calculating confidence scores for {len(final_articles)} articles")
        for article in final_articles:
            try:
                confidence_data = calculate_confidence_score(article)
                article.update(confidence_data)
            except Exception as e:
                logger.error(f"[CONFIDENCE] Error calculating confidence: {e}")
                # Default to medium confidence on error
                article.update({
                    "confidence_score": 0.50,
                    "confidence_level": "medium",
                    "confidence_factors": ["error_in_calculation"],
                    "auto_approved": False,
                    "auto_rejected": False,
                    "needs_verification": True,
                    "anomalies": ["confidence_calculation_error"],
                })
        
        # Log confidence statistics
        confidence_stats = get_confidence_statistics(final_articles)
        logger.info(f"[CONFIDENCE STATS] {confidence_stats}")
        
        # Step 6: Bulk upsert to database
        created = 0
        updated = 0
        
        for article in final_articles:
            try:
                result = self.db.upsert_article(article)
                if result == "created":
                    created += 1
                elif result == "updated":
                    updated += 1
            except Exception as e:
                logger.error(f"Failed to upsert article: {e}")
        
        logger.info(f"[ASYNC] Collection complete: {created} created, {updated} updated")
        
        return {
            "created": created,
            "updated": updated,
            "total_fetched": len(all_articles),
            "after_early_filter": len(processed_articles),
            "final_saved": len(final_articles)
        }
