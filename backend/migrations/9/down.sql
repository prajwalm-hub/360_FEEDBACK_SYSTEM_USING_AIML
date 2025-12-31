-- Down migration for 9: Drop GoI relevance fields
ALTER TABLE IF EXISTS articles
    DROP COLUMN IF EXISTS goi_matched_terms,
    DROP COLUMN IF EXISTS goi_entities,
    DROP COLUMN IF EXISTS goi_schemes,
    DROP COLUMN IF EXISTS goi_ministries,
    DROP COLUMN IF EXISTS relevance_score,
    DROP COLUMN IF EXISTS is_goi;

DROP INDEX IF EXISTS idx_articles_is_goi;