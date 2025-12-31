-- Migration 9: Add GoI relevance fields to articles
ALTER TABLE IF EXISTS articles
    ADD COLUMN IF NOT EXISTS is_goi BOOLEAN,
    ADD COLUMN IF NOT EXISTS relevance_score DOUBLE PRECISION,
    ADD COLUMN IF NOT EXISTS goi_ministries TEXT[],
    ADD COLUMN IF NOT EXISTS goi_schemes TEXT[],
    ADD COLUMN IF NOT EXISTS goi_entities JSONB,
    ADD COLUMN IF NOT EXISTS goi_matched_terms TEXT[];

-- Index to speed up queries
CREATE INDEX IF NOT EXISTS idx_articles_is_goi ON articles (is_goi);
