-- SQL migrations to add performance indexes
-- Run these in PostgreSQL for 2-3x faster queries
-- Migration: Add performance indexes
-- Run date: 2025-12-06
-- Description: Add indexes for frequently queried fields

-- 1. Index on published_at for time-range queries (most common)
CREATE INDEX IF NOT EXISTS idx_articles_published_at 
ON articles(published_at DESC);

-- 2. Index on is_goi for filtering government articles
CREATE INDEX IF NOT EXISTS idx_articles_is_goi 
ON articles(is_goi) 
WHERE is_goi = true;

-- 3. Index on detected_language for language filtering
CREATE INDEX IF NOT EXISTS idx_articles_language 
ON articles(detected_language);

-- 4. Index on sentiment_label and score for sentiment filtering
CREATE INDEX IF NOT EXISTS idx_articles_sentiment 
ON articles(sentiment_label, sentiment_score DESC);

-- 5. GIN index on goi_schemes array for fast scheme searches
CREATE INDEX IF NOT EXISTS idx_articles_goi_schemes 
ON articles USING GIN (goi_schemes);

-- 6. GIN index on goi_ministries array
CREATE INDEX IF NOT EXISTS idx_articles_goi_ministries 
ON articles USING GIN (goi_ministries);

-- 7. Index on source for source-based filtering
CREATE INDEX IF NOT EXISTS idx_articles_source 
ON articles(source);

-- 8. Composite index for common query pattern (published + is_goi + sentiment)
CREATE INDEX IF NOT EXISTS idx_articles_common_query 
ON articles(published_at DESC, is_goi, sentiment_label) 
WHERE is_goi = true;

-- 9. Index on region for geographic filtering
CREATE INDEX IF NOT EXISTS idx_articles_region 
ON articles(region) 
WHERE region IS NOT NULL;

-- 10. Full-text search index on title and summary (English)
CREATE INDEX IF NOT EXISTS idx_articles_fts_en 
ON articles USING GIN(
    to_tsvector('english', 
        COALESCE(title, '') || ' ' || 
        COALESCE(summary, '') || ' ' ||
        COALESCE(translated_title, '') || ' ' ||
        COALESCE(translated_summary, '')
    )
);

-- 11. Full-text search index for Hindi (if postgres has Hindi support)
-- CREATE INDEX IF NOT EXISTS idx_articles_fts_hi 
-- ON articles USING GIN(
--     to_tsvector('hindi', 
--         COALESCE(title, '') || ' ' || 
--         COALESCE(summary, '')
--     )
-- );

-- 12. Index on hash for duplicate detection
CREATE INDEX IF NOT EXISTS idx_articles_hash 
ON articles(hash);

-- 13. Index on url for URL-based lookups
CREATE INDEX IF NOT EXISTS idx_articles_url 
ON articles(url);

-- Analyze tables to update statistics
ANALYZE articles;

-- Check index usage (run after some time to verify indexes are being used)
-- SELECT 
--     schemaname,
--     tablename,
--     indexname,
--     idx_scan,
--     idx_tup_read,
--     idx_tup_fetch
-- FROM pg_stat_user_indexes
-- WHERE tablename = 'articles'
-- ORDER BY idx_scan DESC;
