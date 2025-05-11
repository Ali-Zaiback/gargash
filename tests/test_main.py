import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db, get_default_ai_agent_id
from app.models import Customer, Agent, Call
from datetime import datetime, UTC, timedelta
from sqlalchemy.exc import SQLAlchemyError

@pytest.fixture(scope="function")
def test_customer(db_session):
    customer = Customer(
        name="Test Customer",
        email="test@example.com",
        phone_number="+971501234567"
    )
    db_session.add(customer)
    db_session.commit()
    db_session.refresh(customer)
    return customer

@pytest.fixture(scope="function")
def test_agent(db_session):
    agent = Agent(
        name="Test Agent",
        employee_id="EMP002",
        email="agent@example.com",
        phone_number="+971502345678",
        total_calls_handled=0,
        average_performance_score=0.0,
        specialization="Sales"
    )
    db_session.add(agent)
    db_session.commit()
    db_session.refresh(agent)
    return agent

@pytest.fixture(scope="function")
def test_call(db_session, test_customer, test_agent):
    call = Call(
        customer_id=test_customer.id,
        agent_id=test_agent.id,
        transcript="Test call transcript",
        call_date=datetime.now(UTC),
        agent_performance_score=85.0,
        agent_issues="No issues",
        customer_interest_score=90.0,
        customer_description="Test customer",
        customer_preferences="Test preferences",
        test_drive_readiness=95.0,
        analysis_results={
            "agent_performance_score": 85.0,
            "customer_interest_score": 90.0,
            "test_drive_readiness": 95.0,
            "agent_issues": "No issues",
            "customer_description": "Test customer",
            "customer_preferences": "Test preferences"
        }
    )
    db_session.add(call)
    db_session.commit()
    db_session.refresh(call)
    return call

@pytest.fixture(scope="function")
def db(db_session):
    return db_session

