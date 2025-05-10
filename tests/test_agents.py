import pytest
from fastapi import status

def test_create_agent(client):
    agent_data = {
        "name": "John Agent",
        "employee_id": "EMP001",
        "email": "john.agent@example.com",
        "phone_number": "+971501234567",
        "specialization": "Sales"
    }
    response = client.post("/agents/", json=agent_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == agent_data["name"]
    assert data["employee_id"] == agent_data["employee_id"]
    assert data["email"] == agent_data["email"]
    assert data["phone_number"] == agent_data["phone_number"]
    assert data["specialization"] == agent_data["specialization"]
    assert "id" in data
    assert "created_at" in data
    assert "is_active" in data
    assert "average_performance_score" in data
    assert "total_calls_handled" in data

def test_get_agent(client):
    # First create an agent
    agent_data = {
        "name": "Jane Agent",
        "employee_id": "EMP002",
        "email": "jane.agent@example.com",
        "phone_number": "+971509876543",
        "specialization": "Service"
    }
    create_response = client.post("/agents/", json=agent_data)
    agent_id = create_response.json()["id"]

    # Then get the agent
    response = client.get(f"/agents/{agent_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == agent_data["name"]
    assert data["employee_id"] == agent_data["employee_id"]
    assert data["email"] == agent_data["email"]
    assert data["phone_number"] == agent_data["phone_number"]
    assert data["specialization"] == agent_data["specialization"]

def test_get_nonexistent_agent(client):
    response = client.get("/agents/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_agents_list(client):
    # Create multiple agents
    agents = [
        {
            "name": "Alice Agent",
            "employee_id": "EMP003",
            "email": "alice.agent@example.com",
            "phone_number": "+971501111111",
            "specialization": "AMG"
        },
        {
            "name": "Bob Agent",
            "employee_id": "EMP004",
            "email": "bob.agent@example.com",
            "phone_number": "+971502222222",
            "specialization": "Sales"
        }
    ]
    for agent in agents:
        client.post("/agents/", json=agent)

    # Get all agents
    response = client.get("/agents/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2  # Should have at least our two test agents

def test_update_agent(client):
    # First create an agent
    agent_data = {
        "name": "Original Agent",
        "employee_id": "EMP005",
        "email": "original.agent@example.com",
        "phone_number": "+971503333333",
        "specialization": "Sales"
    }
    create_response = client.post("/agents/", json=agent_data)
    agent_id = create_response.json()["id"]

    # Update the agent
    update_data = {
        "name": "Updated Agent",
        "email": "updated.agent@example.com",
        "phone_number": "+971504444444",
        "specialization": "Service",
        "is_active": False
    }
    response = client.put(f"/agents/{agent_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert data["phone_number"] == update_data["phone_number"]
    assert data["specialization"] == update_data["specialization"]
    assert data["is_active"] == update_data["is_active"] 