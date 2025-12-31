-- Migration 13: Add Confidence Scoring and Verification System
-- Purpose: Enable AI confidence-based routing and PIB officer verification for 100% accuracy

-- Add confidence scoring fields to articles table
ALTER TABLE articles ADD COLUMN IF NOT EXISTS confidence_score DECIMAL(3,2);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS confidence_level VARCHAR(20);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS confidence_factors TEXT[];
ALTER TABLE articles ADD COLUMN IF NOT EXISTS auto_approved BOOLEAN DEFAULT FALSE;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS auto_rejected BOOLEAN DEFAULT FALSE;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS needs_verification BOOLEAN DEFAULT FALSE;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS anomalies TEXT[];

-- Add verification tracking fields
ALTER TABLE articles ADD COLUMN IF NOT EXISTS verified_by VARCHAR(255);
ALTER TABLE articles ADD COLUMN IF NOT EXISTS verified_at TIMESTAMP;
ALTER TABLE articles ADD COLUMN IF NOT EXISTS verification_status VARCHAR(50);

COMMENT ON COLUMN articles.confidence_score IS 'AI confidence score (0.0-1.0) for article being government scheme';
COMMENT ON COLUMN articles.confidence_level IS 'Confidence level: high (0.8+), medium (0.5-0.8), low (<0.5)';
COMMENT ON COLUMN articles.confidence_factors IS 'Array of factors contributing to confidence score';
COMMENT ON COLUMN articles.auto_approved IS 'True if article auto-approved (high confidence)';
COMMENT ON COLUMN articles.auto_rejected IS 'True if article auto-rejected (low confidence)';
COMMENT ON COLUMN articles.needs_verification IS 'True if article needs PIB officer review (medium confidence)';
COMMENT ON COLUMN articles.anomalies IS 'Array of detected anomalies for human review';

-- Create article_verifications table for PIB officer feedback
CREATE TABLE IF NOT EXISTS article_verifications (
    id SERIAL PRIMARY KEY,
    article_id VARCHAR NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    verified_by VARCHAR(255) NOT NULL,
    is_relevant BOOLEAN NOT NULL,
    correct_category VARCHAR(100),
    correction_reason TEXT,
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Track what system predicted for accuracy measurement
    predicted_category VARCHAR(100),
    predicted_should_show BOOLEAN,
    predicted_confidence DECIMAL(3,2),
    
    -- For learning from mistakes
    error_type VARCHAR(50),  -- 'false_positive', 'false_negative', 'miscategorization', 'correct'
    keywords_causing_error TEXT[],
    
    CONSTRAINT unique_verification UNIQUE(article_id, verified_by)
);

CREATE INDEX IF NOT EXISTS idx_verifications_article ON article_verifications(article_id);
CREATE INDEX IF NOT EXISTS idx_verifications_verified_by ON article_verifications(verified_by);
CREATE INDEX IF NOT EXISTS idx_verifications_verified_at ON article_verifications(verified_at);
CREATE INDEX IF NOT EXISTS idx_verifications_error_type ON article_verifications(error_type);
CREATE INDEX IF NOT EXISTS idx_verifications_is_relevant ON article_verifications(is_relevant);

-- Create indexes for confidence-based queries
CREATE INDEX IF NOT EXISTS idx_articles_confidence_level ON articles(confidence_level);
CREATE INDEX IF NOT EXISTS idx_articles_confidence_score ON articles(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_articles_needs_verification ON articles(needs_verification) WHERE needs_verification = TRUE;
CREATE INDEX IF NOT EXISTS idx_articles_auto_approved ON articles(auto_approved) WHERE auto_approved = TRUE;
CREATE INDEX IF NOT EXISTS idx_articles_auto_rejected ON articles(auto_rejected) WHERE auto_rejected = TRUE;
CREATE INDEX IF NOT EXISTS idx_articles_verification_status ON articles(verification_status);

-- Create quality metrics materialized view for fast dashboard queries
CREATE MATERIALIZED VIEW IF NOT EXISTS quality_metrics_daily AS
SELECT 
    DATE(published_at) as date,
    COUNT(*) as total_articles,
    COUNT(*) FILTER (WHERE auto_approved = TRUE) as auto_approved_count,
    COUNT(*) FILTER (WHERE auto_rejected = TRUE) as auto_rejected_count,
    COUNT(*) FILTER (WHERE needs_verification = TRUE) as needs_review_count,
    COUNT(*) FILTER (WHERE confidence_level = 'high') as high_confidence_count,
    COUNT(*) FILTER (WHERE confidence_level = 'medium') as medium_confidence_count,
    COUNT(*) FILTER (WHERE confidence_level = 'low') as low_confidence_count,
    AVG(confidence_score) as avg_confidence,
    COUNT(*) FILTER (WHERE anomalies IS NOT NULL AND array_length(anomalies, 1) > 0) as anomalies_count,
    COUNT(*) FILTER (WHERE verification_status = 'verified') as verified_count
FROM articles
WHERE published_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(published_at)
ORDER BY date DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_quality_metrics_date ON quality_metrics_daily(date);

-- Create accuracy metrics view from verifications
CREATE MATERIALIZED VIEW IF NOT EXISTS accuracy_metrics_daily AS
SELECT 
    DATE(verified_at) as date,
    COUNT(*) as total_verifications,
    COUNT(*) FILTER (WHERE is_relevant = predicted_should_show) as correct_predictions,
    COUNT(*) FILTER (WHERE is_relevant = TRUE AND predicted_should_show = FALSE) as false_negatives,
    COUNT(*) FILTER (WHERE is_relevant = FALSE AND predicted_should_show = TRUE) as false_positives,
    COUNT(*) FILTER (WHERE error_type = 'correct') as correct_count,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_relevant = predicted_should_show) / NULLIF(COUNT(*), 0), 2) as accuracy_percentage,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_relevant = FALSE AND predicted_should_show = TRUE) / NULLIF(COUNT(*), 0), 2) as false_positive_rate,
    ROUND(100.0 * COUNT(*) FILTER (WHERE is_relevant = TRUE AND predicted_should_show = FALSE) / NULLIF(COUNT(*), 0), 2) as false_negative_rate
FROM article_verifications
WHERE verified_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(verified_at)
ORDER BY date DESC;

CREATE UNIQUE INDEX IF NOT EXISTS idx_accuracy_metrics_date ON accuracy_metrics_daily(date);

-- Function to refresh materialized views (call daily via cron)
CREATE OR REPLACE FUNCTION refresh_quality_metrics() RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY quality_metrics_daily;
    REFRESH MATERIALIZED VIEW CONCURRENTLY accuracy_metrics_daily;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION refresh_quality_metrics() IS 'Refresh quality and accuracy metrics views - run daily';
