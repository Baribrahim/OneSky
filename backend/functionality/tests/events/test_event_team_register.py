# Joining a team functionality Testing

#Connector Methods
from unittest.mock import patch, MagicMock
import pytest
from events.connector import EventConnector
from events import routes
from tests.test_validation import _login_get_token, _register_user

SECRET = "supersecret"  # match app config

@pytest.fixture(autouse=True)
def mock_data_access():
    """Auto-use fixture to mock all DataAccess instances and prevent real DB connections."""
    with patch('data_access.pymysql.connect') as mock_connect, \
         patch('auth.connector.DataAccess') as mock_auth_da_class, \
         patch('badges.connector.DataAccess') as mock_badge_da_class, \
         patch('events.connector.DataAccess') as mock_events_da_class:
        
        # Mock pymysql connection to prevent real DB connections
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        
        # Mock DataAccess instances for connectors
        mock_auth_da_instance = MagicMock()
        mock_badge_da_instance = MagicMock()
        mock_events_da_instance = MagicMock()
        
        mock_auth_da_class.return_value = mock_auth_da_instance
        mock_badge_da_class.return_value = mock_badge_da_instance
        mock_events_da_class.return_value = mock_events_da_instance
        
        # Set up default return values for registration/login flow
        mock_auth_da_instance.user_exists.return_value = False
        mock_auth_da_instance.get_user_id_by_email.return_value = 1
        mock_auth_da_instance.get_user_by_email.return_value = {
            "ID": 1,
            "Email": "test@sky.uk",
            "Password": b"$2b$12$hashedpassword",
            "FirstName": "Test",
            "LastName": "User"
        }
        mock_auth_da_instance.verify_user_by_password.return_value = {
            "ID": 1,
            "Email": "test@sky.uk",
            "FirstName": "Test",
            "LastName": "User"
        }
        mock_badge_da_instance.check_and_award_event_badges.return_value = []
        
        yield {
            'auth': mock_auth_da_instance,
            'badge': mock_badge_da_instance,
            'events': mock_events_da_instance
        }

@pytest.fixture
def client():
    from app import create_app
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = SECRET
    with app.test_client() as client:
        yield client


"""Connector methods"""

def test_extract_team_event_details_calls_dao_correctly():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.read_user_teams_with_registration_status.return_value = [
            {"ID": 1, "Name": "Team Alpha", "isRegistered": 1},
            {"ID": 2, "Name": "Team Beta", "isRegistered": 0}
        ]
        connector = EventConnector()
        user_email = "user@example.com"
        event_id = 123

        # Act
        result = connector.extract_team_event_details(user_email, event_id)

        # Assert
        mock_dao_instance.read_user_teams_with_registration_status.assert_called_once_with(event_id, user_email)
        assert result == [
            {"ID": 1, "Name": "Team Alpha", "isRegistered": 1},
            {"ID": 2, "Name": "Team Beta", "isRegistered": 0}
        ]


def test_extract_team_event_details_raises_when_dao_fails():
    with patch('events.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.read_user_teams_with_registration_status.side_effect = Exception("DB error")
        connector = EventConnector()

        # Act & Assert
        try:
            connector.extract_team_event_details("user@example.com", 1)
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
    token, _ = _login_get_token(client, email, "Password123!")

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
    token, _ = _login_get_token(client, email, "Password123!")

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
    token, _ = _login_get_token(client, email, "Password123!")

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
    token, _ = _login_get_token(client, email, "Password123!")

    mock_teams = [
        {"ID": 1, "Name": "Team Alpha", "isRegistered": 1},
        {"ID": 2, "Name": "Team Beta", "isRegistered": 0}
    ]

    with patch.object(routes.con, "extract_team_event_details", return_value=mock_teams):
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