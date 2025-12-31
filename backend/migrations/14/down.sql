"""
Migration 14 Down Script - Rollback Advanced Analytics Features
"""

-- Drop materialized views
DROP MATERIALIZED VIEW IF EXISTS mv_geographic_coverage;
DROP MATERIALIZED VIEW IF EXISTS mv_trending_topics;

-- Drop trigger and function
DROP TRIGGER IF EXISTS trigger_update_press_briefs_timestamp ON press_briefs;
DROP FUNCTION IF EXISTS update_press_briefs_timestamp();

-- Drop tables (in reverse order of dependencies)
DROP TABLE IF EXISTS analytics_query_log;
DROP TABLE IF EXISTS crisis_alerts;
DROP TABLE IF EXISTS scheme_milestones;
DROP TABLE IF EXISTS geo_analytics_cache;
DROP TABLE IF EXISTS policy_timeline_cache;
DROP TABLE IF EXISTS press_briefs;
DROP TABLE IF EXISTS trend_predictions;
