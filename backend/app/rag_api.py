"""
RAG API Endpoints for NewsScope India
"""
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field

from .database import get_database
from .auth import get_current_user
import os
import logging

logger = logging.getLogger(__name__)

# Try OpenAI RAG first, fallback to improved RAG
try:
    USE_OPENAI = os.getenv("USE_OPENAI_RAG", "false").lower() == "true"
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    if USE_OPENAI and OPENAI_API_KEY:
        from .rag_openai import get_openai_rag, OpenAIRAGAssistant as RAGAssistant
        def get_rag_assistant(db):
            return get_openai_rag(db, OPENAI_API_KEY)
        logger.info("Using OpenAI GPT-4 for RAG")
    else:
        from .rag_improved import get_improved_rag as get_rag_assistant, ImprovedRAGAssistant as RAGAssistant
        logger.info("Using open-source models for RAG")
except Exception as e:
    logger.warning(f"Failed to load OpenAI RAG, using fallback: {e}")
    from .rag_improved import get_improved_rag as get_rag_assistant, ImprovedRAGAssistant as RAGAssistant

# Setup logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG Assistant"])


# Optional auth dependency for RAG endpoints (allows unauthenticated access for testing)
def get_optional_user(
    db=Depends(get_database)
):
    """Optional user authentication - allows access without token for RAG assistant"""
    # For now, allow anonymous access to RAG endpoints
    # In production, you might want to enforce auth
    return None


# Request/Response Models
class RAGQuery(BaseModel):
    """RAG query request"""
    question: str = Field(..., description="User question")
    language: str = Field("en", description="Response language (en, hi, etc.)")
    k: int = Field(5, ge=1, le=20, description="Number of documents to retrieve")
    filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")


