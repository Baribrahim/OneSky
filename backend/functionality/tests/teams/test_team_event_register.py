# Joining a team functionality Testing

#Connector Methods
from unittest.mock import patch
import pytest
from teams import routes
from tests.test_validation import _login_get_token, _register_user

SECRET = "supersecret"  # match app config

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = SECRET
    with app.test_client() as client:
        yield client

def test_list_owned_teams_returns_only_owner_teams(client):
    # Arrange
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, "password123!")

    mock_teams = [
        {"ID": 1, "Name": "Team Alpha", "OwnerUserID": "user1", "JoinCode": "AAA", "IsOwner": 1},
        {"ID": 2, "Name": "Team Beta", "OwnerUserID": "user2", "JoinCode": "BBB", "IsOwner": 0},
    ]

    with patch.object(routes.connector, "browse_joined_teams", return_value=mock_teams):
        # Act
        response = client.get(
            "/api/teams/owns",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert "teams" in data
        assert data["count"] == 1  # only owner team remains
        assert data["teams"][0]["name"] == "Team Alpha"


def test_list_teams_returns_500_on_exception(client):
    # Arrange
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, "password123!")

    with patch.object(routes.connector, "browse_joined_teams", side_effect=Exception("DB failed")):
        # Act
        response = client.get(
            "/api/teams/joined",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "Could not load teams"