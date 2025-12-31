-- Migration 10: Add sentiment_polarity column to articles table
-- This column stores sentiment on a scale from -1 (strongly negative) to +1 (strongly positive)

ALTER TABLE articles ADD COLUMN IF NOT EXISTS sentiment_polarity REAL;

-- Add index for polarity-based queries
CREATE INDEX IF NOT EXISTS idx_articles_sentiment_polarity ON articles(sentiment_polarity);

-- Add comment
COMMENT ON COLUMN articles.sentiment_polarity IS 'Sentiment polarity score from -1 (strongly negative) to +1 (strongly positive)';
