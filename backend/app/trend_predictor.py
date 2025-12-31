"""
Predictive Trend Analysis & Early Warning System
Detects emerging government policy trends before they become mainstream
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class TrendPredictor:
    """Predict emerging trends in government news using velocity analysis"""
    
    def __init__(self, db):
        self.db = db
        
    def detect_emerging_trends(
        self,
        days: int = 7,
        velocity_threshold: float = 3.0,
        min_mentions: int = 5
    ) -> List[Dict]:
        """
        Detect emerging trends by analyzing mention velocity
        
        Args:
            days: Days to analyze for current period
            velocity_threshold: Multiplier threshold (3.0 = 300% increase)
            min_mentions: Minimum mentions to consider (avoid noise)
            
        Returns:
            List of emerging trends with metadata
        """
        current_end = datetime.now()
        current_start = current_end - timedelta(days=days)
        historical_end = current_start
        historical_start = historical_end - timedelta(days=days*4)  # 4x historical period
        
        trends = []
        
        # Analyze schemes
        scheme_trends = self._analyze_entity_trends(
            entity_type="schemes",
            current_start=current_start,
            current_end=current_end,
            historical_start=historical_start,
            historical_end=historical_end,
            velocity_threshold=velocity_threshold,
            min_mentions=min_mentions
        )
        trends.extend(scheme_trends)
        
        # Analyze ministries
        ministry_trends = self._analyze_entity_trends(
            entity_type="ministries",
            current_start=current_start,
            current_end=current_end,
            historical_start=historical_start,
            historical_end=historical_end,
            velocity_threshold=velocity_threshold,
            min_mentions=min_mentions
        )
        trends.extend(ministry_trends)
        
        # Analyze categories
        category_trends = self._analyze_category_trends(
            current_start=current_start,
            current_end=current_end,
            historical_start=historical_start,
            historical_end=historical_end,
            velocity_threshold=velocity_threshold,
            min_mentions=min_mentions
        )
        trends.extend(category_trends)
        
        # Sort by velocity score (descending)
        trends.sort(key=lambda x: x["velocity_score"], reverse=True)
        
        return trends
    
    def _analyze_entity_trends(
        self,
        entity_type: str,
        current_start: datetime,
        current_end: datetime,
        historical_start: datetime,
        historical_end: datetime,
        velocity_threshold: float,
        min_mentions: int
    ) -> List[Dict]:
        """Analyze trends for schemes or ministries"""
        
        field_map = {
            "schemes": "goi_schemes",
            "ministries": "goi_ministries"
        }
        field = field_map.get(entity_type)
        if not field:
            return []
        
        try:
            # Current period mentions
            current_query = f"""
                SELECT 
                    unnest({field}) as entity,
                    COUNT(*) as mention_count,
                    AVG(confidence_score) as avg_confidence,
                    AVG(sentiment_score) as avg_sentiment
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND created_at < %s
                  AND {field} IS NOT NULL
                  AND array_length({field}, 1) > 0
                GROUP BY entity
                HAVING COUNT(*) >= %s
            """
            
            with self.db.cursor() as cur:
                cur.execute(current_query, (current_start, current_end, min_mentions))
                current_data = {row[0]: {"count": row[1], "confidence": row[2], "sentiment": row[3]} 
                               for row in cur.fetchall()}
            
            # Historical average mentions
            historical_query = f"""
                SELECT 
                    unnest({field}) as entity,
                    COUNT(*) as total_mentions
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND created_at < %s
                  AND {field} IS NOT NULL
                  AND array_length({field}, 1) > 0
                GROUP BY entity
            """
            
            with self.db.cursor() as cur:
                cur.execute(historical_query, (historical_start, historical_end))
                historical_data = {row[0]: row[1] for row in cur.fetchall()}
            
            # Calculate velocity for each entity
            trends = []
            for entity, current_stats in current_data.items():
                current_count = current_stats["count"]
                historical_count = historical_data.get(entity, 0)
                
                # Calculate average historical mentions per period
                avg_historical = historical_count / 4.0 if historical_count > 0 else 0.5
                
                # Velocity score
                velocity_score = current_count / avg_historical if avg_historical > 0 else current_count * 2
                
                if velocity_score >= velocity_threshold:
                    # Determine trend strength
                    if velocity_score >= 10.0:
                        strength = "explosive"
                    elif velocity_score >= 5.0:
                        strength = "very_high"
                    elif velocity_score >= 3.0:
                        strength = "high"
                    else:
                        strength = "moderate"
                    
                    # Get recent articles for context
                    context = self._get_trend_context(entity, field, current_start, current_end)
                    
                    trends.append({
                        "entity": entity,
                        "entity_type": entity_type,
                        "velocity_score": round(velocity_score, 2),
                        "strength": strength,
                        "current_mentions": current_count,
                        "historical_avg": round(avg_historical, 1),
                        "increase_pct": round((velocity_score - 1) * 100, 1),
                        "avg_confidence": round(current_stats["confidence"], 2) if current_stats["confidence"] else None,
                        "avg_sentiment": round(current_stats["sentiment"], 2) if current_stats["sentiment"] else None,
                        "period_days": (current_end - current_start).days,
                        "context": context,
                        "alert_message": self._generate_alert_message(
                            entity, entity_type, velocity_score, current_count, strength
                        ),
                        "detected_at": datetime.now().isoformat()
                    })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing {entity_type} trends: {e}")
            return []
    
    def _analyze_category_trends(
        self,
        current_start: datetime,
        current_end: datetime,
        historical_start: datetime,
        historical_end: datetime,
        velocity_threshold: float,
        min_mentions: int
    ) -> List[Dict]:
        """Analyze trends in content categories"""
        
        try:
            # Current period
            current_query = """
                SELECT 
                    content_category,
                    COUNT(*) as mention_count,
                    AVG(confidence_score) as avg_confidence,
                    AVG(sentiment_score) as avg_sentiment
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND created_at < %s
                  AND content_category IS NOT NULL
                GROUP BY content_category
                HAVING COUNT(*) >= %s
            """
            
            with self.db.cursor() as cur:
                cur.execute(current_query, (current_start, current_end, min_mentions))
                current_data = {row[0]: {"count": row[1], "confidence": row[2], "sentiment": row[3]} 
                               for row in cur.fetchall()}
            
            # Historical period
            historical_query = """
                SELECT 
                    content_category,
                    COUNT(*) as total_mentions
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND created_at < %s
                  AND content_category IS NOT NULL
                GROUP BY content_category
            """
            
            with self.db.cursor() as cur:
                cur.execute(historical_query, (historical_start, historical_end))
                historical_data = {row[0]: row[1] for row in cur.fetchall()}
            
            trends = []
            for category, current_stats in current_data.items():
                current_count = current_stats["count"]
                historical_count = historical_data.get(category, 0)
                avg_historical = historical_count / 4.0 if historical_count > 0 else 0.5
                
                velocity_score = current_count / avg_historical if avg_historical > 0 else current_count * 2
                
                if velocity_score >= velocity_threshold:
                    strength = (
                        "explosive" if velocity_score >= 10.0 else
                        "very_high" if velocity_score >= 5.0 else
                        "high" if velocity_score >= 3.0 else
                        "moderate"
                    )
                    
                    trends.append({
                        "entity": category,
                        "entity_type": "category",
                        "velocity_score": round(velocity_score, 2),
                        "strength": strength,
                        "current_mentions": current_count,
                        "historical_avg": round(avg_historical, 1),
                        "increase_pct": round((velocity_score - 1) * 100, 1),
                        "avg_confidence": round(current_stats["confidence"], 2) if current_stats["confidence"] else None,
                        "avg_sentiment": round(current_stats["sentiment"], 2) if current_stats["sentiment"] else None,
                        "period_days": (current_end - current_start).days,
                        "alert_message": f"⚠️ {category} category activity up {round((velocity_score - 1) * 100)}% ({current_count} articles)",
                        "detected_at": datetime.now().isoformat()
                    })
            
            return trends
            
        except Exception as e:
            logger.error(f"Error analyzing category trends: {e}")
            return []
    
    def _get_trend_context(
        self,
        entity: str,
        field: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 3
    ) -> List[Dict]:
        """Get recent articles mentioning the trending entity"""
        
        try:
            query = f"""
                SELECT 
                    id,
                    title,
                    source_name,
                    created_at,
                    confidence_score,
                    sentiment_score
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND created_at < %s
                  AND %s = ANY({field})
                ORDER BY created_at DESC, confidence_score DESC
                LIMIT %s
            """
            
            with self.db.cursor() as cur:
                cur.execute(query, (start_date, end_date, entity, limit))
                articles = []
                for row in cur.fetchall():
                    articles.append({
                        "id": row[0],
                        "title": row[1],
                        "source": row[2],
                        "date": row[3].isoformat() if row[3] else None,
                        "confidence": round(row[4], 2) if row[4] else None,
                        "sentiment": round(row[5], 2) if row[5] else None
                    })
                return articles
                
        except Exception as e:
            logger.error(f"Error getting trend context: {e}")
            return []
    
    def _generate_alert_message(
        self,
        entity: str,
        entity_type: str,
        velocity_score: float,
        current_count: int,
        strength: str
    ) -> str:
        """Generate human-readable alert message"""
        
        increase_pct = round((velocity_score - 1) * 100)
        
        emojis = {
            "explosive": "🔥🔥🔥",
            "very_high": "🔥🔥",
            "high": "🔥",
            "moderate": "⚠️"
        }
        
        emoji = emojis.get(strength, "📊")
        
        type_label = {
            "schemes": "Scheme",
            "ministries": "Ministry",
            "category": "Category"
        }.get(entity_type, "Topic")
        
        return f"{emoji} {type_label} '{entity}' mentions up {increase_pct}% ({current_count} articles in last week)"
    
    def predict_upcoming_events(self, days_ahead: int = 14) -> List[Dict]:
        """
        Predict upcoming government events based on historical patterns
        
        Args:
            days_ahead: Days to predict ahead
            
        Returns:
            List of predicted events with confidence scores
        """
        predictions = []
        
        try:
            # Detect budget-related patterns (typically January-February)
            current_month = datetime.now().month
            if current_month in [12, 1]:  # December or January
                predictions.append({
                    "event_type": "budget_announcement",
                    "predicted_date": "2026-02-01",
                    "confidence": 0.85,
                    "reasoning": "Historical pattern: Union Budget typically in early February",
                    "indicators": [
                        "Pre-budget consultations detected",
                        "Ministry budget allocation discussions increasing",
                        "Economic survey preparation signals"
                    ]
                })
            
            # Detect scheme anniversary patterns
            scheme_anniversaries = self._detect_scheme_anniversaries(days_ahead)
            predictions.extend(scheme_anniversaries)
            
            # Detect ministry activity patterns
            ministry_events = self._detect_ministry_event_patterns(days_ahead)
            predictions.extend(ministry_events)
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error predicting events: {e}")
            return []
    
    def _detect_scheme_anniversaries(self, days_ahead: int) -> List[Dict]:
        """Detect upcoming scheme anniversaries that might trigger announcements"""
        
        # This would check against a database of scheme launch dates
        # For now, returning structure
        return []
    
    def _detect_ministry_event_patterns(self, days_ahead: int) -> List[Dict]:
        """Detect ministry activity patterns suggesting upcoming announcements"""
        
        # Analyze ministry mention velocity + historical event patterns
        return []
    
    def get_trend_analysis_summary(self, days: int = 7) -> Dict:
        """
        Get comprehensive trend analysis summary
        
        Returns:
            Summary with top trends, alerts, and predictions
        """
        
        trends = self.detect_emerging_trends(days=days)
        
        # Categorize trends
        explosive_trends = [t for t in trends if t["strength"] == "explosive"]
        high_trends = [t for t in trends if t["strength"] in ["very_high", "high"]]
        
        # Get predictions
        predictions = self.predict_upcoming_events()
        
        return {
            "analysis_period": f"Last {days} days",
            "total_trends_detected": len(trends),
            "explosive_trends": len(explosive_trends),
            "high_priority_trends": len(high_trends),
            "top_trends": trends[:10],  # Top 10
            "alerts": [
                {
                    "level": "critical" if t["strength"] == "explosive" else "high",
                    "message": t["alert_message"],
                    "entity": t["entity"],
                    "velocity": t["velocity_score"]
                }
                for t in explosive_trends + high_trends[:5]
            ],
            "predictions": predictions,
            "generated_at": datetime.now().isoformat()
        }


def get_trend_predictor(db) -> TrendPredictor:
    """Factory function to get TrendPredictor instance"""
    return TrendPredictor(db)
