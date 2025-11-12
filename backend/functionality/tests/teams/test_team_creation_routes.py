import pytest
from flask import Flask, g
from teams import routes as team_routes

def make_app(bp):
    import os
    app = Flask(__name__)  # NOSONAR: CSRF protection disabled for test environment
    # Use environment variable for SECRET_KEY in tests, with test-only fallback
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "test-secret-key-for-testing-only")  # NOSONAR - Test-only fallback, not a production credential
    # CSRF protection is not needed in test environment as tests use mocked authentication
    app.register_blueprint(bp)
    return app

# Auth bypass for tests: set g.current_user and call the view
def token_required_stub(f):
    def wrapper(*args, **kwargs):
        g.current_user = {"sub": "owner@example.com", "first_name": "Owner"}
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

class FakeConnector:
    def __init__(self):
        self.created = None

    def create_team(self, creator_email, name, description, department):
        if not name:
            raise ValueError("Name is required.")
        self.created = {
            "ID": 7,
            "Name": name,
            "Description": description,
            "Department": department,
            "OwnerUserID": 1,
            "JoinCode": "ZXCV1234",
            "IsActive": 1,
        }
        return self.created

    def browse_all_teams(self, user_email=None):
        # emulate list_all_teams newest-first
        return [] if not self.created else [self.created]
    
    def browse_joined_teams(self, user_email=None):
        # emulate list_joined_teams
        return [] if not self.created else [self.created]

def test_post_teams_create_successfully(monkeypatch):
    # Monkeypatch the auth decorator on the module before building the app
    monkeypatch.setattr(team_routes, "token_required", token_required_stub, raising=True)
    # Swap out the connector with our fake
    monkeypatch.setattr(team_routes, "connector", FakeConnector(), raising=True)

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.post(
        "/api/teams",
        json={
            "name": "New Team",
            "description": "Desc",
            "department": "Tech",
        },
    )
    assert resp.status_code == 201
    body = resp.get_json()
    # routes.py returns fields directly (no "data" envelope)
    assert body["name"] == "New Team"
    assert body["join_code"] == "ZXCV1234"
    assert body["owner_user_id"] == 1
    assert body["is_active"] == 1

def test_post_teams_validation_error(monkeypatch):
    monkeypatch.setattr(team_routes, "token_required", token_required_stub, raising=True)
    monkeypatch.setattr(team_routes, "connector", FakeConnector(), raising=True)

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.post("/api/teams", json={"name": ""})  # triggers ValueError in FakeConnector
    assert resp.status_code == 400
    body = resp.get_json()
    # routes.py sends {"error": "<string>"}
    assert isinstance(body["error"], str)
    assert "Name is required" in body["error"]

def test_get_teams_list(monkeypatch):
    monkeypatch.setattr(team_routes, "token_required", token_required_stub, raising=True)
    fake = FakeConnector()
    # seed one in the fake
    fake.create_team("owner@example.com", "A", "D", "Tech")
    monkeypatch.setattr(team_routes, "connector", fake, raising=True)

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.get("/api/teams")
    assert resp.status_code == 200
    body = resp.get_json()
    # routes.py returns {"teams": [...], "count": n}
    assert body["count"] == 1
    assert body["teams"][0]["name"] == "A"
    assert body["teams"][0]["join_code"] == "ZXCV1234"

def test_get_joined_teams(monkeypatch):
    """Test GET /api/teams/joined returns joined teams"""
    monkeypatch.setattr(team_routes, "token_required", token_required_stub, raising=True)
    fake = FakeConnector()
    fake.create_team("owner@example.com", "Joined Team", "Desc", "Tech")
    monkeypatch.setattr(team_routes, "connector", fake, raising=True)

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.get("/api/teams/joined")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "teams" in body
    assert "count" in body

def test_leave_team_success(monkeypatch):
    """Test POST /api/teams/<id>/leave returns 200 on success"""
    monkeypatch.setattr(team_routes, "token_required", token_required_stub, raising=True)
    fake = FakeConnector()
    fake.leave_team = lambda email, team_id: None  # Mock leave_team method
    monkeypatch.setattr(team_routes, "connector", fake, raising=True)

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.post("/api/teams/1/leave")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "message" in body
    assert "left team" in body["message"].lower()

def test_leave_team_value_error(monkeypatch):
    """Test POST /api/teams/<id>/leave returns 400 on ValueError"""
    monkeypatch.setattr(team_routes, "token_required", token_required_stub, raising=True)
    fake = FakeConnector()
    def raise_value_error(email, team_id):
        raise ValueError("Cannot leave team")
    fake.leave_team = raise_value_error
    monkeypatch.setattr(team_routes, "connector", fake, raising=True)

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.post("/api/teams/1/leave")
    assert resp.status_code == 400
    body = resp.get_json()
    assert "error" in body

def test_get_team_members_success(monkeypatch):
    """Test GET /api/teams/<id>/members returns team members"""
    monkeypatch.setattr(team_routes, "token_required", token_required_stub, raising=True)
    fake = FakeConnector()
    fake.read_all_team_members = lambda team_id: [
        {"ID": 1, "FirstName": "John", "LastName": "Doe", "Email": "john@example.com", "ProfileImgPath": None}
    ]
    monkeypatch.setattr(team_routes, "connector", fake, raising=True)

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.get("/api/teams/1/members")
    assert resp.status_code == 200
    body = resp.get_json()
    assert "members" in body
    assert "count" in body
    assert len(body["members"]) == 1
    assert body["members"][0]["first_name"] == "John"