class RAGResponse(BaseModel):
    """RAG query response"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence: float
    retrieved_docs: int
    language: str


class VectorStoreBuild(BaseModel):
    """Vector store build request"""
    days: int = Field(30, ge=1, le=365, description="Days of articles to index")
    filters: Optional[Dict[str, Any]] = None
    force_rebuild: bool = Field(False, description="Force rebuild even if cache exists")


class SummaryRequest(BaseModel):
    """Summary request"""
    filters: Dict[str, Any]
    summary_type: str = Field("topics", description="topics, sentiment, or ministries")


# Endpoints
@router.post("/query", response_model=RAGResponse)
async def query_rag(
    query: RAGQuery,
    db=Depends(get_database),
    current_user=Depends(get_optional_user)
) -> RAGResponse:
    """
    Query the RAG assistant
    
    Example questions:
    - "Summarize today's news about PM Modi"
    - "Show me positive news about Jal Jeevan Mission"
    - "What are the latest schemes announced?"
    """
    logger.info(f"[RAG PIPELINE STARTED] Question: {query.question[:100]}...")
    logger.info(f"[RAG QUERY RECEIVED] Language: {query.language}, K: {query.k}")
    
    try:
        # Get SQLAlchemy session from Database object
        session = db.get_session()
        rag = get_rag_assistant(session)
        
        # Auto-build vector store on first query if not initialized
        if not rag.vectorstore:
            logger.info("[RAG PIPELINE] Vector store not initialized, building automatically...")
            try:
                rag.build_vectorstore(days=30, force_rebuild=False)
                logger.info("[RAG PIPELINE] Vector store built successfully")
            except Exception as build_error:
                logger.error(f"[RAG PIPELINE] Failed to build vector store: {build_error}")
                raise HTTPException(
                    status_code=503,
                    detail=f"RAG system is initializing. Please try again in a few moments."
                )
        
        logger.info(f"[RAG PIPELINE] Querying vector store with {query.k} documents...")
        result = rag.query(
            question=query.question,
            k=query.k,
            filters=query.filters,
            language=query.language
        )
        
        logger.info(f"[RAG RESPONSE GENERATED] Retrieved {result['retrieved_docs']} docs, confidence: {result['confidence']:.2f}")
        logger.info(f"[RAG RESPONSE] Answer preview: {result['answer'][:150]}...")
        
        return RAGResponse(
            answer=result["answer"],
            sources=result["sources"],
            confidence=result["confidence"],
            retrieved_docs=result["retrieved_docs"],
            language=query.language
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[RAG PIPELINE ERROR] {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"RAG query failed: {str(e)}")


@router.post("/build")
async def build_vectorstore(
    build_req: VectorStoreBuild,
    background_tasks: BackgroundTasks,
    db=Depends(get_database),
    current_user=Depends(get_optional_user)
):
    """
    Build or rebuild the vector store (async)
    """
    def build_task():
        try:
            session = db.get_session()
            rag = get_rag_assistant(session)
            rag.build_vectorstore(
                days=build_req.days,
                filters=build_req.filters,
                force_rebuild=build_req.force_rebuild
            )
        except Exception as e:
            print(f"Vector store build failed: {e}")
    
    background_tasks.add_task(build_task)
    
    return {
        "status": "building",
        "message": f"Building vector store from last {build_req.days} days of articles..."
    }


@router.get("/status")
async def get_status(
    db=Depends(get_database),
    current_user=Depends(get_optional_user)
):
    """Get RAG system status"""
    try:
        session = db.get_session()
        rag = get_rag_assistant(session)
        
        return {
            "initialized": rag.vectorstore is not None,
            "last_update": str(rag.last_update) if rag.last_update else None,
            "embedding_model": "openai" if USE_OPENAI else "multilingual",
            "cache_dir": getattr(rag, 'cache_dir', None)  # OpenAIRAGAssistant doesn't have cache_dir
        }
    except Exception as e:
        logger.error(f"[RAG STATUS ERROR] {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summary")
async def get_summary(
    summary_req: SummaryRequest,
    db=Depends(get_database),
    current_user=Depends(get_optional_user)
):
    """
    Get aggregated summary based on filters
    
    Examples:
    - filters: {"date_from": "2024-01-01", "language": "hi", "sentiment": "positive"}
    - summary_type: "topics", "sentiment", "ministries"
    """
    logger.info(f"[RAG SUMMARY] Type: {summary_req.summary_type}, Filters: {summary_req.filters}")
    
    try:
        session = db.get_session()
        rag = get_rag_assistant(session)
        result = rag.get_summary(
            filters=summary_req.filters,
            summary_type=summary_req.summary_type
        )
        
        logger.info(f"[RAG SUMMARY GENERATED] Type: {summary_req.summary_type}")
        return result
    except Exception as e:
        logger.error(f"[RAG SUMMARY ERROR] {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_query_suggestions(
    language: str = Query("en", description="Language code"),
    current_user=Depends(get_optional_user)
):
    """Get suggested questions for the RAG assistant"""
    
    suggestions = {
        "en": [
            "Summarize today's news about the Prime Minister",
            "What are the latest government schemes announced?",
            "Show me positive news about Jal Jeevan Mission",
            "What did the Finance Minister say recently?",
            "Summarize news about digital India initiatives",
            "What are the trending topics in government news?",
            "Show me news about healthcare schemes",
            "What's happening with railway modernization?"
        ],
        "hi": [
            "प्रधानमंत्री के बारे में आज की खबरों का सारांश दें",
            "हाल ही में घोषित सरकारी योजनाएं क्या हैं?",
            "जल जीवन मिशन के बारे में सकारात्मक समाचार दिखाएं",
            "वित्त मंत्री ने हाल ही में क्या कहा?",
            "डिजिटल इंडिया पहल के बारे में समाचारों का सारांश दें",
            "सरकारी समाचारों में ट्रेंडिंग विषय क्या हैं?",
            "स्वास्थ्य योजनाओं के बारे में समाचार दिखाएं",
            "रेलवे आधुनिकीकरण के साथ क्या हो रहा है?"
        ]
    }
    
    return {
        "suggestions": suggestions.get(language, suggestions["en"]),
        "language": language
    }


@router.get("/quick-insights")
async def get_quick_insights(
    days: int = Query(7, ge=1, le=30),
    db=Depends(get_database),
    current_user=Depends(get_optional_user)
):
    """
    Get quick insights from recent news
    """
    try:
        session = db.get_session()
        rag = get_rag_assistant(session)
        
        date_from = datetime.utcnow() - timedelta(days=days)
        
        # Get various summaries
        topics = rag.get_summary(
            filters={"date_from": date_from},
            summary_type="topics"
        )
        
        sentiment = rag.get_summary(
            filters={"date_from": date_from},
            summary_type="sentiment"
        )
        
        ministries = rag.get_summary(
            filters={"date_from": date_from, "is_goi": True},
            summary_type="ministries"
        )
        
        return {
            "period_days": days,
            "date_from": str(date_from),
            "top_topics": topics.get("topics", [])[:5],
            "sentiment_distribution": sentiment.get("sentiment_distribution", {}),
            "top_ministries": ministries.get("ministries", [])[:5]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
