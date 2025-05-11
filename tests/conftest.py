import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Set testing environment and add app directory to path
os.environ["TESTING"] = "1"
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

TEST_DB_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def db_engine():
    """Session-wide test database engine."""
    if os.path.exists("./test.db"):
        os.remove("./test.db")
    engine = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
    )
    import app.database as app_db
    app_db.engine = engine
    app_db.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Creates a new database session for a test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    db = Session()
    # Ensure default AI agent exists in this session
    from app.database import get_default_ai_agent_id
    get_default_ai_agent_id(db)
    try:
        yield db
    finally:
        db.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """Test client with database session override and mock AI service."""
    from app.main import app, get_ai_service
    from app.database import get_db
    from app.services.mock_ai_service import MockAIService
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_ai_service] = lambda: MockAIService()
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear() 