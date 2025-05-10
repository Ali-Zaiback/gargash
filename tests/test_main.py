import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from app.models import Customer, Agent, Call
from datetime import datetime, UTC, timedelta

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

def test_create_call(client, test_customer, test_agent):
    response = client.post(
        "/calls/",
        json={
            "customer_id": test_customer.id,
            "agent_id": test_agent.id,
            "transcript": "Customer: I'm interested in the AMG model. Agent: Great choice! The AMG offers exceptional performance."
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == test_customer.id
    assert data["agent_id"] == test_agent.id
    assert "transcript" in data
    assert "call_date" in data
    assert "agent_performance_score" in data
    assert "agent_issues" in data
    assert "customer_interest_score" in data
    assert "customer_description" in data
    assert "customer_preferences" in data
    assert "test_drive_readiness" in data
    assert "analysis_results" in data

def test_create_call_invalid_customer(client, test_agent):
    response = client.post(
        "/calls/",
        json={
            "customer_id": 999,
            "agent_id": test_agent.id,
            "transcript": "Test transcript"
        }
    )
    assert response.status_code == 404
    assert "Customer not found" in response.json()["detail"]

def test_create_call_invalid_agent(client, test_customer):
    response = client.post(
        "/calls/",
        json={
            "customer_id": test_customer.id,
            "agent_id": 999,
            "transcript": "Test transcript"
        }
    )
    assert response.status_code == 404
    assert "Agent not found" in response.json()["detail"]

def test_create_call_empty_transcript(client, test_customer, test_agent):
    response = client.post(
        "/calls/",
        json={
            "customer_id": test_customer.id,
            "agent_id": test_agent.id,
            "transcript": ""
        }
    )
    assert response.status_code == 422
    assert "Transcript must not be empty" in response.json()["detail"]

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