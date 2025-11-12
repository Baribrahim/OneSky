"""
Pytest configuration and shared fixtures for all tests.
"""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock, patch
from flask import Flask, g

# Add the parent directory to sys.path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add functionality directory to sys.path for route tests
_functionality_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _functionality_dir not in sys.path:
    sys.path.insert(0, _functionality_dir)


def token_required_stub(f):
    """Stub for token_required decorator to bypass authentication in tests."""
    def wrapper(*args, **kwargs):
        g.current_user = {"sub": "test@example.com", "first_name": "Test"}
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper


def setup_auth_patch():
    """Setup auth token_required patch for route tests."""
    from auth import routes as auth_routes
    auth_routes.token_required = token_required_stub
    return auth_routes


def make_test_app(blueprint, register_auth=True):
    """Create Flask app for testing with blueprint registration.
    
    Args:
        blueprint: The blueprint to register
        register_auth: Whether to register auth blueprint (default: True)
    
    Returns:
        Configured Flask app for testing
    """
    app = Flask(__name__)  # NOSONAR: CSRF protection disabled for test environment
    # Use environment variable for SECRET_KEY in tests, with test-only fallback
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")  # NOSONAR - Test-only fallback, not a production credential
    app.config["TESTING"] = True
    # CSRF protection is not needed in test environment as tests use mocked authentication
    if register_auth:
        from auth import routes as auth_routes
        app.register_blueprint(auth_routes.bp)
    app.register_blueprint(blueprint)
    return app


def create_app(testing=False):
    """Create a Flask app for testing."""
    app = Flask(__name__)  # NOSONAR: CSRF protection disabled for test environment
    if testing:
        app.config["TESTING"] = True
        # CSRF protection is not needed in test environment as tests use mocked authentication
    from events.routes import bp
    app.register_blueprint(bp)
    return app


@pytest.fixture(autouse=True)
def mock_db_connection():
    """Auto-use fixture to mock pymysql.connect to prevent real DB connections."""
    with patch('data_access.pymysql.connect') as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        yield mock_connect


@pytest.fixture
def client():
    """Create a test client for Flask app."""
    app = create_app(testing=True)
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_data_access():
    """Create a mock DataAccess object for testing."""
    return Mock()


@pytest.fixture
def sample_badges():
    """Sample badge data for testing."""
    return [
        {
            "ID": 1,
            "Name": "Event Starter",
            "Description": "Registered for 1 upcoming events.",
            "IconURL": "/src/assets/badges/firstStep.png"
        },
        {
            "ID": 2,
            "Name": "Event Enthusiast",
            "Description": "Registered for 5 upcoming events.",
            "IconURL": "/src/assets/badges/eduEnthusiast.png"
        },
        {
            "ID": 3,
            "Name": "First Step",
            "Description": "Completed your first volunteering event.",
            "IconURL": "/src/assets/badges/firstStep.png"
        },
        {
            "ID": 4,
            "Name": "Volunteer Veteran",
            "Description": "Completed 10 volunteering events.",
            "IconURL": "/src/assets/badges/volunteerVetran.png"
        },
        {
            "ID": 5,
            "Name": "Marathon Helper",
            "Description": "Contributed 20+ total volunteering hours.",
            "IconURL": "/src/assets/badges/marathonVolunteer.png"
        },
        {
            "ID": 6,
            "Name": "Weekend Warrior",
            "Description": "Completed an event on a Saturday or Sunday.",
            "IconURL": "/src/assets/badges/weekendWarrior.png"
        }
    ]


@pytest.fixture
def sample_user_stats():
    """Sample user statistics for testing."""
    return {
        "upcoming_events": 3,
        "completed_events": 2,
        "total_hours": 15.0,
        "has_weekend_event": True
    }


@pytest.fixture
def sample_badge_progress():
    """Sample badge progress data for testing."""
    return {
        "event_starter": {"required": 1, "current": 3, "earned": True},
        "event_enthusiast": {"required": 5, "current": 3, "earned": False},
        "first_step": {"required": 1, "current": 2, "earned": True},
        "volunteer_veteran": {"required": 10, "current": 2, "earned": False},
        "marathon_helper": {"required": 20, "current": 15.0, "earned": False},
        "weekend_warrior": {"required": 1, "current": 1, "earned": True}
    }
