import pytest
import random

'''
User registration validation tests

'''

SECRET = "supersecret"  # match app config

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = SECRET
    with app.test_client() as client:
        yield client

def test_password_less_than_8_characters_invalid(client):
    response = client.post("/register", json={"email": "test3@test.com", "password": "1234567"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Password must be at least 8 characters"

def test_password_at_least_8_characters_valid(client):
    response = client.post("/register", json={"email": f"test{random.randint(0,999)}{random.randint(0,999)}@test.com", "password": "12345678", "first_name": "Test", "last_name": "User"})
    assert response.status_code == 200
    data = response.get_json()
    assert "token" in data

def test_email_already_in_use_invalid(client):
    response = client.post("/register", json={"email": "test@test.com", "password": "123456789"})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "User already exists"




    



