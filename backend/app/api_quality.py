"""
Quality Metrics and Verification API Endpoints
Provides PIB officers with accuracy monitoring and verification capabilities

Author: AI Pipeline Team
Date: December 23, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from .database import get_database
from .api import get_db
from .auth import get_current_user
from .schemas import ArticleVerificationCreate, ArticleVerificationOut

router = APIRouter(prefix="/quality", tags=["quality"])
logger = logging.getLogger(__name__)


@router.get("/metrics")
async def get_quality_metrics(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    db = Depends(get_db)
):
    """
    Get comprehensive quality metrics for monitoring system performance.
    Shows confidence distribution, accuracy, and PIB workload.
    """
    try:
        # Date range
        start_date = datetime.now() - timedelta(days=days)
        
        # Total articles metrics
        total_query = text("""
            SELECT 
                COUNT(*) as total_articles,
                COUNT(*) FILTER (WHERE auto_approved = TRUE) as auto_approved,
                COUNT(*) FILTER (WHERE auto_rejected = TRUE) as auto_rejected,
                COUNT(*) FILTER (WHERE needs_verification = TRUE) as needs_review,
                COUNT(*) FILTER (WHERE confidence_level = 'high') as high_confidence,
                COUNT(*) FILTER (WHERE confidence_level = 'medium') as medium_confidence,
                COUNT(*) FILTER (WHERE confidence_level = 'low') as low_confidence,
                AVG(confidence_score) as avg_confidence,
                COUNT(*) FILTER (WHERE anomalies IS NOT NULL AND array_length(anomalies, 1) > 0) as anomalies_detected,
                COUNT(*) FILTER (WHERE verification_status = 'verified') as verified_count
            FROM articles
            WHERE published_at >= :start_date
        """)
        
        result = db.execute(total_query, {"start_date": start_date}).fetchone()
        
        if not result or result[0] == 0:
            return {
                "message": "No articles in the specified time range",
                "days": days,
                "total_articles": 0
            }
        
        total = result[0]
        
        # Accuracy metrics from verifications
        accuracy_query = text("""
            SELECT 
                COUNT(*) as total_verifications,
                COUNT(*) FILTER (WHERE is_relevant = predicted_should_show) as correct_predictions,
                COUNT(*) FILTER (WHERE is_relevant = TRUE AND predicted_should_show = FALSE) as false_negatives,
                COUNT(*) FILTER (WHERE is_relevant = FALSE AND predicted_should_show = TRUE) as false_positives,
                ROUND(100.0 * COUNT(*) FILTER (WHERE is_relevant = predicted_should_show) / NULLIF(COUNT(*), 0), 2) as accuracy_percentage
            FROM article_verifications
            WHERE verified_at >= :start_date
        """)
        
        accuracy_result = db.execute(accuracy_query, {"start_date": start_date}).fetchone()
        
        # Error analysis - most common keywords in false positives
        fp_keywords_query = text("""
            SELECT unnest(keywords_causing_error) as keyword, COUNT(*) as count
            FROM article_verifications
            WHERE error_type = 'false_positive' AND verified_at >= :start_date
            GROUP BY keyword
            ORDER BY count DESC
            LIMIT 10
        """)
        
        fp_keywords = db.execute(fp_keywords_query, {"start_date": start_date}).fetchall()
        
        metrics = {
            "time_range": {
                "days": days,
                "start_date": start_date.isoformat(),
                "end_date": datetime.now().isoformat()
            },
            "collection_metrics": {
                "total_articles": int(result[0]),
                "auto_approved": int(result[1] or 0),
                "auto_rejected": int(result[2] or 0),
                "needs_review": int(result[3] or 0),
                "verified": int(result[9] or 0),
                "pending_verification": int(result[3] or 0) - int(result[9] or 0)
            },
            "confidence_distribution": {
                "high": int(result[4] or 0),
                "medium": int(result[5] or 0),
                "low": int(result[6] or 0),
                "avg_score": round(float(result[7] or 0), 2)
            },
            "pib_workload": {
                "total_for_review": int(result[3] or 0),
                "workload_reduction_pct": round(100 * (1 - (result[3] or 0) / max(total, 1)), 1),
                "auto_processed_pct": round(100 * ((result[1] or 0) + (result[2] or 0)) / max(total, 1), 1)
            },
            "anomalies": {
                "total_detected": int(result[8] or 0),
                "percentage": round(100 * (result[8] or 0) / max(total, 1), 2)
            },
            "accuracy": None if not accuracy_result else {
                "total_verifications": int(accuracy_result[0] or 0),
                "correct_predictions": int(accuracy_result[1] or 0),
                "false_negatives": int(accuracy_result[2] or 0),
                "false_positives": int(accuracy_result[3] or 0),
                "accuracy_percentage": float(accuracy_result[4] or 0),
                "precision": round(100 * (accuracy_result[1] or 0) / max((accuracy_result[1] or 0) + (accuracy_result[3] or 0), 1), 2),
                "recall": round(100 * (accuracy_result[1] or 0) / max((accuracy_result[1] or 0) + (accuracy_result[2] or 0), 1), 2)
            },
            "error_analysis": {
                "common_fp_keywords": [{"keyword": row[0], "count": int(row[1])} for row in fp_keywords]
            }
        }
        
        logger.info(f"[QUALITY METRICS] Generated for {days} days: {metrics['collection_metrics']}")
        
        return metrics
        
    except Exception as e:
        logger.error(f"[QUALITY METRICS] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get quality metrics: {str(e)}")


@router.get("/articles/review")
async def get_articles_for_review(
    limit: int = Query(50, ge=1, le=200),
    confidence_level: Optional[str] = Query(None, regex="^(high|medium|low)$"),
    has_anomalies: Optional[bool] = None,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get articles that need PIB officer review.
    Filters by confidence level and anomaly presence.
    """
    try:
        # Build query dynamically
        where_clauses = ["needs_verification = TRUE", "verification_status IS NULL OR verification_status != 'verified'"]
        params = {"limit": limit}
        
        if confidence_level:
            where_clauses.append("confidence_level = :confidence_level")
            params["confidence_level"] = confidence_level
        
        if has_anomalies is not None:
            if has_anomalies:
                where_clauses.append("anomalies IS NOT NULL AND array_length(anomalies, 1) > 0")
            else:
                where_clauses.append("(anomalies IS NULL OR array_length(anomalies, 1) = 0)")
        
        where_sql = " AND ".join(where_clauses)
        
        query = text(f"""
            SELECT 
                id, title, summary, source, published_at,
                confidence_score, confidence_level, confidence_factors,
                anomalies, content_category, goi_schemes,
                is_goi, relevance_score, language
            FROM articles
            WHERE {where_sql}
            ORDER BY 
                CASE 
                    WHEN anomalies IS NOT NULL AND array_length(anomalies, 1) > 0 THEN 1
                    WHEN confidence_level = 'medium' THEN 2
                    ELSE 3
                END,
                published_at DESC
            LIMIT :limit
        """)
        
        results = db.execute(query, params).fetchall()
        
        articles = []
        for row in results:
            articles.append({
                "id": row[0],
                "title": row[1],
                "summary": row[2],
                "source": row[3],
                "published_at": row[4].isoformat() if row[4] else None,
                "confidence_score": float(row[5]) if row[5] else None,
                "confidence_level": row[6],
                "confidence_factors": row[7],
                "anomalies": row[8],
                "content_category": row[9],
                "goi_schemes": row[10],
                "is_goi": row[11],
                "relevance_score": float(row[12]) if row[12] else None,
                "language": row[13]
            })
        
        return {
            "total": len(articles),
            "articles": articles,
            "filters": {
                "confidence_level": confidence_level,
                "has_anomalies": has_anomalies
            }
        }
        
    except Exception as e:
        logger.error(f"[REVIEW ARTICLES] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get review articles: {str(e)}")


