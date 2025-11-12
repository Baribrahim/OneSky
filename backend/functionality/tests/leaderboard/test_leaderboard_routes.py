"""
Test suite for leaderboard routes using pytest.
Tests cover all leaderboard route endpoints with mocked authentication and data access.
"""

import pytest
from unittest.mock import Mock
from tests.conftest import setup_auth_patch, make_test_app

# Setup auth patch before importing routes
setup_auth_patch()

from leaderboard import routes as leaderboard_routes


class FakeLeaderboardConnector:
    """Fake LeaderboardConnector for testing."""
    
    def __init__(self):
        self.ordered_users = []
        self.user_rank = 1
        self.user_stats = {
            "completed_events": 5,
            "total_hours": 20.0,
            "badges": 3
        }
    
    def get_ordered_users(self, user_email):
        return self.ordered_users
    
    def get_user_current_rank(self, user_email):
        return self.user_rank
    
    def get_user_stats(self, user_email):
        return self.user_stats


@pytest.fixture
def fake_connector():
    """Fixture for fake leaderboard connector."""
    return FakeLeaderboardConnector()


def test_ranked_users_success(monkeypatch, fake_connector):
    """Test successful retrieval of ranked users."""
    monkeypatch.setattr(leaderboard_routes, "lc", fake_connector, raising=True)
    
    fake_connector.ordered_users = [
        {"ID": 1, "FirstName": "User1", "RankScore": 100, "ProfileImgPath": "user1.png"},
        {"ID": 2, "FirstName": "User2", "RankScore": 90, "ProfileImgPath": None}
    ]
    
    app = make_test_app(leaderboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/leaderboard")
    assert response.status_code == 200
    data = response.get_json()
    assert "users" in data
    assert len(data["users"]) == 2
    assert "ProfileImgURL" in data["users"][0]
    assert data["users"][0]["ProfileImgURL"] == "/api/profile/images/user1.png"
    assert data["users"][1]["ProfileImgURL"] == "/api/profile/images/default.png"


def test_ranked_users_no_profile_image(monkeypatch, fake_connector):
    """Test ranked_users when user has no profile image."""
    monkeypatch.setattr(leaderboard_routes, "lc", fake_connector, raising=True)
    
    fake_connector.ordered_users = [
        {"ID": 1, "FirstName": "User1", "RankScore": 100}
    ]
    
    app = make_test_app(leaderboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/leaderboard")
    assert response.status_code == 200
    data = response.get_json()
    assert data["users"][0]["ProfileImgURL"] == "/api/profile/images/default.png"


def test_ranked_users_exception(monkeypatch, fake_connector):
    """Test ranked_users with exception."""
    monkeypatch.setattr(leaderboard_routes, "lc", fake_connector, raising=True)
    
    fake_connector.get_ordered_users = Mock(side_effect=Exception("Database error"))
    
    app = make_test_app(leaderboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/leaderboard")
    assert response.status_code == 500


def test_my_rank_success(monkeypatch, fake_connector):
    """Test successful retrieval of user's current rank."""
    monkeypatch.setattr(leaderboard_routes, "lc", fake_connector, raising=True)
    
    fake_connector.user_rank = 5
    
    app = make_test_app(leaderboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/leaderboard/my-rank")
    assert response.status_code == 200
    data = response.get_json()
    assert "currentRank" in data
    assert data["currentRank"] == 5


def test_my_rank_exception(monkeypatch, fake_connector):
    """Test my_rank with exception."""
    monkeypatch.setattr(leaderboard_routes, "lc", fake_connector, raising=True)
    
    fake_connector.get_user_current_rank = Mock(side_effect=Exception("Database error"))
    
    app = make_test_app(leaderboard_routes.bp)
    client = app.test_client()
    
    response = client.get("/api/leaderboard/my-rank")
    assert response.status_code == 500


def test_get_user_stats_success(monkeypatch, fake_connector):
    """Test successful retrieval of user stats."""
    monkeypatch.setattr(leaderboard_routes, "lc", fake_connector, raising=True)
    
    app = make_test_app(leaderboard_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/leaderboard/stats", json={"email": "test@example.com"})
    assert response.status_code == 200
    data = response.get_json()
    assert "stats" in data
    assert data["stats"]["completed_events"] == 5
    assert data["stats"]["total_hours"] == 20.0
    assert data["stats"]["badges"] == 3


def test_get_user_stats_missing_email(monkeypatch, fake_connector):
    """Test get_user_stats without email."""
    monkeypatch.setattr(leaderboard_routes, "lc", fake_connector, raising=True)
    
    app = make_test_app(leaderboard_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/leaderboard/stats", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_get_user_stats_exception(monkeypatch, fake_connector):
    """Test get_user_stats with exception."""
    monkeypatch.setattr(leaderboard_routes, "lc", fake_connector, raising=True)
    
    fake_connector.get_user_stats = Mock(side_effect=Exception("Database error"))
    
    app = make_test_app(leaderboard_routes.bp)
    client = app.test_client()
    
    response = client.post("/api/leaderboard/stats", json={"email": "test@example.com"})
    assert response.status_code == 500

