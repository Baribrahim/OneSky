import pytest
from flask import Flask, g
from teams import routes as team_routes

def make_app(bp):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test"
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

    def create_team(self, creator_email, name, description, department, capacity):
        if not name:
            raise ValueError("Name is required.")
        self.created = {
            "ID": 7,
            "Name": name,
            "Description": description,
            "Department": department,
            "Capacity": capacity,
            "OwnerUserID": 1,
            "JoinCode": "ZXCV1234",
            "IsActive": 1,
        }
        return self.created

    def browse_all_teams(self):
        # emulate list_all_teams newest-first
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
            "capacity": 10,
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
    fake.create_team("owner@example.com", "A", "D", "Tech", 8)
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
