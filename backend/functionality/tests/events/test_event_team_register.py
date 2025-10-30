# Joining a team functionality Testing

#Connector Methods
from unittest.mock import patch
import pytest
from events.connector import EventConnector
from events import routes
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


"""Connector methods"""

def test_extract_team_unregistered_details_calls_dao_correctly():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.read_user_unregistered_teams.return_value = [
            {"ID": 1, "Name": "Team Alpha"},
            {"ID": 2, "Name": "Team Beta"}
        ]
        connector = EventConnector()
        user_email = "user@example.com"
        event_id = 123

        # Act
        result = connector.extract_team_unregistered_details(user_email, event_id)

        # Assert
        mock_dao_instance.read_user_unregistered_teams.assert_called_once_with(event_id, user_email)
        assert result == [
            {"ID": 1, "Name": "Team Alpha"},
            {"ID": 2, "Name": "Team Beta"}
        ]


def test_extract_team_unregistered_details_raises_when_dao_fails():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.read_user_unregistered_teams.side_effect = Exception("DB error")
        connector = EventConnector()

        # Act & Assert
        try:
            connector.extract_team_unregistered_details("user@example.com", 1)
        except Exception as e:
            assert str(e) == "DB error"
        else:
            assert False, "Expected Exception not raised"


def test_register_team_for_event_calls_dao_correctly():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        connector = EventConnector()
        team_id = 55
        event_id = 77

        # Act
        connector.register_team_for_event(team_id, event_id)

        # Assert
        mock_dao_instance.insert_team_to_event_registration.assert_called_once_with(team_id, event_id)


def test_register_team_for_event_raises_when_dao_fails():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.insert_team_to_event_registration.side_effect = Exception("Insert failed")
        connector = EventConnector()

        # Act & Assert
        try:
            connector.register_team_for_event(1, 2)
        except Exception as e:
            assert str(e) == "Insert failed"
        else:
            assert False, "Expected Exception not raised"


"""Routes Methods"""

def test_successful_team_signup(client):
    """POST /api/events/signup-team returns 200 on success"""
    # Arrange
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, "password123!")

    with patch.object(routes.con, "register_team_for_event", return_value=None) as mock_register:
        # Act
        response = client.post(
            "/api/events/signup-team",
            json={"event_id": 1, "team_id": 2},
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Successfully registered for event!"
        mock_register.assert_called_once_with(2, 1)


def test_signup_team_missing_event_id_returns_400(client):
    """Should return 400 if event_id missing"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, "password123!")

    response = client.post(
        "/api/events/signup-team",
        json={"team_id": 2},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing event_id"


def test_signup_team_missing_team_id_returns_400(client):
    """Should return 400 if team_id missing"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, "password123!")

    response = client.post(
        "/api/events/signup-team",
        json={"event_id": 1},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 400
    assert response.get_json()["error"] == "Missing team_id"


# ---------------------------------------------------------------------
# /api/events/<event_id>/available-teams
# ---------------------------------------------------------------------

def test_get_available_teams_success(client):
    """GET /api/events/<id>/available-teams returns available teams"""
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, "password123!")

    mock_teams = [
        {"ID": 1, "Name": "Team Alpha"},
        {"ID": 2, "Name": "Team Beta"},
    ]

    with patch.object(routes.con, "extract_team_unregistered_details", return_value=mock_teams):
        response = client.get(
            "/api/events/1/available-teams",
            headers={"Authorization": f"Bearer {token}"}
        )

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert "teams" in data
        assert len(data["teams"]) == 2
        assert data["teams"][0]["Name"] == "Team Alpha"