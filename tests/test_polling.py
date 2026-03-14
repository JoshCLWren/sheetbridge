"""Tests for sheetbridge.polling module."""

from unittest.mock import MagicMock, patch

import pytest

from sheetbridge.polling import (
    ChangeResult,
    SpreadsheetPoller,
    SpreadsheetState,
    create_poller,
)


@pytest.fixture
def mock_gspread_client():
    """Mock gspread client."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_spreadsheet():
    """Mock gspread Spreadsheet."""
    spreadsheet = MagicMock()
    spreadsheet.id = "test_spreadsheet_id"
    return spreadsheet


@pytest.fixture
def mock_worksheet():
    """Mock gspread Worksheet."""
    worksheet = MagicMock()
    worksheet.title = "Sheet1"
    return worksheet


@pytest.fixture
def poller(mock_gspread_client):
    """Create a SpreadsheetPoller for testing."""
    return SpreadsheetPoller(mock_gspread_client)


def test_spreadsheet_state_creation():
    """Test creating a SpreadsheetState."""
    state = SpreadsheetState(
        spreadsheet_id="test_id",
        revision_id="rev_123",
        checksum="abc123",
        modified_time="2025-01-01T12:00:00Z",
    )

    assert state.spreadsheet_id == "test_id"
    assert state.revision_id == "rev_123"
    assert state.checksum == "abc123"
    assert state.modified_time == "2025-01-01T12:00:00Z"


def test_change_result_creation():
    """Test creating a ChangeResult."""
    old_state = SpreadsheetState(spreadsheet_id="test_id", checksum="old")
    new_state = SpreadsheetState(spreadsheet_id="test_id", checksum="new")

    result = ChangeResult(
        has_changed=True,
        old_state=old_state,
        new_state=new_state,
        changes=["Sheet1"],
    )

    assert result.has_changed is True
    assert result.old_state == old_state
    assert result.new_state == new_state
    assert result.changes == ["Sheet1"]


def test_poller_init(mock_gspread_client):
    """Test SpreadsheetPoller initialization."""
    poller = SpreadsheetPoller(mock_gspread_client)

    assert poller.client == mock_gspread_client
    assert poller._states == {}


def test_calculate_checksum(poller, mock_spreadsheet, mock_worksheet):
    """Test checksum calculation."""
    mock_worksheet.get_all_records.return_value = [
        {"col1": "value1", "col2": "value2"},
    ]
    mock_spreadsheet.worksheets.return_value = [mock_worksheet]

    checksum = poller.calculate_checksum(mock_spreadsheet)

    assert isinstance(checksum, str)
    assert len(checksum) == 64
    mock_worksheet.get_all_records.assert_called_once()


def test_calculate_checksum_empty(poller, mock_spreadsheet, mock_worksheet):
    """Test checksum calculation with empty worksheet."""
    mock_worksheet.get_all_records.return_value = []
    mock_spreadsheet.worksheets.return_value = [mock_worksheet]

    checksum = poller.calculate_checksum(mock_spreadsheet)

    assert isinstance(checksum, str)
    assert len(checksum) == 64


def test_get_modified_time_success(poller, mock_spreadsheet):
    """Test getting modified time from Drive API."""
    mock_drive_service = MagicMock()
    mock_drive_file = MagicMock()
    mock_drive_file.get.return_value = "2025-01-01T12:00:00Z"
    mock_drive_service.files().get().execute.return_value = mock_drive_file

    with patch("googleapiclient.discovery.build", return_value=mock_drive_service):
        modified_time = poller.get_modified_time(mock_spreadsheet)

    assert modified_time == "2025-01-01T12:00:00Z"


def test_get_modified_time_failure(poller, mock_spreadsheet):
    """Test getting modified time when Drive API fails."""
    mock_drive_service = MagicMock()
    mock_drive_service.files().get().execute.side_effect = Exception("API error")

    with patch("googleapiclient.discovery.build", return_value=mock_drive_service):
        modified_time = poller.get_modified_time(mock_spreadsheet)

    assert modified_time is None


def test_register_new_spreadsheet(poller, mock_spreadsheet, mock_worksheet):
    """Test registering a new spreadsheet."""
    mock_worksheet.get_all_records.return_value = [{"data": "value"}]
    mock_spreadsheet.worksheets.return_value = [mock_worksheet]
    poller.client.open_by_key.return_value = mock_spreadsheet

    state = poller.register("test_id")

    assert state.spreadsheet_id == "test_id"
    assert state.checksum is not None
    assert "test_id" in poller._states


def test_register_existing_spreadsheet(poller):
    """Test registering an already registered spreadsheet."""
    existing_state = SpreadsheetState(spreadsheet_id="test_id", checksum="abc")
    poller._states["test_id"] = existing_state

    state = poller.register("test_id")

    assert state == existing_state


def test_check_for_changes_new_spreadsheet(poller, mock_spreadsheet, mock_worksheet):
    """Test checking for changes on a new spreadsheet."""
    mock_worksheet.get_all_records.return_value = [{"data": "value"}]
    mock_spreadsheet.worksheets.return_value = [mock_worksheet]
    poller.client.open_by_key.return_value = mock_spreadsheet

    result = poller.check_for_changes("test_id")

    assert result.has_changed is True
    assert result.old_state is None
    assert result.new_state.spreadsheet_id == "test_id"


def test_check_for_changes_unchanged(poller, mock_spreadsheet, mock_worksheet):
    """Test checking for changes when spreadsheet hasn't changed."""
    mock_worksheet.get_all_records.return_value = [{"data": "value"}]
    mock_spreadsheet.worksheets.return_value = [mock_worksheet]

    poller.client.open_by_key.return_value = mock_spreadsheet

    poller.check_for_changes("test_id", use_checksum=True)
    second_result = poller.check_for_changes("test_id", use_checksum=True)

    assert second_result.has_changed is False
    assert second_result.old_state is not None
    assert second_result.old_state.checksum == second_result.new_state.checksum


