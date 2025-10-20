import pytest
from flask import Flask, g

def make_app(bp):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test"
    app.register_blueprint(bp)
    return app

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
            "ID": 7, "Name": name, "Description": description,
            "Department": department, "Capacity": capacity,
            "OwnerUserID": 1, "JoinCode": "ZXCV1234", "IsActive": 1
        }
        return self.created
    def browse_all_teams(self):
        return [] if not self.created else [self.created]

def test_post_teams_created(monkeypatch):
    from teams import routes as team_routes
    team_routes.token_required = token_required_stub
    team_routes.connector = FakeConnector()

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.post("/teams", json={
        "name": "New Team",
        "description": "Desc",
        "department": "Tech",
        "capacity": 10
    })
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["data"]["name"] == "New Team"
    assert body["data"]["join_code"] == "ZXCV1234"

def test_post_teams_validation_error(monkeypatch):
    from teams import routes as team_routes
    team_routes.token_required = token_required_stub
    team_routes.connector = FakeConnector()

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.post("/teams", json={"name": ""})
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "VALIDATION_ERROR"

def test_get_teams_list(monkeypatch):
    from teams import routes as team_routes
    team_routes.token_required = token_required_stub
    team_routes.connector = FakeConnector()
    # seed one
    team_routes.connector.create_team("owner@example.com", "A", "D", "Tech", 8)

    app = make_app(team_routes.bp)
    client = app.test_client()

    resp = client.get("/teams")
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["data"]["items"][0]["name"] == "A"
