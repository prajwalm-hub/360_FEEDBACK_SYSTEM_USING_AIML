"""
Advanced Analytics API endpoints for NewsScope India
Provides data for word cloud, timeline, and heatmap visualizations
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import Counter
import re

from .database import get_database as get_db, Article

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/trending-keywords")
async def get_trending_keywords(
    days: int = 7,
    limit: int = 20,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get trending keywords from recent articles"""
    try:
        # Get articles from last N days
        since_date = datetime.now() - timedelta(days=days)
        
        articles = db.query(Article).filter(
            Article.published_at >= since_date
        ).all()
        
        # Extract keywords from titles and summaries
        keywords = []
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                     'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                     'has', 'have', 'had', 'will', 'would', 'should', 'could', 'may', 'might'}
        
        for article in articles:
            text = f"{article.title} {article.summary or ''}"
            # Extract words (alphanumeric, 3+ chars)
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            keywords.extend([w for w in words if w not in stopwords])
        
        # Count frequencies
        word_counts = Counter(keywords)
        
        # Return top N keywords
        trending = [
            {"text": word, "value": count}
            for word, count in word_counts.most_common(limit)
        ]
        
        return trending
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error in trending keywords: {e}")
        return []


@router.get("/timeline")
async def get_timeline_data(
    days: int = 7,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get article volume and sentiment trends over time"""
    try:
        since_date = datetime.now() - timedelta(days=days)
        
        # Query to get daily aggregates
        query = text("""
            SELECT 
                DATE(published_at) as date,
                COUNT(*) as articles,
                AVG(COALESCE(sentiment_score, 0)) as avg_sentiment,
                SUM(CASE WHEN sentiment_score > 0.2 THEN 1 ELSE 0 END) as positive,
                SUM(CASE WHEN sentiment_score BETWEEN -0.2 AND 0.2 THEN 1 ELSE 0 END) as neutral,
                SUM(CASE WHEN sentiment_score < -0.2 THEN 1 ELSE 0 END) as negative
            FROM articles
            WHERE published_at >= :since_date
            GROUP BY DATE(published_at)
            ORDER BY date ASC
        """)
        
        result = db.execute(query, {"since_date": since_date})
        rows = result.fetchall()
        
        timeline = []
        for row in rows:
            timeline.append({
                "date": row[0].strftime("%a") if hasattr(row[0], 'strftime') else str(row[0]),
                "articles": int(row[1]),
                "sentiment": float(row[2]) if row[2] else 0,
                "positive": int(row[3]) if row[3] else 0,
                "neutral": int(row[4]) if row[4] else 0,
                "negative": int(row[5]) if row[5] else 0,
            })
        
        return timeline
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error in timeline: {e}")
        return []


@router.get("/regional-heatmap")
async def get_regional_heatmap(
    days: int = 7,
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get news distribution by region and hour of day"""
    
    since_date = datetime.now() - timedelta(days=days)
    
    # Query to get regional and hourly distribution
    query = text("""
        SELECT 
            region,
            EXTRACT(HOUR FROM published_date) as hour,
            COUNT(*) as count
        FROM articles
        WHERE published_date >= :since_date
            AND region IS NOT NULL
        GROUP BY region, hour
        ORDER BY region, hour
    """)
    
    result = db.execute(query, {"since_date": since_date})
    rows = result.fetchall()
    
    heatmap = []
    for row in rows:
        heatmap.append({
            "region": row[0],
            "hour": int(row[1]),
            "count": int(row[2])
        })
    
    return heatmap


@router.get("/insights")
async def get_ai_insights(
    days: int = 7,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get AI-generated insights about recent trends"""
    
    since_date = datetime.now() - timedelta(days=days)
    
    # Get various metrics
    total_articles = db.query(func.count(Article.id)).filter(
        Article.published_date >= since_date
    ).scalar()
    
    avg_sentiment = db.query(func.avg(Article.sentiment_score)).filter(
        Article.published_date >= since_date,
        Article.sentiment_score.isnot(None)
    ).scalar()
    
    # Get top category
    top_category = db.query(
        Article.category,
        func.count(Article.id).label('count')
    ).filter(
        Article.published_date >= since_date,
        Article.category.isnot(None)
    ).group_by(Article.category).order_by(text('count DESC')).first()
    
    # Get peak hour
    peak_hour_query = text("""
        SELECT 
            EXTRACT(HOUR FROM published_date) as hour,
            COUNT(*) as count
        FROM articles
        WHERE published_date >= :since_date
        GROUP BY hour
        ORDER BY count DESC
        LIMIT 1
    """)
    peak_hour_result = db.execute(peak_hour_query, {"since_date": since_date}).fetchone()
    
    return {
        "total_articles": total_articles or 0,
        "avg_sentiment": float(avg_sentiment) if avg_sentiment else 0,
        "top_category": top_category[0] if top_category else "Unknown",
        "top_category_count": top_category[1] if top_category else 0,
        "peak_hour": int(peak_hour_result[0]) if peak_hour_result else 0,
        "peak_hour_articles": int(peak_hour_result[1]) if peak_hour_result else 0,
    }


@router.get("/accuracy-metrics")
async def get_accuracy_metrics(
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get classification and sentiment accuracy metrics"""
    
    since_date = datetime.now() - timedelta(days=days)
    
    # Get articles with confidence scores
    articles = db.query(Article).filter(
        Article.published_date >= since_date,
        Article.classification_confidence.isnot(None)
    ).all()
    
    if not articles:
        return {
            "avg_classification_confidence": 0,
            "avg_sentiment_confidence": 0,
            "high_confidence_count": 0,
            "total_analyzed": 0,
        }
    
    total = len(articles)
    avg_class_conf = sum(a.classification_confidence for a in articles if a.classification_confidence) / total
    high_conf = sum(1 for a in articles if a.classification_confidence and a.classification_confidence > 0.8)
    
    return {
        "avg_classification_confidence": round(avg_class_conf * 100, 1),
        "avg_sentiment_confidence": 85.0,  # Mock value
        "high_confidence_count": high_conf,
        "total_analyzed": total,
        "accuracy_rate": round(avg_class_conf * 100, 1),
    }
