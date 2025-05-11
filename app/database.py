from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from .models import Base
from app.models import Agent
from app.schemas import AgentCreate
import time
from sqlalchemy.orm import Session

load_dotenv()

# Use test database for testing, otherwise use main database
db_url = "sqlite:///./test.db" if os.getenv("TESTING") == "1" else "sqlite:///./gargash.db"

# Create database engine
engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False} if db_url.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_default_ai_agent_id(db: Session):
    """Get the ID of the default AI agent, creating it if it doesn't exist."""
    try:
        default_agent = db.query(Agent).filter(Agent.employee_id == "AI-001").first()
        if default_agent:
            return default_agent.id
        # Create default AI agent
        agent_data = AgentCreate(
            name="AI Assistant",
            employee_id="AI-001",
            email="ai.assistant@mercedes-benz.com",
            phone_number="+971500000000",
            specialization="AI Support"
        )
        default_agent = Agent(**agent_data.model_dump())
        db.add(default_agent)
        db.commit()
        db.refresh(default_agent)
        print("Default AI agent created successfully")
        return default_agent.id
    except Exception as e:
        print(f"Error creating default AI agent: {str(e)}")
        db.rollback()
        return None 