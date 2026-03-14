"""Tests for sheetbridge.dataframe module."""

from unittest.mock import MagicMock

import pandas as pd
import pytest

from sheetbridge.dataframe import (
    append_dataframe_rows,
    dataframe_to_worksheet,
    filter_dataframe_to_worksheet,
    worksheet_to_dataframe,
)


@pytest.fixture
def mock_worksheet():
    """Mock gspread Worksheet."""
    worksheet = MagicMock()
    return worksheet


def test_worksheet_to_dataframe(mock_worksheet):
    """Test converting worksheet to DataFrame."""
    mock_worksheet.get_all_records.return_value = [
        {"name": "Alice", "age": "30"},
        {"name": "Bob", "age": "25"},
    ]

    result = worksheet_to_dataframe(mock_worksheet)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert list(result.columns) == ["name", "age"]
    assert result["name"].tolist() == ["Alice", "Bob"]
    assert result["age"].tolist() == ["30", "25"]
    mock_worksheet.get_all_records.assert_called_once()


def test_worksheet_to_dataframe_empty(mock_worksheet):
    """Test converting empty worksheet to DataFrame."""
    mock_worksheet.get_all_records.return_value = []

    result = worksheet_to_dataframe(mock_worksheet)

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_dataframe_to_worksheet(mock_worksheet):
    """Test writing DataFrame to worksheet."""
    df = pd.DataFrame(
        {
            "name": ["Alice", "Bob"],
            "age": [30, 25],
        }
    )

    dataframe_to_worksheet(mock_worksheet, df, include_index=False)

    # Verify clear was called
    mock_worksheet.clear.assert_called_once()

    # Verify update was called with headers and data
    mock_worksheet.update.assert_called_once()
    call_args = mock_worksheet.update.call_args
    assert call_args[1]["raw"] is False

    data = call_args[0][0]
    assert data[0] == ["name", "age"]
    assert ["Alice", 30] in data[1:]
    assert ["Bob", 25] in data[1:]


def test_dataframe_to_worksheet_with_index(mock_worksheet):
    """Test writing DataFrame to worksheet with index."""
    df = pd.DataFrame(
        {
            "name": ["Alice", "Bob"],
            "age": [30, 25],
        }
    )

    dataframe_to_worksheet(mock_worksheet, df, include_index=True)

    mock_worksheet.update.assert_called_once()
    call_args = mock_worksheet.update.call_args
    data = call_args[0][0]

    assert data[0] == ["", "name", "age"]
    assert len(data) == 3


def test_dataframe_to_worksheet_empty(mock_worksheet):
    """Test writing empty DataFrame to worksheet."""
    df = pd.DataFrame({"name": [], "age": []})

    dataframe_to_worksheet(mock_worksheet, df, include_index=False)

    mock_worksheet.clear.assert_called_once()
    mock_worksheet.update.assert_called_once()


def test_append_dataframe_rows(mock_worksheet):
    """Test appending DataFrame rows to worksheet."""
    df = pd.DataFrame(
        {
            "name": ["Charlie", "Diana"],
            "age": [35, 28],
        }
    )

    append_dataframe_rows(mock_worksheet, df, include_header=False)

    mock_worksheet.append_rows.assert_called_once()
    call_args = mock_worksheet.append_rows.call_args

    assert call_args[1]["value_input_option"] == "USER_ENTERED"

    data = call_args[0][0]
    assert ["Charlie", 35] in data
    assert ["Diana", 28] in data


def test_append_dataframe_rows_with_header(mock_worksheet):
    """Test appending DataFrame rows with header."""
    df = pd.DataFrame(
        {
            "name": ["Eve"],
            "age": [40],
        }
    )

    append_dataframe_rows(mock_worksheet, df, include_header=True)

    call_args = mock_worksheet.append_rows.call_args
    data = call_args[0][0]

    assert data[0] == ["name", "age"]
    assert ["Eve", 40] in data


def test_filter_dataframe_to_worksheet(mock_worksheet):
    """Test filtering DataFrame and writing to worksheet."""
    df = pd.DataFrame(
        {
            "category": ["A", "B", "A", "B"],
            "value": [1, 2, 3, 4],
        }
    )

    result = filter_dataframe_to_worksheet(mock_worksheet, df, query_col="category", query_val="A")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 2
    assert all(result["category"] == "A")
    assert list(result["value"]) == [1, 3]

    mock_worksheet.clear.assert_called_once()
    mock_worksheet.update.assert_called_once()


def test_filter_dataframe_to_worksheet_empty_result(mock_worksheet):
    """Test filtering DataFrame with no matches."""
    df = pd.DataFrame(
        {
            "category": ["A", "A"],
            "value": [1, 2],
        }
    )

    result = filter_dataframe_to_worksheet(mock_worksheet, df, query_col="category", query_val="B")

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0
