"""
Rule-Based Sentiment Adjuster for Government News
Adjusts IndicBERT sentiment scores based on keyword patterns
Optimized for Indian government news context
"""
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Positive keywords for government news (English + transliterated Hindi/regional)
POSITIVE_KEYWORDS = {
    # English
    'achievement', 'progress', 'success', 'growth', 'development', 'improvement',
    'innovation', 'reform', 'benefit', 'welfare', 'opportunity', 'initiative',
    'launch', 'inaugurate', 'approval', 'sanction', 'allocation', 'boost',
    'enhance', 'strengthen', 'expand', 'accelerate', 'facilitate', 'promote',
    'empowerment', 'inclusive', 'sustainable', 'transparent', 'efficient',
    
    # Hindi (transliterated)
    'vikas', 'pragati', 'safalta', 'sudhar', 'kalyan', 'yojana',
    'shubharambh', 'nirmaan', 'vikasit', 'unnati', 'labh',
    
    # Common government schemes
    'ayushman', 'ujjwala', 'swachh', 'bharatmala', 'sagarmala',
    'digital india', 'make in india', 'skill india', 'smart city',
}

# Negative keywords for government news
NEGATIVE_KEYWORDS = {
    # English
    'crisis', 'decline', 'failure', 'corruption', 'scam', 'scandal',
    'protest', 'strike', 'controversy', 'criticism', 'opposition',
    'delay', 'cancellation', 'shortage', 'problem', 'issue',
    'concern', 'challenge', 'dispute', 'conflict', 'tension',
    'violation', 'breach', 'negligence', 'mismanagement', 'inefficiency',
    
    # Hindi (transliterated)
    'samasya', 'mushkil', 'virodh', 'bhrashtachar', 'ghotala',
    'sangharsh', 'vivad', 'kathinai',
}

# Neutral/Factual keywords (don't adjust)
NEUTRAL_KEYWORDS = {
    'meeting', 'discussion', 'conference', 'statement', 'report',
    'review', 'assessment', 'survey', 'data', 'statistics',
    'announcement', 'notification', 'circular', 'guideline',
    'session', 'parliament', 'assembly', 'cabinet', 'committee',
}

# Strong positive phrases (larger boost)
STRONG_POSITIVE_PHRASES = {
    'major achievement', 'significant progress', 'record growth',
    'historic decision', 'landmark initiative', 'game changer',
    'transformative reform', 'revolutionary step', 'milestone reached',
    'unprecedented success', 'remarkable improvement',
}

# Strong negative phrases (larger penalty)
STRONG_NEGATIVE_PHRASES = {
    'major setback', 'serious concern', 'grave situation',
    'alarming development', 'critical issue', 'severe crisis',
    'massive corruption', 'widespread protest', 'violent clashes',
}


class RuleBasedSentimentAdjuster:
    """
    Adjusts IndicBERT sentiment predictions using rule-based keyword matching.
    Recommended for government news to handle domain-specific vocabulary.
    """
    
    def __init__(self, boost_threshold: float = 0.15):
        """
        Args:
            boost_threshold: Amount to adjust score for keyword matches (0.0 to 1.0)
        """
        self.boost_threshold = boost_threshold
        self.strong_boost_threshold = boost_threshold * 2  # Double for strong phrases
        
    def adjust_sentiment(
        self, 
        text: str, 
        original_label: str, 
        original_score: float
    ) -> Dict[str, any]:
        """
        Adjust sentiment based on keyword rules.
        
        Args:
            text: Article text
            original_label: Predicted label (positive/negative/neutral)
            original_score: Confidence score (0.0 to 1.0)
        
        Returns:
            Dict with adjusted_label, adjusted_score, adjustment_reason
        """
        if not text:
            return {
                'adjusted_label': original_label,
                'adjusted_score': original_score,
                'adjustment_reason': 'no_text',
                'original_label': original_label,
                'original_score': original_score,
            }
        
        text_lower = text.lower()
        
        # Check for strong phrases first (higher priority)
        strong_pos_count = sum(1 for phrase in STRONG_POSITIVE_PHRASES if phrase in text_lower)
        strong_neg_count = sum(1 for phrase in STRONG_NEGATIVE_PHRASES if phrase in text_lower)
        
        # Check for regular keywords
        pos_count = sum(1 for keyword in POSITIVE_KEYWORDS if keyword in text_lower)
        neg_count = sum(1 for keyword in NEGATIVE_KEYWORDS if keyword in text_lower)
        neutral_count = sum(1 for keyword in NEUTRAL_KEYWORDS if keyword in text_lower)
        
        # Calculate total keyword signal
        total_keywords = pos_count + neg_count + neutral_count
        if total_keywords == 0:
            return {
                'adjusted_label': original_label,
                'adjusted_score': original_score,
                'adjustment_reason': 'no_keywords_found',
                'original_label': original_label,
                'original_score': original_score,
            }
        
        # Calculate adjustment
        adjustment = 0.0
        reason = []
        
        # Strong phrase adjustments
        if strong_pos_count > 0:
            adjustment += self.strong_boost_threshold * strong_pos_count
            reason.append(f'+{strong_pos_count}_strong_positive')
        
        if strong_neg_count > 0:
            adjustment -= self.strong_boost_threshold * strong_neg_count
            reason.append(f'-{strong_neg_count}_strong_negative')
        
        # Regular keyword adjustments
        if pos_count > neg_count:
            # Net positive sentiment
            net_positive = pos_count - neg_count
            adjustment += self.boost_threshold * (net_positive / total_keywords)
            reason.append(f'+{pos_count}_positive_keywords')
            
        elif neg_count > pos_count:
            # Net negative sentiment
            net_negative = neg_count - pos_count
            adjustment -= self.boost_threshold * (net_negative / total_keywords)
            reason.append(f'-{neg_count}_negative_keywords')
        
        # Neutral keywords dilute the adjustment
        if neutral_count > 0:
            dilution_factor = neutral_count / total_keywords
            adjustment *= (1 - dilution_factor * 0.5)  # Reduce by up to 50%
            reason.append(f'~{neutral_count}_neutral_keywords')
        
        # Apply adjustment
        adjusted_score = original_score + adjustment
        adjusted_score = max(0.0, min(1.0, adjusted_score))  # Clamp to [0, 1]
        
        # Determine adjusted label based on score thresholds
        adjusted_label = original_label
        if adjusted_score >= 0.6:
            adjusted_label = 'positive'
        elif adjusted_score <= 0.4:
            adjusted_label = 'negative'
        else:
            adjusted_label = 'neutral'
        
        adjustment_reason = ' | '.join(reason) if reason else 'no_adjustment'
        
        # Log if label changed
        if adjusted_label != original_label:
            logger.info(
                f"Sentiment adjusted: {original_label}→{adjusted_label} "
                f"(score: {original_score:.2f}→{adjusted_score:.2f}) "
                f"Reason: {adjustment_reason}"
            )
        
        return {
            'adjusted_label': adjusted_label,
            'adjusted_score': adjusted_score,
            'adjustment_reason': adjustment_reason,
            'original_label': original_label,
            'original_score': original_score,
        }


# Singleton instance
_adjuster = None

def get_sentiment_adjuster(boost_threshold: float = 0.15) -> RuleBasedSentimentAdjuster:
    """Get or create singleton sentiment adjuster."""
    global _adjuster
    if _adjuster is None:
        _adjuster = RuleBasedSentimentAdjuster(boost_threshold)
    return _adjuster
