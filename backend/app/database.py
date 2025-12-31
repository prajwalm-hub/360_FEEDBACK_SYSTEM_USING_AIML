from __future__ import annotations
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

from sqlalchemy import (
    create_engine,
    Column,
    String,
    Text,
    DateTime,
    Float,
    ARRAY,
    JSON,
    Index,
    func,
    Boolean,
    ForeignKey,
    Integer,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, Session, relationship

from .config import settings


Base = declarative_base()


class Article(Base):
    __tablename__ = "articles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(Text, nullable=False)  # Removed unique=True - will use hash-based index instead
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    source = Column(String(255), nullable=True)
    source_type = Column(String(32), nullable=True, default='rss')  # 'rss' or 'scraper'
    region = Column(String(255), nullable=True)
    language = Column(String(64), nullable=True)
    
    # Multilingual fields
    detected_language = Column(String(64), nullable=True)
    detected_script = Column(String(64), nullable=True)
    language_confidence = Column(Float, nullable=True)
    translated_title = Column(Text, nullable=True)
    translated_summary = Column(Text, nullable=True)
    
    published_at = Column(DateTime(timezone=True), nullable=True)
    collected_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    sentiment_label = Column(String(32), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    sentiment_polarity = Column(Float, nullable=True)  # -1 to +1 polarity scale

    topic_labels = Column(ARRAY(String), nullable=True)

    # list of {text, label, start, end, confidence, type}
    entities = Column(JSONB, nullable=True)

    hash = Column(String(64), unique=True, nullable=False)

    # Government of India relevance fields
    is_goi = Column(Boolean, nullable=True)
    relevance_score = Column(Float, nullable=True)
    goi_ministries = Column(ARRAY(String), nullable=True)
    goi_schemes = Column(ARRAY(String), nullable=True)
    goi_entities = Column(JSONB, nullable=True)
    goi_matched_terms = Column(ARRAY(String), nullable=True)
    
    # Content classification fields
    content_category = Column(String(64), nullable=True)  # Government, Political, Entertainment, etc.
    content_sub_category = Column(String(128), nullable=True)  # Scheme Implementation, Election Coverage, etc.
    classification_confidence = Column(Float, nullable=True)
    classification_keywords = Column(ARRAY(String), nullable=True)
    should_show_pib = Column(Boolean, default=False)  # Should show to PIB officers (default False)
    filter_reason = Column(String(255), nullable=True)  # Why filtered


Index("idx_articles_published_at", Article.published_at)
Index("idx_articles_sentiment", Article.sentiment_label)
Index("idx_articles_region", Article.region)
Index("idx_articles_language", Article.language)
Index("idx_articles_detected_language", Article.detected_language)
Index("idx_articles_topic_labels", Article.topic_labels, postgresql_using="gin")
Index("idx_articles_is_goi", Article.is_goi)
Index("idx_articles_source_type", Article.source_type)
Index("idx_articles_content_category", Article.content_category)
Index("idx_articles_should_show_pib", Article.should_show_pib)


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Role: 'admin' or 'pib_officer'
    role = Column(String(50), nullable=False, default='pib_officer')
    
    # PIB Officer specific fields
    region = Column(String(255), nullable=True)  # For PIB Officers
    languages = Column(ARRAY(String), nullable=True)  # Languages they monitor
    phone = Column(String(20), nullable=True)
    department = Column(String(255), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    feedbacks = relationship("NewsFeedback", back_populates="officer", cascade="all, delete-orphan")


Index("idx_users_username", User.username)
Index("idx_users_email", User.email)
Index("idx_users_role", User.role)
Index("idx_users_region", User.region)


class NewsFeedback(Base):
    """Feedback from PIB Officers on news articles"""
    __tablename__ = "news_feedbacks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    officer_id = Column(String, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    # Feedback details
    accuracy_rating = Column(Integer, nullable=True)  # 1-5 scale
    relevance_rating = Column(Integer, nullable=True)  # 1-5 scale
    sentiment_correct = Column(Boolean, nullable=True)
    category = Column(String(100), nullable=True)  # verified, misleading, needs_review, etc.
    
    # Comments
    comments = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Actions
    requires_action = Column(Boolean, default=False)
    action_taken = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    officer = relationship("User", back_populates="feedbacks")


Index("idx_feedbacks_article", NewsFeedback.article_id)
Index("idx_feedbacks_officer", NewsFeedback.officer_id)
Index("idx_feedbacks_category", NewsFeedback.category)
Index("idx_feedbacks_created", NewsFeedback.created_at)


class SystemSettings(Base):
    """System-wide settings managed by Admin"""
    __tablename__ = "system_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    value_type = Column(String(50), nullable=False, default='string')  # string, int, bool, json
    description = Column(Text, nullable=True)
    
    # Metadata
    category = Column(String(100), nullable=True)  # collection, nlp, ui, etc.
    is_public = Column(Boolean, default=False)  # Can PIB officers see this?
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


Index("idx_settings_key", SystemSettings.key)
Index("idx_settings_category", SystemSettings.category)


class PIBAlert(Base):
    """PIB Alert system for negative news detection"""
    __tablename__ = "pib_alerts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String, ForeignKey('articles.id', ondelete='CASCADE'), nullable=False)
    
    # Alert details
    title = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    link = Column(Text, nullable=True)
    language = Column(String(64), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    
    # Alert status
    is_reviewed = Column(Boolean, default=False)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(String, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Email notification
    email_sent = Column(Boolean, default=False)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


Index("idx_pib_alerts_article", PIBAlert.article_id)
Index("idx_pib_alerts_is_reviewed", PIBAlert.is_reviewed)
Index("idx_pib_alerts_created", PIBAlert.created_at)


class Database:
    """PostgreSQL database interface."""
    
    def __init__(self, database_url: Optional[str] = None):
        if settings.DB_PROVIDER.lower() == "mongodb":
            raise ValueError("Use MongoDBRepository for MongoDB. This class is for PostgreSQL only.")
        # Add connection pool settings and statement timeout
        self.engine = create_engine(
            database_url or settings.DATABASE_URL,
            future=True,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            connect_args={"options": "-c statement_timeout=30000"}  # 30 second timeout
        )
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_all(self):
        Base.metadata.create_all(self.engine)
        # Attempt to ensure GoI and classification columns exist (idempotent for Postgres)
        try:
            with self.engine.connect() as conn:
                conn.exec_driver_sql(
                    """
                    ALTER TABLE articles
                    ADD COLUMN IF NOT EXISTS is_goi BOOLEAN,
                    ADD COLUMN IF NOT EXISTS relevance_score DOUBLE PRECISION,
                    ADD COLUMN IF NOT EXISTS goi_ministries TEXT[],
                    ADD COLUMN IF NOT EXISTS goi_schemes TEXT[],
                    ADD COLUMN IF NOT EXISTS goi_entities JSONB,
                    ADD COLUMN IF NOT EXISTS goi_matched_terms TEXT[],
                    ADD COLUMN IF NOT EXISTS content_category VARCHAR(64),
                    ADD COLUMN IF NOT EXISTS content_sub_category VARCHAR(128),
                    ADD COLUMN IF NOT EXISTS classification_confidence DOUBLE PRECISION,
                    ADD COLUMN IF NOT EXISTS classification_keywords TEXT[],
                    ADD COLUMN IF NOT EXISTS should_show_pib BOOLEAN DEFAULT TRUE,
                    ADD COLUMN IF NOT EXISTS filter_reason VARCHAR(255);
                    """
                )
                conn.commit()
        except Exception:
            pass

    def get_session(self) -> Session:
        return self.SessionLocal()

    # Basic CRUD helpers
    def upsert_article(self, data: Dict[str, Any]) -> Tuple[Article, bool]:
        """Insert or update article by URL/hash. Returns (article, created)."""
        # Remove confidence scoring fields that are not in the database schema
        confidence_fields = [
            "confidence_score", "confidence_level", "contributing_factors",
            "auto_approved", "auto_rejected", "needs_verification", "anomalies"
        ]
        data = {k: v for k, v in data.items() if k not in confidence_fields}
        
        with self.get_session() as session:
            existing = (
                session.query(Article)
                .filter((Article.url == data["url"]) | (Article.hash == data["hash"]))
                .first()
            )
            if existing:
                for k, v in data.items():
                    setattr(existing, k, v)
                session.add(existing)
                session.commit()
                session.refresh(existing)
                return existing, False
            art = Article(**data)
            session.add(art)
            session.commit()
            session.refresh(art)
            return art, True

    def list_articles(
        self,
        limit: int = 50,
        offset: int = 0,
        sentiment: Optional[str] = None,
        region: Optional[str] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
        language: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        q: Optional[str] = None,
        goi_only: bool = False,
    ) -> Tuple[List[Article], int]:
        import logging
        logger = logging.getLogger(__name__)
        
        with self.get_session() as session:
            query = session.query(Article)
            
            # Log incoming filters
            logger.info(f"[FILTER] Incoming params: sentiment={sentiment}, region={region}, category={category}, source={source}, language={language}, goi_only={goi_only}")
            
            # Apply different filtering based on language
            # For English/Hindi: Strict filtering (Government category + should_show_pib)
            # For Regional languages: Relaxed filtering (Government category OR should_show_pib OR is_goi)
            if language in ['en', 'hi']:
                # Strict filtering for English/Hindi
                query = query.filter(
                    Article.should_show_pib == True,
                    Article.content_category == 'Government'
                )
                logger.info(f"[FILTER] Applied STRICT filter for {language}")
            elif language in ['kn', 'ta', 'te', 'bn', 'ml', 'mr', 'gu', 'pa', 'or', 'ur', 'as']:
                # Relaxed filtering for regional languages - show if ANY condition is true
                query = query.filter(
                    (Article.content_category == 'Government') |
                    (Article.should_show_pib == True) |
                    (Article.is_goi == True)
                )
                logger.info(f"[FILTER] Applied RELAXED filter for regional language {language}")
            else:
                # No specific language filter or "All Languages" - show Government category articles
                query = query.filter(
                    Article.should_show_pib == True,
                    Article.content_category == 'Government'
                )
                logger.info(f"[FILTER] Applied DEFAULT filter (no language or mixed)")
            
            if goi_only:
                query = query.filter(Article.is_goi.is_(True))
            
            # Normalize sentiment filter (lowercase)
            if sentiment:
                sentiment_normalized = sentiment.lower().strip()
                query = query.filter(func.lower(Article.sentiment_label) == sentiment_normalized)
                logger.info(f"[FILTER] Applied sentiment filter: {sentiment_normalized}")
            
            # Region filter - case-insensitive partial match
            if region:
                query = query.filter(Article.region.ilike(f"%{region}%"))
                logger.info(f"[FILTER] Applied region filter: {region}")
            
            if source:
                query = query.filter(Article.source == source)
                logger.info(f"[FILTER] Applied source filter: {source}")
            
            # Language filter - check both language and detected_language fields
            if language:
                query = query.filter(
                    (Article.language == language) | 
                    (Article.detected_language == language)
                )
                logger.info(f"[FILTER] Applied language filter: {language}")
            
            # Category filter - search in topic_labels array
            if category:
                query = query.filter(Article.topic_labels.any(category))
                logger.info(f"[FILTER] Applied category filter: {category}")
            
            # Search filter - case-insensitive search in title, summary, content
            if q:
                search_term = f"%{q}%"
                query = query.filter(
                    (Article.title.ilike(search_term)) |
                    (Article.summary.ilike(search_term)) |
                    (Article.content.ilike(search_term))
                )
                logger.info(f"[FILTER] Applied search filter: {q}")
            
            if date_from:
                query = query.filter(Article.published_at >= date_from)
            if date_to:
                query = query.filter(Article.published_at <= date_to)
            
            # Count total matching documents
            try:
                total = query.count()
                logger.info(f"[FILTER] Total matching documents: {total}")
            except Exception as e:
                logger.error(f"[FILTER] Error counting documents: {e}")
                total = 0
            
            # Get rows - sort by published_at desc
            try:
                rows = (
                    query.order_by(Article.published_at.desc().nullslast(), Article.collected_at.desc())
                    .offset(offset)
                    .limit(limit)
                    .all()
                )
                logger.info(f"[FILTER] Returned {len(rows)} documents")
            except Exception as e:
                logger.error(f"[FILTER] Query error: {e}")
                rows = []
            
            return rows, total

    def analytics_sentiment(self) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            rows = (
                session.query(Article.sentiment_label, func.count(Article.id))
                .filter(
                    Article.should_show_pib == True,
                    Article.content_category == 'Government'
                )
                .group_by(Article.sentiment_label)
                .all()
            )
            return [
                {"sentiment": s or "unknown", "count": int(c)} for s, c in rows
            ]

    def analytics_category(self) -> List[Dict[str, Any]]:
        # Flatten topic labels and count
        with self.get_session() as session:
            # Use raw SQL to unnest topic_labels array
            conn = session.connection().connection
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT label, COUNT(*) FROM (
                        SELECT unnest(topic_labels) AS label FROM articles 
                        WHERE topic_labels IS NOT NULL 
                        AND should_show_pib = TRUE
                        AND content_category = 'Government'
                    ) t
                    GROUP BY label
                    ORDER BY COUNT(*) DESC
                    LIMIT 50
                    """
                )
                rows = cur.fetchall()
            return [{"category": r[0], "count": int(r[1])} for r in rows]

    def analytics_region(self) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            rows = (
                session.query(Article.region, func.count(Article.id))
                .filter(
                    Article.should_show_pib == True,
                    Article.content_category == 'Government'
                )
                .group_by(Article.region)
                .order_by(func.count(Article.id).desc())
                .all()
            )
            return [{"region": r or "unknown", "count": int(c)} for r, c in rows]

    def analytics_sources(self) -> List[Dict[str, Any]]:
        with self.get_session() as session:
            rows = (
                session.query(Article.source, func.count(Article.id))
                .filter(
                    Article.should_show_pib == True,
                    Article.content_category == 'Government'
                )
                .group_by(Article.source)
                .order_by(func.count(Article.id).desc())
                .all()
            )
            return [{"source": s or "unknown", "count": int(c)} for s, c in rows]


def get_database() -> Union[Database, Any]:
    """Factory function to get the appropriate database implementation."""
    if settings.DB_PROVIDER.lower() == "mongodb":
        from .mongodb import MongoDBRepository
        return MongoDBRepository()
    else:
        return Database()