def test_check_for_changes_checksum_differs(poller, mock_spreadsheet, mock_worksheet):
    """Test checking for changes when checksum differs."""
    mock_worksheet.get_all_records.side_effect = [
        [{"data": "value1"}],
        [{"data": "value2"}],
    ]
    mock_spreadsheet.worksheets.return_value = [mock_worksheet]
    poller.client.open_by_key.return_value = mock_spreadsheet

    poller.check_for_changes("test_id", use_checksum=True)
    result = poller.check_for_changes("test_id", use_checksum=True)

    assert result.has_changed is True


def test_get_state(poller):
    """Test getting state for a registered spreadsheet."""
    state = SpreadsheetState(spreadsheet_id="test_id", checksum="abc")
    poller._states["test_id"] = state

    retrieved_state = poller.get_state("test_id")

    assert retrieved_state == state


def test_check_for_changes_modified_time_only(poller, mock_spreadsheet, mock_worksheet):
    """Test checking for changes when only modified time differs."""
    mock_worksheet.get_all_records.return_value = [{"data": "value"}]
    mock_spreadsheet.worksheets.return_value = [mock_worksheet]
    poller.client.open_by_key.return_value = mock_spreadsheet

    mock_drive_service = MagicMock()
    mock_drive_file = MagicMock()
    mock_drive_file.get.return_value = "2025-01-01T12:00:00Z"
    mock_drive_service.files().get().execute.return_value = mock_drive_file

    with patch("googleapiclient.discovery.build", return_value=mock_drive_service):
        poller.check_for_changes("test_id", use_checksum=False, use_modified_time=True)

    assert "test_id" in poller._states
    assert poller._states["test_id"].modified_time is not None


def test_get_state_not_registered(poller):
    """Test getting state for an unregistered spreadsheet."""
    assert poller.get_state("nonexistent") is None


def test_register_spreadsheet_with_explicit_state(poller):
    """Test registering a spreadsheet with an explicit state."""
    explicit_state = SpreadsheetState(
        spreadsheet_id="test_id",
        checksum="explicit_checksum",
        modified_time="2025-01-01T12:00:00Z",
    )

    result = poller.register("test_id", state=explicit_state)

    assert result == explicit_state
    assert poller._states["test_id"] == explicit_state


def test_check_for_changes_modified_time_only_when_checksum_matches(
    poller, mock_spreadsheet, mock_worksheet
):
    """Test checking for changes when modified time changes but checksum matches."""
    mock_worksheet.get_all_records.return_value = [{"data": "value"}]
    mock_spreadsheet.worksheets.return_value = [mock_worksheet]
    poller.client.open_by_key.return_value = mock_spreadsheet

    # Register with explicit state
    initial_state = SpreadsheetState(
        spreadsheet_id="test_id",
        checksum="old_checksum",
        modified_time="2025-01-01T12:00:00Z",
    )
    poller._states["test_id"] = initial_state

    # When checksum doesn't change but modified time does
    result = poller.check_for_changes("test_id", use_checksum=True, use_modified_time=True)

    # Should detect change via modified time
    assert result.has_changed is True


def test_clear_state(poller):
    """Test clearing state for a spreadsheet."""
    state = SpreadsheetState(spreadsheet_id="test_id", checksum="abc")
    poller._states["test_id"] = state

    poller.clear_state("test_id")

    assert "test_id" not in poller._states


def test_clear_all_states(poller):
    """Test clearing all states."""
    poller._states["id1"] = SpreadsheetState(spreadsheet_id="id1", checksum="abc")
    poller._states["id2"] = SpreadsheetState(spreadsheet_id="id2", checksum="def")

    poller.clear_all_states()

    assert len(poller._states) == 0


@patch("sheetbridge.polling.gspread.authorize")
@patch("google.oauth2.service_account.Credentials")
def test_create_poller(mock_credentials, mock_authorize):
    """Test create_poller factory function."""
    mock_creds_instance = MagicMock()
    mock_credentials.from_service_account_file.return_value = mock_creds_instance
    mock_client = MagicMock()
    mock_authorize.return_value = mock_client

    poller = create_poller("test_credentials.json")

    assert isinstance(poller, SpreadsheetPoller)
    mock_credentials.from_service_account_file.assert_called_once()
    mock_authorize.assert_called_once_with(mock_creds_instance)
