"""
Test suite for badge routes using pytest.
Tests cover all badge route endpoints with mocked authentication and data access.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from flask import Flask, g

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Patch token_required in auth.routes BEFORE importing badge_routes
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

from badges import routes as badge_routes


def make_app(bp):
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["TESTING"] = True
    # Register auth blueprint for login_page route
    from auth import routes as auth_routes
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(bp)
    return app


class FakeBadgeConnector:
    """Fake BadgeConnector for testing."""
    
    def __init__(self):
        self.data_access = Mock()
        self.data_access.get_user_id_by_email.return_value = 1
        self.user_badges = []
        self.all_badges = []
        self.newly_awarded = []
        self.progress = {}
    
    def get_user_badges(self, user_id):
        return self.user_badges
    
    def get_all_badges(self):
        return self.all_badges
    
    def check_and_award_event_badges(self, user_id):
        return self.newly_awarded
    
    def get_user_badge_progress(self, user_id):
        return self.progress
    
    def award_badge_to_user(self, user_id, badge_id):
        return (True, "Badge awarded successfully")


@pytest.fixture
def fake_connector():
    """Fixture for fake badge connector."""
    return FakeBadgeConnector()


def test_get_user_badges_success(monkeypatch, fake_connector):
    """Test successful retrieval of user badges."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.user_badges = [
        {"ID": 1, "Name": "Event Starter", "Description": "Test", "IconURL": "/test.png"}
    ]
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/badges")
    assert response.status_code == 200
    data = response.get_json()
    assert "badges" in data
    assert len(data["badges"]) == 1


def test_get_user_badges_user_not_found(monkeypatch, fake_connector):
    """Test get_user_badges when user is not found."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.data_access.get_user_id_by_email.return_value = None
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/badges")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_get_user_badges_no_auth(monkeypatch, fake_connector):
    """Test get_user_badges without authentication."""
    # Temporarily restore original token_required to test auth requirement
    original_token_required = auth_routes.token_required
    def no_auth_stub(f):
        def wrapper(*args, **kwargs):
            # Simulate token_required redirecting when no token
            from flask import redirect, url_for
            return redirect(url_for("auth.login_page"))
        wrapper.__name__ = f.__name__
        return wrapper
    
    # Reload badge_routes to apply new decorator
    import importlib
    monkeypatch.setattr(auth_routes, "token_required", no_auth_stub, raising=True)
    importlib.reload(badge_routes)
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/badges", follow_redirects=False)
    # Should redirect (302) when no auth
    assert response.status_code == 302
    
    # Restore original
    auth_routes.token_required = original_token_required
    importlib.reload(badge_routes)


def test_get_user_badges_exception(monkeypatch, fake_connector):
    """Test get_user_badges with exception."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.get_user_badges = Mock(side_effect=Exception("Database error"))
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/badges")
    assert response.status_code == 500


def test_get_all_badges_success(monkeypatch, fake_connector):
    """Test successful retrieval of all badges."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.all_badges = [
        {"ID": 1, "Name": "Event Starter", "Description": "Test", "IconURL": "/test.png"},
        {"ID": 2, "Name": "Event Enthusiast", "Description": "Test", "IconURL": "/test2.png"}
    ]
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/badges/all")
    assert response.status_code == 200
    data = response.get_json()
    assert "badges" in data
    assert len(data["badges"]) == 2


def test_get_all_badges_exception(monkeypatch, fake_connector):
    """Test get_all_badges with exception."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.get_all_badges = Mock(side_effect=Exception("Database error"))
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/badges/all")
    assert response.status_code == 500


def test_check_and_award_badges_success(monkeypatch, fake_connector):
    """Test successful badge check and award."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.newly_awarded = [
        {"ID": 1, "Name": "Event Starter", "Description": "Test", "IconURL": "/test.png"}
    ]
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/badges/check")
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "newly_awarded" in data
    assert "count" in data
    assert data["count"] == 1


def test_check_and_award_badges_user_not_found(monkeypatch, fake_connector):
    """Test check_and_award_badges when user is not found."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.data_access.get_user_id_by_email.return_value = None
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/badges/check")
    assert response.status_code == 404


def test_check_and_award_badges_exception(monkeypatch, fake_connector):
    """Test check_and_award_badges with exception."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.check_and_award_event_badges = Mock(side_effect=Exception("Database error"))
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/badges/check")
    assert response.status_code == 500


def test_get_badge_progress_success(monkeypatch, fake_connector):
    """Test successful retrieval of badge progress."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.progress = {
        "upcoming_events": 3,
        "completed_events": 2,
        "total_hours": 15.0,
        "has_weekend_event": True,
        "badge_progress": {}
    }
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/badges/progress")
    assert response.status_code == 200
    data = response.get_json()
    assert "progress" in data
    assert data["progress"]["upcoming_events"] == 3


def test_get_badge_progress_user_not_found(monkeypatch, fake_connector):
    """Test get_badge_progress when user is not found."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.data_access.get_user_id_by_email.return_value = None
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/badges/progress")
    assert response.status_code == 404


def test_get_badge_progress_exception(monkeypatch, fake_connector):
    """Test get_badge_progress with exception."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.get_user_badge_progress = Mock(side_effect=Exception("Database error"))
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/badges/progress")
    assert response.status_code == 500


def test_award_badge_success(monkeypatch, fake_connector):
    """Test successful badge award."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/badges/award", json={"badge_id": 1})
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data


def test_award_badge_missing_id(monkeypatch, fake_connector):
    """Test award_badge without badge_id."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/badges/award", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_award_badge_failure(monkeypatch, fake_connector):
    """Test award_badge when award fails."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.award_badge_to_user = Mock(return_value=(False, "User already has this badge"))
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/badges/award", json={"badge_id": 1})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_award_badge_user_not_found(monkeypatch, fake_connector):
    """Test award_badge when user is not found."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.data_access.get_user_id_by_email.return_value = None
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/badges/award", json={"badge_id": 1})
    assert response.status_code == 404


def test_award_badge_exception(monkeypatch, fake_connector):
    """Test award_badge with exception."""
    monkeypatch.setattr(badge_routes, "BadgeConnector", lambda: fake_connector, raising=True)
    
    fake_connector.award_badge_to_user = Mock(side_effect=Exception("Database error"))
    
    app = make_app(badge_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/badges/award", json={"badge_id": 1})
    assert response.status_code == 500

