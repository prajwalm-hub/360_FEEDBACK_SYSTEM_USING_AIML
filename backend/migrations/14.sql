-- Migration 14: Advanced Analytics & Intelligence Features
-- Adds tables for trend predictions, press briefs, and timeline caching
-- Author: AI Pipeline Team
-- Date: December 23, 2025

-- ============================================================================
-- 1. TREND PREDICTIONS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS trend_predictions (
    id SERIAL PRIMARY KEY,
    entity VARCHAR(255) NOT NULL,
    entity_type VARCHAR(50) NOT NULL, -- 'scheme', 'ministry', 'category'
    velocity_score DECIMAL(5,2) NOT NULL,
    strength VARCHAR(20) NOT NULL, -- 'explosive', 'very_high', 'high', 'moderate'
    current_mentions INTEGER NOT NULL,
    historical_avg DECIMAL(8,2),
    increase_pct DECIMAL(6,2),
    avg_confidence DECIMAL(3,2),
    avg_sentiment DECIMAL(4,2),
    period_days INTEGER NOT NULL,
    alert_message TEXT,
    context JSONB, -- Array of recent articles
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_trend_predictions_entity ON trend_predictions(entity);
CREATE INDEX idx_trend_predictions_entity_type ON trend_predictions(entity_type);
CREATE INDEX idx_trend_predictions_strength ON trend_predictions(strength);
CREATE INDEX idx_trend_predictions_velocity ON trend_predictions(velocity_score DESC);
CREATE INDEX idx_trend_predictions_detected_at ON trend_predictions(detected_at DESC);


-- ============================================================================
-- 2. PRESS BRIEFS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS press_briefs (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    date_range VARCHAR(100),
    scheme VARCHAR(255),
    ministry VARCHAR(255),
    category VARCHAR(100),
    total_articles INTEGER,
    avg_confidence DECIMAL(3,2),
    sections JSONB NOT NULL, -- JSON structure with all brief sections
    generated_by VARCHAR(255), -- User who generated it
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_press_briefs_scheme ON press_briefs(scheme);
CREATE INDEX idx_press_briefs_ministry ON press_briefs(ministry);
CREATE INDEX idx_press_briefs_category ON press_briefs(category);
CREATE INDEX idx_press_briefs_generated_at ON press_briefs(generated_at DESC);
CREATE INDEX idx_press_briefs_is_published ON press_briefs(is_published);


-- ============================================================================
-- 3. POLICY TIMELINE CACHE
-- ============================================================================
CREATE TABLE IF NOT EXISTS policy_timeline_cache (
    id SERIAL PRIMARY KEY,
    scheme VARCHAR(255) NOT NULL UNIQUE,
    timeline_data JSONB NOT NULL, -- Complete timeline data
    months_analyzed INTEGER NOT NULL,
    total_articles INTEGER,
    avg_sentiment DECIMAL(4,2),
    first_mention TIMESTAMP,
    latest_mention TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_policy_timeline_scheme ON policy_timeline_cache(scheme);
CREATE INDEX idx_policy_timeline_updated ON policy_timeline_cache(last_updated DESC);


-- ============================================================================
-- 4. GEOGRAPHIC ANALYTICS CACHE
-- ============================================================================
CREATE TABLE IF NOT EXISTS geo_analytics_cache (
    id SERIAL PRIMARY KEY,
    region VARCHAR(255) NOT NULL,
    analysis_type VARCHAR(50) NOT NULL, -- 'heatmap', 'scheme_coverage', 'ministry_footprint'
    period_days INTEGER NOT NULL,
    article_count INTEGER,
    avg_confidence DECIMAL(3,2),
    avg_sentiment DECIMAL(4,2),
    analytics_data JSONB NOT NULL, -- GeoJSON or analysis data
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(region, analysis_type, period_days)
);

CREATE INDEX idx_geo_analytics_region ON geo_analytics_cache(region);
CREATE INDEX idx_geo_analytics_type ON geo_analytics_cache(analysis_type);
CREATE INDEX idx_geo_analytics_updated ON geo_analytics_cache(last_updated DESC);


-- ============================================================================
-- 5. SCHEME MILESTONES TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS scheme_milestones (
    id SERIAL PRIMARY KEY,
    scheme VARCHAR(255) NOT NULL,
    milestone_date TIMESTAMP NOT NULL,
    milestone_type VARCHAR(50) NOT NULL, -- 'announcement', 'budget_allocation', 'implementation', 'achievement', 'expansion', 'review'
    title VARCHAR(500) NOT NULL,
    article_id VARCHAR(255) REFERENCES articles(id) ON DELETE SET NULL,
    source_name VARCHAR(255),
    sentiment VARCHAR(20),
    confidence_score DECIMAL(3,2),
    auto_detected BOOLEAN DEFAULT TRUE,
    verified_by VARCHAR(255),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_scheme_milestones_scheme ON scheme_milestones(scheme);
CREATE INDEX idx_scheme_milestones_date ON scheme_milestones(milestone_date DESC);
CREATE INDEX idx_scheme_milestones_type ON scheme_milestones(milestone_type);
CREATE INDEX idx_scheme_milestones_verified ON scheme_milestones(verified_by);


-- ============================================================================
-- 6. CRISIS ALERTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS crisis_alerts (
    id SERIAL PRIMARY KEY,
    region VARCHAR(255) NOT NULL,
    severity VARCHAR(20) NOT NULL, -- 'high', 'medium'
    article_count INTEGER NOT NULL,
    avg_sentiment DECIMAL(4,2) NOT NULL,
    primary_issue VARCHAR(100),
    alert_message TEXT,
    recent_headlines TEXT[], -- Array of headlines
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMP,
    resolved_at TIMESTAMP,
    resolution_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_crisis_alerts_region ON crisis_alerts(region);
CREATE INDEX idx_crisis_alerts_severity ON crisis_alerts(severity);
CREATE INDEX idx_crisis_alerts_detected_at ON crisis_alerts(detected_at DESC);
CREATE INDEX idx_crisis_alerts_acknowledged ON crisis_alerts(acknowledged_by);


-- ============================================================================
-- 7. ANALYTICS QUERY LOG (Performance Tracking)
-- ============================================================================
CREATE TABLE IF NOT EXISTS analytics_query_log (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(255) NOT NULL,
    query_type VARCHAR(50) NOT NULL, -- 'trend', 'brief', 'timeline', 'geo'
    parameters JSONB,
    execution_time_ms INTEGER,
    result_count INTEGER,
    user_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analytics_query_endpoint ON analytics_query_log(endpoint);
CREATE INDEX idx_analytics_query_type ON analytics_query_log(query_type);
CREATE INDEX idx_analytics_query_created_at ON analytics_query_log(created_at DESC);


-- ============================================================================
-- 8. UPDATE TRIGGER FOR press_briefs
-- ============================================================================
CREATE OR REPLACE FUNCTION update_press_briefs_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_press_briefs_timestamp ON press_briefs;
CREATE TRIGGER trigger_update_press_briefs_timestamp
    BEFORE UPDATE ON press_briefs
    FOR EACH ROW
    EXECUTE FUNCTION update_press_briefs_timestamp();


-- ============================================================================
-- 9. MATERIALIZED VIEW: Trending Topics Summary
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_trending_topics;
CREATE MATERIALIZED VIEW mv_trending_topics AS
SELECT 
    unnest(goi_schemes) as entity,
    'scheme' as entity_type,
    COUNT(*) as mention_count,
    AVG(confidence_score) as avg_confidence,
    AVG(sentiment_score) as avg_sentiment,
    DATE_TRUNC('day', created_at) as mention_date
FROM articles
WHERE is_goi = TRUE
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
  AND goi_schemes IS NOT NULL
  AND array_length(goi_schemes, 1) > 0
GROUP BY unnest(goi_schemes), DATE_TRUNC('day', created_at)

UNION ALL

SELECT 
    unnest(goi_ministries) as entity,
    'ministry' as entity_type,
    COUNT(*) as mention_count,
    AVG(confidence_score) as avg_confidence,
    AVG(sentiment_score) as avg_sentiment,
    DATE_TRUNC('day', created_at) as mention_date
FROM articles
WHERE is_goi = TRUE
  AND created_at >= CURRENT_DATE - INTERVAL '30 days'
  AND goi_ministries IS NOT NULL
  AND array_length(goi_ministries, 1) > 0
GROUP BY unnest(goi_ministries), DATE_TRUNC('day', created_at);

CREATE INDEX idx_mv_trending_entity ON mv_trending_topics(entity);
CREATE INDEX idx_mv_trending_date ON mv_trending_topics(mention_date DESC);


-- ============================================================================
-- 10. MATERIALIZED VIEW: Geographic Coverage Summary
-- ============================================================================
DROP MATERIALIZED VIEW IF EXISTS mv_geographic_coverage;
CREATE MATERIALIZED VIEW mv_geographic_coverage AS
SELECT 
    detected_region as region,
    COUNT(*) as total_articles,
    AVG(confidence_score) as avg_confidence,
    AVG(sentiment_score) as avg_sentiment,
    COUNT(DISTINCT source_name) as unique_sources,
    DATE_TRUNC('week', created_at) as coverage_week
FROM articles
WHERE is_goi = TRUE
  AND created_at >= CURRENT_DATE - INTERVAL '90 days'
  AND detected_region IS NOT NULL
  AND detected_region != 'India'
GROUP BY detected_region, DATE_TRUNC('week', created_at);

CREATE INDEX idx_mv_geo_region ON mv_geographic_coverage(region);
CREATE INDEX idx_mv_geo_week ON mv_geographic_coverage(coverage_week DESC);


-- ============================================================================
-- 11. GRANT PERMISSIONS
-- ============================================================================
-- Grant access to web application user (adjust username as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO your_app_user;
-- GRANT SELECT ON ALL MATERIALIZED VIEWS IN SCHEMA public TO your_app_user;


-- ============================================================================
-- 12. REFRESH MATERIALIZED VIEWS (Run after migration)
-- ============================================================================
-- REFRESH MATERIALIZED VIEW mv_trending_topics;
-- REFRESH MATERIALIZED VIEW mv_geographic_coverage;


-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- This migration adds advanced analytics capabilities:
-- - Trend predictions with velocity scoring
-- - Automated press brief generation and storage
-- - Policy timeline caching for performance
-- - Geographic analytics with GeoJSON support
-- - Scheme milestone tracking
-- - Crisis detection and alerting
-- - Analytics query performance logging
-- - Materialized views for fast reporting
--
-- Next steps:
-- 1. Run this migration: psql -U user -d dbname -f 14.sql
-- 2. Refresh materialized views (every 6-24 hours via cron)
-- 3. Test new API endpoints in api_assistant.py
-- 4. Build frontend dashboards for visualization
-- ============================================================================