def test_create_customer(client):
    response = client.post(
        "/customers/",
        json={
            "name": "New Customer",
            "email": "new@example.com",
            "phone_number": "+971503456789"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Customer"
    assert data["email"] == "new@example.com"
    assert data["phone_number"] == "+971503456789"
    assert "id" in data

def test_create_customer_duplicate_email(client, test_customer):
    response = client.post(
        "/customers/",
        json={
            "name": "Another Customer",
            "email": test_customer.email,
            "phone_number": "+971504567890"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_create_customer_invalid_email(client):
    response = client.post(
        "/customers/",
        json={
            "name": "Invalid Customer",
            "email": "invalid-email",
            "phone_number": "+971505678901"
        }
    )
    assert response.status_code == 422

def test_create_agent(client):
    response = client.post(
        "/agents/",
        json={
            "name": "New Agent",
            "employee_id": "EMP001",
            "email": "new.agent@example.com",
            "phone_number": "+971506789012",
            "specialization": "Sales"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Agent"
    assert data["email"] == "new.agent@example.com"
    assert data["phone_number"] == "+971506789012"
    assert data["employee_id"] == "EMP001"
    assert data["specialization"] == "Sales"
    assert "id" in data
    assert data["total_calls_handled"] == 0
    assert data["average_performance_score"] == 0.0

def test_create_agent_duplicate_email(client, test_agent):
    response = client.post(
        "/agents/",
        json={
            "name": "Another Agent",
            "employee_id": "EMP003",
            "email": test_agent.email,
            "phone_number": "+971507890123",
            "specialization": "Sales"
        }
    )
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]

def test_get_call(client, test_call):
    response = client.get(f"/calls/{test_call.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_call.id
    assert data["customer_id"] == test_call.customer_id
    assert data["agent_id"] == test_call.agent_id
    assert data["transcript"] == test_call.transcript
    assert data["analysis_results"] == test_call.analysis_results

def test_get_call_not_found(client):
    response = client.get("/calls/999")
    assert response.status_code == 404
    assert "Call not found" in response.json()["detail"]

def test_get_customer_calls(client, test_call, test_customer):
    response = client.get(f"/customers/{test_customer.id}/calls")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_call.id
    assert data[0]["customer_id"] == test_customer.id
    assert data[0]["analysis_results"] == test_call.analysis_results

def test_get_customer_calls_empty(client, test_customer, db_session):
    # Delete existing calls
    db_session.query(Call).delete()
    db_session.commit()
    response = client.get(f"/customers/{test_customer.id}/calls")
    assert response.status_code == 200
    assert response.json() == []

def test_get_agent_calls(client, test_call, test_agent):
    response = client.get(f"/agents/{test_agent.id}/calls")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_call.id
    assert data[0]["agent_id"] == test_agent.id
    assert data[0]["analysis_results"] == test_call.analysis_results

def test_get_agent_calls_with_days(client, test_call, test_agent, db_session):
    # Create an old call
    old_call = Call(
        customer_id=test_call.customer_id,
        agent_id=test_agent.id,
        transcript="Old call transcript",
        call_date=datetime.now(UTC) - timedelta(days=31),
        agent_performance_score=80.0,
        agent_issues="No issues",
        customer_interest_score=85.0,
        customer_description="Test customer",
        customer_preferences="Test preferences",
        test_drive_readiness=90.0,
        analysis_results={
            "agent_performance_score": 80.0,
            "customer_interest_score": 85.0,
            "test_drive_readiness": 90.0,
            "agent_issues": "No issues",
            "customer_description": "Test customer",
            "customer_preferences": "Test preferences"
        }
    )
    db_session.add(old_call)
    db_session.commit()
    # Test with default 30 days
    response = client.get(f"/agents/{test_agent.id}/calls")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1  # Only the recent call
    # Test with 60 days
    response = client.get(f"/agents/{test_agent.id}/calls?days=60")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # Both calls

def test_get_agent_calls_empty(client, test_agent, db_session):
    # Delete existing calls
    db_session.query(Call).delete()
    db_session.commit()
    response = client.get(f"/agents/{test_agent.id}/calls")
    assert response.status_code == 200
    assert response.json() == []

def test_ai_analysis_different_scenarios(client, test_customer, test_agent):
    scenarios = [
        {
            "transcript": "I'm interested in the E-Class model",
            "expected_description": "Very interested in E-Class"
        },
        {
            "transcript": "I want to test drive the G-Class",
            "expected_description": "Luxury SUV customer"
        },
        {
            "transcript": "Tell me about the EQE electric model",
            "expected_description": "Interested in electric vehicles"
        },
        {
            "transcript": "I'm looking for a pre-owned vehicle",
            "expected_description": "Interested in pre-owned vehicles"
        },
        {
            "transcript": "I need service for my Mercedes",
            "expected_description": "Service inquiry"
        }
    ]

    for scenario in scenarios:
        response = client.post(
            "/calls/",
            json={
                "customer_id": test_customer.id,
                "agent_id": test_agent.id,
                "transcript": scenario["transcript"]
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["customer_description"] == scenario["expected_description"]
        assert "analysis_results" in data

def test_create_inquiry_new_customer(client, db):
    """Test creating an inquiry with a new customer."""
    inquiry_data = {
        "phone_number": "+971501234567",
        "email": "newcustomer@example.com",
        "name": "New Customer",
        "referral_nr": "REF123"
    }
    
    response = client.post("/inquiries/", json=inquiry_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["phone_number"] == inquiry_data["phone_number"]
    assert data["email"] == inquiry_data["email"]
    assert data["name"] == inquiry_data["name"]
    assert data["referral_nr"] == inquiry_data["referral_nr"]
    assert data["status"] == "calling"
    assert "id" in data
    assert "customer_id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_inquiry_existing_customer(client, db):
    """Test creating an inquiry with an existing customer."""
    # First create a customer
    customer_data = {
        "name": "Existing Customer",
        "email": "existing@example.com",
        "phone_number": "+971501234568"
    }
    client.post("/customers/", json=customer_data)
    
    # Now create an inquiry for this customer
    inquiry_data = {
        "phone_number": customer_data["phone_number"],
        "email": customer_data["email"],
        "name": customer_data["name"],
        "referral_nr": "REF456"
    }
    
    response = client.post("/inquiries/", json=inquiry_data)
    assert response.status_code == 200
    data = response.json()
    
    assert data["phone_number"] == inquiry_data["phone_number"]
    assert data["referral_nr"] == inquiry_data["referral_nr"]
    assert data["status"] == "calling"

def test_create_inquiry_duplicate(client, db):
    """Test creating a duplicate inquiry (same customer and referral number)."""
    # First create an inquiry
    inquiry_data = {
        "phone_number": "+971501234569",
        "email": "duplicate@example.com",
        "name": "Duplicate Test",
        "referral_nr": "REF789"
    }
    
    # Create first inquiry
    response1 = client.post("/inquiries/", json=inquiry_data)
    assert response1.status_code == 200
    
    # Try to create duplicate inquiry
    response2 = client.post("/inquiries/", json=inquiry_data)
    assert response2.status_code == 200
    
    # Both responses should have the same customer_id and referral_nr
    data1 = response1.json()
    data2 = response2.json()
    assert data1["customer_id"] == data2["customer_id"]
    assert data1["referral_nr"] == data2["referral_nr"]

def test_create_inquiry_invalid_phone(client, db):
    """Test creating an inquiry with invalid phone number format."""
    inquiry_data = {
        "phone_number": "1234567890",  # Invalid format
        "email": "invalid@example.com",
        "name": "Invalid Phone",
        "referral_nr": "REF999"
    }
    
    response = client.post("/inquiries/", json=inquiry_data)
    assert response.status_code == 422  # Validation error

def test_create_inquiry_invalid_email(client, db):
    """Test creating an inquiry with invalid email format."""
    inquiry_data = {
        "phone_number": "+971501234570",
        "email": "invalid-email",  # Invalid format
        "name": "Invalid Email",
        "referral_nr": "REF888"
    }
    
    response = client.post("/inquiries/", json=inquiry_data)
    assert response.status_code == 422  # Validation error

def test_update_inquiry_with_transcripts(client, db):
    """Test updating an inquiry with transcripts."""
    # First create an inquiry
    inquiry_data = {
        "phone_number": "+971501234571",
        "email": "update@example.com",
        "name": "Update Test",
        "referral_nr": "REF101"
    }
    
    # Create initial inquiry
    response = client.post("/inquiries/", json=inquiry_data)
    assert response.status_code == 200
    inquiry_id = response.json()["id"]
    
    # Update the inquiry with transcript
    update_data = {
        "inquiry_id": inquiry_id,
        "variables": {
            "model": "C-Class",
            "color": "Black"
        },
        "concatenated_transcript": "assistant: Hello, how can I help you today?\nuser: I'm interested in a C-Class"
    }
    
    response = client.post("/inquiries/webhook", json=update_data)
    assert response.status_code == 200
    data = response.json()
    
    # Verify the inquiry was updated
    assert data["id"] == inquiry_id
    
    # Verify a call was created
    calls_response = client.get(f"/customers/{data['customer_id']}/calls/")
    assert calls_response.status_code == 200
    calls = calls_response.json()
    assert len(calls) == 1
    assert "assistant: Hello, how can I help you today?" in calls[0]["transcript"]
    assert "user: I'm interested in a C-Class" in calls[0]["transcript"]

def test_update_inquiry_not_found(client, db):
    """Test updating a non-existent inquiry."""
    update_data = {
        "inquiry_id": 999999,  # Non-existent ID
        "variables": {"test": "value"},
        "concatenated_transcript": "assistant: Test message"
    }
    
    response = client.post("/inquiries/webhook", json=update_data)
    assert response.status_code == 404

def test_update_inquiry_invalid_data(client, db):
    """Test updating an inquiry with invalid data."""
    # First create an inquiry
    inquiry_data = {
        "phone_number": "+971501234572",
        "email": "invalid@example.com",
        "name": "Invalid Test",
        "referral_nr": "REF103"
    }
    
    response = client.post("/inquiries/", json=inquiry_data)
    assert response.status_code == 200
    inquiry_id = response.json()["id"]
    
    # Try to update with invalid data
    invalid_data = {
        "inquiry_id": inquiry_id,
        "variables": "not a dict",  # Should be a dict
        "concatenated_transcript": "assistant: Test message"
    }
    
    response = client.post("/inquiries/webhook", json=invalid_data)
    assert response.status_code == 422

def test_update_inquiry_empty_transcripts(client, db):
    """Test updating an inquiry with empty transcripts."""
    # First create an inquiry
    inquiry_data = {
        "phone_number": "+971501234573",
        "email": "empty@example.com",
        "name": "Empty Test",
        "referral_nr": "REF104"
    }
    
    response = client.post("/inquiries/", json=inquiry_data)
    assert response.status_code == 200
    inquiry_id = response.json()["id"]
    
    # Update with empty transcript
    update_data = {
        "inquiry_id": inquiry_id,
        "variables": {"test": "value"},
        "concatenated_transcript": ""
    }
    
    response = client.post("/inquiries/webhook", json=update_data)
    assert response.status_code == 200
    
    # Verify no call was created
    calls_response = client.get(f"/customers/{response.json()['customer_id']}/calls/")
    assert calls_response.status_code == 200
    calls = calls_response.json()
    assert len(calls) == 0

def test_agent_performance_calculation(client, test_agent, test_customer):
    """Test agent performance score calculation after multiple calls."""
    # Create multiple calls with different performance scores
    calls_data = [
        {
            "customer_id": test_customer.id,
            "agent_id": test_agent.id,
            "transcript": "Test call 1",
            "agent_performance_score": 85.0
        },
        {
            "customer_id": test_customer.id,
            "agent_id": test_agent.id,
            "transcript": "Test call 2",
            "agent_performance_score": 95.0
        }
    ]
    
    for call_data in calls_data:
        response = client.post("/calls/", json=call_data)
        assert response.status_code == 200
    
    # Get agent performance
    response = client.get(f"/agents/{test_agent.id}/performance")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["average_performance_score"], float)
    assert 0.0 <= data["average_performance_score"] <= 100.0
    assert data["total_calls_handled"] == 2

def test_inquiry_status_transitions(client, db):
    """Test inquiry status transitions."""
    # Create initial inquiry
    inquiry_data = {
        "phone_number": "+971501234574",
        "email": "status@example.com",
        "name": "Status Test",
        "referral_nr": "REF105"
    }
    
    response = client.post("/inquiries/", json=inquiry_data)
    assert response.status_code == 200
    inquiry_id = response.json()["id"]
    
    # Update inquiry with transcript (should change status)
    update_data = {
        "inquiry_id": inquiry_id,
        "variables": {"test": "value"},
        "concatenated_transcript": "assistant: Test message"
    }
    
    response = client.post("/inquiries/webhook", json=update_data)
    assert response.status_code == 200
    assert response.json()["status"] == "deal"

def test_concurrent_access(client, db):
    """Test handling of concurrent access to the same resource."""
    # Create a customer
    customer_data = {
        "name": "Concurrent Test",
        "email": "concurrent@example.com",
        "phone_number": "+971501234576"
    }
    
    response1 = client.post("/customers/", json=customer_data)
    assert response1.status_code == 200
    
    # Try to create another customer with same email
    response2 = client.post("/customers/", json=customer_data)
    assert response2.status_code == 400
    assert "Email already registered" in response2.json()["detail"]

def test_transcript_length_validation(client, test_customer, test_agent):
    """Test validation of transcript length."""
    # Create a call with very long transcript
    long_transcript = "x" * 10001  # Assuming max length is 10000
    response = client.post(
        "/calls/",
        json={
            "customer_id": test_customer.id,
            "agent_id": test_agent.id,
            "transcript": long_transcript
        }
    )
    assert response.status_code == 422
    assert "Transcript too long" in response.json()["detail"] 