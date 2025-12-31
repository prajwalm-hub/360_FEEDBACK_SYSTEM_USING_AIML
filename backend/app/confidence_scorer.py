"""
Confidence Scoring System for Government News Classification
Calculates multi-factor confidence scores to enable auto-approval/rejection
and reduce PIB officer workload by 70%+

Author: AI Pipeline Team
Date: December 23, 2025
"""

import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# Trusted government sources (official sources get +0.20 confidence)
TRUSTED_GOV_SOURCES = [
    "pib.gov.in",
    "mygov.in", 
    "india.gov.in",
    "pmindia.gov.in",
    "pmjay.gov.in",
    "pmkisan.gov.in",
    "swachhbharat.mygov.in",
    "digitalindia.gov.in",
    "makeinindia.com",
    "startupindia.gov.in",
    "uidai.gov.in",
    "epfindia.gov.in",
    "pfrda.org.in",
]

# Ministry keywords for ministry detection
MINISTRY_KEYWORDS = [
    "ministry", "mantralaya", "मंत्रालय", "ಮಂತ್ರಾಲಯ",
    "minister", "mantri", "मंत्री", "ಮಂತ್ರಿ",
    "department", "vibhag", "विभाग", "ವಿಭಾಗ",
]

# Entertainment/Sports keywords (penalty)
ENTERTAINMENT_KEYWORDS = [
    "bollywood", "बॉलीवुड", "cricket", "ipl", "match",
    "film", "फिल्म", "actor", "अभिनेता", "actress",
    "movie", "सिनेमा", "celebrity", "सेलिब्रिटी",
    "sports", "खेल", "ಕ್ರೀಡೆ", "championship", "tournament",
]

# Political tribute keywords (penalty)
TRIBUTE_KEYWORDS = [
    "paid tribute", "श्रद्धांजलि", "condolence", "शोक",
    "death anniversary", "पुण्यतिथि", "remembering", "स्मरण",
    "demise", "निधन", "passed away", "गुजर गए",
]

# Exclusion keywords (penalty)
STRONG_EXCLUSION_KEYWORDS = [
    "bangladesh", "dhaka", "pakistan", "islamabad",
    "china", "beijing", "nepal", "kathmandu",
    "sri lanka", "colombo", "afghanistan", "kabul",
]


def count_government_keywords(title: str, summary: str) -> int:
    """
    Count government-related keywords in text.
    Returns count of keywords found (0-N)
    """
    from app.goi_filter import GOI_KEYWORDS
    
    text = (title + " " + summary).lower()
    count = 0
    
    # Check English keywords
    for keyword in GOI_KEYWORDS.get("en", []):
        if keyword.lower() in text:
            count += 1
    
    return count


def detect_schemes(title: str, summary: str) -> List[str]:
    """
    Detect government schemes in text.
    Returns list of detected scheme names.
    """
    try:
        from app.schemes_database import find_schemes_in_text
        return find_schemes_in_text(title + " " + summary)
    except Exception as e:
        logger.warning(f"[CONFIDENCE] Scheme detection failed: {e}")
        return []


def detect_ministries(title: str, summary: str) -> List[str]:
    """
    Detect ministry mentions in text.
    Returns list of detected ministries.
    """
    text = (title + " " + summary).lower()
    ministries = []
    
    # Check for ministry keywords
    for keyword in MINISTRY_KEYWORDS:
        if keyword.lower() in text:
            # Extract ministry name (simplified)
            pattern = rf"(\w+\s+){{0,3}}{keyword}"
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                ministries.append(match.group(0))
    
    return list(set(ministries))[:5]  # Max 5 unique ministries


def is_trusted_source(source: str) -> bool:
    """Check if source is from trusted government domain."""
    source_lower = source.lower()
    return any(trusted in source_lower for trusted in TRUSTED_GOV_SOURCES)


def has_entertainment_keywords(title: str, summary: str) -> bool:
    """Check if text contains entertainment/sports keywords."""
    text = (title + " " + summary).lower()
    return any(keyword in text for keyword in ENTERTAINMENT_KEYWORDS)


def has_tribute_keywords(title: str, summary: str) -> bool:
    """Check if text contains political tribute keywords."""
    text = (title + " " + summary).lower()
    return any(keyword in text for keyword in TRIBUTE_KEYWORDS)


def has_strong_exclusion_keywords(title: str, summary: str) -> bool:
    """Check if text contains strong exclusion keywords (international)."""
    text = (title + " " + summary).lower()
    return any(keyword in text for keyword in STRONG_EXCLUSION_KEYWORDS)


