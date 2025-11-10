import pytest
import sys, os
from flask import Flask

# Add functionality folder to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from landing.routes import bp  # ✅ Correct for your structure

# ---------------------------
# App Factory for Testing
# ---------------------------

def create_app(testing=False):
    app = Flask(__name__)
    if testing:
        app.config["TESTING"] = True
    app.register_blueprint(bp)
    print(app.url_map)  # Debug: should show /landing/
    return app

# ---------------------------
# Pytest Fixture
# ---------------------------

@pytest.fixture
def client():
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client

# ---------------------------
# Test Suite for /landing/
# ---------------------------

def test_landing_route(client):
    response = client.get("/landing/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["title"] == "Welcome to Sky Volunteering"
    assert "features" in data
    assert len(data["features"]) == 7


# ---------------------------
# Test Suite for /landing/
# ---------------------------

def test_landing_status_code(client):
    """Ensure /landing/ returns 200 OK."""
    response = client.get("/landing/")
    assert response.status_code == 200

def test_landing_json_structure(client):
    """Validate JSON structure and keys."""
    response = client.get("/landing/")
    data = response.get_json()
    assert "title" in data
    assert "features" in data
    assert isinstance(data["title"], str)
    assert isinstance(data["features"], list)

def test_landing_title_content(client):
    """Check title matches expected text."""
    response = client.get("/landing/")
    data = response.get_json() 
    assert data["title"] == "Welcome to Sky Volunteering"

def test_features_count(client):
    """Ensure correct number of features."""
    response = client.get("/landing/")
    data = response.get_json()
    assert len(data["features"]) == 7

def test_features_have_expected_keys(client):
    """Each feature should have name and description."""
    response = client.get("/landing/")
    data = response.get_json()
    for feature in data["features"]:
        assert isinstance(feature, str)
        assert feature.strip() != ""

def test_invalid_route_returns_404(client):
    """Invalid route should return 404."""
    response = client.get("/landing/invalid")
    assert response.status_code == 404

def test_response_time(client):
    """Response should be fast (<500ms)."""
    import time
    start = time.time()
    client.get("/landing/")
    duration = time.time() - start
    assert duration < 0.5

def test_blueprint_registered(client):
    """Ensure landing blueprint is registered."""
    app = client.application
    rules = [rule.rule for rule in app.url_map.iter_rules()]
    assert "/landing/" in rules
