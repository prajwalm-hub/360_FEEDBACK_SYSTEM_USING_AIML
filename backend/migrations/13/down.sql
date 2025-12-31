-- Rollback Migration 13: Remove Confidence Scoring and Verification System

-- Drop materialized views
DROP MATERIALIZED VIEW IF EXISTS accuracy_metrics_daily;
DROP MATERIALIZED VIEW IF EXISTS quality_metrics_daily;
DROP FUNCTION IF EXISTS refresh_quality_metrics();

-- Drop article_verifications table
DROP TABLE IF EXISTS article_verifications;

-- Drop indexes from articles table
DROP INDEX IF EXISTS idx_articles_verification_status;
DROP INDEX IF EXISTS idx_articles_auto_rejected;
DROP INDEX IF EXISTS idx_articles_auto_approved;
DROP INDEX IF EXISTS idx_articles_needs_verification;
DROP INDEX IF EXISTS idx_articles_confidence_score;
DROP INDEX IF EXISTS idx_articles_confidence_level;

-- Remove columns from articles table
ALTER TABLE articles DROP COLUMN IF EXISTS verification_status;
ALTER TABLE articles DROP COLUMN IF EXISTS verified_at;
ALTER TABLE articles DROP COLUMN IF EXISTS verified_by;
ALTER TABLE articles DROP COLUMN IF EXISTS anomalies;
ALTER TABLE articles DROP COLUMN IF EXISTS needs_verification;
ALTER TABLE articles DROP COLUMN IF EXISTS auto_rejected;
ALTER TABLE articles DROP COLUMN IF EXISTS auto_approved;
ALTER TABLE articles DROP COLUMN IF EXISTS confidence_factors;
ALTER TABLE articles DROP COLUMN IF EXISTS confidence_level;
ALTER TABLE articles DROP COLUMN IF EXISTS confidence_score;
