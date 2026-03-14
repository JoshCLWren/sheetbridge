"""Tests for sheetbridge.client module."""

from unittest.mock import MagicMock, patch

import pytest

from sheetbridge.client import SheetsClient


@pytest.fixture
def mock_credentials():
    """Mock Google credentials."""
    with patch("sheetbridge.client.Credentials") as mock_creds:
        yield mock_creds


@pytest.fixture
def mock_gspread_client():
    """Mock gspread client."""
    with patch("sheetbridge.client.gspread.authorize") as mock_auth:
        mock_client = MagicMock()
        mock_auth.return_value = mock_client
        yield mock_client


@pytest.fixture
def test_client():
    """Create a test SheetsClient instance."""
    with patch("sheetbridge.client.Credentials") as mock_creds_cls:
        with patch("sheetbridge.client.gspread.authorize") as mock_auth:
            mock_creds_instance = MagicMock()
            mock_creds_cls.from_service_account_file.return_value = mock_creds_instance
            mock_client = MagicMock()
            mock_auth.return_value = mock_client

            client = SheetsClient(credentials_path="test_credentials.json")

            # Verify credentials were created
            mock_creds_cls.from_service_account_file.assert_called_once()
            mock_auth.assert_called_once_with(mock_creds_instance)

            return client


def test_sheets_client_init_default_scopes():
    """Test SheetsClient initialization with default scopes."""
    with patch("sheetbridge.client.Credentials") as mock_creds_cls:
        with patch("sheetbridge.client.gspread.authorize"):
            mock_creds_instance = MagicMock()
            mock_creds_cls.from_service_account_file.return_value = mock_creds_instance

            SheetsClient(credentials_path="test.json")

            expected_scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]
            mock_creds_cls.from_service_account_file.assert_called_once_with(
                "test.json", scopes=expected_scopes
            )


def test_sheets_client_init_custom_scopes():
    """Test SheetsClient initialization with custom scopes."""
    custom_scopes = ["https://www.googleapis.com/auth/spreadsheets"]

    with patch("sheetbridge.client.Credentials") as mock_creds_cls:
        with patch("sheetbridge.client.gspread.authorize"):
            mock_creds_instance = MagicMock()
            mock_creds_cls.from_service_account_file.return_value = mock_creds_instance

            SheetsClient(credentials_path="test.json", scopes=custom_scopes)

            mock_creds_cls.from_service_account_file.assert_called_once_with(
                "test.json", scopes=custom_scopes
            )


def test_open_spreadsheet(test_client):
    """Test opening a spreadsheet by ID."""
    mock_spreadsheet = MagicMock()
    test_client.client.open_by_key.return_value = mock_spreadsheet

    result = test_client.open_spreadsheet("test_spreadsheet_id")

    assert result == mock_spreadsheet
    test_client.client.open_by_key.assert_called_once_with("test_spreadsheet_id")


def test_open_spreadsheet_by_title(test_client):
    """Test opening a spreadsheet by title."""
    mock_spreadsheet = MagicMock()
    test_client.client.open.return_value = mock_spreadsheet

    result = test_client.open_spreadsheet_by_title("Test Sheet")

    assert result == mock_spreadsheet
    test_client.client.open.assert_called_once_with("Test Sheet")


def test_get_worksheet(test_client):
    """Test getting a specific worksheet."""
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    mock_spreadsheet.worksheet.return_value = mock_worksheet
    test_client.client.open_by_key.return_value = mock_spreadsheet

    result = test_client.get_worksheet("sheet_id", "Sheet1")

    assert result == mock_worksheet
    test_client.client.open_by_key.assert_called_once_with("sheet_id")
    mock_spreadsheet.worksheet.assert_called_once_with("Sheet1")
