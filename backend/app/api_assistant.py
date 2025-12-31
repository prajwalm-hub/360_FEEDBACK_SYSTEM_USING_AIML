"""
Enhanced RAG API Endpoints for PIB Officers
Provides AI assistant with confidence-aware insights

Author: AI Pipeline Team
Date: December 23, 2025
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from .database import get_database, get_database as get_db
from .auth import get_current_user
from .rag_assistant import get_rag_assistant
from .trend_predictor import get_trend_predictor
from .press_brief_generator import get_press_brief_generator
from .policy_timeline import get_policy_timeline_analyzer
from .geo_intelligence import get_geo_intelligence

router = APIRouter(prefix="/assistant", tags=["assistant"])


class QueryRequest(BaseModel):
    """Standard RAG query request"""
    question: str
    k: int = 5
    filters: Optional[Dict[str, Any]] = None
    language: str = "en"


class PIBQueryRequest(BaseModel):
    """PIB officer-specific query with quality insights"""
    question: str
    k: int = 5
    filters: Optional[Dict[str, Any]] = None


@router.post("/query")
async def query_assistant(
    request: QueryRequest,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Standard RAG query - retrieves relevant articles and generates answer.
    """
    try:
        rag = get_rag_assistant(db)
        
        # Build vector store if not exists
        if not rag.vectorstore:
            filters = request.filters or {}
            filters.update({"is_goi": True})  # Only government news
            rag.build_vectorstore(days=30, filters=filters)
        
        result = rag.query(
            question=request.question,
            k=request.k,
            filters=request.filters,
            language=request.language
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.post("/pib/query")
async def query_pib_insights(
    request: PIBQueryRequest,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    PIB officer-specific query with confidence and quality insights.
    Returns answer + quality metrics + recommendations.
    """
    try:
        rag = get_rag_assistant(db)
        
        # Build vector store with high-confidence articles
        if not rag.vectorstore:
            filters = request.filters or {}
            filters.update({"is_goi": True})
            rag.build_vectorstore(days=30, filters=filters)
        
        result = rag.query_pib_insights(
            question=request.question,
            filters=request.filters,
            k=request.k
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PIB query failed: {str(e)}")


@router.get("/schemes/summary")
async def get_schemes_summary(
    days: int = Query(30, ge=1, le=90),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get summary of all government schemes in recent articles.
    Shows scheme coverage, confidence scores, and related ministries.
    """
    try:
        rag = get_rag_assistant(db)
        result = rag.get_scheme_summary(days=days)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheme summary failed: {str(e)}")


@router.get("/accuracy/insights")
async def get_accuracy_insights(
    days: int = Query(7, ge=1, le=30),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get accuracy and quality insights for PIB officers.
    Shows confidence distribution, processing stats, and quality metrics.
    """
    try:
        rag = get_rag_assistant(db)
        result = rag.get_accuracy_insights(days=days)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Accuracy insights failed: {str(e)}")


@router.get("/schemes/{scheme_name}")
async def get_scheme_info(
    scheme_name: str,
    k: int = Query(10, ge=1, le=50),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get detailed information about a specific government scheme.
    Retrieves all articles mentioning the scheme with confidence scores.
    """
    try:
        rag = get_rag_assistant(db)
        
        # Build vector store if needed
        if not rag.vectorstore:
            rag.build_vectorstore(days=90, filters={"is_goi": True})
        
        # Use standard query for scheme information
        result = rag.query(
            question=f"Tell me about {scheme_name} government scheme",
            k=k,
            filters={"is_goi": True}
        )
        
        # Filter sources to only those mentioning the scheme
        if result.get('sources'):
            filtered_sources = [
                s for s in result['sources']
                if any(scheme_name.lower() in scheme.lower() for scheme in s.get('schemes', []))
            ]
            result['sources'] = filtered_sources
            result['scheme_name'] = scheme_name
            result['found'] = len(filtered_sources) > 0
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheme query failed: {str(e)}")


@router.post("/rebuild")
async def rebuild_vectorstore(
    days: int = Query(30, ge=1, le=90),
    force: bool = Query(False),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Rebuild the vector store with latest articles.
    Use force=True to rebuild even if cache exists.
    """
    try:
        rag = get_rag_assistant(db)
        
        filters = {"is_goi": True}
        vectorstore = rag.build_vectorstore(
            days=days,
            filters=filters,
            force_rebuild=force
        )
        
        # Count documents
        doc_count = vectorstore.index.ntotal if hasattr(vectorstore.index, 'ntotal') else 0
        
        return {
            "status": "success",
            "message": f"Vector store rebuilt with {doc_count} document chunks",
            "days": days,
            "last_update": rag.last_update.isoformat() if rag.last_update else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")


@router.get("/health")
async def assistant_health(
    db = Depends(get_db)
):
    """
    Check AI assistant health status.
    """
    try:
        rag = get_rag_assistant(db)
        
        return {
            "status": "healthy",
            "vectorstore_loaded": rag.vectorstore is not None,
            "last_update": rag.last_update.isoformat() if rag.last_update else None,
            "use_openai": rag.use_openai
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@router.get("/examples")
async def get_example_queries():
    """
    Get example queries for PIB officers.
    """
    return {
        "general_queries": [
            "What are the latest PM Kisan updates?",
            "Tell me about Ayushman Bharat scheme",
            "What government schemes were announced this week?",
            "Show me articles about Digital India",
            "What is the status of Swachh Bharat Mission?"
        ],
        "ministry_queries": [
            "What schemes is the Ministry of Agriculture running?",
            "Latest updates from Ministry of Health",
            "What is Ministry of Education doing for skill development?"
        ],
        "regional_queries": [
            "Government schemes for Karnataka",
            "What schemes are available in Tamil Nadu?",
            "Show me schemes for rural development"
        ],
        "quality_queries": [
            "Show me only high-confidence articles about PM Awas Yojana",
            "What schemes have been verified by PIB officers?",
            "Articles with anomalies in the last week"
        ]
    }


# ============================================================================
# NEW FEATURES: Trend Analysis, Press Briefs, Timeline, Geo Intelligence
# ============================================================================

@router.get("/trends/emerging")
async def get_emerging_trends(
    days: int = Query(7, ge=1, le=30),
    velocity_threshold: float = Query(3.0, ge=2.0, le=10.0),
    min_mentions: int = Query(5, ge=3, le=20),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Detect emerging trends in government news using velocity analysis.**
    
    - **days**: Days to analyze for current period (default: 7)
    - **velocity_threshold**: Multiplier threshold (3.0 = 300% increase)
    - **min_mentions**: Minimum mentions to consider (avoid noise)
    
    Returns trends with velocity scores, strength indicators, and context.
    """
    try:
        predictor = get_trend_predictor(db)
        trends = predictor.detect_emerging_trends(
            days=days,
            velocity_threshold=velocity_threshold,
            min_mentions=min_mentions
        )
        
        return {
            "period": f"Last {days} days",
            "total_trends": len(trends),
            "trends": trends,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend detection failed: {str(e)}")


@router.get("/trends/summary")
async def get_trend_summary(
    days: int = Query(7, ge=1, le=30),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Get comprehensive trend analysis summary with alerts and predictions.**
    
    Returns:
    - Top trending topics
    - Critical alerts
    - Upcoming event predictions
    """
    try:
        predictor = get_trend_predictor(db)
        summary = predictor.get_trend_analysis_summary(days=days)
        return summary
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend summary failed: {str(e)}")


@router.post("/briefs/generate")
async def generate_press_brief(
    scheme: Optional[str] = None,
    ministry: Optional[str] = None,
    category: Optional[str] = None,
    days: int = Query(7, ge=1, le=30),
    focus: List[str] = Query(["achievements", "coverage", "implementation"]),
    min_confidence: float = Query(0.7, ge=0.5, le=1.0),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Generate automated press brief from verified articles.**
    
    PIB officers can generate weekly briefs for schemes, ministries, or categories.
    
    - **scheme**: Specific scheme (e.g., "PM Kisan")
    - **ministry**: Specific ministry
    - **category**: Content category
    - **days**: Days to analyze (default: 7)
    - **focus**: Areas to emphasize ["achievements", "coverage", "implementation", "challenges"]
    - **min_confidence**: Minimum confidence score (default: 0.7)
    
    Returns structured press brief with:
    - Key highlights
    - Regional coverage
    - Media sentiment
    - Talking points
    - Statistics
    """
    try:
        generator = get_press_brief_generator(db)
        brief = generator.generate_press_brief(
            scheme=scheme,
            ministry=ministry,
            category=category,
            days=days,
            focus=focus,
            min_confidence=min_confidence
        )
        
        return brief
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Brief generation failed: {str(e)}")


@router.get("/timeline/scheme/{scheme_name}")
async def get_scheme_timeline(
    scheme_name: str,
    months: int = Query(12, ge=1, le=24),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Get comprehensive timeline for a scheme showing evolution over time.**
    
    - **scheme_name**: Name of the scheme
    - **months**: Months to analyze (default: 12)
    
    Returns:
    - Milestones (announcement, budget, implementation, achievements)
    - Sentiment evolution (monthly trends)
    - Impact metrics (beneficiaries, budget, coverage)
    - Regional rollout timeline
    - Ministry involvement
    - Media coverage patterns
    """
    try:
        analyzer = get_policy_timeline_analyzer(db)
        timeline = analyzer.get_scheme_timeline(
            scheme=scheme_name,
            months=months
        )
        
        return timeline
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Timeline generation failed: {str(e)}")


@router.post("/timeline/compare")
async def compare_schemes_timeline(
    schemes: List[str],
    months: int = Query(6, ge=1, le=24),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Compare multiple schemes side-by-side.**
    
    - **schemes**: List of scheme names to compare
    - **months**: Months to analyze (default: 6)
    
    Returns comparison with insights on:
    - Most media coverage
    - Best sentiment
    - Widest geographic reach
    """
    try:
        analyzer = get_policy_timeline_analyzer(db)
        comparison = analyzer.compare_schemes(
            schemes=schemes,
            months=months
        )
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheme comparison failed: {str(e)}")


@router.get("/geo/heatmap")
async def get_geo_heatmap(
    days: int = Query(30, ge=7, le=90),
    min_articles: int = Query(1, ge=1, le=10),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Get geographic heat map showing news activity by state.**
    
    - **days**: Days to analyze (default: 30)
    - **min_articles**: Minimum articles to include state
    
    Returns GeoJSON-compatible data for mapping with:
    - State coordinates
    - Article counts
    - Confidence scores
    - Sentiment scores
    - Heat intensity
    """
    try:
        geo = get_geo_intelligence(db)
        heatmap = geo.get_heat_map_data(
            days=days,
            min_articles=min_articles
        )
        
        return heatmap
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap generation failed: {str(e)}")


@router.get("/geo/scheme-coverage/{scheme_name}")
async def get_scheme_coverage_map(
    scheme_name: str,
    days: int = Query(90, ge=30, le=180),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Show which states are implementing/covering a specific scheme.**
    
    - **scheme_name**: Name of the scheme
    - **days**: Days to analyze (default: 90)
    
    Returns map data showing:
    - States with scheme coverage
    - Coverage status (high/medium/low)
    - First and latest mentions
    - Related ministries
    """
    try:
        geo = get_geo_intelligence(db)
        coverage_map = geo.get_scheme_coverage_map(
            scheme=scheme_name,
            days=days
        )
        
        return coverage_map
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coverage map failed: {str(e)}")


@router.get("/geo/ministry-footprint/{ministry_name}")
async def get_ministry_footprint(
    ministry_name: str,
    days: int = Query(60, ge=30, le=180),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Track ministry activity across states (geographic footprint).**
    
    - **ministry_name**: Name of the ministry
    - **days**: Days to analyze (default: 60)
    
    Returns footprint data with:
    - States where ministry is active
    - Schemes being implemented
    - Sentiment per state
    """
    try:
        geo = get_geo_intelligence(db)
        footprint = geo.get_ministry_footprint(
            ministry=ministry_name,
            days=days
        )
        
        return footprint
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ministry footprint failed: {str(e)}")


@router.get("/geo/crisis-zones")
async def detect_crisis_zones(
    days: int = Query(7, ge=3, le=30),
    sentiment_threshold: float = Query(-0.5, ge=-1.0, le=-0.3),
    min_articles: int = Query(3, ge=2, le=10),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Detect regions with sudden spike in negative news (crisis detection).**
    
    - **days**: Days to analyze (default: 7)
    - **sentiment_threshold**: Negative sentiment threshold (default: -0.5)
    - **min_articles**: Minimum articles to trigger alert
    
    Returns crisis zones with:
    - Severity level
    - Primary issue
    - Recent headlines
    - Alert messages
    """
    try:
        geo = get_geo_intelligence(db)
        crisis_zones = geo.detect_crisis_zones(
            days=days,
            sentiment_threshold=sentiment_threshold,
            min_articles=min_articles
        )
        
        return {
            "total_crisis_zones": len(crisis_zones),
            "crisis_zones": crisis_zones,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Crisis detection failed: {str(e)}")


@router.post("/geo/compare-regions")
async def compare_regions(
    regions: List[str],
    days: int = Query(30, ge=7, le=90),
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    **Compare government news activity across specific regions.**
    
    - **regions**: List of region names to compare
    - **days**: Days to analyze (default: 30)
    
    Returns comparison with insights on most active region and best sentiment.
    """
    try:
        geo = get_geo_intelligence(db)
        comparison = geo.get_regional_comparison(
            regions=regions,
            days=days
        )
        
        return comparison
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Regional comparison failed: {str(e)}")
