"""Apply database migrations"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine, text
from app.config import settings

def apply_migration_13():
    """Apply migration 13: Confidence scoring and verification system"""
    print("Applying migration 13...")
    
    # Create engine using DATABASE_URL
    engine = create_engine(settings.DATABASE_URL)
    
    # Read migration file
    with open('migrations/13.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Split into statements and execute
    statements = [s.strip() for s in sql.split(';') if s.strip()]
    
    success_count = 0
    error_count = 0
    
    with engine.connect() as conn:
        for i, stmt in enumerate(statements):
            try:
                print(f"Executing statement {i+1}/{len(statements)}...", end=' ')
                conn.execute(text(stmt))
                conn.commit()
                print("[OK]")
                success_count += 1
            except Exception as e:
                # Continue on errors (might be already applied)
                print(f"[WARN] {str(e)[:80]}")
                error_count += 1
    
    print(f"\n[DONE] Migration 13 complete: {success_count} successful, {error_count} skipped/errors")

if __name__ == "__main__":
    apply_migration_13()
