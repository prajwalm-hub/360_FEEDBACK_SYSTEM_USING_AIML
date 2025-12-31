-- Rollback Migration 8: Remove multilingual support fields
-- Description: Remove language detection, script detection, and translation fields from articles table

-- Drop indexes
DROP INDEX IF EXISTS idx_articles_detected_script;
DROP INDEX IF EXISTS idx_articles_detected_language;
DROP INDEX IF EXISTS idx_articles_language;

-- Remove columns
ALTER TABLE articles 
DROP COLUMN IF EXISTS translated_summary,
DROP COLUMN IF EXISTS translated_title,
DROP COLUMN IF EXISTS language_confidence,
DROP COLUMN IF EXISTS detected_script,
DROP COLUMN IF EXISTS detected_language;