@router.post("/verify/{article_id}", response_model=ArticleVerificationOut)
async def verify_article(
    article_id: int,
    verification: ArticleVerificationCreate,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    PIB officer verifies an article as relevant or not.
    Records ground truth for accuracy measurement and learning.
    """
    try:
        # Get article details
        article_query = text("""
            SELECT content_category, should_show_pib, confidence_score
            FROM articles
            WHERE id = :article_id
        """)
        
        article = db.execute(article_query, {"article_id": article_id}).fetchone()
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        predicted_category = article[0]
        predicted_should_show = article[1]
        predicted_confidence = float(article[2]) if article[2] else None
        
        # Determine error type
        error_type = "correct"
        if verification.is_relevant and not predicted_should_show:
            error_type = "false_negative"
        elif not verification.is_relevant and predicted_should_show:
            error_type = "false_positive"
        elif verification.correct_category and verification.correct_category != predicted_category:
            error_type = "miscategorization"
        
        # Insert verification
        insert_query = text("""
            INSERT INTO article_verifications (
                article_id, verified_by, is_relevant, correct_category,
                correction_reason, predicted_category, predicted_should_show,
                predicted_confidence, error_type
            ) VALUES (
                :article_id, :verified_by, :is_relevant, :correct_category,
                :correction_reason, :predicted_category, :predicted_should_show,
                :predicted_confidence, :error_type
            )
            ON CONFLICT (article_id, verified_by) DO UPDATE SET
                is_relevant = EXCLUDED.is_relevant,
                correct_category = EXCLUDED.correct_category,
                correction_reason = EXCLUDED.correction_reason,
                verified_at = CURRENT_TIMESTAMP,
                error_type = EXCLUDED.error_type
            RETURNING id, article_id, verified_by, is_relevant, correct_category,
                      correction_reason, verified_at, predicted_category,
                      predicted_should_show, predicted_confidence, error_type
        """)
        
        result = db.execute(insert_query, {
            "article_id": article_id,
            "verified_by": current_user["username"],
            "is_relevant": verification.is_relevant,
            "correct_category": verification.correct_category,
            "correction_reason": verification.correction_reason,
            "predicted_category": predicted_category,
            "predicted_should_show": predicted_should_show,
            "predicted_confidence": predicted_confidence,
            "error_type": error_type
        }).fetchone()
        
        # Update article verification status
        update_article_query = text("""
            UPDATE articles
            SET verification_status = 'verified',
                verified_by = :verified_by,
                verified_at = CURRENT_TIMESTAMP
            WHERE id = :article_id
        """)
        
        db.execute(update_article_query, {
            "article_id": article_id,
            "verified_by": current_user["username"]
        })
        
        db.commit()
        
        logger.info(f"[VERIFICATION] Article {article_id} verified by {current_user['username']} as {error_type}")
        
        return ArticleVerificationOut(
            id=result[0],
            article_id=result[1],
            verified_by=result[2],
            is_relevant=result[3],
            correct_category=result[4],
            correction_reason=result[5],
            verified_at=result[6],
            predicted_category=result[7],
            predicted_should_show=result[8],
            predicted_confidence=result[9],
            error_type=result[10]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"[VERIFICATION] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to verify article: {str(e)}")


@router.get("/dashboard/summary")
async def get_dashboard_summary(db = Depends(get_db)):
    """
    Get quick summary stats for dashboard display.
    """
    try:
        query = text("""
            SELECT 
                COUNT(*) as total_today,
                COUNT(*) FILTER (WHERE auto_approved = TRUE) as auto_approved_today,
                COUNT(*) FILTER (WHERE needs_verification = TRUE) as pending_review,
                AVG(confidence_score) as avg_confidence_today
            FROM articles
            WHERE published_at >= CURRENT_DATE
        """)
        
        result = db.execute(query).fetchone()
        
        # Last 7 days accuracy
        accuracy_query = text("""
            SELECT 
                ROUND(100.0 * COUNT(*) FILTER (WHERE is_relevant = predicted_should_show) / NULLIF(COUNT(*), 0), 2) as accuracy_7d
            FROM article_verifications
            WHERE verified_at >= CURRENT_DATE - INTERVAL '7 days'
        """)
        
        accuracy = db.execute(accuracy_query).fetchone()
        
        return {
            "today": {
                "total_collected": int(result[0] or 0),
                "auto_approved": int(result[1] or 0),
                "pending_review": int(result[2] or 0),
                "avg_confidence": round(float(result[3] or 0), 2)
            },
            "accuracy_7d": float(accuracy[0]) if accuracy and accuracy[0] else None
        }
        
    except Exception as e:
        logger.error(f"[DASHBOARD] Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard summary: {str(e)}")
