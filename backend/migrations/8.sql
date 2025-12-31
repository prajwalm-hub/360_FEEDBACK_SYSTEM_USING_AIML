-- Migration 8: Add multilingual support fields
-- Description: Add language detection, script detection, and translation fields to articles table

-- Add new columns for multilingual support
ALTER TABLE articles 
ADD COLUMN IF NOT EXISTS detected_language VARCHAR(64),
ADD COLUMN IF NOT EXISTS detected_script VARCHAR(64),
ADD COLUMN IF NOT EXISTS language_confidence FLOAT,
ADD COLUMN IF NOT EXISTS translated_title TEXT,
ADD COLUMN IF NOT EXISTS translated_summary TEXT;

-- Create indexes for language filtering
CREATE INDEX IF NOT EXISTS idx_articles_language ON articles(language);
CREATE INDEX IF NOT EXISTS idx_articles_detected_language ON articles(detected_language);
CREATE INDEX IF NOT EXISTS idx_articles_detected_script ON articles(detected_script);

-- Add comments for documentation
COMMENT ON COLUMN articles.detected_language IS 'Auto-detected language code (ISO 639-1)';
COMMENT ON COLUMN articles.detected_script IS 'Auto-detected script (Devanagari, Tamil, Telugu, etc.)';
COMMENT ON COLUMN articles.language_confidence IS 'Confidence score for language detection (0-1)';
COMMENT ON COLUMN articles.translated_title IS 'English translation of title (for non-English articles)';
COMMENT ON COLUMN articles.translated_summary IS 'English translation of summary (for non-English articles)';
