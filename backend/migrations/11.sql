-- Migration 11: Add source_type column to distinguish RSS vs Web Scraping
-- This enables independent collection from both RSS feeds and direct web scraping

ALTER TABLE articles 
ADD COLUMN source_type VARCHAR(32) DEFAULT 'rss';

-- Update existing articles to mark them as RSS-sourced
UPDATE articles 
SET source_type = 'rss' 
WHERE source_type IS NULL;

-- Create index for filtering by source type
CREATE INDEX idx_articles_source_type ON articles(source_type);

-- Add comment for documentation
COMMENT ON COLUMN articles.source_type IS 'Collection method: rss (from RSS feeds) or scraper (direct web scraping)';
