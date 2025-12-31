"""
Automated Press Brief Generator for PIB Officers
Generates draft press briefs from verified high-confidence articles
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)


class PressBriefGenerator:
    """Generate press briefs from government news articles"""
    
    def __init__(self, db):
        self.db = db
    
    def generate_press_brief(
        self,
        scheme: Optional[str] = None,
        ministry: Optional[str] = None,
        category: Optional[str] = None,
        days: int = 7,
        focus: List[str] = None,
        min_confidence: float = 0.7
    ) -> Dict:
        """
        Generate a press brief from verified articles
        
        Args:
            scheme: Specific scheme to focus on
            ministry: Specific ministry to focus on
            category: Content category to focus on
            days: Days to analyze
            focus: Areas to emphasize ["achievements", "coverage", "implementation", "challenges"]
            min_confidence: Minimum confidence score for articles
            
        Returns:
            Structured press brief with sections
        """
        
        if focus is None:
            focus = ["achievements", "coverage", "implementation"]
        
        # Collect relevant articles
        articles = self._collect_articles(
            scheme=scheme,
            ministry=ministry,
            category=category,
            days=days,
            min_confidence=min_confidence
        )
        
        if not articles:
            return {
                "error": "No articles found matching criteria",
                "criteria": {
                    "scheme": scheme,
                    "ministry": ministry,
                    "category": category,
                    "days": days
                }
            }
        
        # Generate brief structure
        brief = {
            "title": self._generate_title(scheme, ministry, category, days),
            "date_range": self._format_date_range(days),
            "generated_at": datetime.now().isoformat(),
            "total_articles": len(articles),
            "avg_confidence": round(sum(a["confidence_score"] for a in articles if a["confidence_score"]) / len(articles), 2),
            "sections": {}
        }
        
        # Key highlights
        if "achievements" in focus:
            brief["sections"]["key_highlights"] = self._generate_highlights(articles, scheme, ministry)
        
        # Regional coverage
        if "coverage" in focus:
            brief["sections"]["regional_coverage"] = self._analyze_regional_coverage(articles)
        
        # Implementation status
        if "implementation" in focus:
            brief["sections"]["implementation"] = self._analyze_implementation(articles, scheme)
        
        # Media sentiment
        brief["sections"]["media_sentiment"] = self._analyze_sentiment(articles)
        
        # Talking points
        brief["sections"]["talking_points"] = self._generate_talking_points(articles, scheme, ministry)
        
        # Challenges (if requested)
        if "challenges" in focus:
            brief["sections"]["challenges"] = self._identify_challenges(articles)
        
        # Statistics
        brief["sections"]["statistics"] = self._extract_statistics(articles)
        
        return brief
    
    def _collect_articles(
        self,
        scheme: Optional[str],
        ministry: Optional[str],
        category: Optional[str],
        days: int,
        min_confidence: float
    ) -> List[Dict]:
        """Collect relevant articles based on criteria"""
        
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Build query
            conditions = ["is_goi = TRUE", "created_at >= %s", "confidence_score >= %s"]
            params = [start_date, min_confidence]
            
            if scheme:
                conditions.append("%s = ANY(goi_schemes)")
                params.append(scheme)
            
            if ministry:
                conditions.append("%s = ANY(goi_ministries)")
                params.append(ministry)
            
            if category:
                conditions.append("content_category = %s")
                params.append(category)
            
            query = f"""
                SELECT 
                    id, title, full_text, source_name, created_at,
                    confidence_score, sentiment_score, sentiment,
                    goi_schemes, goi_ministries, detected_region,
                    content_category, goi_keywords
                FROM articles
                WHERE {" AND ".join(conditions)}
                ORDER BY confidence_score DESC, created_at DESC
                LIMIT 100
            """
            
            with self.db.cursor() as cur:
                cur.execute(query, params)
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
            logger.error(f"Error collecting articles: {e}")
            return []
    
    def _generate_title(
        self,
        scheme: Optional[str],
        ministry: Optional[str],
        category: Optional[str],
        days: int
    ) -> str:
        """Generate press brief title"""
        
        if scheme:
            return f"{scheme.upper()} - WEEKLY BRIEF"
        elif ministry:
            return f"{ministry.upper()} - WEEKLY BRIEF"
        elif category:
            return f"{category.upper()} NEWS BRIEF"
        else:
            return f"GOVERNMENT NEWS BRIEF - LAST {days} DAYS"
    
    def _format_date_range(self, days: int) -> str:
        """Format date range for brief"""
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        return f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    
    def _generate_highlights(
        self,
        articles: List[Dict],
        scheme: Optional[str],
        ministry: Optional[str]
    ) -> List[str]:
        """Generate key highlights from articles"""
        
        highlights = []
        
        # Extract statistics and key points
        stats = self._extract_statistics(articles)
        
        # Top 5 most confident articles' titles
        top_articles = sorted(articles, key=lambda x: x["confidence_score"] or 0, reverse=True)[:5]
        
        for article in top_articles:
            # Extract key sentences (simplified - could use NLP for better extraction)
            title = article["title"]
            if len(title) > 20:  # Valid title
                highlights.append(f"• {title}")
        
        # Add statistics as highlights
        if stats:
            if stats.get("beneficiaries"):
                highlights.insert(0, f"• {stats['beneficiaries']} beneficiaries reached")
            if stats.get("budget"):
                highlights.insert(0, f"• {stats['budget']} allocated/disbursed")
        
        return highlights[:8]  # Top 8 highlights
    
    def _analyze_regional_coverage(self, articles: List[Dict]) -> Dict:
        """Analyze regional coverage of news"""
        
        regional_data = defaultdict(int)
        
        for article in articles:
            region = article.get("detected_region")
            if region and region != "India":  # Skip generic India
                regional_data[region] += 1
        
        # Sort by coverage
        sorted_regions = sorted(regional_data.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "total_regions": len(sorted_regions),
            "top_regions": [
                {"region": region, "articles": count}
                for region, count in sorted_regions[:10]
            ],
            "coverage_summary": self._format_regional_summary(sorted_regions[:5])
        }
    
    def _format_regional_summary(self, top_regions: List[Tuple[str, int]]) -> str:
        """Format regional coverage as text"""
        
        if not top_regions:
            return "Pan-India coverage"
        
        region_list = ", ".join([f"{region} ({count})" for region, count in top_regions])
        return f"Major coverage in: {region_list}"
    
    def _analyze_implementation(self, articles: List[Dict], scheme: Optional[str]) -> Dict:
        """Analyze implementation status from articles"""
        
        # Keywords indicating implementation status
        implementation_keywords = {
            "launched": ["launched", "inaugurated", "started", "begun"],
            "progress": ["progress", "ongoing", "implementing", "rollout"],
            "completed": ["completed", "achieved", "reached", "target met"],
            "challenges": ["delayed", "pending", "issues", "challenges"]
        }
        
        status_counts = defaultdict(int)
        
        for article in articles:
            text = (article.get("full_text") or "").lower()
            for status, keywords in implementation_keywords.items():
                if any(kw in text for kw in keywords):
                    status_counts[status] += 1
        
        total = sum(status_counts.values())
        
        return {
            "status_distribution": dict(status_counts),
            "summary": self._format_implementation_summary(status_counts, total)
        }
    
    def _format_implementation_summary(self, status_counts: Dict, total: int) -> str:
        """Format implementation summary"""
        
        if total == 0:
            return "Implementation status not clearly indicated in articles"
        
        # Find dominant status
        dominant = max(status_counts.items(), key=lambda x: x[1])
        
        summaries = {
            "launched": "Recent launches and new initiatives detected",
            "progress": "Implementation in progress across regions",
            "completed": "Targets and milestones being achieved",
            "challenges": "Some implementation challenges reported"
        }
        
        return summaries.get(dominant[0], "Mixed implementation signals")
    
    def _analyze_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyze media sentiment"""
        
        sentiment_counts = defaultdict(int)
        sentiment_scores = []
        
        for article in articles:
            sentiment = article.get("sentiment")
            score = article.get("sentiment_score")
            
            if sentiment:
                sentiment_counts[sentiment] += 1
            if score is not None:
                sentiment_scores.append(score)
        
        total = sum(sentiment_counts.values())
        avg_score = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        # Calculate percentages
        percentages = {
            s: round((count / total * 100), 1) if total > 0 else 0
            for s, count in sentiment_counts.items()
        }
        
        return {
            "distribution": dict(sentiment_counts),
            "percentages": percentages,
            "avg_score": round(avg_score, 2),
            "summary": self._format_sentiment_summary(percentages, avg_score)
        }
    
    def _format_sentiment_summary(self, percentages: Dict, avg_score: float) -> str:
        """Format sentiment summary"""
        
        positive_pct = percentages.get("positive", 0)
        
        if positive_pct >= 75:
            return f"Highly positive media coverage ({positive_pct}% positive sentiment)"
        elif positive_pct >= 50:
            return f"Mostly positive media coverage ({positive_pct}% positive sentiment)"
        elif positive_pct >= 30:
            return f"Mixed media coverage ({positive_pct}% positive sentiment)"
        else:
            return f"Neutral to negative media coverage ({positive_pct}% positive sentiment)"
    
    def _generate_talking_points(
        self,
        articles: List[Dict],
        scheme: Optional[str],
        ministry: Optional[str]
    ) -> List[str]:
        """Generate talking points for PIB officers"""
        
        talking_points = []
        
        # Extract most common keywords
        keyword_counts = defaultdict(int)
        for article in articles:
            for keyword in article.get("goi_keywords", []):
                keyword_counts[keyword] += 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Generate points based on top keywords and sentiment
        if top_keywords:
            talking_points.append(
                f"Focus areas: {', '.join([kw for kw, _ in top_keywords])}"
            )
        
        # Sentiment-based point
        sentiment_dist = defaultdict(int)
        for article in articles:
            if article.get("sentiment"):
                sentiment_dist[article["sentiment"]] += 1
        
        if sentiment_dist.get("positive", 0) > len(articles) * 0.6:
            talking_points.append("Strong positive media reception")
        
        # High confidence point
        high_conf_count = sum(1 for a in articles if (a.get("confidence_score") or 0) >= 0.8)
        if high_conf_count > len(articles) * 0.7:
            talking_points.append(
                f"High verification rate ({high_conf_count}/{len(articles)} articles verified)"
            )
        
        # Regional coverage point
        regions = set()
        for article in articles:
            if article.get("detected_region") and article["detected_region"] != "India":
                regions.add(article["detected_region"])
        
        if len(regions) >= 5:
            talking_points.append(f"Wide regional coverage ({len(regions)} states/regions)")
        
        return talking_points[:6]  # Top 6 points
    
    def _identify_challenges(self, articles: List[Dict]) -> List[str]:
        """Identify challenges mentioned in articles"""
        
        challenge_keywords = [
            "delayed", "pending", "challenges", "issues", "problems",
            "shortage", "lack of", "insufficient", "criticism"
        ]
        
        challenges = []
        
        for article in articles:
            text = (article.get("full_text") or "").lower()
            title = (article.get("title") or "").lower()
            
            # Check for challenge keywords
            for keyword in challenge_keywords:
                if keyword in text or keyword in title:
                    # Extract sentence containing keyword (simplified)
                    challenges.append(f"• {article['title'][:100]}...")
                    break
        
        return challenges[:5]  # Top 5 challenges
    
    def _extract_statistics(self, articles: List[Dict]) -> Dict:
        """Extract statistics from articles (numbers, budgets, beneficiaries)"""
        
        import re
        
        stats = {
            "beneficiaries": None,
            "budget": None,
            "coverage_pct": None,
            "numbers": []
        }
        
        # Patterns to match
        beneficiary_pattern = r'(\d+(?:\.\d+)?)\s*(crore|lakh|million|thousand)?\s*(farmers|students|beneficiaries|people|families)'
        budget_pattern = r'[₹$]\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(crore|lakh|billion|million|thousand)?'
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        
        for article in articles:
            text = article.get("full_text") or ""
            
            # Extract beneficiaries
            beneficiary_match = re.search(beneficiary_pattern, text, re.IGNORECASE)
            if beneficiary_match and not stats["beneficiaries"]:
                stats["beneficiaries"] = f"{beneficiary_match.group(1)} {beneficiary_match.group(2) or ''} {beneficiary_match.group(3)}".strip()
            
            # Extract budget
            budget_match = re.search(budget_pattern, text)
            if budget_match and not stats["budget"]:
                stats["budget"] = f"₹{budget_match.group(1)} {budget_match.group(2) or ''}".strip()
            
            # Extract percentages
            pct_matches = re.findall(percentage_pattern, text)
            if pct_matches:
                stats["numbers"].extend([f"{p}%" for p in pct_matches[:3]])
        
        return stats


def get_press_brief_generator(db) -> PressBriefGenerator:
    """Factory function to get PressBriefGenerator instance"""
    return PressBriefGenerator(db)
