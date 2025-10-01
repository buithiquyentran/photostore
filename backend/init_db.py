"""
Initialize Database - Create all tables
Run: python init_db.py
"""

from sqlmodel import SQLModel
from db.session import engine

# Import tất cả models để SQLModel biết
from models.users import Users, RefreshToken
from models.projects import Projects
from models.folders import Folders
from models.assets import Assets
from models.embeddings import Embeddings

def init_database():
    """Create all tables in database"""
    print("🔨 Creating database tables...")
    
    try:
        # Tạo tất cả bảng
        SQLModel.metadata.create_all(engine)
        
        print("✅ Database tables created successfully!")
        print("\nTables created:")
        print("  - users")
        print("  - refresh_token")
        print("  - projects")
        print("  - folders")
        print("  - assets")
        print("  - embeddings (with project_id, folder_id)")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        raise

if __name__ == "__main__":
    init_database()

