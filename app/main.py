from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from . import models, schemas
from .database import get_db, engine
from .services.agent_service import AgentService
from .services.call_service import CallService
from .services.customer_service import CustomerService
from .services.ai_service import AIService
from .services.inquiry_service import InquiryService
from pydantic import ValidationError

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Call Analysis System",
    description="AI-powered call analysis for Mercedes-Benz dealership",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
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

@app.get("/calls/", response_model=List[schemas.Call])
def get_all_calls(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get a list of all calls."""
    return CallService(db).get_calls(skip=skip, limit=limit)

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

@app.post("/inquiries/", response_model=schemas.InquiryResponse)
def create_inquiry(inquiry: schemas.InquiryCreate, db: Session = Depends(get_db)):
    inquiry_service = InquiryService(db)
    try:
        db_inquiry = inquiry_service.create_inquiry(inquiry)
        # Merge Inquiry and Customer fields for the response
        customer = db_inquiry.customer
        return {
            "id": db_inquiry.id,
            "customer_id": db_inquiry.customer_id,
            "referral_nr": db_inquiry.referral_nr,
            "status": db_inquiry.status,
            "created_at": db_inquiry.created_at,
            "updated_at": db_inquiry.updated_at,
            "phone_number": customer.phone_number,
            "email": customer.email,
            "name": customer.name
        }
    except ValidationError as e:
        # Convert ValueError in ctx to string for JSON serialization
        errors = e.errors()
        for err in errors:
            if 'ctx' in err and 'error' in err['ctx']:
                err['ctx']['error'] = str(err['ctx']['error'])
        raise HTTPException(status_code=422, detail=errors)

@app.put("/inquiries/", response_model=schemas.InquiryResponse)
def update_inquiry(
    inquiry_update: schemas.InquiryUpdate,
    db: Session = Depends(get_db)
):
    """Update an inquiry by ID."""
    inquiry_service = InquiryService(db)
    try:
        db_inquiry = inquiry_service.update_inquiry(inquiry_update.inquiry_id, inquiry_update)
        # Merge Inquiry and Customer fields for the response
        customer = db_inquiry.customer
        return {
            "id": db_inquiry.id,
            "customer_id": db_inquiry.customer_id,
            "referral_nr": db_inquiry.referral_nr,
            "status": db_inquiry.status,
            "created_at": db_inquiry.created_at,
            "updated_at": db_inquiry.updated_at,
            "phone_number": customer.phone_number,
            "email": customer.email,
            "name": customer.name
        }
    except ValidationError as e:
        # Convert ValueError in ctx to string for JSON serialization
        errors = e.errors()
        for err in errors:
            if 'ctx' in err and 'error' in err['ctx']:
                err['ctx']['error'] = str(err['ctx']['error'])
        raise HTTPException(status_code=422, detail=errors)