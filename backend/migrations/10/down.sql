-- Rollback Migration 10: Remove sentiment_polarity column

DROP INDEX IF EXISTS idx_articles_sentiment_polarity;
ALTER TABLE articles DROP COLUMN IF EXISTS sentiment_polarity;
