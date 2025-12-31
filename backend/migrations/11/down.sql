-- Rollback Migration 11: Remove source_type column

DROP INDEX IF EXISTS idx_articles_source_type;

ALTER TABLE articles 
DROP COLUMN IF EXISTS source_type;
