import pytest
import random
import string
from http import HTTPStatus
import sys, os
from unittest.mock import patch, MagicMock
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

'''
User registration validation tests

'''

SECRET = "supersecret"  # match app config

@pytest.fixture(autouse=True)
def mock_data_access():
    """Auto-use fixture to mock all DataAccess instances and prevent real DB connections."""
    with patch('data_access.pymysql.connect') as mock_connect, \
         patch('auth.connector.DataAccess') as mock_auth_da_class, \
         patch('badges.connector.DataAccess') as mock_badge_da_class, \
         patch('dashboard.connector.DataAccess') as mock_dashboard_da_class:
        
        # Mock pymysql connection to prevent real DB connections
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock DataAccess instances for connectors
        mock_auth_da_instance = MagicMock()
        mock_badge_da_instance = MagicMock()
        mock_dashboard_da_instance = MagicMock()
        
        mock_auth_da_class.return_value = mock_auth_da_instance
        mock_badge_da_class.return_value = mock_badge_da_instance
        mock_dashboard_da_class.return_value = mock_dashboard_da_instance
        
        # Set up default return values for registration/login flow
        # Use side_effect to return the actual email passed in
        def get_user_by_email_side_effect(email):
            return {
                "ID": 1,
                "Email": email,
                "Password": b"$2b$12$hashedpassword",
                "FirstName": "Test",
                "LastName": "User"
            }
        
        def verify_user_by_password_side_effect(email, password):
            # Default: return user dict with the email
            return {
                "ID": 1,
                "Email": email,
                "FirstName": "Test",
                "LastName": "User"
            }
        
        mock_auth_da_instance.user_exists.return_value = False
        mock_auth_da_instance.get_user_id_by_email.return_value = 1
        mock_auth_da_instance.get_user_by_email.side_effect = get_user_by_email_side_effect
        mock_auth_da_instance.verify_user_by_password.side_effect = verify_user_by_password_side_effect
        
        # Set up badge DataAccess methods that are called during badge checking
        mock_badge_da_instance.get_user_id_by_email.return_value = 1
        mock_badge_da_instance.get_upcoming_events_count.return_value = 0
        mock_badge_da_instance.get_completed_events_count.return_value = 0
        mock_badge_da_instance.get_total_hours.return_value = 0.0
        mock_badge_da_instance.user_completed_weekend_event.return_value = False
        mock_badge_da_instance.get_badge_by_name.return_value = None
        mock_badge_da_instance.user_has_badge.return_value = False
        mock_badge_da_instance.award_badge_to_user.return_value = None
        
        # Set up dashboard DataAccess methods
        mock_dashboard_da_instance.get_user_id_by_email.return_value = 1
        mock_dashboard_da_instance.get_upcoming_events.return_value = []
        mock_dashboard_da_instance.get_upcoming_events_count.return_value = 0
        mock_dashboard_da_instance.get_total_hours.return_value = 10.5
        mock_dashboard_da_instance.get_completed_events_count.return_value = 3
        mock_dashboard_da_instance.get_badges.return_value = []
        
        yield {
            'auth': mock_auth_da_instance,
            'badge': mock_badge_da_instance,
            'dashboard': mock_dashboard_da_instance
        }

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = SECRET
    with app.test_client() as client:
        yield client

# ---------- helpers ----------

def _rand_email(prefix="test"):
    n1 = random.randint(0, 9999)
    n2 = random.randint(0, 9999)
    return f"{prefix}{n1}{n2}@sky.uk"

def _register_user(client, email=None, password="Password123!", first="Test", last="User"):
    email = email or _rand_email()
    resp = client.post("/register", json={
        "email": email,
        "password": password,
        "first_name": first,
        "last_name": last
    })
    return email, resp

def _login_get_token(client, email, password):
    resp = client.post("/login", json={"email": email, "password": password})
    assert resp.status_code == HTTPStatus.OK
    data = resp.get_json()
    assert "token" in data
    return data["token"], resp

# ---------- REGISTER tests ----------

def test_register_missing_password_returns_400(client):
    # Arrange
    email = _rand_email()

    # Act
    resp = client.post("/register", json={"email": email, "first_name": "A", "last_name": "B"})

    # Assert
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    data = resp.get_json()
    assert "error" in data

def test_register_missing_email_returns_400(client):
    # Arrange
    # Act
    resp = client.post("/register", json={"password": "password123!", "first_name": "A", "last_name": "B"})

    # Assert
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    data = resp.get_json()
    assert "error" in data

def test_register_sets_cookie_and_returns_token(client):
    # Arrange
    email = _rand_email()

    # Act
    resp = client.post("/register", json={
        "email": email,
        "password": "Password123!",
        "first_name": "A",
        "last_name": "B"
    })

    # Assert
    assert resp.status_code == HTTPStatus.OK
    data = resp.get_json()
    assert "token" in data
    # cookie is set even for JSON flow in your code
    set_cookie = resp.headers.get("Set-Cookie", "")
    assert "access_token=" in set_cookie

