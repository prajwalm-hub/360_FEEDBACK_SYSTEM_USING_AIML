from pydantic_settings import BaseSettings
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "360-Degree Feedback Backend"
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    API_PREFIX: str = "/api"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Security & Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production-min-32-chars-long"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database (PostgreSQL default)
    DB_PROVIDER: str = "postgres"  # "postgres" or "mongodb"
    DATABASE_URL: str = (
        "postgresql+psycopg2://postgres:postgres@db:5432/newsdb"
    )

    # Mongo (optional)
    MONGODB_URI: str = "mongodb://mongo:27017"
    MONGODB_DB: str = "newsdb"

    # NLP
    NLP_ENABLED: bool = True
    SENTIMENT_MODEL: str = "nlptown/bert-base-multilingual-uncased-sentiment"  # Multilingual fallback (5-star rating)
    ZERO_SHOT_MODEL: str = "joeddav/xlm-roberta-large-xnli"
    NER_MODEL: str = "xlm-roberta-large-finetuned-conll03-english"
    ZERO_SHOT_ENABLED: bool = False  # Disable zero-shot classification (slow to load)
    NER_ENABLED: bool = False  # Disable NER (requires additional models, optional)
    USE_GPU: bool = False
    MODEL_CACHE_DIR: Optional[str] = None
    BATCH_SIZE: int = 8
    MAX_LENGTH: int = 512
    
    # Multilingual Translation (MANDATORY for all regional languages)
    TRANSLATION_ENABLED: bool = True  # ALWAYS enabled - mandatory for regional language articles
    TRANSLATION_MODEL: str = "ai4bharat/indictrans2-indic-en-1B"
    
    # Hybrid Sentiment Analysis Configuration
    # English Articles: Cardiff RoBERTa (best for English news/social media)
    ENGLISH_SENTIMENT_MODEL: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"
    
    # IndicBERT Sentiment (Recommended for Indian Government News)
    INDICBERT_SENTIMENT_ENABLED: bool = True  # Enable for Indian languages
    INDICBERT_SENTIMENT_MODEL: str = "ai4bharat/indic-bert"  # Base IndicBERT model
    INDICBERT_FINETUNED_MODEL: str = "cardiffnlp/twitter-xlm-roberta-base-sentiment"  # Multilingual sentiment (supports Indian languages)
    
    # Rule-Based Sentiment Adjuster (Applied to ALL languages)
    RULE_BASED_ADJUSTER_ENABLED: bool = True  # Enable keyword-based sentiment adjustment
    SENTIMENT_BOOST_THRESHOLD: float = 0.15  # Boost/reduce score by this amount for keyword matches
    
    # Regional Entity Recognition
    REGIONAL_ENTITY_NORMALIZATION: bool = True  # Normalize regional entity names
    GAZETTEER_MATCHING: bool = True  # Enable India-specific gazetteer matching
    
    TOPIC_LABELS: List[str] = [
        "health",
        "education",
        "agriculture",
        "policy",
        "infrastructure",
        "economy",
        "environment",
        "defense",
        "politics",
        "technology",
        "sports",
        "law & order",
        "social welfare",
        "transport",
        "rural development",
        "energy",
        "women & child",
        "finance",
        "employment",
        "foreign affairs",
    ]

    # Collector
    FEEDS_FILE: str = "app/feeds.yaml"
    COLLECT_INTERVAL_MIN: int = 60
    GDELT_ENABLED: bool = False

    # CORS
    CORS_ORIGINS: List[str] = ["*", "http://localhost:5173", "http://127.0.0.1:5173"]
    
    # PIB Alert System - SMTP Email Configuration
    SMTP_ENABLED: bool = True  # Enable/disable email alerts
    SMTP_SERVER: str = "smtp.gmail.com"  # Gmail SMTP server
    SMTP_PORT: int = 587  # TLS port
    SMTP_USE_TLS: bool = True
    SMTP_USERNAME: str = ""  # Set via environment variable
    SMTP_PASSWORD: str = ""  # Set via environment variable (use App Password for Gmail)
    SMTP_FROM_EMAIL: str = "newsscope.india@gmail.com"
    PIB_ALERT_EMAIL: str = "viratkohlivc523@gmail.com"  # PIB Officer email
    FRONTEND_URL: str = "http://localhost:5173"  # Frontend URL for alert links
    
    # Alert trigger thresholds
    ALERT_NEGATIVE_THRESHOLD: float = 0.6  # Trigger alert if negative confidence >= 0.6
    ALERT_ENABLED: bool = True  # Master switch for PIB alert system

    # OpenAI API for lightweight RAG
    OPENAI_API_KEY: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

# Ensure .env is loaded from the backend directory explicitly
_ENV_PATH = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)
# Fix potential UTF-8 BOM-prefixed environment variable keys (e.g., \ufeffDATABASE_URL)
for key in list(os.environ.keys()):
    if key and key[0] == "\ufeff":
        os.environ[key.lstrip("\ufeff")] = os.environ[key]
        del os.environ[key]
settings = Settings()