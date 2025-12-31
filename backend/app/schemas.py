from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, HttpUrl, EmailStr


# ============================================================================
# Authentication & User Schemas
# ============================================================================

class UserLogin(BaseModel):
    """Login request schema"""
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=6)


class UserOut(BaseModel):
    """User response schema"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    role: str
    region: Optional[str] = None
    languages: Optional[List[str]] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserCreate(BaseModel):
    """Create user request schema"""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2, max_length=255)
    
    # PIB Officer fields
    region: Optional[str] = None
    languages: Optional[List[str]] = None
    phone: Optional[str] = None
    department: Optional[str] = None


class UserUpdate(BaseModel):
    """Update user request schema"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    region: Optional[str] = None
    languages: Optional[List[str]] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None


class UserChangePassword(BaseModel):
    """Change password request schema"""
    current_password: str
    new_password: str = Field(..., min_length=6)


# ============================================================================
# Feedback Schemas
# ============================================================================

class FeedbackCreate(BaseModel):
    """Create feedback request schema"""
    article_id: str
    accuracy_rating: Optional[int] = Field(None, ge=1, le=5)
    relevance_rating: Optional[int] = Field(None, ge=1, le=5)
    sentiment_correct: Optional[bool] = None
    category: Optional[str] = None
    comments: Optional[str] = None
    internal_notes: Optional[str] = None
    requires_action: bool = False
    action_taken: Optional[str] = None


# ============================================================================
# Article Verification Schemas (for 100% Accuracy System)
# ============================================================================

class ArticleVerificationCreate(BaseModel):
    """PIB officer verification of article"""
    article_id: int
    is_relevant: bool  # True = correct government news, False = unwanted
    correct_category: Optional[str] = None  # If miscategorized
    correction_reason: str  # Why is this correct/incorrect?


class ArticleVerificationOut(BaseModel):
    """Article verification response"""
    id: int
    article_id: int
    verified_by: str
    is_relevant: bool
    correct_category: Optional[str] = None
    correction_reason: str
    verified_at: datetime
    
    # System predictions (for accuracy measurement)
    predicted_category: Optional[str] = None
    predicted_should_show: Optional[bool] = None
    predicted_confidence: Optional[float] = None
    error_type: Optional[str] = None
    
    model_config = {
        "from_attributes": True
    }


class FeedbackUpdate(BaseModel):
    """Update feedback request schema"""
    accuracy_rating: Optional[int] = Field(None, ge=1, le=5)
    relevance_rating: Optional[int] = Field(None, ge=1, le=5)
    sentiment_correct: Optional[bool] = None
    category: Optional[str] = None
    comments: Optional[str] = None
    internal_notes: Optional[str] = None
    requires_action: Optional[bool] = None
    action_taken: Optional[str] = None


class FeedbackOut(BaseModel):
    """Feedback response schema"""
    id: str
    article_id: str
    officer_id: str
    accuracy_rating: Optional[int] = None
    relevance_rating: Optional[int] = None
    sentiment_correct: Optional[bool] = None
    category: Optional[str] = None
    comments: Optional[str] = None
    internal_notes: Optional[str] = None
    requires_action: bool
    action_taken: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


# ============================================================================
# System Settings Schemas
# ============================================================================

class SettingCreate(BaseModel):
    """Create system setting schema"""
    key: str
    value: str
    value_type: str = "string"
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: bool = False


class SettingUpdate(BaseModel):
    """Update system setting schema"""
    value: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class SettingOut(BaseModel):
    """System setting response schema"""
    id: str
    key: str
    value: str
    value_type: str
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


# ============================================================================
# PIB Alert Schemas
# ============================================================================

class PIBAlertOut(BaseModel):
    """PIB Alert response schema"""
    id: str
    article_id: str
    title: str
    summary: Optional[str] = None
    link: Optional[str] = None
    language: Optional[str] = None
    sentiment_score: Optional[float] = None
    is_reviewed: bool
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    email_sent: bool
    email_sent_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = {
        "from_attributes": True
    }


class PIBAlertListResponse(BaseModel):
    """List of PIB alerts response"""
    items: List[PIBAlertOut]
    total: int
    unread_count: int


class PIBAlertReview(BaseModel):
    """Mark PIB alert as reviewed"""
    is_reviewed: bool = True


# ============================================================================
# Article Schemas (existing, kept for compatibility)
# ============================================================================

class Entity(BaseModel):
    text: str
    label: str
    start: Optional[int] = None
    end: Optional[int] = None
    confidence: Optional[float] = None
    type: Optional[str] = None  # gazetteer | ner

    # Be lenient: accept extra keys that may be present in stored JSONB
    model_config = {
        "extra": "allow"
    }


class ArticleIn(BaseModel):
    url: HttpUrl
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    region: Optional[str] = None
    language: Optional[str] = None
    detected_language: Optional[str] = None
    detected_script: Optional[str] = None
    language_confidence: Optional[float] = None
    translated_title: Optional[str] = None
    translated_summary: Optional[str] = None
    published_at: Optional[datetime] = None


class ArticleOut(BaseModel):
    id: str
    url: str
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    source: Optional[str] = None
    source_type: Optional[str] = None  # 'rss' or 'scraper'
    region: Optional[str] = None
    language: Optional[str] = None
    detected_language: Optional[str] = None
    detected_script: Optional[str] = None
    language_confidence: Optional[float] = None
    translated_title: Optional[str] = None
    translated_summary: Optional[str] = None
    translation_status: Optional[str] = None  # 'translated', 'not_translated', 'original'
    published_at: Optional[datetime] = None
    collected_at: Optional[datetime] = None
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    sentiment_polarity: Optional[float] = None  # -1 to +1 polarity scale
    topic_labels: Optional[List[str]] = None
    # Allow extra keys within each entity dict to avoid validation 500s
    entities: Optional[List[Entity]] = None
    # GoI relevance fields (optional; frontend ignores if unused)
    is_goi: Optional[bool] = None
    relevance_score: Optional[float] = None
    goi_ministries: Optional[List[str]] = None
    goi_schemes: Optional[List[str]] = None
    goi_matched_terms: Optional[List[str]] = None
    
    # Content classification fields
    content_category: Optional[str] = None
    content_sub_category: Optional[str] = None
    classification_confidence: Optional[float] = None
    classification_keywords: Optional[List[str]] = None
    should_show_pib: Optional[bool] = None
    filter_reason: Optional[str] = None

    class Config:
        from_attributes = True


class NewsListResponse(BaseModel):
    items: List[ArticleOut]
    total: int


class AnalyticsBucket(BaseModel):
    key: str = Field(..., alias="label", description="Alias for uniformity when needed")
    count: int


class SentimentAnalytics(BaseModel):
    sentiment: str
    count: int


class CategoryAnalytics(BaseModel):
    category: str
    count: int


class RegionAnalytics(BaseModel):
    region: str
    count: int


class SourceAnalytics(BaseModel):
    source: str
    count: int


class LanguageAnalytics(BaseModel):
    language: str
    language_name: Optional[str] = None
    script: Optional[str] = None
    count: int


class ScriptAnalytics(BaseModel):
    script: str
    count: int


# Rebuild models to resolve forward references
TokenResponse.model_rebuild()
