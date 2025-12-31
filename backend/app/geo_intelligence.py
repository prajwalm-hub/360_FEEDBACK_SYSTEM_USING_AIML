"""
Geospatial Intelligence Dashboard
Live maps showing government news heat zones, scheme coverage, ministry activity
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class GeoIntelligence:
    """Analyze geographic distribution of government news"""
    
    # Indian states and UTs with coordinates (approximate centers)
    STATE_COORDINATES = {
        "Andhra Pradesh": {"lat": 15.9129, "lng": 79.7400},
        "Arunachal Pradesh": {"lat": 28.2180, "lng": 94.7278},
        "Assam": {"lat": 26.2006, "lng": 92.9376},
        "Bihar": {"lat": 25.0961, "lng": 85.3131},
        "Chhattisgarh": {"lat": 21.2787, "lng": 81.8661},
        "Goa": {"lat": 15.2993, "lng": 74.1240},
        "Gujarat": {"lat": 22.2587, "lng": 71.1924},
        "Haryana": {"lat": 29.0588, "lng": 76.0856},
        "Himachal Pradesh": {"lat": 31.1048, "lng": 77.1734},
        "Jharkhand": {"lat": 23.6102, "lng": 85.2799},
        "Karnataka": {"lat": 15.3173, "lng": 75.7139},
        "Kerala": {"lat": 10.8505, "lng": 76.2711},
        "Madhya Pradesh": {"lat": 22.9734, "lng": 78.6569},
        "Maharashtra": {"lat": 19.7515, "lng": 75.7139},
        "Manipur": {"lat": 24.6637, "lng": 93.9063},
        "Meghalaya": {"lat": 25.4670, "lng": 91.3662},
        "Mizoram": {"lat": 23.1645, "lng": 92.9376},
        "Nagaland": {"lat": 26.1584, "lng": 94.5624},
        "Odisha": {"lat": 20.9517, "lng": 85.0985},
        "Punjab": {"lat": 31.1471, "lng": 75.3412},
        "Rajasthan": {"lat": 27.0238, "lng": 74.2179},
        "Sikkim": {"lat": 27.5330, "lng": 88.5122},
        "Tamil Nadu": {"lat": 11.1271, "lng": 78.6569},
        "Telangana": {"lat": 18.1124, "lng": 79.0193},
        "Tripura": {"lat": 23.9408, "lng": 91.9882},
        "Uttar Pradesh": {"lat": 26.8467, "lng": 80.9462},
        "Uttarakhand": {"lat": 30.0668, "lng": 79.0193},
        "West Bengal": {"lat": 22.9868, "lng": 87.8550},
        "Andaman and Nicobar Islands": {"lat": 11.7401, "lng": 92.6586},
        "Chandigarh": {"lat": 30.7333, "lng": 76.7794},
        "Dadra and Nagar Haveli and Daman and Diu": {"lat": 20.1809, "lng": 73.0169},
        "Delhi": {"lat": 28.7041, "lng": 77.1025},
        "Jammu and Kashmir": {"lat": 33.7782, "lng": 76.5762},
        "Ladakh": {"lat": 34.1526, "lng": 77.5771},
        "Lakshadweep": {"lat": 10.5667, "lng": 72.6417},
        "Puducherry": {"lat": 11.9416, "lng": 79.8083}
    }
    
    def __init__(self, db):
        self.db = db
    
    def get_heat_map_data(
        self,
        days: int = 30,
        min_articles: int = 1
    ) -> Dict:
        """
        Generate heat map data showing news activity by state
        
        Args:
            days: Days to analyze
            min_articles: Minimum articles to include state
            
        Returns:
            GeoJSON-compatible data for mapping
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            # Get article counts by region
            query = """
                SELECT 
                    detected_region,
                    COUNT(*) as article_count,
                    AVG(confidence_score) as avg_confidence,
                    AVG(sentiment_score) as avg_sentiment,
                    COUNT(DISTINCT source_name) as unique_sources
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND detected_region IS NOT NULL
                  AND detected_region != 'India'
                GROUP BY detected_region
                HAVING COUNT(*) >= %s
            """
            
            with self.db.cursor() as cur:
                cur.execute(query, (start_date, min_articles))
                
                features = []
                max_count = 0
                
                for row in cur.fetchall():
                    region = row[0]
                    article_count = row[1]
                    avg_confidence = row[2]
                    avg_sentiment = row[3]
                    unique_sources = row[4]
                    
                    max_count = max(max_count, article_count)
                    
                    # Get coordinates
                    coords = self.STATE_COORDINATES.get(region)
                    if coords:
                        features.append({
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [coords["lng"], coords["lat"]]
                            },
                            "properties": {
                                "name": region,
                                "article_count": article_count,
                                "avg_confidence": round(avg_confidence, 2) if avg_confidence else None,
                                "avg_sentiment": round(avg_sentiment, 2) if avg_sentiment else None,
                                "unique_sources": unique_sources,
                                "heat_intensity": self._calculate_heat_intensity(article_count, max_count)
                            }
                        })
                
                return {
                    "type": "FeatureCollection",
                    "features": features,
                    "metadata": {
                        "period_days": days,
                        "total_states": len(features),
                        "max_articles": max_count,
                        "generated_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Error generating heat map: {e}")
            return {"type": "FeatureCollection", "features": [], "error": str(e)}
    
    def _calculate_heat_intensity(self, count: int, max_count: int) -> float:
        """Calculate heat intensity (0.0-1.0) for visualization"""
        if max_count == 0:
            return 0.0
        return min(count / max_count, 1.0)
    
    def get_scheme_coverage_map(
        self,
        scheme: str,
        days: int = 90
    ) -> Dict:
        """
        Show which states are implementing/covering a specific scheme
        
        Args:
            scheme: Scheme name
            days: Days to analyze
            
        Returns:
            Map data showing scheme coverage by state
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            query = """
                SELECT 
                    detected_region,
                    COUNT(*) as article_count,
                    AVG(confidence_score) as avg_confidence,
                    AVG(sentiment_score) as avg_sentiment,
                    array_agg(DISTINCT goi_ministries) as ministries,
                    MIN(created_at) as first_mention,
                    MAX(created_at) as latest_mention
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND %s = ANY(goi_schemes)
                  AND detected_region IS NOT NULL
                  AND detected_region != 'India'
                GROUP BY detected_region
            """
            
            with self.db.cursor() as cur:
                cur.execute(query, (start_date, scheme))
                
                features = []
                
                for row in cur.fetchall():
                    region = row[0]
                    coords = self.STATE_COORDINATES.get(region)
                    
                    if coords:
                        # Flatten ministries array
                        ministries = []
                        if row[4]:
                            for ministry_array in row[4]:
                                if ministry_array:
                                    ministries.extend(ministry_array)
                        unique_ministries = list(set(ministries))
                        
                        features.append({
                            "type": "Feature",
                            "geometry": {
                                "type": "Point",
                                "coordinates": [coords["lng"], coords["lat"]]
                            },
                            "properties": {
                                "name": region,
                                "scheme": scheme,
                                "article_count": row[1],
                                "avg_confidence": round(row[2], 2) if row[2] else None,
                                "avg_sentiment": round(row[3], 2) if row[3] else None,
                                "ministries": unique_ministries[:3],  # Top 3
                                "first_mention": row[5].isoformat() if row[5] else None,
                                "latest_mention": row[6].isoformat() if row[6] else None,
                                "coverage_status": self._determine_coverage_status(row[1], row[2])
                            }
                        })
                
                return {
                    "type": "FeatureCollection",
                    "features": features,
                    "metadata": {
                        "scheme": scheme,
                        "period_days": days,
                        "states_covered": len(features),
                        "generated_at": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"Error generating scheme coverage map: {e}")
            return {"type": "FeatureCollection", "features": [], "error": str(e)}
    
    def _determine_coverage_status(self, article_count: int, avg_confidence: float) -> str:
        """Determine coverage status for a region"""
        
        if article_count >= 10 and (avg_confidence or 0) >= 0.7:
            return "high_coverage"
        elif article_count >= 5:
            return "medium_coverage"
        else:
            return "low_coverage"
    
    def get_ministry_footprint(
        self,
        ministry: str,
        days: int = 60
    ) -> Dict:
        """
        Track ministry activity across states
        
        Args:
            ministry: Ministry name
            days: Days to analyze
            
        Returns:
            Geographic footprint of ministry activity
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            query = """
                SELECT 
                    detected_region,
                    COUNT(*) as article_count,
                    array_agg(DISTINCT goi_schemes) as schemes,
                    AVG(sentiment_score) as avg_sentiment
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND %s = ANY(goi_ministries)
                  AND detected_region IS NOT NULL
                  AND detected_region != 'India'
                GROUP BY detected_region
                ORDER BY article_count DESC
            """
            
            with self.db.cursor() as cur:
                cur.execute(query, (start_date, ministry))
                
                footprint = []
                
                for row in cur.fetchall():
                    region = row[0]
                    coords = self.STATE_COORDINATES.get(region)
                    
                    if coords:
                        # Flatten schemes
                        schemes = []
                        if row[2]:
                            for scheme_array in row[2]:
                                if scheme_array:
                                    schemes.extend(scheme_array)
                        unique_schemes = list(set(schemes))
                        
                        footprint.append({
                            "region": region,
                            "coordinates": coords,
                            "article_count": row[1],
                            "schemes": unique_schemes[:5],  # Top 5
                            "avg_sentiment": round(row[3], 2) if row[3] else None
                        })
                
                return {
                    "ministry": ministry,
                    "period_days": days,
                    "total_states": len(footprint),
                    "footprint": footprint,
                    "generated_at": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error getting ministry footprint: {e}")
            return {"error": str(e)}
    
    def detect_crisis_zones(
        self,
        days: int = 7,
        sentiment_threshold: float = -0.5,
        min_articles: int = 3
    ) -> List[Dict]:
        """
        Detect regions with sudden spike in negative news
        
        Args:
            days: Days to analyze
            sentiment_threshold: Negative sentiment threshold
            min_articles: Minimum articles to trigger alert
            
        Returns:
            List of crisis zones with details
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        try:
            query = """
                SELECT 
                    detected_region,
                    COUNT(*) as article_count,
                    AVG(sentiment_score) as avg_sentiment,
                    array_agg(content_category) as categories,
                    array_agg(title ORDER BY created_at DESC) as recent_titles
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND detected_region IS NOT NULL
                  AND detected_region != 'India'
                  AND sentiment_score < %s
                GROUP BY detected_region
                HAVING COUNT(*) >= %s
                ORDER BY AVG(sentiment_score) ASC
            """
            
            with self.db.cursor() as cur:
                cur.execute(query, (start_date, sentiment_threshold, min_articles))
                
                crisis_zones = []
                
                for row in cur.fetchall():
                    # Count category occurrences
                    categories = row[3] or []
                    category_counts = defaultdict(int)
                    for cat in categories:
                        if cat:
                            category_counts[cat] += 1
                    
                    top_category = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else "Unknown"
                    
                    crisis_zones.append({
                        "region": row[0],
                        "severity": "high" if row[2] < -0.7 else "medium",
                        "article_count": row[1],
                        "avg_sentiment": round(row[2], 2),
                        "primary_issue": top_category,
                        "recent_headlines": row[4][:3] if row[4] else [],
                        "alert_message": f"⚠️ {row[0]}: {row[1]} negative articles about {top_category} (sentiment: {round(row[2], 2)})"
                    })
                
                return crisis_zones
                
        except Exception as e:
            logger.error(f"Error detecting crisis zones: {e}")
            return []
    
    def get_regional_comparison(
        self,
        regions: List[str],
        days: int = 30
    ) -> Dict:
        """
        Compare government news activity across specific regions
        
        Args:
            regions: List of region names
            days: Days to analyze
            
        Returns:
            Comparison data
        """
        
        start_date = datetime.now() - timedelta(days=days)
        
        comparison = {
            "regions": regions,
            "period_days": days,
            "comparison_data": []
        }
        
        try:
            for region in regions:
                query = """
                    SELECT 
                        COUNT(*) as total_articles,
                        AVG(confidence_score) as avg_confidence,
                        AVG(sentiment_score) as avg_sentiment,
                        array_agg(DISTINCT goi_schemes) as schemes,
                        array_agg(DISTINCT goi_ministries) as ministries,
                        COUNT(DISTINCT content_category) as unique_categories
                    FROM articles
                    WHERE is_goi = TRUE
                      AND created_at >= %s
                      AND detected_region = %s
                """
                
                with self.db.cursor() as cur:
                    cur.execute(query, (start_date, region))
                    row = cur.fetchone()
                    
                    if row:
                        # Flatten arrays
                        schemes = []
                        if row[3]:
                            for scheme_array in row[3]:
                                if scheme_array:
                                    schemes.extend(scheme_array)
                        
                        ministries = []
                        if row[4]:
                            for ministry_array in row[4]:
                                if ministry_array:
                                    ministries.extend(ministry_array)
                        
                        comparison["comparison_data"].append({
                            "region": region,
                            "total_articles": row[0],
                            "avg_confidence": round(row[1], 2) if row[1] else None,
                            "avg_sentiment": round(row[2], 2) if row[2] else None,
                            "unique_schemes": len(set(schemes)),
                            "unique_ministries": len(set(ministries)),
                            "unique_categories": row[5]
                        })
            
            # Add insights
            if comparison["comparison_data"]:
                most_active = max(comparison["comparison_data"], key=lambda x: x["total_articles"])
                best_sentiment = max(comparison["comparison_data"], key=lambda x: x["avg_sentiment"] or -1)
                
                comparison["insights"] = {
                    "most_active_region": most_active["region"],
                    "best_sentiment_region": best_sentiment["region"]
                }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error in regional comparison: {e}")
            return {"error": str(e)}


def get_geo_intelligence(db) -> GeoIntelligence:
    """Factory function to get GeoIntelligence instance"""
    return GeoIntelligence(db)
