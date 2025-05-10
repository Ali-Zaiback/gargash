import pytest
from fastapi import status

def test_create_customer(client):
    customer_data = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone_number": "+971501234567"
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == customer_data["name"]
    assert data["email"] == customer_data["email"]
    assert data["phone_number"] == customer_data["phone_number"]
    assert "id" in data
    assert "created_at" in data

def test_get_customer(client):
    # First create a customer
    customer_data = {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone_number": "+971509876543"
    }
    create_response = client.post("/customers/", json=customer_data)
    customer_id = create_response.json()["id"]

    # Then get the customer
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == customer_data["name"]
    assert data["email"] == customer_data["email"]
    assert data["phone_number"] == customer_data["phone_number"]

def test_get_nonexistent_customer(client):
    response = client.get("/customers/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_get_customers_list(client):
    # Create multiple customers
    customers = [
        {
            "name": "Alice Smith",
            "email": "alice@example.com",
            "phone_number": "+971501111111"
        },
        {
            "name": "Bob Smith",
            "email": "bob@example.com",
            "phone_number": "+971502222222"
        }
    ]
    for customer in customers:
        client.post("/customers/", json=customer)

    # Get all customers
    response = client.get("/customers/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2  # Should have at least our two test customers

def test_update_customer(client):
    # First create a customer
    customer_data = {
        "name": "Original Name",
        "email": "original@example.com",
        "phone_number": "+971503333333"
    }
    create_response = client.post("/customers/", json=customer_data)
    customer_id = create_response.json()["id"]

    # Update the customer
    update_data = {
        "name": "Updated Name",
        "email": "updated@example.com",
        "phone_number": "+971504444444"
    }
    response = client.put(f"/customers/{customer_id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert data["phone_number"] == update_data["phone_number"] 