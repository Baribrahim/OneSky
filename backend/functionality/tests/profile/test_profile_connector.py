"""
Test suite for ProfileConnector using pytest.
Tests cover all ProfileConnector methods with mocked data access.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os
import types
import importlib.util
import bcrypt

# Test-only password constants (not real credentials)
TEST_OLD_PASSWORD = "test-old-password-for-testing-only"  # NOSONAR: test-only password constant
TEST_NEW_PASSWORD = "test-new-password-for-testing-only"  # NOSONAR: test-only password constant
TEST_WRONG_PASSWORD = "test-wrong-password-for-testing-only"  # NOSONAR: test-only password constant

# Add the parent directory to sys.path to import modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Create a fake profile package to avoid conflict with built-in profile module
profile_connector_path = os.path.join(parent_dir, "profile", "connector.py")
spec = importlib.util.spec_from_file_location("profile.connector", profile_connector_path)
profile_connector_module = importlib.util.module_from_spec(spec)

# Create profile package module
profile_package = types.ModuleType('profile')
profile_package.connector = profile_connector_module
sys.modules['profile'] = profile_package
sys.modules['profile.connector'] = profile_connector_module
spec.loader.exec_module(profile_connector_module)
ProfileConnector = profile_connector_module.ProfileConnector

from data_access import DataAccess


@pytest.fixture
def mock_data_access():
    """Fixture for mocked DataAccess."""
    return Mock(spec=DataAccess)


@pytest.fixture
def connector(mock_data_access):
    """Fixture for ProfileConnector with mocked data access."""
    return ProfileConnector(dao=mock_data_access)


def test_get_user_details_success(connector, mock_data_access):
    """Test successful retrieval of user details."""
    expected_details = {
        "ID": 1,
        "Email": "test@example.com",
        "FirstName": "Test",
        "LastName": "User"
    }
    mock_data_access.read_user_info.return_value = expected_details
    
    result = connector.get_user_details("test@example.com")
    
    assert result == expected_details
    mock_data_access.read_user_info.assert_called_once_with("test@example.com")


def test_get_user_details_none(connector, mock_data_access):
    """Test get_user_details when user is not found."""
    mock_data_access.read_user_info.return_value = None
    
    result = connector.get_user_details("nonexistent@example.com")
    
    assert result is None
    mock_data_access.read_user_info.assert_called_once_with("nonexistent@example.com")


def test_update_profile_image_success(connector, mock_data_access):
    """Test successful profile image update."""
    mock_data_access.update_profile_image.return_value = True
    
    result = connector.update_profile_image("test@example.com", "new_image.png")
    
    assert result is True
    mock_data_access.update_profile_image.assert_called_once_with("test@example.com", "new_image.png")


def test_update_profile_image_failure(connector, mock_data_access):
    """Test profile image update failure."""
    mock_data_access.update_profile_image.return_value = False
    
    result = connector.update_profile_image("test@example.com", "new_image.png")
    
    assert result is False
    mock_data_access.update_profile_image.assert_called_once_with("test@example.com", "new_image.png")


def test_update_user_password_success(connector, mock_data_access):
    """Test successful password update."""
    mock_data_access.verify_user_by_password.return_value = {"ID": 1}
    
    result = connector.update_user_password("test@example.com", TEST_OLD_PASSWORD, TEST_NEW_PASSWORD)
    
    assert result is True
    mock_data_access.verify_user_by_password.assert_called_once_with("test@example.com", TEST_OLD_PASSWORD)
    mock_data_access.update_user_password.assert_called_once()
    # Verify the password was hashed
    call_args = mock_data_access.update_user_password.call_args
    assert call_args[0][0] == "test@example.com"
    assert isinstance(call_args[0][1], bytes)  # Hashed password should be bytes


def test_update_user_password_incorrect_old(connector, mock_data_access):
    """Test password update with incorrect old password."""
    mock_data_access.verify_user_by_password.return_value = None
    
    result = connector.update_user_password("test@example.com", TEST_WRONG_PASSWORD, TEST_NEW_PASSWORD)
    
    assert result is False
    mock_data_access.verify_user_by_password.assert_called_once_with("test@example.com", TEST_WRONG_PASSWORD)
    mock_data_access.update_user_password.assert_not_called()


def test_update_user_password_verification_exception(connector, mock_data_access):
    """Test password update when verification raises exception."""
    mock_data_access.verify_user_by_password.side_effect = Exception("Database error")
    
    # Should handle exception gracefully
    with pytest.raises(Exception):
        connector.update_user_password("test@example.com", TEST_OLD_PASSWORD, TEST_NEW_PASSWORD)
    
    mock_data_access.update_user_password.assert_not_called()


def test_update_user_password_hash_verification(connector, mock_data_access):
    """Test that password is properly hashed before storage."""
    mock_data_access.verify_user_by_password.return_value = {"ID": 1}
    
    connector.update_user_password("test@example.com", TEST_OLD_PASSWORD, TEST_NEW_PASSWORD)
    
    # Verify update_user_password was called with hashed password
    call_args = mock_data_access.update_user_password.call_args
    hashed_password = call_args[0][1]
    
    # Verify it's a bcrypt hash
    assert isinstance(hashed_password, bytes)
    # Verify the hash can be used to verify the password
    assert bcrypt.checkpw(TEST_NEW_PASSWORD.encode("utf-8"), hashed_password)


def test_connector_initialization_with_dao():
    """Test ProfileConnector initialization with provided DataAccess."""
    mock_dao = Mock(spec=DataAccess)
    connector = ProfileConnector(dao=mock_dao)
    
    assert connector.dao == mock_dao


def test_connector_initialization_without_dao():
    """Test ProfileConnector initialization without provided DataAccess."""
    connector = ProfileConnector()
    
    assert connector.dao is not None
    assert isinstance(connector.dao, DataAccess)

