
-- Update news articles with realistic Indian newspaper URLs
UPDATE news_articles SET source_url = 'https://www.jagran.com/politics/national-health-ministry-announces-new-scheme-23456789.html' WHERE id = 1;
UPDATE news_articles SET source_url = 'https://www.hindustantimes.com/education/digital-initiative-in-education-sector-101687654321000.html' WHERE id = 2;
UPDATE news_articles SET source_url = 'https://www.anandabazar.com/technology/new-investment-in-it-sector-1.876543' WHERE id = 3;
UPDATE news_articles SET source_url = 'https://maharashtratimes.com/environment/new-rules-for-environmental-protection/articleshow/98765432.cms' WHERE id = 4;
UPDATE news_articles SET source_url = 'https://www.thehindu.com/news/national/tamil-nadu/new-medical-college-in-tamil-nadu/article67890123.ece' WHERE id = 5;
UPDATE news_articles SET source_url = 'https://www.eenadu.net/telugu-news/economic-reforms-in-financial-sector/1234567890' WHERE id = 6;
UPDATE news_articles SET source_url = 'https://www.gujaratsamachar.com/news/solar-energy-project-in-gujarat-45678901' WHERE id = 7;
UPDATE news_articles SET source_url = 'https://www.vijaykarnataka.com/karnataka/changes-in-agricultural-policy-67890123' WHERE id = 8;
UPDATE news_articles SET source_url = 'https://www.jagran.com/health/new-health-scheme-launched-89012345.html' WHERE id = 9;
UPDATE news_articles SET source_url = 'https://www.thehindu.com/news/national/kerala/kerala-improves-healthcare-infrastructure/article12345678.ece' WHERE id = 10;

-- Update remaining articles with realistic URLs
UPDATE news_articles SET 
  source_url = CASE 
    WHEN source_name = 'Dainik Jagran' THEN 'https://www.jagran.com/news/article-' || id || '.html'
    WHEN source_name = 'Hindustan Times' THEN 'https://www.hindustantimes.com/news/article-' || id || '.html'
    WHEN source_name = 'The Hindu' THEN 'https://www.thehindu.com/news/article' || id || '.ece'
    WHEN source_name = 'The Hindu Tamil' THEN 'https://www.thehindu.com/tamil/news/article' || id || '.ece'
    WHEN source_name = 'Times of India' THEN 'https://timesofindia.indiatimes.com/news/article' || id || '.cms'
    WHEN source_name = 'Indian Express' THEN 'https://indianexpress.com/article/news-' || id
    WHEN source_name = 'Anandabazar Patrika' THEN 'https://www.anandabazar.com/news/article-' || id
    WHEN source_name = 'Maharashtra Times' THEN 'https://maharashtratimes.com/news/article' || id || '.cms'
    WHEN source_name = 'Eenadu' THEN 'https://www.eenadu.net/telugu-news/article-' || id
    WHEN source_name = 'Gujarat Samachar' THEN 'https://www.gujaratsamachar.com/news/article-' || id
    WHEN source_name = 'Vijaya Karnataka' THEN 'https://www.vijaykarnataka.com/news/article-' || id
    WHEN source_name = 'Malayala Manorama' THEN 'https://www.manorama.com/news/kerala/article-' || id || '.html'
    WHEN source_name = 'Mathrubhumi' THEN 'https://www.mathrubhumi.com/news/kerala/article-' || id
    WHEN source_name = 'Dinakaran' THEN 'https://www.dinakaran.com/news/article-' || id
    WHEN source_name = 'Deccan Chronicle' THEN 'https://www.deccanchronicle.com/news/article' || id
    WHEN source_name = 'Punjab Kesari' THEN 'https://www.punjabkesari.in/news/article-' || id
    WHEN source_name = 'Sambad' THEN 'https://sambad.in/news/article-' || id || '.html'
    WHEN source_name = 'Aaj Tak' THEN 'https://www.aajtak.in/news/article-' || id
    WHEN source_name = 'NDTV' THEN 'https://www.ndtv.com/news/article-' || id
    ELSE source_url
  END
WHERE source_url LIKE '%example.com%' OR source_url IS NULL;
