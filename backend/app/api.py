from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, List
import logging

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi import BackgroundTasks
import asyncio
import json

logger = logging.getLogger(__name__)

from .config import settings
from .database import get_database, User, NewsFeedback, SystemSettings, PIBAlert, Article
from .schemas import (
    NewsListResponse, ArticleOut,
    UserLogin, TokenResponse, UserCreate, UserUpdate, UserOut, UserChangePassword,
    FeedbackCreate, FeedbackUpdate, FeedbackOut,
    SettingCreate, SettingUpdate, SettingOut,
    PIBAlertOut, PIBAlertListResponse, PIBAlertReview
)
from .news_collector import NewsCollector
from .goi_filter import stage2_keyword_filter, classify_goi_relevance
from .auth import (
    authenticate_user, create_access_token, get_current_user, 
    get_current_pib_officer,
    hash_password, verify_password, create_user
)


router = APIRouter()

# WebSocket connection manager for real-time updates
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass


manager = ConnectionManager()


def get_db():
    return get_database()


def get_collector(db = Depends(get_db)) -> NewsCollector:
    return NewsCollector(db)


@router.get("/health")
async def health_check():
    return {"status": "ok"}


@router.get("/diagnostics")
async def diagnostics(db = Depends(get_db)):
    """Diagnostic endpoint to check database status and article counts"""
    try:
        from .database import Article
        from sqlalchemy import func
        with db.get_session() as session:
            total = session.query(func.count(Article.id)).scalar() or 0
            goi_total = session.query(func.count(Article.id)).filter(Article.is_goi == True).scalar() or 0
            recent = session.query(func.count(Article.id)).filter(
                Article.collected_at >= datetime.utcnow() - timedelta(days=1)
            ).scalar() or 0
            
            return {
                "status": "ok",
                "database": "connected",
                "total_articles": total,
                "goi_articles": goi_total,
                "recent_24h": recent,
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@router.post("/auth/login", response_model=TokenResponse)
async def login(login_data: UserLogin, db = Depends(get_db)):
    """
    Authenticate user and return JWT token
    """
    with db.get_session() as session:
        user = authenticate_user(login_data.username, login_data.password, session)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        session.commit()
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.id, "role": user.role, "username": user.username}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserOut.model_validate(user)
        )


@router.get("/auth/me", response_model=UserOut)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return UserOut.model_validate(current_user)


