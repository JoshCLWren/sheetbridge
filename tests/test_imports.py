"""Tests for sheetbridge package imports."""

from sheetbridge import (
    ChangeResult,
    SheetsClient,
    SpreadsheetPoller,
    SpreadsheetState,
    __version__,
    append_dataframe_rows,
    create_poller,
    dataframe_to_worksheet,
    filter_dataframe_to_worksheet,
    worksheet_to_dataframe,
)


def test_public_api_exports():
    """Test that all public API items are exported."""
    assert __version__ == "0.1.0"


def test_client_is_importable():
    """Test that SheetsClient can be imported."""
    assert SheetsClient is not None


def test_dataframe_functions_are_importable():
    """Test that dataframe functions can be imported."""
    assert worksheet_to_dataframe is not None
    assert dataframe_to_worksheet is not None
    assert append_dataframe_rows is not None
    assert filter_dataframe_to_worksheet is not None


def test_polling_classes_are_importable():
    """Test that polling classes can be imported."""
    assert SpreadsheetState is not None
    assert ChangeResult is not None
    assert SpreadsheetPoller is not None
    assert create_poller is not None
