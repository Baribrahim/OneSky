"""
Basic unit tests for ChatbotConnector functionality.
Tests core chatbot features including date extraction, memory, and message processing.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import date, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from chatbot.connector import ChatbotConnector


@pytest.fixture
def mock_data_access():
    """Create a mock DataAccess object."""
    mock_dao = Mock()
    mock_dao.get_user_by_email.return_value = {
        "ID": 1,
        "Email": "test@example.com",
        "FirstName": "John",
        "LastName": "Doe"
    }
    mock_dao.get_user_id_by_email.return_value = 1
    mock_dao.get_filtered_events.return_value = []
    mock_dao.search_events_with_embeddings.return_value = []
    mock_dao.get_location.return_value = ["London", "Manchester", "Leeds"]
    return mock_dao


@pytest.fixture
def chatbot_connector(mock_data_access):
    """Create a ChatbotConnector instance with mocked dependencies."""
    with patch('chatbot.connector.DataAccess', return_value=mock_data_access):
        with patch('chatbot.connector.OpenAI'):
            with patch('chatbot.connector.EmbeddingHelper'):
                connector = ChatbotConnector()
                connector.dao = mock_data_access
                return connector


class TestDateExtraction:
    """Tests for date range extraction functionality."""
    
    def test_extract_tomorrow(self, chatbot_connector):
        """Test extraction of 'tomorrow' date."""
        today = date.today()
        start_date, end_date = chatbot_connector._extract_date_range("What events are happening tomorrow?")
        
        assert start_date == today + timedelta(days=1)
        assert end_date == start_date
    
    def test_extract_this_week(self, chatbot_connector):
        """Test extraction of 'this week' date range."""
        today = date.today()
        start_date, end_date = chatbot_connector._extract_date_range("Show me events this week")
        
        assert start_date == today
        days_until_sunday = (6 - today.weekday()) % 7
        expected_end = today + timedelta(days=days_until_sunday) if days_until_sunday > 0 else today
        assert end_date == expected_end
    
    def test_extract_next_month(self, chatbot_connector):
        """Test extraction of 'next month' date range."""
        today = date.today()
        start_date, end_date = chatbot_connector._extract_date_range("Events next month")
        
        if today.month == 12:
            assert start_date.year == today.year + 1
            assert start_date.month == 1
        else:
            assert start_date.month == today.month + 1
            assert start_date.year == today.year
        
        assert end_date is not None
    
    def test_extract_december(self, chatbot_connector):
        """Test extraction of month name."""
        today = date.today()
        start_date, end_date = chatbot_connector._extract_date_range("Events in December")
        
        assert start_date.month == 12
        assert end_date.month == 12
        assert end_date.day == 31
    
    def test_extract_this_weekend(self, chatbot_connector):
        """Test extraction of 'this weekend' date range."""
        today = date.today()
        start_date, end_date = chatbot_connector._extract_date_range("What's happening this weekend?")
        
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            # Today is Saturday
            assert start_date == today
            assert end_date == today + timedelta(days=1)
        else:
            saturday = today + timedelta(days=days_until_saturday)
            assert start_date == saturday
            assert end_date == saturday + timedelta(days=1)
    
    def test_extract_no_date(self, chatbot_connector):
        """Test that queries without dates return None."""
        start_date, end_date = chatbot_connector._extract_date_range("Show me events")
        
        assert start_date is None
        assert end_date is None


class TestLocationExtraction:
    """Tests for location extraction functionality."""
    
    def test_extract_location_london(self, chatbot_connector):
        """Test extraction of London location."""
        location = chatbot_connector._extract_location("Find events in London")
        
        assert location == "London"
    
    def test_extract_location_manchester(self, chatbot_connector):
        """Test extraction of Manchester location."""
        location = chatbot_connector._extract_location("Events near Manchester")
        
        assert location == "Manchester"
    
    def test_extract_no_location(self, chatbot_connector):
        """Test that queries without locations return None."""
        location = chatbot_connector._extract_location("Show me events")
        
        assert location is None


class TestMemorySystem:
    """Tests for short-term and long-term memory functionality."""
    
    def test_long_term_memory_caching(self, chatbot_connector):
        """Test that user first name is cached after first lookup."""
        user_email = "test@example.com"
        
        # First call should fetch from database
        first_name = chatbot_connector._get_user_first_name(user_email)
        assert first_name == "John"
        assert chatbot_connector.dao.get_user_by_email.call_count == 1
        
        # Second call should use cache
        first_name2 = chatbot_connector._get_user_first_name(user_email)
        assert first_name2 == "John"
        # Should still be 1 call (cached)
        assert chatbot_connector.dao.get_user_by_email.call_count == 1
    
    def test_short_term_memory_storage(self, chatbot_connector):
        """Test that conversation history is stored correctly."""
        user_email = "test@example.com"
        
        # Add user message
        chatbot_connector._add_to_conversation_history(user_email, "user", "Hello")
        history = chatbot_connector._get_conversation_history(user_email)
        
        assert len(history) == 1
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
    
    def test_short_term_memory_limit(self, chatbot_connector):
        """Test that conversation history is limited to 10 messages."""
        user_email = "test@example.com"
        
        # Add 15 messages
        for i in range(15):
            chatbot_connector._add_to_conversation_history(user_email, "user", f"Message {i}")
        
        history = chatbot_connector._get_conversation_history(user_email)
        
        assert len(history) == 10
        assert history[0]["content"] == "Message 5"  # First 5 should be dropped
    
    def test_conversation_context_formatting(self, chatbot_connector):
        """Test that conversation context is formatted correctly."""
        user_email = "test@example.com"
        
        chatbot_connector._add_to_conversation_history(user_email, "user", "Hello")
        chatbot_connector._add_to_conversation_history(user_email, "assistant", "Hi there!")
        
        context = chatbot_connector._format_conversation_context(user_email)
        
        assert "Previous conversation" in context
        assert "User: Hello" in context
        assert "Assistant: Hi there!" in context


class TestMessageProcessing:
    """Tests for basic message processing functionality."""
    
    @patch('chatbot.connector.ChatbotConnector.get_ai_response')
    def test_process_message_general(self, mock_ai_response, chatbot_connector):
        """Test processing a general message."""
        mock_ai_response.return_value = "Hello! How can I help you?"
        
        response, category, events, teams, badges, team_events = chatbot_connector.process_message(
            "Hello",
            "test@example.com"
        )
        
        assert category == "general"
        assert response == "Hello! How can I help you?"
        assert events is None
        assert teams is None
        assert badges is None
    
    @patch('chatbot.connector.ChatbotConnector.get_ai_response')
    def test_process_message_with_memory(self, mock_ai_response, chatbot_connector):
        """Test that messages are stored in memory."""
        mock_ai_response.return_value = "Response"
        
        chatbot_connector.process_message("First message", "test@example.com")
        chatbot_connector.process_message("Second message", "test@example.com")
        
        history = chatbot_connector._get_conversation_history("test@example.com")
        assert len(history) >= 2
    
    def test_process_message_without_email(self, chatbot_connector):
        """Test processing message without user email."""
        with patch('chatbot.connector.ChatbotConnector.get_ai_response', return_value="Response"):
            response, category, _, _, _, _ = chatbot_connector.process_message("Hello")
            
            assert response is not None
            assert category is not None


class TestIntentClassification:
    """Tests for intent classification functionality."""
    
    # def test_classify_events_intent(self, chatbot_connector):
    #     """Test classification of events-related queries."""
    #     category, _ = chatbot_connector._classify_intent_with_ai("find volunteer events")
        
    #     assert category == "events"
    
    def test_classify_teams_intent(self, chatbot_connector):
        """Test classification of teams-related queries."""
        category, _ = chatbot_connector._classify_intent_with_ai("show me teams")
        
        assert category == "teams"
    
    def test_classify_badges_intent(self, chatbot_connector):
        """Test classification of badges-related queries."""
        category, _ = chatbot_connector._classify_intent_with_ai("what badges do I have")
        
        assert category == "badges"
    
    def test_classify_general_intent(self, chatbot_connector):
        """Test classification of general queries."""
        category, _ = chatbot_connector._classify_intent_with_ai("hello")
        
        assert category == "general"
    
    def test_empty_message(self, chatbot_connector):
        """Test handling of empty messages."""
        category, _ = chatbot_connector._classify_intent_with_ai("")
        
        assert category == "general"


class TestDatePatternRemoval:
    """Tests for removing date patterns from messages."""
    
    def test_remove_date_patterns(self, chatbot_connector):
        """Test that date patterns are removed from messages."""
        message = "find events this week in London"
        cleaned = chatbot_connector._remove_date_patterns_from_message(message)
        
        assert "this week" not in cleaned.lower()
        assert "london" in cleaned.lower()  # Location should remain
    
    def test_remove_month_patterns(self, chatbot_connector):
        """Test that month names are removed."""
        message = "show me events in December"
        cleaned = chatbot_connector._remove_date_patterns_from_message(message)
        
        assert "december" not in cleaned.lower()


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_missing_user_email(self, chatbot_connector):
        """Test handling when user email is None."""
        with patch('chatbot.connector.ChatbotConnector.get_ai_response', return_value="Response"):
            response, category, _, _, _, _ = chatbot_connector.process_message("Hello", None)
            
            assert response is not None
            assert category is not None
    
    def test_database_error_handling(self, chatbot_connector):
        """Test handling of database errors gracefully."""
        chatbot_connector.dao.get_user_by_email.side_effect = Exception("DB Error")
        
        # Should not crash, should return None
        first_name = chatbot_connector._get_user_first_name("test@example.com")
        
        assert first_name is None