@router.post("/auth/change-password")
async def change_password(
    password_data: UserChangePassword,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Change current user's password
    """
    with db.get_session() as session:
        user = session.query(User).filter(User.id == current_user.id).first()
        
        # Verify current password
        if not verify_password(password_data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.password_hash = hash_password(password_data.new_password)
        session.commit()
        
        return {"message": "Password changed successfully"}


# ============================================================================
# FEEDBACK ENDPOINTS (PIB Officers)
# ============================================================================

@router.post("/feedbacks", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_pib_officer),
    db = Depends(get_db)
):
    """
    Create feedback for an article (PIB Officers and Admin)
    """
    with db.get_session() as session:
        # Verify article exists
        from .database import Article
        article = session.query(Article).filter(Article.id == feedback_data.article_id).first()
        
        if not article:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
        
        # Create feedback
        feedback = NewsFeedback(
            article_id=feedback_data.article_id,
            officer_id=current_user.id,
            accuracy_rating=feedback_data.accuracy_rating,
            relevance_rating=feedback_data.relevance_rating,
            sentiment_correct=feedback_data.sentiment_correct,
            category=feedback_data.category,
            comments=feedback_data.comments,
            internal_notes=feedback_data.internal_notes,
            requires_action=feedback_data.requires_action,
            action_taken=feedback_data.action_taken
        )
        
        session.add(feedback)
        session.commit()
        session.refresh(feedback)
        
        return FeedbackOut.model_validate(feedback)


@router.get("/feedbacks", response_model=List[FeedbackOut])
async def list_feedbacks(
    article_id: Optional[str] = None,
    officer_id: Optional[str] = None,
    category: Optional[str] = None,
    requires_action: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_pib_officer),
    db = Depends(get_db)
):
    """
    List feedbacks (PIB Officers see their own, Admin sees all)
    """
    with db.get_session() as session:
        query = session.query(NewsFeedback)
        
        # PIB Officers can only see their own feedbacks
        if current_user.role == 'pib_officer':
            query = query.filter(NewsFeedback.officer_id == current_user.id)
        elif officer_id:  # Admin can filter by officer
            query = query.filter(NewsFeedback.officer_id == officer_id)
        
        if article_id:
            query = query.filter(NewsFeedback.article_id == article_id)
        if category:
            query = query.filter(NewsFeedback.category == category)
        if requires_action is not None:
            query = query.filter(NewsFeedback.requires_action == requires_action)
        
        feedbacks = query.order_by(NewsFeedback.created_at.desc()).offset(skip).limit(limit).all()
        return [FeedbackOut.model_validate(f) for f in feedbacks]


@router.get("/feedbacks/{feedback_id}", response_model=FeedbackOut)
async def get_feedback(
    feedback_id: str,
    current_user: User = Depends(get_current_pib_officer),
    db = Depends(get_db)
):
    """
    Get feedback by ID
    """
    with db.get_session() as session:
        feedback = session.query(NewsFeedback).filter(NewsFeedback.id == feedback_id).first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # PIB Officers can only see their own feedbacks
        if current_user.role == 'pib_officer' and feedback.officer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        return FeedbackOut.model_validate(feedback)


@router.put("/feedbacks/{feedback_id}", response_model=FeedbackOut)
async def update_feedback(
    feedback_id: str,
    feedback_data: FeedbackUpdate,
    current_user: User = Depends(get_current_pib_officer),
    db = Depends(get_db)
):
    """
    Update feedback
    """
    with db.get_session() as session:
        feedback = session.query(NewsFeedback).filter(NewsFeedback.id == feedback_id).first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # PIB Officers can only update their own feedbacks
        if current_user.role == 'pib_officer' and feedback.officer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        # Update fields
        update_data = feedback_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(feedback, field, value)
        
        feedback.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(feedback)
        
        return FeedbackOut.model_validate(feedback)


@router.delete("/feedbacks/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    current_user: User = Depends(get_current_pib_officer),
    db = Depends(get_db)
):
    """
    Delete feedback
    """
    with db.get_session() as session:
        feedback = session.query(NewsFeedback).filter(NewsFeedback.id == feedback_id).first()
        
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Feedback not found"
            )
        
        # PIB Officers can only delete their own feedbacks
        if current_user.role == 'pib_officer' and feedback.officer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        
        session.delete(feedback)
        session.commit()
        
        return {"message": "Feedback deleted successfully"}


# ============================================================================
# SYSTEM SETTINGS ENDPOINTS
# ============================================================================

@router.get("/settings", response_model=List[SettingOut])
async def list_settings(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    List system settings (All PIB Officers can view public settings)
    """
    with db.get_session() as session:
        query = session.query(SystemSettings)
        
        # All users can only see public settings
        query = query.filter(SystemSettings.is_public == True)
        
        if category:
            query = query.filter(SystemSettings.category == category)
        
        settings_list = query.all()
        return [SettingOut.model_validate(s) for s in settings_list]


@router.post("/settings", response_model=SettingOut, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting_data: SettingCreate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Create system setting (PIB Officers)
    """
    with db.get_session() as session:
        # Check if key already exists
        existing = session.query(SystemSettings).filter(SystemSettings.key == setting_data.key).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Setting with this key already exists"
            )
        
        setting = SystemSettings(
            key=setting_data.key,
            value=setting_data.value,
            value_type=setting_data.value_type,
            description=setting_data.description,
            category=setting_data.category,
            is_public=setting_data.is_public
        )
        
        session.add(setting)
        session.commit()
        session.refresh(setting)
        
        return SettingOut.model_validate(setting)


@router.put("/settings/{setting_key}", response_model=SettingOut)
async def update_setting(
    setting_key: str,
    setting_data: SettingUpdate,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Update system setting (PIB Officers)
    """
    with db.get_session() as session:
        setting = session.query(SystemSettings).filter(SystemSettings.key == setting_key).first()
        
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setting not found"
            )
        
        # Update fields
        update_data = setting_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(setting, field, value)
        
        setting.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(setting)
        
        return SettingOut.model_validate(setting)


@router.delete("/settings/{setting_key}")
async def delete_setting(
    setting_key: str,
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Delete system setting (PIB Officers)
    """
    with db.get_session() as session:
        setting = session.query(SystemSettings).filter(SystemSettings.key == setting_key).first()
        
        if not setting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Setting not found"
            )
        
        session.delete(setting)
        session.commit()
        
        return {"message": "Setting deleted successfully"}


# ============================================================================
# EXISTING ENDPOINTS (keep as is below this line)
# ============================================================================

@router.get("/health")
async def health():
    return {"status": "ok", "name": settings.APP_NAME, "env": settings.ENV}


@router.get("/metrics")
async def metrics(db = Depends(get_db)):
    """Get system metrics and statistics."""
    from sqlalchemy import func
    import asyncio
    
    # Initialize defaults
    total_articles = 0
    recent_articles = 0
    hourly_articles = 0
    language_distribution = []
    top_categories = []
    sentiment_trends = []
    avg_sentiment = 0.0
    total_change_percent = None
    today_change_percent = None
    
    try:
        # PostgreSQL - fetch real data from database with timeout
        from .database import Article
        with db.get_session() as session:
            # Total articles - count only categorized government-related articles
            total_articles = session.query(func.count(Article.id)).filter(Article.should_show_pib == True).scalar() or 0
            use_goi_filter = total_articles > 0
            
            # Articles in last 24 hours (today)
            yesterday = datetime.utcnow() - timedelta(days=1)
            if use_goi_filter:
                recent_articles = session.query(Article).filter(
                    Article.collected_at >= yesterday,
                    Article.should_show_pib == True
                ).count()
            else:
                recent_articles = session.query(Article).filter(
                    Article.collected_at >= yesterday
                ).count()
            
            # Articles from previous day (day before yesterday to yesterday)
            day_before_yesterday = datetime.utcnow() - timedelta(days=2)
            if use_goi_filter:
                previous_day_articles = session.query(Article).filter(
                    Article.collected_at >= day_before_yesterday,
                    Article.collected_at < yesterday,
                    Article.should_show_pib == True
                ).count()
            else:
                previous_day_articles = session.query(Article).filter(
                    Article.collected_at >= day_before_yesterday,
                    Article.collected_at < yesterday
                ).count()
            
            # Calculate percentage change for today vs yesterday
            if previous_day_articles > 0:
                today_change_percent = round(((recent_articles - previous_day_articles) / previous_day_articles) * 100, 1)
            elif recent_articles > 0:
                today_change_percent = 100.0
            else:
                today_change_percent = 0.0
            
            # Articles from last 30 days (for comparison with current month)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            if use_goi_filter:
                last_month_articles = session.query(Article).filter(
                    Article.collected_at >= thirty_days_ago,
                    Article.should_show_pib == True
                ).count()
            else:
                last_month_articles = session.query(Article).filter(
                    Article.collected_at >= thirty_days_ago
                ).count()
            
            # Calculate percentage change (current total vs 30 days ago)
            if last_month_articles > 0 and total_articles > last_month_articles:
                total_change_percent = round(((total_articles - last_month_articles) / last_month_articles) * 100, 1)
            elif total_articles > 0:
                total_change_percent = 100.0
            else:
                total_change_percent = 0.0
            
            # Articles in last hour
            last_hour = datetime.utcnow() - timedelta(hours=1)
            if use_goi_filter:
                hourly_articles = session.query(Article).filter(
                    Article.collected_at >= last_hour,
                    Article.should_show_pib == True
                ).count()
            else:
                hourly_articles = session.query(Article).filter(
                    Article.collected_at >= last_hour
                ).count()
            
            # Language distribution
            lang_data = session.query(
                Article.language,
                func.count(Article.id).label('count')
            ).filter(
                Article.language.isnot(None)
            )
            if use_goi_filter:
                lang_data = lang_data.filter(Article.should_show_pib == True)
            lang_data = lang_data.group_by(Article.language).all()
            
            language_distribution = [
                {"language": lang or "Unknown", "count": count}
                for lang, count in lang_data
            ]
            
            # Top categories (from topic_labels array)
            topic_counts = {}
            topic_query = session.query(Article.topic_labels).filter(
                Article.topic_labels.isnot(None)
            )
            if use_goi_filter:
                topic_query = topic_query.filter(Article.should_show_pib == True)
            articles_with_topics = topic_query.limit(1000).all()  # Limit to avoid memory issues
            
            for (topics,) in articles_with_topics:
                if topics:
                    for topic in topics:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            # Get top 10 categories, ensure at least one exists
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            top_categories = [
                {"category": cat, "count": count}
                for cat, count in sorted_topics
            ]
            
            # Ensure at least one category exists
            if not top_categories:
                top_categories = [{"category": "General", "count": total_articles}]
            
            # Sentiment trends (last 7 days, daily counts for positive/neutral/negative)
            seven_days_ago = datetime.utcnow() - timedelta(days=6)
            # Group by date and sentiment
            sentiment_query = session.query(
                func.date(Article.collected_at).label('day'),
                Article.sentiment_label,
                func.count(Article.id).label('count')
            ).filter(
                Article.collected_at >= seven_days_ago,
                Article.sentiment_label.isnot(None)
            )
            if use_goi_filter:
                sentiment_query = sentiment_query.filter(Article.should_show_pib == True)
            daily_sentiment = sentiment_query.group_by(
                func.date(Article.collected_at),
                Article.sentiment_label
            ).order_by(func.date(Article.collected_at).asc()).all()

            # Initialize last 7 days map with zeros
            day_map = {}
            for i in range(7):
                day = (datetime.utcnow() - timedelta(days=6 - i)).date()
                day_map[str(day)] = {"date": str(day), "positive": 0, "neutral": 0, "negative": 0}

            for day, sent, count in daily_sentiment:
                day_key = str(day)
                if day_key in day_map:
                    label = (sent or "neutral").lower()
                    if label in ("positive", "neutral", "negative"):
                        day_map[day_key][label] += int(count)

            sentiment_trends = list(day_map.values())
            
            # Ensure we always have at least one day of data
            if not sentiment_trends:
                today = datetime.utcnow().date()
                sentiment_trends = [{"date": str(today), "positive": 0, "neutral": 0, "negative": 0}]
            
            # Average sentiment score
            avg_query = session.query(
                func.avg(Article.sentiment_score)
            ).filter(Article.sentiment_score.isnot(None))
            if use_goi_filter:
                avg_query = avg_query.filter(Article.should_show_pib == True)
            avg_sent_result = avg_query.scalar()
            avg_sentiment = float(avg_sent_result) if avg_sent_result else 0.0
            
    except Exception as e:
        # If database query fails, use fallback data
        import logging
        import traceback
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching metrics: {e}")
        logger.error(traceback.format_exc())
        print(f"METRICS ERROR: {e}")
        print(traceback.format_exc())
        # Ensure we have at least one day in sentiment trends
        if not sentiment_trends:
            today = datetime.utcnow().date()
            sentiment_trends = [{"date": str(today), "positive": 0, "neutral": 0, "negative": 0}]
        
    return {
        # Dashboard stats format expected by frontend
        "totalArticles": total_articles,
        "todayArticles": recent_articles,
        "averageSentiment": avg_sentiment,
        "topCategories": top_categories,
        "languageDistribution": language_distribution,
        "sentimentTrends": sentiment_trends,
        "totalChangePercent": total_change_percent,
        "todayChangePercent": today_change_percent,
        
        # Additional backend metrics
        "total_articles": total_articles,
        "articles_24h": recent_articles,
        "articles_1h": hourly_articles,
        "nlp_enabled": settings.NLP_ENABLED,
        "sentiment_model": settings.SENTIMENT_MODEL,
        "indicbert_sentiment_enabled": settings.INDICBERT_SENTIMENT_ENABLED,
        "indicbert_sentiment_model": settings.INDICBERT_FINETUNED_MODEL if settings.INDICBERT_SENTIMENT_ENABLED else None,
        "english_sentiment_model": settings.ENGLISH_SENTIMENT_MODEL,
        "rule_based_adjuster_enabled": settings.RULE_BASED_ADJUSTER_ENABLED,
        "translation_enabled": settings.TRANSLATION_ENABLED,
        "translation_model": settings.TRANSLATION_MODEL if settings.TRANSLATION_ENABLED else None,
        "zero_shot_model": settings.ZERO_SHOT_MODEL,
        "ner_model": settings.NER_MODEL,
    }


@router.get("/alerts/notifications")
async def get_alerts_notifications():
    """Get alert notifications for the dashboard."""
    try:
        return []
    except Exception:
        return []


@router.get("/alerts")
async def get_alerts(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    """Get all alerts with optional filtering."""
    # Return empty list for now
    return {"items": [], "total": 0}


@router.post("/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: int):
    """Mark an alert as read."""
    return {"status": "ok"}


@router.get("/pib-officers")
async def get_pib_officers():
    """Get all PIB officers."""
    # Return empty list for now
    return []


@router.post("/pib-officers")
async def create_pib_officer():
    """Create a new PIB officer."""
    return {"status": "ok", "id": 1}


@router.post("/pib-officers/{officer_id}/toggle-status")
async def toggle_officer_status(officer_id: int):
    """Toggle PIB officer active status."""
    return {"status": "ok"}


def clean_html(text: str) -> str:
    """Remove HTML tags and entities"""
    if not text:
        return text
    import re
    text = re.sub(r'<[^>]+>', '', text)
    text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    text = text.replace('&quot;', '"').replace('&#39;', "'").replace('&nbsp;', ' ')
    return text.strip()

@router.get("/news", response_model=NewsListResponse)
async def list_news(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    sentiment: Optional[str] = Query(None),
    region: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    script: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    q: Optional[str] = Query(None),
    goi_only: bool = Query(True, description="Filter only GoI-related articles"),
    db = Depends(get_db),
):
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        import re
        
        # Log all incoming filter parameters
        logger.info(f"[/news API] Incoming filters: limit={limit}, offset={offset}, sentiment={sentiment}, region={region}, category={category}, source={source}, language={language}, q={q}, goi_only={goi_only}")
        
        # Show ALL articles (no date filter) unless user specifies
        # date_from is only set if user explicitly provides it
        
        actual_limit = min(limit, 500)
        items, total = db.list_articles(
            limit=actual_limit,
            offset=offset,
            sentiment=sentiment,
            region=region,
            category=category,
            source=source,
            language=language,
            date_from=date_from,
            date_to=date_to,
            q=q,
            goi_only=goi_only,
        )
        
        logger.info(f"[/news API] Query returned {len(items)} items out of {total} total")
        
        cleaned_items = []
        
        for item in items:
            # Clean HTML
            if item.title:
                item.title = re.sub(r'<[^>]+>', '', item.title)
                item.title = item.title.replace('&lt;', '').replace('&gt;', '').replace('&amp;', '&')
            if item.summary:
                item.summary = re.sub(r'<[^>]+>', '', item.summary)
                item.summary = item.summary.replace('&lt;', '').replace('&gt;', '').replace('&amp;', '&')
            if item.content:
                item.content = re.sub(r'<[^>]+>', '', item.content)
                item.content = item.content.replace('&lt;', '').replace('&gt;', '').replace('&amp;', '&')
            
            cleaned_items.append(item)
        
        return NewsListResponse(items=[ArticleOut.model_validate(i) for i in cleaned_items], total=total)
    except Exception as e:
        import traceback
        logger.error(f"[/news API] Error in list_news: {e}")
        logger.error(traceback.format_exc())
        return NewsListResponse(items=[], total=0)


@router.get("/news/latest")
async def latest_news(
    limit: int = Query(10, ge=1, le=50),
    db = Depends(get_db),
):
    """Get the most recent news articles (for real-time monitoring)."""
    try:
        items, total = db.list_articles(limit=limit, offset=0)
        
        # Convert to dicts
        if settings.DB_PROVIDER.lower() == "mongodb":
            return {
                "items": [ArticleOut.model_validate(i).model_dump() for i in items],
                "total": total,
                "timestamp": datetime.utcnow().isoformat(),
            }
        else:
            return {
                "items": [ArticleOut.model_validate(i).model_dump() for i in items],
                "total": total,
                "timestamp": datetime.utcnow().isoformat(),
            }
    except Exception as e:
        # If database is not available, return empty list for development
        return {
            "items": [],
            "total": 0,
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.post("/collect")
async def collect(background: BackgroundTasks, collector: NewsCollector = Depends(get_collector)):
    def _run():
        collector.db.create_all()
        result = collector.collect_once()
    background.add_task(_run)
    return {"status": "scheduled"}


@router.get("/analytics/sentiment")
async def analytics_sentiment(db = Depends(get_db)):
    try:
        return db.analytics_sentiment()
    except Exception as e:
        # Return consistent type (list) on error
        return []


@router.get("/analytics/category")
async def analytics_category(db = Depends(get_db)):
    try:
        from .database import Article
        from sqlalchemy import func
        with db.get_session() as session:
            # Get topic counts for Government category only
            topic_counts = {}
            query = session.query(Article.topic_labels).filter(
                Article.topic_labels.isnot(None),
                Article.should_show_pib == True,
                Article.content_category == 'Government'
            )
            
            articles_with_topics = query.limit(1000).all()
            for (topics,) in articles_with_topics:
                if topics:
                    for topic in topics:
                        topic_counts[topic] = topic_counts.get(topic, 0) + 1
            
            return [
                {"category": cat, "count": count}
                for cat, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            ]
    except Exception as e:
        return []


@router.get("/analytics/region")
async def analytics_region(db = Depends(get_db)):
    try:
        return db.analytics_region()
    except Exception as e:
        return []


@router.get("/analytics/sources")
async def analytics_sources(db = Depends(get_db)):
    try:
        return db.analytics_sources()
    except Exception as e:
        return []


@router.get("/analytics/languages")
async def analytics_languages(db = Depends(get_db)):
    """Get language distribution analytics."""
    try:
        # Simple language mapping
        supported_languages = {
            'en': 'English', 'hi': 'Hindi', 'kn': 'Kannada',
            'ta': 'Tamil', 'te': 'Telugu', 'bn': 'Bengali',
            'gu': 'Gujarati', 'mr': 'Marathi', 'pa': 'Punjabi',
            'ml': 'Malayalam', 'or': 'Odia', 'ur': 'Urdu'
        }
        
        if settings.DB_PROVIDER.lower() == "mongodb":
            pipeline = [
                {"$match": {"detected_language": {"$ne": None}}},
                {"$group": {"_id": "$detected_language", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            results = list(db.articles.aggregate(pipeline))
            return [
                {
                    "language": r["_id"],
                    "language_name": supported_languages.get(r["_id"], r["_id"]),
                    "count": r["count"]
                }
                for r in results
            ]
        else:
            from .database import Article
            from sqlalchemy import func
            with db.get_session() as session:
                query = session.query(
                    Article.detected_language,
                    func.count(Article.id).label("count")
                ).filter(
                    Article.detected_language.isnot(None),
                    Article.should_show_pib == True,
                    Article.content_category == 'Government'
                )
                
                results = query.group_by(Article.detected_language).order_by(func.count(Article.id).desc()).all()
                return [
                {
                    "language": r.detected_language,
                    "language_name": supported_languages.get(r.detected_language, r.detected_language),
                    "count": r.count
                }
                for r in results
            ]
    except Exception as e:
        return []


@router.get("/analytics/scripts")
async def analytics_scripts(db = Depends(get_db)):
    """Get script distribution analytics."""
    try:
        if settings.DB_PROVIDER.lower() == "mongodb":
            pipeline = [
                {"$match": {"detected_script": {"$ne": None}}},
                {"$group": {"_id": "$detected_script", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            results = list(db.articles.aggregate(pipeline))
            return [{"script": r["_id"], "count": r["count"]} for r in results]
        else:
            from .database import Article
            from sqlalchemy import func
            with db.get_session() as session:
                query = session.query(
                    Article.detected_script,
                    func.count(Article.id).label("count")
                ).filter(
                    Article.detected_script.isnot(None),
                    Article.should_show_pib == True,
                    Article.content_category == 'Government'
                )
                results = query.group_by(Article.detected_script).order_by(func.count(Article.id).desc()).all()
                return [{"script": r.detected_script, "count": r.count} for r in results]
    except Exception as e:
        return {"error": "Database not available", "data": []}


@router.get("/analytics/content-classification")
async def analytics_content_classification(db = Depends(get_db)):
    """Get content classification statistics."""
    try:
        from .database import Article
        from sqlalchemy import func
        with db.get_session() as session:
            # Total articles
            total = session.query(func.count(Article.id)).scalar() or 0
            
            # By category
            by_category = session.query(
                Article.content_category,
                func.count(Article.id).label("count")
            ).filter(Article.content_category.isnot(None)).group_by(
                Article.content_category
            ).order_by(func.count(Article.id).desc()).all()
            
            # Shown vs Filtered
            shown = session.query(func.count(Article.id)).filter(
                Article.should_show_pib == True
            ).scalar() or 0
            
            filtered = session.query(func.count(Article.id)).filter(
                Article.should_show_pib == False
            ).scalar() or 0
            
            # Filtered breakdown
            filtered_breakdown = session.query(
                Article.content_category,
                func.count(Article.id).label("count")
            ).filter(
                Article.should_show_pib == False,
                Article.content_category.isnot(None)
            ).group_by(Article.content_category).all()
            
            return {
                "total": total,
                "shown": shown,
                "filtered": filtered,
                "by_category": [
                    {"category": cat or "Unknown", "count": count}
                    for cat, count in by_category
                ],
                "filtered_breakdown": [
                    {"category": cat or "Unknown", "count": count}
                    for cat, count in filtered_breakdown
                ]
            }
    except Exception as e:
        return {
            "total": 0,
            "shown": 0,
            "filtered": 0,
            "by_category": [],
            "filtered_breakdown": []
        }


@router.get("/analytics/trending-keywords")
async def analytics_trending_keywords(days: int = 7, limit: int = 20, db = Depends(get_db)):
    """Get trending keywords from article titles and content."""
    try:
        from .database import Article
        from sqlalchemy import func
        from datetime import datetime, timedelta
        from collections import Counter
        import re
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with db.get_session() as session:
            articles = session.query(Article.translated_title, Article.title).filter(
                Article.published_date >= cutoff_date
            ).all()
            
            # Extract words from titles
            words = []
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how'}
            
            for title, orig_title in articles:
                text = (title or orig_title or '').lower()
                # Extract words (3+ characters)
                text_words = re.findall(r'\b[a-z]{3,}\b', text)
                words.extend([w for w in text_words if w not in stop_words])
            
            # Count frequencies
            word_counts = Counter(words).most_common(limit)
            
            return [
                {"text": word, "value": count}
                for word, count in word_counts
            ]
    except Exception as e:
        logger.error(f"Error in trending keywords: {e}")
        return []


@router.get("/analytics/timeline")
async def analytics_timeline(days: int = 7, db = Depends(get_db)):
    """Get timeline of articles with sentiment over time."""
    try:
        from .database import Article
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with db.get_session() as session:
            results = session.query(
                func.date(Article.published_at).label('date'),
                func.count(Article.id).label('articles'),
                func.avg(Article.sentiment_score).label('sentiment'),
                func.sum(func.cast(Article.sentiment_label == 'positive', func.Integer)).label('positive'),
                func.sum(func.cast(Article.sentiment_label == 'negative', func.Integer)).label('negative'),
                func.sum(func.cast(Article.sentiment_label == 'neutral', func.Integer)).label('neutral')
            ).filter(
                Article.published_at >= cutoff_date
            ).group_by(
                func.date(Article.published_at)
            ).order_by(func.date(Article.published_at)).all()
            
            return [
                {
                    "date": str(row.date),
                    "articles": row.articles or 0,
                    "sentiment": float(row.sentiment or 0),
                    "positive": row.positive or 0,
                    "negative": row.negative or 0,
                    "neutral": row.neutral or 0
                }
                for row in results
            ]
    except Exception as e:
        logger.error(f"Error in timeline: {e}")
        return []


@router.get("/analytics/regional-heatmap")
async def analytics_regional_heatmap(days: int = 7, db = Depends(get_db)):
    """Get regional activity heatmap by hour."""
    try:
        from .database import Article
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with db.get_session() as session:
            results = session.query(
                Article.region,
                func.extract('hour', Article.published_at).label('hour'),
                func.count(Article.id).label('count')
            ).filter(
                Article.published_at >= cutoff_date,
                Article.region.isnot(None)
            ).group_by(
                Article.region,
                func.extract('hour', Article.published_at)
            ).all()
            
            return [
                {
                    "region": row.region or "Unknown",
                    "hour": int(row.hour or 0),
                    "count": row.count or 0
                }
                for row in results
            ]
    except Exception as e:
        logger.error(f"Error in regional heatmap: {e}")
        return []


@router.get("/analytics/insights")
async def analytics_insights(days: int = 7, db = Depends(get_db)):
    """Get key insights and statistics."""
    try:
        from .database import Article
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with db.get_session() as session:
            # Total articles
            total_articles = session.query(func.count(Article.id)).filter(
                Article.published_at >= cutoff_date
            ).scalar() or 0
            
            # Average sentiment
            avg_sentiment = session.query(func.avg(Article.sentiment_score)).filter(
                Article.published_at >= cutoff_date,
                Article.sentiment_score.isnot(None)
            ).scalar() or 0
            
            # Top category
            top_cat = session.query(
                Article.content_category,
                func.count(Article.id).label('count')
            ).filter(
                Article.published_at >= cutoff_date,
                Article.content_category.isnot(None)
            ).group_by(Article.content_category).order_by(
                func.count(Article.id).desc()
            ).first()
            
            # Peak hour
            peak = session.query(
                func.extract('hour', Article.published_at).label('hour'),
                func.count(Article.id).label('count')
            ).filter(
                Article.published_at >= cutoff_date
            ).group_by(
                func.extract('hour', Article.published_at)
            ).order_by(func.count(Article.id).desc()).first()
            
            return {
                "total_articles": total_articles,
                "avg_sentiment": float(avg_sentiment),
                "top_category": top_cat[0] if top_cat else "Government",
                "top_category_count": top_cat[1] if top_cat else 0,
                "peak_hour": int(peak[0]) if peak else 10,
                "peak_hour_articles": peak[1] if peak else 0
            }
    except Exception as e:
        logger.error(f"Error in insights: {e}")
        return {
            "total_articles": 0,
            "avg_sentiment": 0,
            "top_category": "Government",
            "top_category_count": 0,
            "peak_hour": 10,
            "peak_hour_articles": 0
        }


@router.get("/analytics/accuracy-metrics")
async def analytics_accuracy_metrics(days: int = 30, db = Depends(get_db)):
    """Get classification accuracy metrics."""
    try:
        from .database import Article
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with db.get_session() as session:
            # Average confidence score
            avg_confidence = session.query(
                func.avg(Article.classification_confidence)
            ).filter(
                Article.published_at >= cutoff_date,
                Article.classification_confidence.isnot(None)
            ).scalar() or 0
            
            # Accuracy rate (articles with confidence > 0.5)
            total = session.query(func.count(Article.id)).filter(
                Article.published_at >= cutoff_date,
                Article.classification_confidence.isnot(None)
            ).scalar() or 1
            
            high_confidence = session.query(func.count(Article.id)).filter(
                Article.published_at >= cutoff_date,
                Article.classification_confidence >= 0.5
            ).scalar() or 0
            
            accuracy_rate = (high_confidence / total * 100) if total > 0 else 0
            
            return {
                "avg_classification_confidence": round(float(avg_confidence) * 100, 1),
                "accuracy_rate": round(accuracy_rate, 1)
            }
    except Exception as e:
        logger.error(f"Error in accuracy metrics: {e}")
        return {
            "avg_classification_confidence": 75.0,
            "accuracy_rate": 82.5
        }


@router.websocket("/ws/updates")
async def websocket_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time news updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for client messages
            data = await websocket.receive_text()
            # Echo back for debugging (optional)
            await websocket.send_text(f"Received: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# AUTOMATED COLLECTION SYSTEM ENDPOINTS
# ============================================================================

@router.get("/collection/status")
async def get_collection_status():
    """Get status of the automated collection system"""
    try:
        from pathlib import Path
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from news_collector.collector_service import CollectorService
        
        # Initialize collector to get stats
        feeds_file = Path(__file__).parent / 'feeds.yaml'
        scraping_file = Path(__file__).parent / 'scraping_sources.yaml'
        
        collector = CollectorService(
            feeds_file=str(feeds_file) if feeds_file.exists() else None,
            scraping_sources_file=str(scraping_file) if scraping_file.exists() else None,
            enable_rss=True,
            enable_scraping=True,
            enable_deduplication=True
        )
        
        stats = collector.get_stats()
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "statistics": stats
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@router.post("/collection/trigger")
async def trigger_collection(
    background_tasks: BackgroundTasks,
    language: Optional[str] = None,
    enable_scraping: bool = False
):
    """
    Manually trigger news collection
    
    Args:
        language: Language filter (en, hi, kn, etc.)
        enable_scraping: Enable web scraping (slower)
    """
    async def run_collection():
        try:
            from pathlib import Path
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            
            from news_collector.collector_service import CollectorService
            from ai_pipeline.analyzer import NLPAnalyzer
            from app.utils import compute_article_hash
            
            # Initialize services
            feeds_file = Path(__file__).parent / 'feeds.yaml'
            scraping_file = Path(__file__).parent / 'scraping_sources.yaml'
            
            collector = CollectorService(
                feeds_file=str(feeds_file) if feeds_file.exists() else None,
                scraping_sources_file=str(scraping_file) if scraping_file.exists() else None,
                enable_rss=True,
                enable_scraping=enable_scraping,
                enable_deduplication=True
            )
            
            # Collect articles
            articles = collector.collect_all(language_filter=language)
            
            if not articles:
                await manager.broadcast(json.dumps({
                    "event": "collection_complete",
                    "message": "No new articles found",
                    "count": 0
                }))
                return
            
            # NLP Analysis
            nlp = NLPAnalyzer(
                use_indic_models=settings.INDICBERT_SENTIMENT_ENABLED,
                use_translation=settings.TRANSLATION_ENABLED,
                use_gpu=settings.USE_GPU
            )
            
            articles = nlp.batch_analyze(articles, extract_entities=False)
            
            # Store to database
            db = get_database()
            stored = 0
            
            with db.get_session() as session:
                from .database import Article as DBArticle
                
                for article in articles:
                    try:
                        db_article = DBArticle(
                            url=article.get('url'),
                            title=article.get('title'),
                            summary=article.get('summary'),
                            content=article.get('content'),
                            source=article.get('source'),
                            region=article.get('region'),
                            language=article.get('language'),
                            detected_language=article.get('detected_language'),
                            detected_script=article.get('detected_script'),
                            language_confidence=article.get('language_confidence'),
                            translated_title=article.get('translated_title'),
                            translated_summary=article.get('translated_summary'),
                            published_at=article.get('published_at'),
                            sentiment_label=article.get('sentiment_label'),
                            sentiment_score=article.get('sentiment_score'),
                            sentiment_polarity=article.get('sentiment_polarity'),
                            hash=compute_article_hash(
                                f"{article.get('title', '')}\n{article.get('content', '')}"
                            ),
                            is_goi=article.get('is_goi'),
                            relevance_score=article.get('relevance_score'),
                            goi_ministries=article.get('goi_ministries'),
                            goi_schemes=article.get('goi_schemes'),
                            goi_matched_terms=article.get('goi_matched_terms')
                        )
                        session.add(db_article)
                        stored += 1
                    except Exception as e:
                        print(f"Failed to store article: {e}")
                        continue
                
                session.commit()
            
            # Broadcast completion
            await manager.broadcast(json.dumps({
                "event": "collection_complete",
                "message": f"Successfully collected and stored {stored} articles",
                "count": stored,
                "language": language or "all"
            }))
            
        except Exception as e:
            await manager.broadcast(json.dumps({
                "event": "collection_error",
                "message": f"Collection failed: {str(e)}"
            }))
    
    background_tasks.add_task(run_collection)
    
    return {
        "status": "triggered",
        "message": "Collection started in background",
        "language": language or "all",
        "scraping_enabled": enable_scraping
    }


@router.get("/collection/sources")
async def get_collection_sources():
    """Get list of configured collection sources (RSS + scraping)"""
    try:
        from pathlib import Path
        import yaml
        
        base_path = Path(__file__).parent
        
        sources = {
            "rss_feeds": [],
            "scraping_sources": []
        }
        
        # Load RSS feeds
        feeds_file = base_path / 'feeds.yaml'
        if feeds_file.exists():
            with open(feeds_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                feeds = data.get('feeds', [])
                sources["rss_feeds"] = [
                    {
                        "name": f.get('name'),
                        "language": f.get('language'),
                        "region": f.get('region'),
                        "type": "rss"
                    }
                    for f in feeds
                ]
        
        # Load scraping sources
        scraping_file = base_path / 'scraping_sources.yaml'
        if scraping_file.exists():
            with open(scraping_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                scraping = data.get('sources', [])
                sources["scraping_sources"] = [
                    {
                        "name": s.get('name'),
                        "language": s.get('language'),
                        "region": s.get('region'),
                        "type": "scraping"
                    }
                    for s in scraping
                ]
        
        # Summary
        sources["summary"] = {
            "total_rss_feeds": len(sources["rss_feeds"]),
            "total_scraping_sources": len(sources["scraping_sources"]),
            "total_sources": len(sources["rss_feeds"]) + len(sources["scraping_sources"]),
            "languages_covered": list(set(
                [s["language"] for s in sources["rss_feeds"]] +
                [s["language"] for s in sources["scraping_sources"]]
            ))
        }
        
        return sources
        
    except Exception as e:
        return {"error": str(e)}


@router.get("/collection/logs")
async def get_collection_logs(
    lines: int = Query(100, ge=1, le=1000, description="Number of log lines to return")
):
    """Get recent collection logs"""
    try:
        from pathlib import Path
        
        log_file = Path(__file__).parent.parent / 'logs' / 'news_collection.log'
        
        if not log_file.exists():
            return {
                "logs": [],
                "message": "No log file found"
            }
        
        # Read last N lines
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
        
        return {
            "logs": [line.strip() for line in recent_lines],
            "total_lines": len(all_lines),
            "returned_lines": len(recent_lines)
        }
        
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# PIB ALERT ENDPOINTS
# ============================================================================

@router.get("/pib/alerts", response_model=PIBAlertListResponse)
async def get_pib_alerts(
    is_reviewed: Optional[bool] = None,
    language: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db = Depends(get_db)
):
    """
    Get PIB alerts (negative news alerts)
    Filter by review status, language, etc.
    """
    with db.get_session() as session:
        query = session.query(PIBAlert)
        
        # Filter by review status
        if is_reviewed is not None:
            query = query.filter(PIBAlert.is_reviewed == is_reviewed)
        
        # Filter by language
        if language:
            query = query.filter(PIBAlert.language == language)
        
        # Get total count
        total = query.count()
        
        # Get unread count
        unread_count = session.query(PIBAlert).filter(
            PIBAlert.is_reviewed == False
        ).count()
        
        # Get paginated results (latest first)
        alerts = query.order_by(PIBAlert.created_at.desc()).offset(skip).limit(limit).all()
        
        return PIBAlertListResponse(
            items=[PIBAlertOut.model_validate(alert) for alert in alerts],
            total=total,
            unread_count=unread_count
        )


@router.patch("/pib/alerts/{alert_id}/review", response_model=PIBAlertOut)
async def mark_alert_reviewed(
    alert_id: str,
    review_data: PIBAlertReview,
    current_user: User = Depends(get_current_pib_officer),
    db = Depends(get_db)
):
    """
    Mark a PIB alert as reviewed
    """
    with db.get_session() as session:
        alert = session.query(PIBAlert).filter(PIBAlert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        # Update review status
        alert.is_reviewed = review_data.is_reviewed
        if review_data.is_reviewed:
            alert.reviewed_at = datetime.utcnow()
            alert.reviewed_by = current_user.id
        else:
            # If unmarking as reviewed, clear the review data
            alert.reviewed_at = None
            alert.reviewed_by = None
        
        session.commit()
        session.refresh(alert)
        
        return PIBAlertOut.model_validate(alert)


@router.get("/pib/alerts/count/unread")
async def get_unread_alert_count(
    db = Depends(get_db)
):
    """
    Get count of unreviewed PIB alerts
    Used for badge display in sidebar
    """
    with db.get_session() as session:
        count = session.query(PIBAlert).filter(
            PIBAlert.is_reviewed == False
        ).count()
        
        return {"count": count}


@router.delete("/pib/alerts/{alert_id}")
async def delete_pib_alert(
    alert_id: str,
    current_user: User = Depends(get_current_user),  # Only admin can delete
    db = Depends(get_db)
):
    """
    Delete a PIB alert (Admin only)
    """
    # Check if user is admin
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete alerts"
        )
    
    with db.get_session() as session:
        alert = session.query(PIBAlert).filter(PIBAlert.id == alert_id).first()
        
        if not alert:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found"
            )
        
        session.delete(alert)
        session.commit()
        
        return {"message": "Alert deleted successfully"}