def detect_anomalies(article: Dict) -> List[str]:
    """
    Detect unusual patterns that might indicate classification errors.
    Returns list of anomaly descriptions.
    """
    anomalies = []
    
    title = article.get("title", "")
    summary = article.get("summary", "")
    
    # Anomaly 1: Government keywords + Entertainment keywords
    gov_count = count_government_keywords(title, summary)
    if gov_count >= 2 and has_entertainment_keywords(title, summary):
        anomalies.append("government_entertainment_mix")
    
    # Anomaly 2: Government source but entertainment content
    if is_trusted_source(article.get("source", "")) and has_entertainment_keywords(title, summary):
        anomalies.append("government_source_entertainment_content")
    
    # Anomaly 3: Very high sentiment for government news (unusual)
    sentiment_score = article.get("sentiment_score", 0) or 0
    if sentiment_score > 0.95:
        anomalies.append("unusually_positive_sentiment")
    
    # Anomaly 4: Scheme mentioned but marked non-government
    schemes = article.get("goi_schemes", [])
    category = article.get("content_category", "")
    if schemes and category and category.lower() != "government":
        anomalies.append("scheme_non_government_category_mismatch")
    
    # Anomaly 5: Unusually long title (might be scraping error)
    if len(title) > 200:
        anomalies.append("unusually_long_title")
    
    # Anomaly 6: No language detected
    if not article.get("language"):
        anomalies.append("no_language_detected")
    
    # Anomaly 7: Government keywords but international keywords
    if gov_count >= 2 and has_strong_exclusion_keywords(title, summary):
        anomalies.append("government_international_keyword_mix")
    
    return anomalies


def calculate_confidence_score(article: Dict) -> Dict:
    """
    Calculate multi-factor confidence score for article being government scheme news.
    
    Returns:
        {
            "confidence_score": float (0.0-1.0),
            "confidence_level": str ("high", "medium", "low"),
            "contributing_factors": List[str],
            "auto_approved": bool,
            "auto_rejected": bool,
            "needs_verification": bool,
            "anomalies": List[str]
        }
    """
    title = article.get("title", "")
    summary = article.get("summary", "")
    source = article.get("source", "")
    
    score = 0.0
    factors = []
    
    # ========== POSITIVE FACTORS (Increase confidence) ==========
    
    # Factor 1: Government keyword density (0-0.25)
    gov_keywords = count_government_keywords(title, summary)
    if gov_keywords >= 5:
        score += 0.25
        factors.append(f"strong_keyword_match_{gov_keywords}")
    elif gov_keywords >= 3:
        score += 0.20
        factors.append(f"good_keyword_match_{gov_keywords}")
    elif gov_keywords >= 1:
        score += 0.10
        factors.append(f"moderate_keyword_match_{gov_keywords}")
    
    # Factor 2: Scheme detection (0-0.30) - MOST IMPORTANT
    detected_schemes = detect_schemes(title, summary)
    scheme_count = len(detected_schemes)
    if detected_schemes:
        # Convert scheme objects to just names for database storage
        scheme_names = [s["name"] if isinstance(s, dict) else s for s in detected_schemes]
        article["goi_schemes"] = scheme_names  # Update article
    
    if scheme_count >= 3:
        score += 0.30
        factors.append(f"multiple_schemes_{scheme_count}")
    elif scheme_count == 2:
        score += 0.25
        factors.append("two_schemes")
    elif scheme_count == 1:
        score += 0.20
        factors.append("single_scheme")
    
    # Factor 3: Trusted source (0-0.20)
    if is_trusted_source(source):
        score += 0.20
        factors.append("official_government_source")
    
    # Factor 4: Ministry mentioned (0-0.15)
    ministries = detect_ministries(title, summary)
    if ministries:
        article["goi_ministries"] = ministries  # Update article
        score += 0.15
        factors.append(f"ministry_mentioned_{len(ministries)}")
    
    # Factor 5: Classification confidence from NLP (0-0.10)
    classification_confidence = article.get("classification_confidence", 0) or 0
    if classification_confidence > 0.9:
        score += 0.10
        factors.append("high_nlp_confidence")
    elif classification_confidence > 0.7:
        score += 0.05
        factors.append("medium_nlp_confidence")
    
    # Factor 6: Marked as GoI by filter (0-0.10)
    if article.get("is_goi"):
        score += 0.10
        factors.append("goi_filter_positive")
    
    # ========== NEGATIVE FACTORS (Decrease confidence) ==========
    
    # Penalty 1: Strong exclusion keywords (-0.60) - STRONGEST PENALTY
    if has_strong_exclusion_keywords(title, summary):
        score -= 0.60
        factors.append("international_keywords_detected")
    
    # Penalty 2: Entertainment/Sports keywords (-0.40)
    if has_entertainment_keywords(title, summary):
        score -= 0.40
        factors.append("entertainment_keywords_detected")
    
    # Penalty 3: Political tributes (-0.30)
    if has_tribute_keywords(title, summary):
        score -= 0.30
        factors.append("tribute_keywords_detected")
    
    # Penalty 4: No government keywords at all (-0.20)
    if gov_keywords == 0:
        score -= 0.20
        factors.append("no_government_keywords")
    
    # Penalty 5: Very old article (>30 days) (-0.10)
    try:
        published_at = article.get("published_at")
        if published_at:
            if isinstance(published_at, str):
                published_at = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            days_old = (datetime.now(published_at.tzinfo) - published_at).days
            if days_old > 30:
                score -= 0.10
                factors.append(f"old_article_{days_old}days")
    except Exception as e:
        logger.warning(f"[CONFIDENCE] Date parsing failed: {e}")
    
    # ========== FINAL SCORE CALCULATION ==========
    
    # Clamp score to 0.0-1.0 range
    final_score = max(0.0, min(1.0, score))
    
    # Determine confidence level
    if final_score >= 0.80:
        confidence_level = "high"
        auto_approved = True
        auto_rejected = False
        needs_verification = False  # No review needed for high confidence
    elif final_score >= 0.50:
        confidence_level = "medium"
        auto_approved = False
        auto_rejected = False
        needs_verification = True  # PIB officer review needed
    else:
        confidence_level = "low"
        auto_approved = False
        auto_rejected = True
        needs_verification = False  # No review needed, already rejected
    
    # Detect anomalies
    anomalies = detect_anomalies(article)
    if anomalies:
        # Anomalies ALWAYS require verification (override auto-approve/reject)
        needs_verification = True
        auto_approved = False
        # Keep auto_rejected as is (low confidence should still be rejected)
    
    result = {
        "confidence_score": round(final_score, 2),
        "confidence_level": confidence_level,
        "contributing_factors": factors,
        "auto_approved": auto_approved,
        "auto_rejected": auto_rejected,
        "needs_verification": needs_verification,
        "anomalies": anomalies if anomalies else None,
    }
    
    logger.info(
        f"[CONFIDENCE] Score: {final_score:.2f} ({confidence_level}) | "
        f"Schemes: {scheme_count} | Keywords: {gov_keywords} | "
        f"Action: {'AUTO_APPROVE' if auto_approved else 'AUTO_REJECT' if auto_rejected else 'NEEDS_REVIEW'}"
    )
    
    return result


