"""
Updated unit tests for the new tool-calling ChatbotConnector.
This version matches the newer connector.py that:
- calls OpenAI once to decide a tool
- executes the tool (DataAccess)
- calls OpenAI again to write the final answer
"""

import pytest
import sys
import os
from datetime import date
from types import SimpleNamespace
from unittest.mock import Mock, patch

# make sure we can import chatbot.connector
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from chatbot.connector import ChatbotConnector


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def mock_data_access():
    """
    Create a mock DataAccess with the methods the new connector uses.
    """
    dao = Mock()

    # user
    dao.get_user_by_email.return_value = {
        "ID": 1,
        "Email": "test@example.com",
        "FirstName": "John",
        "LastName": "Doe",
    }
    dao.get_user_id_by_email.return_value = 1

    # events
    dao.get_upcoming_events.return_value = [
        {
            "ID": 101,
            "Title": "Beach Cleanup",
            "Date": "2025-11-10",
            "StartTime": "10:00:00",
            "EndTime": "12:00:00",
            "LocationCity": "London",
        }
    ]

    # teams
    dao.get_all_joined_teams.return_value = [
        {
            "ID": 201,
            "Name": "Green Team",
            "Description": "Environmental volunteering",
            "Department": "CSR",
            "OwnerUserID": 1,
            "IsActive": 1,
            "JoinCode": "ABC123",
        }
    ]
    dao.get_all_teams.return_value = [
        {
            "ID": 202,
            "Name": "Charity Runners",
            "Description": "Running for good causes",
            "Department": "CSR",
            "OwnerUserID": 2,
            "IsActive": 1,
            "JoinCode": "JOINME",
        }
    ]

    # badges
    dao.get_user_badges.return_value = [
        {
            "ID": 301,
            "Name": "Event Starter",
            "Description": "Your first event!",
            "IconURL": None,
        }
    ]

    # impact/stats
    dao.get_total_hours.return_value = 5.0
    dao.get_completed_events_count.return_value = 2
    dao.get_upcoming_events_count.return_value = 1
    dao.get_badges.return_value = [{"ID": 301}]

    # event search fallbacks (not always used)
    dao.get_filtered_events.return_value = []
    dao.search_events_with_embeddings.return_value = []
    dao.get_user_events.return_value = []

    # team events
    dao.get_team_events.return_value = []

    return dao


def _fake_tool_call_message(tool_name: str, arguments: dict | None = None):
    """
    Build a fake OpenAI message object that requests a tool call.
    This mirrors the structure the connector expects.
    """
    return SimpleNamespace(
        tool_calls=[
            SimpleNamespace(
                id="call_1",
                function=SimpleNamespace(
                    name=tool_name, arguments="{}" if arguments is None else json_dumps(arguments)
                ),
            )
        ],
        content=None,
    )


def _fake_text_message(text: str):
    """Build a fake OpenAI message object with plain text."""
    return SimpleNamespace(content=text)


def json_dumps(d: dict) -> str:
    import json

    return json.dumps(d)


