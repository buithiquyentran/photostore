from sqlmodel import SQLModel, create_engine, Session
from core.config import settings

# Tạo engine kết nối MySQL
engine = create_engine(
    settings.DATABASE_URL,
    echo=True,  # In câu SQL ra console để debug
)

# Dependency để dùng trong FastAPI route
def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)