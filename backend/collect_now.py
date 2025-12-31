"""Manual collection focused on regional languages"""
from app.news_collector import NewsCollector
from app.database import Database
from app.nlp_model import NLPModel
import logging

# Suppress debug logs
logging.basicConfig(level=logging.WARNING)

print("Starting collection...")
db = Database()
collector = NewsCollector(db, NLPModel())
result = collector.collect_once()

print(f"\n✓ Collection complete!")
print(f"  Created: {result.get('created', 0)}")
print(f"  Updated: {result.get('updated', 0)}")
