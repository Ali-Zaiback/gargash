from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime, UTC
import re
from app.models import InquiryStatus

class AgentBase(BaseModel):
    """Basic agent information."""
    name: str
    employee_id: str
    email: EmailStr
    phone_number: str
    specialization: Optional[str] = None

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^\+971\d{9}$', v):
            raise ValueError('Phone must be +971XXXXXXXXX')
        return v

class AgentCreate(AgentBase):
    """Data for creating a new agent."""
    pass

class Agent(AgentBase):
    """Complete agent information."""
    id: int
    created_at: datetime
    is_active: bool
    average_performance_score: float
    total_calls_handled: int

    class Config:
        from_attributes = True

class AgentUpdate(BaseModel):
    """Data for updating an agent."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    specialization: Optional[str] = None
    is_active: Optional[bool] = None

class CustomerBase(BaseModel):
    """Basic customer information."""
    name: str
    phone_number: str
    email: EmailStr

    @field_validator('phone_number')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^\+971\d{9}$', v):
            raise ValueError('Phone must be +971XXXXXXXXX')
        return v

class CustomerCreate(CustomerBase):
    """Data for creating a new customer."""
    pass

class CustomerUpdate(BaseModel):
    """Data for updating a customer."""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None

class Customer(CustomerBase):
    """Complete customer information."""
    id: int
    created_at: datetime

class CallBase(BaseModel):
    """Basic call information."""
    customer_id: int
    agent_id: int
    transcript: str
    call_date: datetime = datetime.now(UTC)

class CallCreate(CallBase):
    """Data for creating a new call."""
    pass

class Call(CallBase):
    """Complete call information with analysis."""
    id: int
    call_date: datetime
    agent_performance_score: float = 0.0
    agent_issues: str = ""
    customer_interest_score: float = 0.0
    customer_description: str = ""
    customer_preferences: str = ""
    test_drive_readiness: float = 0.0
    analysis_results: Dict[str, Any] = {}

class AgentPerformance(BaseModel):
    """Agent performance summary."""
    agent_id: int
    agent_name: str
    total_calls_handled: int
    average_performance_score: float
    average_customer_interest: float
    average_test_drive_readiness: float
    agent_issues: List[str]
    specialization: str
    is_active: bool

class InquiryBase(BaseModel):
    phone_number: str
    email: str
    name: str
    referral_nr: str
    status: InquiryStatus = InquiryStatus.CALLING

class InquiryCreate(InquiryBase):
    pass

class InquiryResponse(InquiryBase):
    id: int
    customer_id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InquiryUpdate(BaseModel):
    """Data for updating an inquiry."""
    inquiry_id: int
    variables: Dict[str, Any]
    concatenated_transcript: str

    class Config:
        extra = "allow" 