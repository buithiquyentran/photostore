"""
Migration script để cập nhật bảng assets
"""
from sqlalchemy import create_engine, text
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from core.config import settings

def run_migration():
    """Run migration to update assets table"""
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Read migration SQL
        migration_file = os.path.join(os.path.dirname(__file__), "update_assets_table.sql")
        with open(migration_file, "r", encoding="utf-8") as f:
            sql = f.read()
            
        # Split into individual statements
        statements = sql.split(";")
        
        # Execute each statement
        with engine.connect() as conn:
            for statement in statements:
                if statement.strip():
                    print(f"Executing: {statement[:100]}...")  # Print first 100 chars
                    conn.execute(text(statement))
                    conn.commit()
            
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise

if __name__ == "__main__":
    run_migration()
