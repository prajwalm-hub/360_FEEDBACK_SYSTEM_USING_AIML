from fastapi import APIRouter, Depends
from sqlalchemy import func, text
from datetime import datetime, timedelta
from .database import get_database, Article

router = APIRouter()

@router.get("/metrics")
async def get_metrics(db = Depends(get_database)):
    with db.get_session() as session:
        session.execute(text("SET statement_timeout = '10s'"))
        
        # Only show Government category articles
        total = session.query(func.count(Article.id)).filter(
            Article.should_show_pib == True,
            Article.content_category == 'Government'
        ).scalar() or 0
        
        # Today's articles
        yesterday = datetime.utcnow() - timedelta(days=1)
        today = session.query(Article).filter(
            Article.collected_at >= yesterday,
            Article.should_show_pib == True,
            Article.content_category == 'Government'
        ).count()
        
        # Yesterday's articles for trend
        day_before = datetime.utcnow() - timedelta(days=2)
        yesterday_count = session.query(Article).filter(
            Article.collected_at >= day_before,
            Article.collected_at < yesterday,
            Article.should_show_pib == True,
            Article.content_category == 'Government'
        ).count()
        
        # Calculate today's trend
        today_change = None
        if yesterday_count > 0:
            today_change = round(((today - yesterday_count) / yesterday_count) * 100, 1)
        
        # Last month's articles for total trend
        last_month = datetime.utcnow() - timedelta(days=30)
        month_ago = datetime.utcnow() - timedelta(days=60)
        last_month_count = session.query(Article).filter(
            Article.collected_at >= month_ago,
            Article.collected_at < last_month,
            Article.should_show_pib == True,
            Article.content_category == 'Government'
        ).count()
        
        this_month_count = session.query(Article).filter(
            Article.collected_at >= last_month,
            Article.should_show_pib == True,
            Article.content_category == 'Government'
        ).count()
        
        # Calculate total trend
        total_change = None
        if last_month_count > 0:
            total_change = round(((this_month_count - last_month_count) / last_month_count) * 100, 1)
        
        # Language distribution
        langs = [{"language": l or "Unknown", "count": c} for l, c in session.query(
            Article.language, func.count(Article.id)
        ).filter(
            Article.language.isnot(None),
            Article.should_show_pib == True,
            Article.content_category == 'Government'
        ).group_by(Article.language).all()]
        
        # Sentiment trends
        seven_days = datetime.utcnow() - timedelta(days=6)
        sent_q = session.query(
            func.date(Article.collected_at), Article.sentiment_label, func.count(Article.id)
        ).filter(
            Article.collected_at >= seven_days,
            Article.sentiment_label.isnot(None),
            Article.should_show_pib == True,
            Article.content_category == 'Government'
        )
        
        day_map = {str((datetime.utcnow() - timedelta(days=6-i)).date()): {"date": str((datetime.utcnow() - timedelta(days=6-i)).date()), "positive": 0, "neutral": 0, "negative": 0} for i in range(7)}
        for day, sent, cnt in sent_q.group_by(func.date(Article.collected_at), Article.sentiment_label).all():
            if str(day) in day_map and sent and sent.lower() in ("positive", "neutral", "negative"):
                day_map[str(day)][sent.lower()] += cnt
        
        # Average sentiment
        avg = float(session.query(func.avg(Article.sentiment_score)).filter(
            Article.sentiment_score.isnot(None),
            Article.should_show_pib == True,
            Article.content_category == 'Government'
        ).scalar() or 0.0)
        
        # PIB-relevant categories from topic_labels
        pib_categories = [
            "Government", "Policy", "Parliament", "Ministry", "Scheme", 
            "Budget", "Health", "Education", "Agriculture", "Infrastructure",
            "Economy", "Defense", "Foreign Affairs", "Technology", "Environment"
        ]
        
        cat_q = session.query(Article.topic_labels).filter(
            Article.topic_labels.isnot(None),
            Article.should_show_pib == True,
            Article.content_category == 'Government'
        )
        
        category_counts = {}
        for (topics,) in cat_q.all():
            if topics:
                for topic in topics:
                    if topic in pib_categories:
                        category_counts[topic] = category_counts.get(topic, 0) + 1
        
        top_cats = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        top_categories = [{"category": cat, "count": cnt} for cat, cnt in top_cats]
        
        if not top_categories:
            top_categories = [{"category": "Government", "count": total}]
        
        return {
            "totalArticles": total,
            "todayArticles": today,
            "averageSentiment": avg,
            "topCategories": top_categories,
            "languageDistribution": langs,
            "sentimentTrends": list(day_map.values()),
            "totalChangePercent": total_change,
            "todayChangePercent": today_change
        }
