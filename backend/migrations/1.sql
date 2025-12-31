
CREATE TABLE news_articles (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  summary TEXT,
  original_language TEXT NOT NULL,
  translated_title TEXT,
  translated_content TEXT,
  source_url TEXT,
  source_name TEXT,
  published_at DATETIME,
  category TEXT,
  sentiment_score REAL,
  sentiment_label TEXT,
  region TEXT,
  tags TEXT,
  image_url TEXT,
  is_processed BOOLEAN DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  description TEXT,
  color TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sentiment_analytics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  article_id INTEGER NOT NULL,
  positive_score REAL DEFAULT 0,
  negative_score REAL DEFAULT 0,
  neutral_score REAL DEFAULT 0,
  overall_sentiment TEXT,
  confidence_score REAL DEFAULT 0,
  keywords TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_articles_published_at ON news_articles(published_at);
CREATE INDEX idx_news_articles_category ON news_articles(category);
CREATE INDEX idx_news_articles_sentiment_label ON news_articles(sentiment_label);
CREATE INDEX idx_news_articles_original_language ON news_articles(original_language);
CREATE INDEX idx_news_articles_region ON news_articles(region);
CREATE INDEX idx_sentiment_analytics_article_id ON sentiment_analytics(article_id);