def batch_calculate_confidence(articles: List[Dict]) -> List[Dict]:
    """
    Calculate confidence scores for multiple articles efficiently.
    Updates articles in-place with confidence data.
    
    Args:
        articles: List of article dictionaries
    
    Returns:
        Updated articles with confidence scores
    """
    logger.info(f"[CONFIDENCE] Calculating confidence for {len(articles)} articles")
    
    for article in articles:
        try:
            confidence_data = calculate_confidence_score(article)
            article.update(confidence_data)
        except Exception as e:
            logger.error(f"[CONFIDENCE] Error calculating confidence: {e}")
            # Default to needs verification on error
            article.update({
                "confidence_score": 0.50,
                "confidence_level": "medium",
                "contributing_factors": ["error_in_calculation"],
                "auto_approved": False,
                "auto_rejected": False,
                "needs_verification": True,
                "anomalies": ["confidence_calculation_error"],
            })
    
    return articles


def get_confidence_statistics(articles: List[Dict]) -> Dict:
    """
    Get statistics about confidence distribution in article batch.
    Useful for monitoring and optimization.
    """
    if not articles:
        return {}
    
    high_count = sum(1 for a in articles if a.get("confidence_level") == "high")
    medium_count = sum(1 for a in articles if a.get("confidence_level") == "medium")
    low_count = sum(1 for a in articles if a.get("confidence_level") == "low")
    
    auto_approved = sum(1 for a in articles if a.get("auto_approved"))
    auto_rejected = sum(1 for a in articles if a.get("auto_rejected"))
    needs_review = sum(1 for a in articles if a.get("needs_verification"))
    
    anomaly_count = sum(1 for a in articles if a.get("anomalies"))
    
    avg_score = sum(a.get("confidence_score", 0) for a in articles) / len(articles)
    
    stats = {
        "total_articles": len(articles),
        "confidence_distribution": {
            "high": high_count,
            "medium": medium_count,
            "low": low_count,
        },
        "action_distribution": {
            "auto_approved": auto_approved,
            "auto_rejected": auto_rejected,
            "needs_review": needs_review,
        },
        "avg_confidence_score": round(avg_score, 2),
        "anomalies_detected": anomaly_count,
        "pib_workload_reduction": f"{round(100 * (1 - needs_review / len(articles)), 1)}%",
    }
    
    logger.info(
        f"[CONFIDENCE STATS] High: {high_count} | Medium: {medium_count} | Low: {low_count} | "
        f"Auto-Approved: {auto_approved} | Needs Review: {needs_review} | "
        f"Workload Reduction: {stats['pib_workload_reduction']}"
    )
    
    return stats


if __name__ == "__main__":
    # Test with sample article
    test_article = {
        "title": "PM Modi launches Ayushman Bharat scheme for healthcare",
        "summary": "Prime Minister Narendra Modi today launched the Ayushman Bharat Yojana, providing health insurance to 50 crore citizens",
        "source": "pib.gov.in",
        "published_at": datetime.now().isoformat(),
        "is_goi": True,
        "classification_confidence": 0.95,
    }
    
    result = calculate_confidence_score(test_article)
    print("\n=== Test Article ===")
    print(f"Title: {test_article['title']}")
    print(f"\nConfidence Score: {result['confidence_score']}")
    print(f"Confidence Level: {result['confidence_level']}")
    print(f"Factors: {', '.join(result['contributing_factors'])}")
    print(f"Auto Approved: {result['auto_approved']}")
    print(f"Needs Verification: {result['needs_verification']}")
