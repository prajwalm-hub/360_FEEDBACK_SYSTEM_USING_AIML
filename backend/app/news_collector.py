from __future__ import annotations
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

import feedparser  # type: ignore
import yaml  # type: ignore
from dateutil import parser as dtparser  # type: ignore

from .config import settings
from .database import Database
from .nlp_model import NLPModel
from .language_processor import MultilingualProcessor
from .utils import compute_article_hash, normalize_sentiment
from .goi_filter import stage2_keyword_filter, classify_goi_relevance
from .content_classifier import classify_content
from .pib_alerts import send_pib_alert
from .schemes_database import find_schemes_in_text
from .confidence_scorer import calculate_confidence_score
try:
    from .geo_classifier import classify_article_region
except ImportError:
    def classify_article_region(article_dict):
        return None

logger = logging.getLogger(__name__)

# Enable web scraping for regional languages
ENABLE_WEB_SCRAPING = False
REGIONAL_LANGUAGES = ['kn', 'ta', 'te', 'bn', 'ml', 'mr', 'gu', 'pa', 'or', 'ur', 'as']


class NewsCollector:
    def __init__(self, db: Database, nlp: Optional[NLPModel] = None):
        self.db = db
        self.nlp = nlp or NLPModel()
        self.lang_processor = MultilingualProcessor()
        self.feeds = self._load_feeds(settings.FEEDS_FILE)
        self.scraping_sources = self._load_scraping_sources() if ENABLE_WEB_SCRAPING else []

    def _load_feeds(self, path: str) -> List[Dict[str, Any]]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                return data.get("feeds", [])
        except FileNotFoundError:
            logger.warning("Feeds file not found at %s", path)
            return []
    
    def _load_scraping_sources(self) -> List[Dict[str, Any]]:
        try:
            scraping_file = Path(settings.FEEDS_FILE).parent / "scraping_sources.yaml"
            with open(scraping_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
                sources = data.get("sources", [])
                logger.info(f"Loaded {len(sources)} web scraping sources")
                return sources
        except FileNotFoundError:
            logger.warning("Scraping sources file not found")
            return []
    
    def _scrape_article(self, source: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape articles from a web source using newspaper3k with improved extraction"""
        try:
            from newspaper import Article, Config
            import requests
            from bs4 import BeautifulSoup
            from urllib.parse import urljoin, urlparse
            
            url = source.get("url")
            language = source.get("language", "en")
            source_name = source.get("name", "")
            
            # Enhanced config for better scraping
            config = Config()
            config.browser_user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            config.request_timeout = 15
            config.fetch_images = False
            config.memoize_articles = False
            
            # Get article links from the page
            headers = {
                'User-Agent': config.browser_user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            response = requests.get(url, timeout=15, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links - more intelligent filtering
            all_links = soup.find_all('a', href=True)
            article_links = []
            base_domain = urlparse(url).netloc
            
            for a_tag in all_links:
                link = a_tag.get('href', '')
                if not link:
                    continue
                    
                # Make absolute URL
                if link.startswith('/'):
                    link = urljoin(url, link)
                elif not link.startswith('http'):
                    continue
                
                # Filter: Must be from same domain and look like article URL
                link_domain = urlparse(link).netloc
                if link_domain != base_domain:
                    continue
                
                # Skip common non-article pages
                skip_patterns = ['login', 'signup', 'subscribe', 'advertise', 'about', 
                                'contact', 'terms', 'privacy', 'category', 'tag', 
                                'author', 'search', '#', 'javascript:', 'mailto:']
                if any(pattern in link.lower() for pattern in skip_patterns):
                    continue
                
                # Prefer URLs that look like article URLs
                if any(pattern in link for pattern in ['/news/', '/article/', '/story/', '/india/', '/national/', 
                                                        '/politics/', '/government/', '202', '2025']):
                    if link not in article_links:
                        article_links.append(link)
                elif link not in article_links and len(article_links) < 30:
                    article_links.append(link)
            
            logger.debug(f"Found {len(article_links)} potential article links from {source_name}")
            
            articles = []
            # Try up to 10 articles to find at least 3 valid ones
            for article_url in article_links[:10]:
                if len(articles) >= 3:  # Stop after finding 3 valid articles
                    break
                    
                try:
                    article = Article(article_url, config=config, language=language)
                    article.download()
                    article.parse()
                    
                    # More lenient validation - accept if we have either good title OR good content
                    has_title = article.title and len(article.title.strip()) > 10
                    has_content = article.text and len(article.text.strip()) > 100
                    
                    if has_title and has_content:
                        articles.append({
                            'url': article_url,
                            'title': article.title.strip(),
                            'summary': article.text[:500].strip(),
                            'content': article.text.strip(),
                            'source': source_name,
                            'language': language,
                            'region': source.get('region'),
                            'published_at': article.publish_date or datetime.utcnow()
                        })
                        logger.debug(f"Successfully extracted article: {article.title[:50]}...")
                    else:
                        logger.debug(f"Skipping article with insufficient content: title_len={len(article.title) if article.title else 0}, content_len={len(article.text) if article.text else 0}")
                        
                except Exception as e:
                    logger.debug(f"Failed to scrape {article_url}: {str(e)[:100]}")
                    continue
            
            if articles:
                logger.info(f"Successfully scraped {len(articles)} articles from {source_name}")
            else:
                logger.warning(f"No articles extracted from {source_name} despite trying {len(article_links)} URLs")
            
            return articles
            
        except Exception as e:
            logger.error(f"Failed to scrape {source.get('name')}: {str(e)[:200]}")
            return []

    def _parse_date(self, entry: Dict[str, Any]) -> Optional[datetime]:
        candidates = [
            entry.get("published"),
            entry.get("updated"),
            entry.get("pubDate"),
        ]
        for c in candidates:
            if not c:
                continue
            try:
                return dtparser.parse(c)
            except Exception:
                continue
        return None

    def _entry_to_article(self, feed_meta: Dict[str, Any], entry: Dict[str, Any]) -> Dict[str, Any]:
        url = entry.get("link") or entry.get("id")
        title = entry.get("title") or ""
        summary = entry.get("summary") or entry.get("description") or ""
        content = summary
        source = feed_meta.get("name")
        region = feed_meta.get("region")
        language = feed_meta.get("language")  # Feed-declared language
        feed_script = feed_meta.get("script")  # Feed-declared script
        published_at = self._parse_date(entry)

        # Auto-detect language and script from content
        detected_lang = None
        detected_script = None
        lang_confidence = None
        full_text = f"{title}\n\n{summary}"
        is_pib_source = "pib" in feed_meta.get("name", "").lower()
        is_regional_feed = language in ["mr", "ur", "as", "kn", "ta", "te", "bn", "ml", "gu", "pa", "or"]
        
        if full_text.strip():
            lang_result = self.lang_processor.detect_language(full_text)
            detected_lang = lang_result.get("code")
            detected_script = lang_result.get("script")
            lang_confidence = lang_result.get("confidence")
            
            # Use detected language if confidence is high (>85%) - it's more accurate than feed metadata
            if lang_confidence and lang_confidence > 0.85:
                # High confidence detection - use it
                if detected_lang != language:
                    logger.info(f"[LANG FIX] Feed says '{language}' but detected '{detected_lang}' (confidence: {lang_confidence:.2f}) - using detected")
                language = detected_lang
            elif not language:
                # No feed language - use detection
                language = detected_lang or language
        
        # Translate non-English content to English for NLP processing
        text_for_nlp = full_text
        translated_title = None
        translated_summary = None
        
        if language and language != "en" and settings.TRANSLATION_ENABLED:
            # Translate to English for NLP processing
            logger.debug("Translating %s content to English for NLP", language)
            translated_text = self.lang_processor.translate_to_english(full_text, language)
            if translated_text:
                text_for_nlp = translated_text
                # Also translate title and summary separately for storage
                translated_title = self.lang_processor.translate_to_english(title, language)
                translated_summary = self.lang_processor.translate_to_english(summary, language)
                logger.info("Successfully translated %s article: %s", language, title[:50])
            else:
                # If translation fails, NLP will work on original text (multilingual models)
                logger.debug("Translation not available, using original text for NLP")

        # Stage 2: quick GoI keyword pre-filter on original text (title+summary)
        prelim_goi = stage2_keyword_filter(full_text, detected_lang or language)

        # NLP analysis (on English text or translated text)
        # Pass detected language for language-specific sentiment models
        sentiment_label = None
        sentiment_score = None
        sentiment_polarity = None  # -1 to +1 polarity scale
        topic_labels: List[str] = []
        entities: List[Dict[str, Any]] = []
        if settings.NLP_ENABLED and self.nlp and prelim_goi:
            # Use detected language for NLP (MuRIL will be used for Indian languages)
            analysis = self.nlp.analyze(text_for_nlp, language=detected_lang or language)
            sentiment = analysis.get("sentiment") or {}
            if sentiment:
                label, score = normalize_sentiment(sentiment)
                sentiment_label = label
                sentiment_score = score
                # Extract polarity score if available
                sentiment_polarity = sentiment.get("polarity", 0.0)
            topic_labels = analysis.get("topics", []) or []
            entities = analysis.get("entities", []) or []

        # Stage 3: relevance scoring/classification (works with or without entities)
        relevance = classify_goi_relevance(full_text, entities)
        is_goi = relevance.get("is_goi", False)
        relevance_score = float(relevance.get("score", 0.0))
        goi_ministries = relevance.get("ministries") or []
        goi_schemes = relevance.get("schemes") or []
        goi_entities = relevance.get("goi_entities") or []
        goi_matched_terms = relevance.get("matched_terms") or []
        
        # IMPROVEMENT: Enhanced scheme detection with regional language support
        detected_schemes = find_schemes_in_text(full_text, detected_lang or language)
        if detected_schemes:
            # Add detected scheme names to goi_schemes list
            scheme_names = [scheme["name"] for scheme in detected_schemes]
            goi_schemes = list(set(goi_schemes + scheme_names))  # Merge and deduplicate
            # Boost relevance if schemes detected
            if not is_goi and len(detected_schemes) > 0:
                is_goi = True
                relevance_score = max(relevance_score, 0.8)  # High confidence for scheme-related articles
                logger.info(f"[SCHEME BOOST] Detected {len(detected_schemes)} schemes in article, marking as GoI relevant")
        
        # Geographic classification
        detected_region = classify_article_region({
            'title': title,
            'summary': summary,
            'content': content
        })
        if detected_region:
            region = detected_region
            logger.info(f"[GEO] Article classified to: {region}")
        
        # Content classification (Government/Political/Entertainment/etc.)
        # Use translated text if available for better accuracy
        text_for_classification = text_for_nlp if (language and language != "en" and text_for_nlp != full_text) else full_text
        classification = classify_content(text_for_classification, title, detected_lang or language or "en")
        content_category = classification.get("primary_category")
        content_sub_category = classification.get("sub_category")
        classification_confidence = classification.get("confidence")
        classification_keywords = classification.get("matched_keywords", [])
        should_show_pib = classification.get("should_show")
        filter_reason = classification.get("filter_reason")
        
        logger.info(f"[CLASSIFICATION] {title[:50]} -> {content_category}/{content_sub_category} (show: {should_show_pib})")

        h = compute_article_hash(url, title, published_at)

        article_dict = {
            "url": url,
            "title": title,
            "summary": summary,
            "content": content,
            "source": source,
            "region": region,  # Auto-detected or feed-declared
            "language": language,  # Detected or feed-declared language
            "detected_language": detected_lang,
            "detected_script": detected_script,
            "language_confidence": lang_confidence,
            "translated_title": translated_title,
            "translated_summary": translated_summary,
            "published_at": published_at,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "sentiment_polarity": sentiment_polarity,  # -1 to +1 scale
            "topic_labels": topic_labels,
            "entities": entities,
            "is_goi": is_goi,
            "relevance_score": relevance_score,
            "goi_ministries": goi_ministries,
            "goi_schemes": goi_schemes,
            "goi_entities": goi_entities,
            "goi_matched_terms": goi_matched_terms,
            "content_category": content_category,
            "content_sub_category": content_sub_category,
            "classification_confidence": classification_confidence,
            "classification_keywords": classification_keywords,
            "should_show_pib": should_show_pib,
            "filter_reason": filter_reason,
            "hash": h,
        }
        
        # Calculate confidence score
        try:
            confidence_data = calculate_confidence_score(article_dict)
            article_dict.update(confidence_data)
        except Exception as e:
            logger.error(f"[CONFIDENCE] Error calculating confidence: {e}")
            # Default to medium confidence on error
            article_dict.update({
                "confidence_score": 0.50,
                "confidence_level": "medium",
                "confidence_factors": ["error_in_calculation"],
                "auto_approved": False,
                "auto_rejected": False,
                "needs_verification": True,
                "anomalies": ["confidence_calculation_error"],
            })
        
        return article_dict

    def collect_once(self) -> Dict[str, int]:
        created = 0
        updated = 0
        
        # Collect from RSS feeds
        for feed in self.feeds:
            url = feed.get("url")
            if not url:
                continue
            try:
                parsed = feedparser.parse(url)
                entries = parsed.get("entries", [])
                for e in entries:
                    art = self._entry_to_article(feed, e)
                    if not art.get("url"):
                        continue
                    
                    # Determine if we should save the article - STRICT FILTERING (Government only)
                    should_save = False
                    feed_lang = feed.get("language", "en")
                    
                    # STRICT FILTERING: Only save Government category articles
                    # Exception: PIB sources with schemes/ministries (official government source)
                    
                    is_gov_category = art.get("content_category") == "Government"
                    should_show = art.get("should_show_pib") == True
                    relevance_score = art.get("relevance_score", 0)
                    is_pib_source = "pib" in feed.get("name", "").lower()
                    has_schemes = len(art.get("goi_schemes", [])) > 0
                    has_ministries = len(art.get("goi_ministries", [])) > 0
                    confidence_score = art.get("confidence_score", 0)
                    content_category = art.get("content_category", "")
                    
                    # PRIORITY 1: PIB sources with schemes/ministries - ALWAYS SAVE (trusted official source)
                    if is_pib_source and (has_schemes or has_ministries):
                        should_save = True
                        logger.info(f"✓ ACCEPTED-PIB ({feed_lang}): {art.get('title', '')[:60]} | Schemes: {has_schemes} | Ministries: {has_ministries}")
                    
                    # PRIORITY 2: Government category articles ONLY (strict filter)
                    elif is_gov_category and should_show:
                        if (relevance_score >= 0.4 or confidence_score >= 0.7 or has_schemes or has_ministries):
                            should_save = True
                            logger.info(f"✓ ACCEPTED-GOV ({feed_lang}): {art.get('title', '')[:60]} | Relevance: {relevance_score:.2f} | Conf: {confidence_score:.2f}")
                        else:
                            logger.debug(f"✗ REJECTED (weak signals): {art.get('title', '')[:60]}")
                    
                    else:
                        logger.debug(f"✗ REJECTED: {art.get('title', '')[:60]} (cat={content_category}, rel={relevance_score:.2f})")
                    
                    if should_save:
                        article_obj, is_created = self.db.upsert_article(art)
                        created += 1 if is_created else 0
                        updated += 0 if is_created else 1
                        
                        # Check for negative sentiment and trigger PIB alert (Scheme-related ONLY)
                        if settings.ALERT_ENABLED and is_created and article_obj:
                            sentiment_label = art.get("sentiment_label") or ""
                            sentiment_label = sentiment_label.lower() if sentiment_label else ""
                            sentiment_score = art.get("sentiment_score", 0.0)
                            schemes = art.get("schemes", [])
                            
                            # Only send alert if: negative sentiment AND schemes mentioned
                            if schemes and sentiment_label == "negative" and sentiment_score >= settings.ALERT_NEGATIVE_THRESHOLD:
                                try:
                                    send_pib_alert(
                                        article_title=art.get("title", ""),
                                        article_summary=art.get("summary", ""),
                                        article_link=art.get("url", ""),
                                        language=art.get("language", "en"),
                                        sentiment_score=sentiment_score,
                                        article_id=str(article_obj.id),
                                        schemes=schemes
                                    )
                                except Exception as alert_error:
                                    logger.warning(f"Failed to send PIB alert: {alert_error}")
                    else:
                        logger.debug(f"Filtered out article: {art.get('title', '')[:50]}... (cat={art.get('content_category')}, relevance={art.get('relevance_score', 0):.2f})")
            except Exception as e:
                logger.exception("Failed collecting from %s: %s", url, e)
        
        # Collect from web scraping (regional languages only)
        if ENABLE_WEB_SCRAPING and self.scraping_sources:
            logger.info(f"Starting web scraping for {len(self.scraping_sources)} sources")
            for source in self.scraping_sources:
                source_lang = source.get('language')
                if source_lang not in REGIONAL_LANGUAGES:
                    continue
                
                try:
                    scraped_articles = self._scrape_article(source)
                    logger.info(f"Scraped {len(scraped_articles)} articles from {source.get('name')}")
                    
                    for raw_art in scraped_articles:
                        # Process scraped article same as RSS
                        art = self._process_scraped_article(raw_art)
                        
                        # Regional language scraping: More lenient
                        should_save = False
                        if source_lang in REGIONAL_LANGUAGES:
                            # Accept if ANY GoI indicators present
                            if (art.get("is_goi") or 
                                art.get("relevance_score", 0) > 0.05 or
                                art.get("content_category") == "Government"):
                                should_save = True
                                logger.debug(f"Accepting scraped regional article ({source_lang}): {art.get('title', '')[:50]}...")
                        else:
                            # Strict filtering for non-regional
                            if art.get("content_category") == "Government" and art.get("should_show_pib") == True:
                                should_save = True
                        
                        if should_save:
                            article_obj, is_created = self.db.upsert_article(art)
                            created += 1 if is_created else 0
                            updated += 0 if is_created else 1
                            
                            # Check for negative sentiment and trigger PIB alert (Scheme-related ONLY)
                            if settings.ALERT_ENABLED and is_created and article_obj:
                                sentiment_label = art.get("sentiment_label", "").lower()
                                sentiment_score = art.get("sentiment_score", 0.0)
                                schemes = art.get("schemes", [])
                                
                                # Only send alert if: negative sentiment AND schemes mentioned
                                if schemes and sentiment_label == "negative" and sentiment_score >= settings.ALERT_NEGATIVE_THRESHOLD:
                                    try:
                                        send_pib_alert(
                                            article_title=art.get("title", ""),
                                            article_summary=art.get("summary", ""),
                                            article_link=art.get("url", ""),
                                            language=art.get("language", "en"),
                                            sentiment_score=sentiment_score,
                                            article_id=str(article_obj.id),
                                            schemes=schemes
                                        )
                                    except Exception as alert_error:
                                        logger.warning(f"Failed to send PIB alert: {alert_error}")
                        else:
                            logger.debug(f"Filtered out scraped article: {art.get('title', '')[:50]}...")
                except Exception as e:
                    logger.error(f"Failed scraping {source.get('name')}: {e}")
        
        return {"created": created, "updated": updated}
    
    def _process_scraped_article(self, raw_art: Dict[str, Any]) -> Dict[str, Any]:
        """Process scraped article through NLP pipeline"""
        title = raw_art.get('title', '')
        summary = raw_art.get('summary', '')
        content = raw_art.get('content', '')
        url = raw_art.get('url', '')
        source = raw_art.get('source', '')
        region = raw_art.get('region', '')
        language = raw_art.get('language', 'en')
        published_at = raw_art.get('published_at')
        
        full_text = f"{title}\n\n{summary}"
        
        # Detect language
        lang_result = self.lang_processor.detect_language(full_text)
        detected_lang = lang_result.get("code")
        detected_script = lang_result.get("script")
        lang_confidence = lang_result.get("confidence")
        
        # Translate if needed
        text_for_nlp = full_text
        translated_title = None
        translated_summary = None
        
        if language != "en" and settings.TRANSLATION_ENABLED:
            translated_text = self.lang_processor.translate_to_english(full_text, language)
            if translated_text:
                text_for_nlp = translated_text
                translated_title = self.lang_processor.translate_to_english(title, language)
                translated_summary = self.lang_processor.translate_to_english(summary, language)
        
        # GoI filter
        prelim_goi = stage2_keyword_filter(full_text, detected_lang or language)
        
        # NLP analysis
        sentiment_label = None
        sentiment_score = None
        sentiment_polarity = None
        topic_labels = []
        entities = []
        
        if settings.NLP_ENABLED and self.nlp and prelim_goi:
            analysis = self.nlp.analyze(text_for_nlp, language=detected_lang or language)
            sentiment = analysis.get("sentiment") or {}
            if sentiment:
                label, score = normalize_sentiment(sentiment)
                sentiment_label = label
                sentiment_score = score
                sentiment_polarity = sentiment.get("polarity", 0.0)
            topic_labels = analysis.get("topics", []) or []
            entities = analysis.get("entities", []) or []
        
        # Relevance scoring
        relevance = classify_goi_relevance(full_text, entities)
        is_goi = relevance.get("is_goi", False)
        relevance_score = float(relevance.get("score", 0.0))
        
        # Geographic classification
        detected_region = classify_article_region({'title': title, 'summary': summary, 'content': content})
        if detected_region:
            region = detected_region
        
        # Content classification
        classification = classify_content(text_for_nlp if text_for_nlp != full_text else full_text, title, detected_lang or language)
        
        h = compute_article_hash(url, title, published_at)
        
        return {
            "url": url,
            "title": title,
            "summary": summary,
            "content": content,
            "source": source,
            "region": region,
            "language": language,
            "detected_language": detected_lang,
            "detected_script": detected_script,
            "language_confidence": lang_confidence,
            "translated_title": translated_title,
            "translated_summary": translated_summary,
            "published_at": published_at,
            "sentiment_label": sentiment_label,
            "sentiment_score": sentiment_score,
            "sentiment_polarity": sentiment_polarity,
            "topic_labels": topic_labels,
            "entities": entities,
            "is_goi": is_goi,
            "relevance_score": relevance_score,
            "goi_ministries": relevance.get("ministries") or [],
            "goi_schemes": relevance.get("schemes") or [],
            "goi_entities": relevance.get("goi_entities") or [],
            "goi_matched_terms": relevance.get("matched_terms") or [],
            "content_category": classification.get("primary_category"),
            "content_sub_category": classification.get("sub_category"),
            "classification_confidence": classification.get("confidence"),
            "classification_keywords": classification.get("matched_keywords", []),
            "should_show_pib": classification.get("should_show"),
            "filter_reason": classification.get("filter_reason"),
            "hash": h,
        }
