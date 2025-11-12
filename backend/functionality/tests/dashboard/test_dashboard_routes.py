"""
Test suite for dashboard routes using pytest.
Tests cover all dashboard route endpoints with mocked authentication and data access.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from flask import Flask, g

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Patch token_required in auth.routes BEFORE importing dashboard_routes
from auth import routes as auth_routes

# Auth bypass for tests: set g.current_user and call the view
def token_required_stub(f):
    """Stub for token_required decorator."""
    def wrapper(*args, **kwargs):
        g.current_user = {"sub": "test@example.com", "first_name": "Test"}
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Patch token_required before importing routes that use it
auth_routes.token_required = token_required_stub

from dashboard import routes as dashboard_routes


def make_app(bp):
    """Create Flask app for testing."""
    import os
    app = Flask(__name__)  # NOSONAR: CSRF protection disabled for test environment
    # Use environment variable for SECRET_KEY in tests, with test-only fallback
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")
    app.config["TESTING"] = True
    # CSRF protection is not needed in test environment as tests use mocked authentication
    # Register auth blueprint for login_page route
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(bp)
    return app


class FakeDashboardConnector:
    """Fake DashboardConnector for testing."""
    
    def __init__(self):
        self.dashboard_data = {
            "upcoming_events": [],
            "upcoming_count": 0,
            "total_hours": 0.0,
            "completed_events": 0,
            "badges": []
        }
        self.upcoming_events = []
        self.completed_events = []
        self.badges = []
    
    def get_dashboard(self, email, limit=5):
        return self.dashboard_data
    
    def get_upcoming_events_paged(self, email, limit=5, offset=0):
        return self.upcoming_events
    
    def get_upcoming_events_count(self, email):
        return len(self.upcoming_events)
    
    def get_completed_events(self, email, limit=50):
        return self.completed_events
    
    def get_badges(self, email):
        return self.badges


@pytest.fixture
def fake_connector():
    """Fixture for fake dashboard connector."""
    return FakeDashboardConnector()


def test_dashboard_impact_success(monkeypatch, fake_connector):
    """Test successful retrieval of dashboard impact."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.dashboard_data = {
        "upcoming_events": [{"ID": 1, "Title": "Event 1"}],
        "upcoming_count": 1,
        "total_hours": 10.5,
        "completed_events": 5,
        "badges": [{"ID": 1, "Name": "Badge 1"}]
    }
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/impact")
    assert response.status_code == 200
    data = response.get_json()
    assert "first_name" in data
    assert "total_hours" in data
    assert "events_completed" in data
    assert "counts" in data


def test_dashboard_impact_with_limit(monkeypatch, fake_connector):
    """Test dashboard_impact with limit parameter."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/impact?limit=10")
    assert response.status_code == 200


def test_dashboard_impact_value_error(monkeypatch, fake_connector):
    """Test dashboard_impact with ValueError."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_dashboard = Mock(side_effect=ValueError("Invalid email"))
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/impact")
    assert response.status_code == 400


def test_dashboard_impact_exception(monkeypatch, fake_connector):
    """Test dashboard_impact with exception."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_dashboard = Mock(side_effect=Exception("Database error"))
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/impact")
    assert response.status_code == 500


def test_dashboard_impact_with_missing_keys(monkeypatch, fake_connector):
    """Test dashboard_impact when get_dashboard returns data with missing keys."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    # Return minimal data with missing keys to test default value handling
    fake_connector.dashboard_data = {
        "upcoming_events": [],
        # Missing other keys to test defaults
    }
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/impact")
    assert response.status_code == 200
    data = response.get_json()
    assert "first_name" in data
    assert "total_hours" in data
    assert data["total_hours"] == 0.0  # Should default to 0.0
    assert "events_completed" in data
    assert data["events_completed"] == 0  # Should default to 0
    assert "counts" in data
    assert "upcoming_events" in data["counts"]
    assert "badges" in data["counts"]


