import hashlib
from datetime import datetime
from typing import Optional


def compute_article_hash(url: str, title: str, published_at: Optional[datetime]) -> str:
    base = f"{url}|{title}|{(published_at or '').isoformat() if published_at else ''}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


def normalize_sentiment(score_map):
    """Normalize sentiment output with proper thresholds"""
    label = score_map.get("label", "neutral")
    score = float(score_map.get("score", 0.5))
    
    # Model label mapping
    label_map = {
        "LABEL_0": "negative",
        "LABEL_1": "neutral",
        "LABEL_2": "positive",
        "1 star": "negative",
        "2 stars": "negative",
        "3 stars": "neutral",
        "4 stars": "positive",
        "5 stars": "positive",
        "pos": "positive",
        "neg": "negative",
        "neu": "neutral",
    }
    
    # Normalize label
    label_lower = label.lower()
    if label in label_map:
        label = label_map[label]
    elif label_lower in label_map:
        label = label_map[label_lower]
    else:
        label = label_lower
    
    # Apply threshold logic for better classification
    # If model is confident (score > 0.6), trust the label
    # If uncertain (0.4 < score < 0.6), classify as neutral
    if score >= 0.6:
        # High confidence - keep the label
        pass
    elif score <= 0.4:
        # Low confidence - might be opposite
        if label == "positive":
            label = "negative"
        elif label == "negative":
            label = "positive"
    else:
        # Medium confidence (0.4-0.6) - neutral
        label = "neutral"
    
    return label, score
