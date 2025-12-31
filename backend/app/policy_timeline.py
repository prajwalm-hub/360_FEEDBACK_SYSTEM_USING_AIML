"""
Interactive Policy Impact Visualization
Track scheme evolution from announcement → implementation → impact
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics

logger = logging.getLogger(__name__)


class PolicyTimelineAnalyzer:
    """Analyze policy/scheme lifecycle and impact over time"""
    
    def __init__(self, db):
        self.db = db
    
    def get_scheme_timeline(
        self,
        scheme: str,
        months: int = 12
    ) -> Dict:
        """
        Get comprehensive timeline for a scheme showing evolution
        
        Args:
            scheme: Scheme name
            months: Months to analyze
            
        Returns:
            Timeline with milestones, sentiment evolution, impact metrics
        """
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        # Get all articles about the scheme
        articles = self._get_scheme_articles(scheme, start_date, end_date)
        
        if not articles:
            return {
                "scheme": scheme,
                "error": "No articles found for this scheme",
                "period": f"Last {months} months"
            }
        
        # Build timeline
        timeline = {
            "scheme": scheme,
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "months": months
            },
            "overview": self._generate_overview(articles, scheme),
            "milestones": self._extract_milestones(articles),
            "sentiment_evolution": self._analyze_sentiment_evolution(articles, months),
            "impact_metrics": self._extract_impact_metrics(articles),
            "regional_rollout": self._analyze_regional_rollout(articles),
            "ministry_involvement": self._get_ministry_involvement(articles),
            "media_coverage": self._analyze_media_coverage(articles, months),
            "related_schemes": self._find_related_schemes(articles, scheme),
            "generated_at": datetime.now().isoformat()
        }
        
        return timeline
    
    def _get_scheme_articles(
        self,
        scheme: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get all articles mentioning the scheme"""
        
        try:
            query = """
                SELECT 
                    id, title, full_text, source_name, created_at,
                    confidence_score, sentiment_score, sentiment,
                    goi_schemes, goi_ministries, detected_region,
                    content_category, goi_keywords
                FROM articles
                WHERE is_goi = TRUE
                  AND created_at >= %s
                  AND created_at <= %s
                  AND %s = ANY(goi_schemes)
                ORDER BY created_at ASC
            """
            
            with self.db.cursor() as cur:
                cur.execute(query, (start_date, end_date, scheme))
                articles = []
                for row in cur.fetchall():
                    articles.append({
                        "id": row[0],
                        "title": row[1],
                        "full_text": row[2],
                        "source_name": row[3],
                        "created_at": row[4],
                        "confidence_score": row[5],
                        "sentiment_score": row[6],
                        "sentiment": row[7],
                        "goi_schemes": row[8] or [],
                        "goi_ministries": row[9] or [],
                        "detected_region": row[10],
                        "content_category": row[11],
                        "goi_keywords": row[12] or []
                    })
                return articles
                
        except Exception as e:
            logger.error(f"Error getting scheme articles: {e}")
            return []
    
    def _generate_overview(self, articles: List[Dict], scheme: str) -> Dict:
        """Generate scheme overview"""
        
        total_articles = len(articles)
        avg_sentiment = statistics.mean([a["sentiment_score"] for a in articles if a["sentiment_score"] is not None]) if articles else 0
        
        # Get first and last article dates
        first_article = min(articles, key=lambda x: x["created_at"])
        last_article = max(articles, key=lambda x: x["created_at"])
        
        # Count unique sources and regions
        unique_sources = len(set(a["source_name"] for a in articles if a["source_name"]))
        unique_regions = len(set(a["detected_region"] for a in articles if a["detected_region"] and a["detected_region"] != "India"))
        
        return {
            "scheme_name": scheme,
            "total_articles": total_articles,
            "first_mention": first_article["created_at"].isoformat(),
            "latest_mention": last_article["created_at"].isoformat(),
            "avg_sentiment_score": round(avg_sentiment, 2),
            "unique_media_sources": unique_sources,
            "states_covered": unique_regions,
            "overall_sentiment": self._categorize_sentiment(avg_sentiment)
        }
    
    def _extract_milestones(self, articles: List[Dict]) -> List[Dict]:
        """Extract key milestones from articles"""
        
        milestone_keywords = {
            "announcement": ["announced", "launched", "introduced", "unveiled"],
            "budget_allocation": ["budget", "allocated", "sanctioned", "approved funds"],
            "implementation": ["implemented", "rolled out", "started", "began"],
            "achievement": ["achieved", "reached", "crossed", "milestone", "target met"],
            "expansion": ["expanded", "extended", "increased coverage", "scaling up"],
            "review": ["reviewed", "evaluated", "assessment", "performance review"]
        }
        
        milestones = []
        
        for article in articles:
            text = (article.get("full_text") or "").lower()
            title = (article.get("title") or "").lower()
            
            for milestone_type, keywords in milestone_keywords.items():
                if any(kw in text or kw in title for kw in keywords):
                    milestones.append({
                        "date": article["created_at"].isoformat(),
                        "type": milestone_type,
                        "title": article["title"],
                        "source": article["source_name"],
                        "sentiment": article["sentiment"],
                        "confidence": round(article["confidence_score"], 2) if article["confidence_score"] else None,
                        "article_id": article["id"]
                    })
                    break  # Only one milestone type per article
        
        # Sort by date
        milestones.sort(key=lambda x: x["date"])
        
        return milestones
    
    def _analyze_sentiment_evolution(
        self,
        articles: List[Dict],
        months: int
    ) -> Dict:
        """Analyze how sentiment evolved over time"""
        
        # Group by month
        monthly_sentiment = defaultdict(list)
        
        for article in articles:
            if article["sentiment_score"] is not None:
                month_key = article["created_at"].strftime("%Y-%m")
                monthly_sentiment[month_key].append(article["sentiment_score"])
        
        # Calculate averages
        timeline = []
        for month in sorted(monthly_sentiment.keys()):
            scores = monthly_sentiment[month]
            avg_score = statistics.mean(scores)
            timeline.append({
                "month": month,
                "avg_sentiment": round(avg_score, 2),
                "article_count": len(scores),
                "sentiment_label": self._categorize_sentiment(avg_score)
            })
        
        # Detect trends
        if len(timeline) >= 2:
            first_half_avg = statistics.mean([t["avg_sentiment"] for t in timeline[:len(timeline)//2]])
            second_half_avg = statistics.mean([t["avg_sentiment"] for t in timeline[len(timeline)//2:]])
            trend = "improving" if second_half_avg > first_half_avg else "declining" if second_half_avg < first_half_avg else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "timeline": timeline,
            "trend": trend,
            "current_sentiment": timeline[-1]["avg_sentiment"] if timeline else None
        }
    
    def _categorize_sentiment(self, score: float) -> str:
        """Categorize sentiment score"""
        if score >= 0.4:
            return "positive"
        elif score <= -0.4:
            return "negative"
        else:
            return "neutral"
    
    def _extract_impact_metrics(self, articles: List[Dict]) -> Dict:
        """Extract impact metrics (beneficiaries, budget, coverage)"""
        
        import re
        
        metrics = {
            "beneficiaries": [],
            "budget_amounts": [],
            "coverage_percentages": [],
            "timeline": []
        }
        
        # Patterns
        beneficiary_pattern = r'(\d+(?:\.\d+)?)\s*(crore|lakh|million)?\s*(farmers|students|beneficiaries|people|families|workers)'
        budget_pattern = r'[₹$]\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(crore|lakh|billion|million|thousand)?'
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%\s*(coverage|covered|reached|achieved)'
        
        for article in articles:
            text = article.get("full_text") or ""
            date = article["created_at"]
            
            # Beneficiaries
            beneficiary_matches = re.findall(beneficiary_pattern, text, re.IGNORECASE)
            for match in beneficiary_matches:
                metrics["beneficiaries"].append({
                    "date": date.isoformat(),
                    "value": f"{match[0]} {match[1] or ''} {match[2]}".strip(),
                    "article_id": article["id"]
                })
            
            # Budget
            budget_matches = re.findall(budget_pattern, text)
            for match in budget_matches:
                metrics["budget_amounts"].append({
                    "date": date.isoformat(),
                    "value": f"₹{match[0]} {match[1] or ''}".strip(),
                    "article_id": article["id"]
                })
            
            # Coverage percentage
            pct_matches = re.findall(percentage_pattern, text, re.IGNORECASE)
            for match in pct_matches:
                metrics["coverage_percentages"].append({
                    "date": date.isoformat(),
                    "value": f"{match[0]}%",
                    "context": match[1],
                    "article_id": article["id"]
                })
        
        # Create timeline of metrics
        all_metrics = []
        for metric_list in [metrics["beneficiaries"], metrics["budget_amounts"], metrics["coverage_percentages"]]:
            all_metrics.extend(metric_list)
        
        all_metrics.sort(key=lambda x: x["date"])
        metrics["timeline"] = all_metrics
        
        return metrics
    
    def _analyze_regional_rollout(self, articles: List[Dict]) -> Dict:
        """Analyze regional rollout over time"""
        
        # Track first mention per region
        regional_timeline = {}
        regional_counts = defaultdict(int)
        
        for article in articles:
            region = article.get("detected_region")
            if region and region != "India":
                regional_counts[region] += 1
                
                # Track first mention
                if region not in regional_timeline:
                    regional_timeline[region] = {
                        "first_mention": article["created_at"].isoformat(),
                        "article_count": 0
                    }
                
                regional_timeline[region]["article_count"] += 1
        
        # Sort by first mention
        rollout_sequence = sorted(
            [{"region": r, **data} for r, data in regional_timeline.items()],
            key=lambda x: x["first_mention"]
        )
        
        return {
            "total_regions": len(rollout_sequence),
            "rollout_sequence": rollout_sequence,
            "top_regions_by_coverage": sorted(
                regional_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        }
    
    def _get_ministry_involvement(self, articles: List[Dict]) -> Dict:
        """Get ministry involvement in scheme"""
        
        ministry_counts = defaultdict(int)
        
        for article in articles:
            for ministry in article.get("goi_ministries", []):
                ministry_counts[ministry] += 1
        
        sorted_ministries = sorted(ministry_counts.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_ministries": len(sorted_ministries),
            "primary_ministry": sorted_ministries[0][0] if sorted_ministries else None,
            "all_ministries": [
                {"ministry": m, "mentions": count}
                for m, count in sorted_ministries
            ]
        }
    
    def _analyze_media_coverage(self, articles: List[Dict], months: int) -> Dict:
        """Analyze media coverage patterns"""
        
        # Coverage by month
        monthly_coverage = defaultdict(int)
        
        for article in articles:
            month_key = article["created_at"].strftime("%Y-%m")
            monthly_coverage[month_key] += 1
        
        # Top sources
        source_counts = defaultdict(int)
        for article in articles:
            if article.get("source_name"):
                source_counts[article["source_name"]] += 1
        
        top_sources = sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Calculate velocity (recent vs older)
        mid_point = datetime.now() - timedelta(days=(months * 30) // 2)
        recent_count = sum(1 for a in articles if a["created_at"] >= mid_point)
        older_count = len(articles) - recent_count
        
        velocity = "increasing" if recent_count > older_count else "decreasing" if recent_count < older_count else "stable"
        
        return {
            "total_articles": len(articles),
            "monthly_breakdown": dict(monthly_coverage),
            "top_sources": [{"source": s, "articles": c} for s, c in top_sources],
            "coverage_velocity": velocity,
            "recent_vs_older": {
                "recent_half": recent_count,
                "older_half": older_count
            }
        }
    
    def _find_related_schemes(self, articles: List[Dict], current_scheme: str) -> List[str]:
        """Find schemes frequently mentioned together"""
        
        scheme_co_occurrence = defaultdict(int)
        
        for article in articles:
            for scheme in article.get("goi_schemes", []):
                if scheme != current_scheme:
                    scheme_co_occurrence[scheme] += 1
        
        # Sort and return top 5
        related = sorted(scheme_co_occurrence.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [
            {"scheme": s, "co_mentions": count}
            for s, count in related
        ]
    
    def compare_schemes(
        self,
        schemes: List[str],
        months: int = 6
    ) -> Dict:
        """
        Compare multiple schemes side-by-side
        
        Args:
            schemes: List of scheme names to compare
            months: Months to analyze
            
        Returns:
            Comparison data with metrics for each scheme
        """
        
        comparison = {
            "schemes": schemes,
            "period": f"Last {months} months",
            "comparison_data": []
        }
        
        for scheme in schemes:
            timeline = self.get_scheme_timeline(scheme, months)
            
            if "error" not in timeline:
                comparison["comparison_data"].append({
                    "scheme": scheme,
                    "total_articles": timeline["overview"]["total_articles"],
                    "avg_sentiment": timeline["overview"]["avg_sentiment_score"],
                    "states_covered": timeline["overview"]["states_covered"],
                    "media_sources": timeline["overview"]["unique_media_sources"],
                    "sentiment_trend": timeline["sentiment_evolution"]["trend"],
                    "milestones_count": len(timeline["milestones"])
                })
        
        # Add comparison insights
        if comparison["comparison_data"]:
            # Most covered
            most_covered = max(comparison["comparison_data"], key=lambda x: x["total_articles"])
            # Best sentiment
            best_sentiment = max(comparison["comparison_data"], key=lambda x: x["avg_sentiment"])
            # Widest reach
            widest_reach = max(comparison["comparison_data"], key=lambda x: x["states_covered"])
            
            comparison["insights"] = {
                "most_media_coverage": most_covered["scheme"],
                "best_sentiment": best_sentiment["scheme"],
                "widest_geographic_reach": widest_reach["scheme"]
            }
        
        return comparison


def get_policy_timeline_analyzer(db) -> PolicyTimelineAnalyzer:
    """Factory function to get PolicyTimelineAnalyzer instance"""
    return PolicyTimelineAnalyzer(db)
