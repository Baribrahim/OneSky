import pytest
import random
import string
from http import HTTPStatus
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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

def test_register_duplicate_email_returns_400(client):
    # Arrange
    email, resp1 = _register_user(client)
    assert resp1.status_code == HTTPStatus.OK

    # Act (duplicate)
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

def test_login_wrong_password_returns_401(client):
    # Arrange
    email, r = _register_user(client, password="Password123!")
    assert r.status_code == HTTPStatus.OK

    # Act
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

def test_dashboard_impact_with_token_returns_200_and_shape(client):
    # Arrange
    email, r = _register_user(client, password="Password123!")
    assert r.status_code == HTTPStatus.OK
    token, _ = _login_get_token(client, email, "Password123!")

    # Act
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




    



