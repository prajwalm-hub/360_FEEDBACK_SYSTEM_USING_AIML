
-- Revert to example URLs
UPDATE news_articles SET source_url = 'https://example.com/news' || id WHERE id <= 20;
