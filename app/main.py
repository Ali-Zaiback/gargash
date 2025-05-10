from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import get_db, engine
from .services.agent_service import AgentService
from .services.call_service import CallService
from .services.customer_service import CustomerService
from .services.ai_service import AIService

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Call Analysis System",
    description="AI-powered call analysis for Mercedes-Benz dealership",
    version="1.0.0"
)

# Dependency for AI service (for test overrides)
def get_ai_service():
    from .services.ai_service import AIService
    return AIService()

# Agent endpoints
@app.post("/agents/", response_model=schemas.Agent)
def create_agent(agent: schemas.AgentCreate, db: Session = Depends(get_db)):
    """Create a new agent."""
    return AgentService(db).create_agent(agent)

@app.get("/agents/", response_model=List[schemas.Agent])
def get_agents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of agents."""
    return AgentService(db).get_agents(skip, limit)

@app.get("/agents/{agent_id}", response_model=schemas.Agent)
def get_agent(agent_id: int, db: Session = Depends(get_db)):
    """Get agent by ID."""
    agent = AgentService(db).get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.put("/agents/{agent_id}", response_model=schemas.Agent)
def update_agent(agent_id: int, agent: schemas.AgentUpdate, db: Session = Depends(get_db)):
    """Update agent."""
    updated = AgentService(db).update_agent(agent_id, agent)
    if not updated:
        raise HTTPException(status_code=404, detail="Agent not found")
    return updated

@app.get("/agents/{agent_id}/performance", response_model=schemas.AgentPerformance)
def get_agent_performance(agent_id: int, db: Session = Depends(get_db)):
    """Get agent performance metrics."""
    performance = AgentService(db).calculate_performance(agent_id)
    if not performance:
        raise HTTPException(status_code=404, detail="Agent not found")
    return performance

# Customer endpoints
@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    """Create a new customer."""
    return CustomerService(db).create_customer(customer)

@app.get("/customers/", response_model=List[schemas.Customer])
def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get list of customers."""
    return CustomerService(db).get_customers(skip, limit)

@app.get("/customers/{customer_id}", response_model=schemas.Customer)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    """Get customer by ID."""
    customer = CustomerService(db).get_customer(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=schemas.Customer)
def update_customer(customer_id: int, customer: schemas.CustomerUpdate, db: Session = Depends(get_db)):
    """Update customer."""
    updated = CustomerService(db).update_customer(customer_id, customer)
    if not updated:
        raise HTTPException(status_code=404, detail="Customer not found")
    return updated

# Call endpoints
@app.post("/calls/", response_model=schemas.Call)
def create_call(call: schemas.CallCreate, db: Session = Depends(get_db), ai_service=Depends(get_ai_service)):
    """Create a new call with AI analysis."""
    return CallService(db, ai_service).create_call(call)

@app.get("/calls/{call_id}", response_model=schemas.Call)
def get_call(call_id: int, db: Session = Depends(get_db)):
    """Get call by ID."""
    call = CallService(db).get_call(call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    return call

@app.get("/customers/{customer_id}/calls/", response_model=List[schemas.Call])
def get_customer_calls(customer_id: int, db: Session = Depends(get_db)):
    """Get all calls for a customer."""
    return CallService(db).get_customer_calls(customer_id)

@app.get("/agents/{agent_id}/calls/", response_model=List[schemas.Call])
def get_agent_calls(agent_id: int, days: int = 30, db: Session = Depends(get_db)):
    """Get recent calls for an agent."""
    return CallService(db).get_agent_calls(agent_id, days) 