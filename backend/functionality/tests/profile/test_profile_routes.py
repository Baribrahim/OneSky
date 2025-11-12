"""
Test suite for profile routes using pytest.
Tests cover all profile route endpoints with mocked authentication and data access.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import types
import importlib.util
from flask import Flask, g

# Add the parent directory to sys.path to import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Create a fake profile package to avoid conflict with built-in profile module
# First, load the connector
profile_connector_path = os.path.join(parent_dir, "profile", "connector.py")
connector_spec = importlib.util.spec_from_file_location("profile.connector", profile_connector_path)
profile_connector = importlib.util.module_from_spec(connector_spec)

# Create profile package module
profile_package = types.ModuleType('profile')
profile_package.connector = profile_connector
sys.modules['profile'] = profile_package
sys.modules['profile.connector'] = profile_connector
connector_spec.loader.exec_module(profile_connector)

# Patch token_required in auth.routes BEFORE loading profile routes
from auth import routes as auth_routes

# Auth bypass for tests: set g.current_user and call the view
def token_required_stub(f):
    """Stub for token_required decorator."""
    def wrapper(*args, **kwargs):
        g.current_user = {"sub": "test@example.com", "first_name": "Test"}
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# Patch token_required before loading routes that use it
auth_routes.token_required = token_required_stub

# Now load routes which imports from profile.connector
profile_routes_path = os.path.join(parent_dir, "profile", "routes.py")
routes_spec = importlib.util.spec_from_file_location("profile.routes", profile_routes_path)
profile_routes = importlib.util.module_from_spec(routes_spec)
profile_package.routes = profile_routes
sys.modules['profile.routes'] = profile_routes
routes_spec.loader.exec_module(profile_routes)


def make_app(bp):
    """Create Flask app for testing."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret-key"
    app.config["TESTING"] = True
    app.config["UPLOAD_FOLDER"] = "/tmp/test_uploads"
    # Register auth blueprint for login_page route
    app.register_blueprint(auth_routes.bp)
    app.register_blueprint(bp)
    return app


class FakeProfileConnector:
    """Fake ProfileConnector for testing."""
    
    def __init__(self):
        self.user_details = {
            "ID": 1,
            "Email": "test@example.com",
            "FirstName": "Test",
            "LastName": "User",
            "ProfileImgPath": "test.png"
        }
    
    def get_user_details(self, email):
        return self.user_details
    
    def update_profile_image(self, email, image_path):
        return True
    
    def update_user_password(self, email, old_password, new_password):
        return True


@pytest.fixture
def fake_connector():
    """Fixture for fake profile connector."""
    return FakeProfileConnector()


def test_user_details_success(monkeypatch, fake_connector):
    """Test successful retrieval of user details."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.get_json()
    assert "info" in data
    assert data["info"]["Email"] == "test@example.com"
    assert "ProfileImgURL" in data["info"]


def test_user_details_no_image(monkeypatch, fake_connector):
    """Test user_details when user has no profile image."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    fake_connector.user_details = {
        "ID": 1,
        "Email": "test@example.com",
        "FirstName": "Test",
        "LastName": "User"
    }
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.get_json()
    assert "info" in data


def test_user_details_exception(monkeypatch, fake_connector):
    """Test user_details with exception."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    fake_connector.get_user_details = Mock(side_effect=Exception("Database error"))
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/profile")
    assert response.status_code == 500


def test_user_details_returns_none(monkeypatch, fake_connector):
    """Test user_details when connector returns None."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    fake_connector.get_user_details = Mock(return_value=None)
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/profile")
    assert response.status_code == 200
    data = response.get_json()
    assert "info" in data
    assert data["info"] is None




def test_update_profile_image_no_file(monkeypatch, fake_connector):
    """Test update_profile_image without file."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/profile/update-image")
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_update_profile_image_empty_filename(monkeypatch, fake_connector):
    """Test update_profile_image with empty filename."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    from io import BytesIO
    data = {'image': (BytesIO(b'fake image data'), '')}
    
    response = client.post("/api/profile/update-image", data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_update_profile_image_exception(monkeypatch, fake_connector):
    """Test update_profile_image with exception."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    fake_connector.update_profile_image = Mock(side_effect=Exception("Database error"))
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    from io import BytesIO
    data = {'image': (BytesIO(b'fake image data'), 'test.jpg')}
    
    response = client.post("/api/profile/update-image", data=data, content_type='multipart/form-data')
    assert response.status_code == 500


@patch('profile.routes.send_from_directory')
def test_serve_user_image_success(mock_send, monkeypatch):
    """Test successful serving of user image."""
    monkeypatch.setattr(profile_routes, "token_required", token_required_stub, raising=True)
    
    mock_send.return_value = "image data"
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/profile/images/test.png")
    assert response.status_code == 200


@patch('profile.routes.send_from_directory')
def test_serve_user_image_not_found(mock_send, monkeypatch):
    """Test serve_user_image when image not found."""
    monkeypatch.setattr(profile_routes, "token_required", token_required_stub, raising=True)
    
    from werkzeug.exceptions import NotFound
    mock_send.side_effect = NotFound("Image not found")
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/profile/images/nonexistent.png")
    assert response.status_code == 404


def test_update_password_success(monkeypatch, fake_connector):
    """Test successful password update."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/profile/update-password", json={
        "old_password": "oldpass",
        "new_password": "newpass"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data


def test_update_password_missing_new(monkeypatch, fake_connector):
    """Test update_password without new_password."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/profile/update-password", json={
        "old_password": "oldpass"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_update_password_missing_old(monkeypatch, fake_connector):
    """Test update_password without old_password."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/profile/update-password", json={
        "new_password": "newpass"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_update_password_incorrect_old(monkeypatch, fake_connector):
    """Test update_password with incorrect old password."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    fake_connector.update_user_password = Mock(return_value=False)
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/profile/update-password", json={
        "old_password": "wrongpass",
        "new_password": "newpass"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_update_password_exception(monkeypatch, fake_connector):
    """Test update_password with exception."""
    monkeypatch.setattr(profile_routes, "pc", fake_connector, raising=True)
    
    fake_connector.update_user_password = Mock(side_effect=Exception("Database error"))
    
    app = make_app(profile_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/profile/update-password", json={
        "old_password": "oldpass",
        "new_password": "newpass"
    })
    assert response.status_code == 500