def test_dashboard_upcoming_success(monkeypatch, fake_connector):
    """Test successful retrieval of upcoming events."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.upcoming_events = [
        {"ID": 1, "Title": "Event 1"},
        {"ID": 2, "Title": "Event 2"}
    ]
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/upcoming")
    assert response.status_code == 200
    data = response.get_json()
    assert "upcoming_events" in data
    assert "count" in data
    assert "total" in data
    assert "has_more" in data


def test_dashboard_upcoming_with_pagination(monkeypatch, fake_connector):
    """Test dashboard_upcoming with pagination parameters."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.upcoming_events = [{"ID": i, "Title": f"Event {i}"} for i in range(10)]
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/upcoming?limit=5&offset=0")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 10


def test_dashboard_upcoming_value_error(monkeypatch, fake_connector):
    """Test dashboard_upcoming with ValueError."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_upcoming_events_paged = Mock(side_effect=ValueError("Invalid email"))
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/upcoming")
    assert response.status_code == 400


def test_dashboard_upcoming_exception(monkeypatch, fake_connector):
    """Test dashboard_upcoming with exception."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_upcoming_events_paged = Mock(side_effect=Exception("Database error"))
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/upcoming")
    assert response.status_code == 500


def test_dashboard_achievements_success(monkeypatch, fake_connector):
    """Test successful retrieval of achievements."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.badges = [
        {"ID": 1, "Name": "Badge 1", "Description": "Test", "IconURL": "/test.png"},
        {"ID": 2, "Name": "Badge 2", "Description": "Test", "IconURL": "/test2.png"}
    ]
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/achievements")
    assert response.status_code == 200
    data = response.get_json()
    assert "badges" in data
    assert "count" in data
    assert data["count"] == 2


def test_dashboard_achievements_value_error(monkeypatch, fake_connector):
    """Test dashboard_achievements with ValueError."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_badges = Mock(side_effect=ValueError("Invalid email"))
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/achievements")
    assert response.status_code == 400


def test_dashboard_achievements_exception(monkeypatch, fake_connector):
    """Test dashboard_achievements with exception."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_badges = Mock(side_effect=Exception("Database error"))
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/achievements")
    assert response.status_code == 500


def test_dashboard_completed_events_success(monkeypatch, fake_connector):
    """Test successful retrieval of completed events."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.completed_events = [
        {"ID": 1, "Title": "Past Event 1"},
        {"ID": 2, "Title": "Past Event 2"}
    ]
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/completed-events")
    assert response.status_code == 200
    data = response.get_json()
    assert "completed_events" in data
    assert len(data["completed_events"]) == 2


def test_dashboard_completed_events_with_limit(monkeypatch, fake_connector):
    """Test dashboard_completed_events with limit parameter."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/completed-events?limit=10")
    assert response.status_code == 200


def test_dashboard_completed_events_value_error(monkeypatch, fake_connector):
    """Test dashboard_completed_events with ValueError."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_completed_events = Mock(side_effect=ValueError("Invalid email"))
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/completed-events")
    assert response.status_code == 400


def test_dashboard_completed_events_exception(monkeypatch, fake_connector):
    """Test dashboard_completed_events with exception."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_completed_events = Mock(side_effect=Exception("Database error"))
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard/completed-events")
    assert response.status_code == 500


@patch('dashboard.routes.render_template')
def test_dashboard_page_success(mock_render, monkeypatch, fake_connector):
    """Test successful rendering of dashboard page."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    mock_render.return_value = "rendered template"
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard_page")
    assert response.status_code == 200
    mock_render.assert_called_once()


@patch('dashboard.routes.render_template')
def test_dashboard_page_value_error(mock_render, monkeypatch, fake_connector):
    """Test dashboard_page with ValueError."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_dashboard = Mock(side_effect=ValueError("Invalid email"))
    mock_render.return_value = "rendered template"
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard_page")
    assert response.status_code == 400
    mock_render.assert_called_once()


@patch('dashboard.routes.render_template')
def test_dashboard_page_exception(mock_render, monkeypatch, fake_connector):
    """Test dashboard_page with exception."""
    monkeypatch.setattr(dashboard_routes, "dc", fake_connector, raising=True)
    
    fake_connector.get_dashboard = Mock(side_effect=Exception("Database error"))
    mock_render.return_value = "rendered template"
    
    app = make_app(dashboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/dashboard_page")
    assert response.status_code == 500
    mock_render.assert_called_once()

