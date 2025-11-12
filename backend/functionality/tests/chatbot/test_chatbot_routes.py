"""
Test suite for chatbot routes using pytest.
Tests cover chatbot route endpoints with mocked authentication and chatbot connector.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
from flask import Flask, g

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Patch token_required in auth.routes BEFORE importing chatbot_routes
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

from chatbot import routes as chatbot_routes
from chatbot.connector import PromptInjectionError


def make_app(bp):
    """Create Flask app for testing."""
    app = Flask(__name__)  # NOSONAR: CSRF protection disabled for test environment
    # Use environment variable for SECRET_KEY in tests, with test-only fallback
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")
    app.config["TESTING"] = True
    # CSRF protection is not needed in test environment as tests use mocked authentication
    # Register auth blueprint for login_page route
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(bp)
    return app


class FakeChatbotConnector:
    """Fake ChatbotConnector for testing."""
    
    def __init__(self):
        self.response_text = "Test response"
        self.category = "general"
        self.events_list = []
        self.teams_list = []
        self.badges_list = []
        self.team_events_list = []
    
    def process_message(self, message, user_email):
        return (
            self.response_text,
            self.category,
            self.events_list,
            self.teams_list,
            self.badges_list,
            self.team_events_list
        )


@pytest.fixture
def fake_connector():
    """Fixture for fake chatbot connector."""
    return FakeChatbotConnector()


def test_chat_success(monkeypatch, fake_connector):
    """Test successful chat request."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "Hello"})
    assert response.status_code == 200
    data = response.get_json()
    assert "response" in data
    assert "category" in data
    assert data["category"] == "general"


def test_chat_with_events(monkeypatch, fake_connector):
    """Test chat request that returns events."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    fake_connector.events_list = [{"ID": 1, "Title": "Event 1"}]
    fake_connector.category = "general"
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "Show events"})
    assert response.status_code == 200
    data = response.get_json()
    assert "events" in data
    assert data["category"] == "events"


def test_chat_with_teams(monkeypatch, fake_connector):
    """Test chat request that returns teams."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    fake_connector.teams_list = [{"ID": 1, "Name": "Team 1"}]
    fake_connector.category = "general"
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "Show teams"})
    assert response.status_code == 200
    data = response.get_json()
    assert "teams" in data
    assert data["category"] == "teams"


def test_chat_with_badges(monkeypatch, fake_connector):
    """Test chat request that returns badges."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    fake_connector.badges_list = [{"ID": 1, "Name": "Badge 1"}]
    fake_connector.category = "general"
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "Show badges"})
    assert response.status_code == 200
    data = response.get_json()
    assert "badges" in data
    assert data["category"] == "badges"


def test_chat_with_team_events(monkeypatch, fake_connector):
    """Test chat request that returns team events."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    fake_connector.team_events_list = [{"ID": 1, "Title": "Team Event 1"}]
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "Show team events"})
    assert response.status_code == 200
    data = response.get_json()
    assert "team_events" in data


def test_chat_no_message(monkeypatch, fake_connector):
    """Test chat request without message."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_chat_empty_message(monkeypatch, fake_connector):
    """Test chat request with empty/whitespace message."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "   "})
    assert response.status_code == 400


def test_chat_prompt_injection_error(monkeypatch, fake_connector):
    """Test chat request with prompt injection error."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    fake_connector.process_message = Mock(side_effect=PromptInjectionError("Suspicious input"))
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "malicious input"})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_chat_value_error(monkeypatch, fake_connector):
    """Test chat request with ValueError."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    fake_connector.process_message = Mock(side_effect=ValueError("Configuration error"))
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "Hello"})
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data


def test_chat_general_exception(monkeypatch, fake_connector):
    """Test chat request with general exception."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    fake_connector.process_message = Mock(side_effect=Exception("Unexpected error"))
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "Hello"})
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data


def test_chat_events_category_override(monkeypatch, fake_connector):
    """Test that events override category even if connector sets different category."""
    monkeypatch.setattr(chatbot_routes, "ChatbotConnector", lambda: fake_connector, raising=True)
    
    fake_connector.events_list = [{"ID": 1, "Title": "Event 1"}]
    fake_connector.category = "badges"  # Connector says badges, but events should override
    
    app = make_app(chatbot_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/chatbot/chat", json={"message": "Show events"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["category"] == "events"  # Should be overridden to events

