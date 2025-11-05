# Joining a team functionality Testing


from unittest.mock import MagicMock, patch
import pytest
from teams import routes
from teams.connector import TeamConnector
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

#Connector Methods
def test_verify_team_code_returns_true_when_codes_match():
    with patch('teams.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.get_team_code.return_value = "ABC12345"
        team_id = 1
        connector = TeamConnector()

        #Act
        result = connector.verify_team_code(team_id, "ABC12345")

        #Assert
        assert result is True
        mock_dao_instance.get_team_code.assert_called_once_with(team_id)

def test_verify_team_code_returns_false_when_codes_do_not_match():
    with patch('teams.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao_instance = MockDAO.return_value
        mock_dao_instance.get_team_code.return_value = "54321CBA"
        team_id = 1
        connector = TeamConnector()

        #Act
        result = connector.verify_team_code(team_id, "ABC12345")

        #Assert
        assert result is False
        mock_dao_instance.get_team_code.assert_called_once_with(team_id)

def test_add_user_to_team_calls_insert():
    with patch('teams.connector.DataAccess') as MockDAO:
        # Arrange
        mock_dao = MockDAO.return_value
        connector = TeamConnector()

        # Mock owner_id_from_email to return a fake user_id
        connector.owner_id_from_email = MagicMock(return_value=1)

        user_email = "test@example.com"
        team_id = 1

        # Act
        connector.add_user_to_team(user_email, team_id)

        # Assert
        mock_dao.insert_user_in_team.assert_called_once_with(1, team_id)

#Route Methods
def test_successful_team_join(client):
    #Arrange
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, "Password123!")
   
    with patch.object(routes.connector, 'verify_team_code', return_value=True), \
         patch.object(routes.connector, 'add_user_to_team', return_value=None):

       #Act
        response = client.post(
            '/api/teams/join',
            json={"team_id": 1, "join_code": "valid_code"},
            headers={"Authorization": f"Bearer {token}"}
        )

        #Assert
        assert response.status_code == 200
        assert b"Successfully registered for team" in response.data


def test_invalid_join_code(client):
    #Arrange
    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, "Password123!")

    with patch.object(routes.connector, 'verify_team_code', return_value=False), \
         patch.object(routes.connector, 'add_user_to_team', return_value=None):
    #Act
        response = client.post('/api/teams/join',
                               json={"team_id": 1, "join_code": "valid_code"},
                               headers={"Authorization": f"Bearer {token}"})

        #Assert
        assert response.status_code == 400
        assert b"Invalid code" in response.data

def test_missing_join_code(client):   
    #Arrange

    email, _ = _register_user(client)
    token, _ = _login_get_token(client, email, "Password123!")

    #Act
    response = client.post('/api/teams/join',
                            json={"team_id": 1, "join_code": ""},
                            headers={"Authorization": f"Bearer {token}"})

    #Assert
    print(response.get_json())
    assert response.status_code == 400
    assert b"Missing join_code" in response.data