def test_register_duplicate_email_returns_400(client, mock_data_access):
    # Arrange
    email, resp1 = _register_user(client)
    assert resp1.status_code == HTTPStatus.OK

    # Act (duplicate) - mock user_exists to return True for duplicate
    mock_data_access['auth'].user_exists.return_value = True  # User already exists
    
    resp2 = client.post("/register", json={
        "email": email,
        "password": "Password123!",
        "first_name": "A",
        "last_name": "B"
    })

    # Assert
    assert resp2.status_code == HTTPStatus.BAD_REQUEST
    data = resp2.get_json()
    assert data.get("error") == "User already exists"

# ---------- LOGIN tests ----------

def test_login_success_returns_token_and_sets_cookie(client):
    # Arrange
    email, r = _register_user(client, password="Password123!")
    assert r.status_code == HTTPStatus.OK

    # Act
    token, resp = _login_get_token(client, email, "Password123!")

    # Assert
    assert isinstance(token, str) and len(token) > 10
    set_cookie = resp.headers.get("Set-Cookie", "")
    assert "access_token=" in set_cookie

def test_login_wrong_password_returns_401(client, mock_data_access):
    # Arrange
    email, r = _register_user(client, password="Password123!")
    assert r.status_code == HTTPStatus.OK

    # Act - mock verify_user_by_password to return None for wrong password
    # Reset side_effect so return_value can be used
    mock_data_access['auth'].verify_user_by_password.side_effect = None
    mock_data_access['auth'].verify_user_by_password.return_value = None  # Wrong password
    
    resp = client.post("/login", json={"email": email, "password": "WRONGPASS"})

    # Assert
    assert resp.status_code == HTTPStatus.UNAUTHORIZED
    data = resp.get_json()
    assert data.get("error") == "Invalid credentials"

# ---------- New validation tests to test validation logic ----------

def test_register_invalid_email_domain_returns_400(client):
    # Arrange
    bad_email = "user@example.com"
    # Act
    resp = client.post("/register", json={
        "email": bad_email,
        "password": "Password123!",
        "first_name": "A",
        "last_name": "B"
    })
    # Assert
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    data = resp.get_json()
    assert data.get("error") == "Email address not in a valid format"

@pytest.mark.parametrize("pwd, reason", [
    ("Passw1!", "too short"),
    ("password123!", "no uppercase"),
    ("PASSWORD!!!", "no digit"),
    ("Password123", "no special"),
])
def test_register_password_strength_enforced_returns_400(client, pwd, reason):
    # Arrange
    email = _rand_email()
    # Act
    resp = client.post("/register", json={
        "email": email,
        "password": pwd,
        "first_name": "A",
        "last_name": "B"
    })
    # Assert
    assert resp.status_code == HTTPStatus.BAD_REQUEST, f"Expected 400 for {reason}"
    data = resp.get_json()
    assert data.get("error") == "Password must be at least 8 characters and include an uppercase letter, a number, and a special character."

def test_login_missing_fields_returns_400(client):
    # Arrange
    # Act
    resp = client.post("/login", json={"email": _rand_email()})  # no password
    # Assert
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    data = resp.get_json()
    assert "error" in data

# ---------- /api/me test (header token flow) ----------

def test_me_returns_user_info_with_bearer_token(client):
    # Arrange: register + login to obtain token
    email, r = _register_user(client, password="Password123!", first="Jane", last="Doe")
    assert r.status_code == HTTPStatus.OK
    token, _ = _login_get_token(client, email, "Password123!")

    # Act: call /api/me with Authorization header
    resp = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert resp.status_code == HTTPStatus.OK
    data = resp.get_json()
    assert data.get("email") == email
    assert data.get("first_name") in ("Jane", "User", "Test")  # depending on your stored value

# ---------- (Optional) Auth guard sanity for dashboard ----------

def test_dashboard_impact_requires_auth(client):
    # Arrange/Act: no token
    resp = client.get("/dashboard/impact", follow_redirects=False)

    # Assert: token_required for HTML typically redirects; for API you may get a 302 or 401 depending on your decorator
    assert resp.status_code in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FOUND, HTTPStatus.SEE_OTHER)

def test_dashboard_impact_with_token_returns_200_and_shape(client, mock_data_access):
    # Arrange
    email, r = _register_user(client, password="Password123!")
    assert r.status_code == HTTPStatus.OK
    token, _ = _login_get_token(client, email, "Password123!")

    # Act - dashboard connector already mocked in fixture
    resp = client.get("/dashboard/impact", headers={"Authorization": f"Bearer {token}"})

    # Assert
    assert resp.status_code == HTTPStatus.OK
    data = resp.get_json()
    # basic shape checks
    assert "first_name" in data
    assert "total_hours" in data
    assert "events_completed" in data
    assert "counts" in data and isinstance(data["counts"], dict)
    assert "upcoming_events" in data["counts"]
    assert "badges" in data["counts"]




    



