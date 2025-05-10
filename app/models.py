from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, UTC

Base = declarative_base()

class Agent(Base):
    """Represents a call center agent with performance metrics."""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    employee_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    is_active = Column(Boolean, default=True)
    
    # Performance metrics
    average_performance_score = Column(Float, default=0.0)
    total_calls_handled = Column(Integer, default=0)
    specialization = Column(String)  # e.g., "Sales", "Service", "AMG Specialist"
    
    calls = relationship("Call", back_populates="agent")

class Customer(Base):
    """Represents a customer in the system."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    calls = relationship("Call", back_populates="customer")

class Call(Base):
    """Represents a call between a customer and an agent with analysis results."""
    __tablename__ = "calls"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    agent_id = Column(Integer, ForeignKey("agents.id"))
    transcript = Column(Text)
    call_date = Column(DateTime, default=lambda: datetime.now(UTC))
    
    # Agent Analysis
    agent_performance_score = Column(Float, default=0.0)
    agent_issues = Column(Text, default="")
    
    # Customer Analysis
    customer_interest_score = Column(Float, default=0.0)
    customer_description = Column(Text, default="")
    customer_preferences = Column(Text, default="")
    test_drive_readiness = Column(Float, default=0.0)
    
    # Raw analysis results
    analysis_results = Column(JSON, default=dict)
    
    customer = relationship("Customer", back_populates="calls")
    agent = relationship("Agent", back_populates="calls") 