# ---------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------
class TestChatbotToolCalling:
    @patch("chatbot.connector.EmbeddingHelper")  # we don't need real embeddings
    def test_get_my_upcoming_events_flow(self, mock_emb, mock_data_access):
        """
        First model call: asks for get_my_upcoming_events
        Then connector runs DAO, then second model call: returns final text
        """
        # build two fake OpenAI responses
        first_ai_response = SimpleNamespace(
            choices=[SimpleNamespace(message=_fake_tool_call_message("get_my_upcoming_events"))]
        )
        second_ai_response = SimpleNamespace(
            choices=[SimpleNamespace(message=_fake_text_message("Here are your upcoming events."))]
        )

        with patch("chatbot.connector.DataAccess", return_value=mock_data_access):
            with patch("chatbot.connector.OpenAI") as MockOpenAI:
                client_instance = MockOpenAI.return_value
                # First call -> tool, Second call -> final text
                client_instance.chat.completions.create.side_effect = [
                    first_ai_response,
                    second_ai_response,
                ]

                connector = ChatbotConnector()
                connector.dao = mock_data_access

                response, category, events, teams, badges, team_events = connector.process_message(
                    "show my events", "test@example.com"
                )

        assert category == "events"
        assert response == "Here are your upcoming events."
        assert events is not None
        assert len(events) == 1
        assert events[0]["id"] == 101  # normalized

    @patch("chatbot.connector.EmbeddingHelper")
    def test_get_my_teams_flow(self, mock_emb, mock_data_access):
        """
        Model calls get_my_teams → connector returns teams → model writes short answer
        """
        first_ai_response = SimpleNamespace(
            choices=[SimpleNamespace(message=_fake_tool_call_message("get_my_teams"))]
        )
        second_ai_response = SimpleNamespace(
            choices=[SimpleNamespace(message=_fake_text_message("Here are your teams."))]
        )

        with patch("chatbot.connector.DataAccess", return_value=mock_data_access):
            with patch("chatbot.connector.OpenAI") as MockOpenAI:
                client_instance = MockOpenAI.return_value
                client_instance.chat.completions.create.side_effect = [
                    first_ai_response,
                    second_ai_response,
                ]

                connector = ChatbotConnector()
                connector.dao = mock_data_access

                response, category, events, teams, badges, team_events = connector.process_message(
                    "what teams am i in", "test@example.com"
                )

        assert category == "teams"
        assert response == "Here are your teams."
        assert teams is not None
        assert len(teams) == 1
        assert teams[0]["id"] == 201  # normalized

    @patch("chatbot.connector.EmbeddingHelper")
    def test_get_my_badges_flow(self, mock_emb, mock_data_access):
        """
        Model calls get_my_badges → connector returns badges → model writes answer
        """
        first_ai_response = SimpleNamespace(
            choices=[SimpleNamespace(message=_fake_tool_call_message("get_my_badges"))]
        )
        second_ai_response = SimpleNamespace(
            choices=[SimpleNamespace(message=_fake_text_message("These are your badges."))]
        )

        with patch("chatbot.connector.DataAccess", return_value=mock_data_access):
            with patch("chatbot.connector.OpenAI") as MockOpenAI:
                client_instance = MockOpenAI.return_value
                client_instance.chat.completions.create.side_effect = [
                    first_ai_response,
                    second_ai_response,
                ]

                connector = ChatbotConnector()
                connector.dao = mock_data_access

                response, category, events, teams, badges, team_events = connector.process_message(
                    "show my badges", "test@example.com"
                )

        assert category == "badges"
        assert response == "These are your badges."
        assert badges is not None
        assert len(badges) == 1
        assert badges[0]["id"] == 301

    @patch("chatbot.connector.EmbeddingHelper")
    def test_get_my_stats_flow(self, mock_emb, mock_data_access):
        """
        Model calls get_my_stats → connector returns impact → model writes answer
        """
        first_ai_response = SimpleNamespace(
            choices=[SimpleNamespace(message=_fake_tool_call_message("get_my_stats"))]
        )
        second_ai_response = SimpleNamespace(
            choices=[SimpleNamespace(message=_fake_text_message("Here are your stats."))]
        )

        with patch("chatbot.connector.DataAccess", return_value=mock_data_access):
            with patch("chatbot.connector.OpenAI") as MockOpenAI:
                client_instance = MockOpenAI.return_value
                client_instance.chat.completions.create.side_effect = [
                    first_ai_response,
                    second_ai_response,
                ]

                connector = ChatbotConnector()
                connector.dao = mock_data_access

                response, category, events, teams, badges, team_events = connector.process_message(
                    "show my impact", "test@example.com"
                )

        assert category == "impact"
        assert response == "Here are your stats."
        # no events/teams/badges expected from stats
        assert events is None
        assert teams is None

    # -----------------------------------------------------------------
    # Memory / helpers
    # -----------------------------------------------------------------
    @patch("chatbot.connector.EmbeddingHelper")
    def test_first_name_cached(self, mock_emb, mock_data_access):
        """
        New connector still caches user first name.
        """
        with patch("chatbot.connector.DataAccess", return_value=mock_data_access):
            with patch("chatbot.connector.OpenAI"):
                connector = ChatbotConnector()
                connector.dao = mock_data_access

                name1 = connector._get_user_first_name("test@example.com")
                name2 = connector._get_user_first_name("test@example.com")

        assert name1 == "John"
        assert name2 == "John"
        # DataAccess.get_user_by
