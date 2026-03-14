"""Google Sheets client with DataFrame sync and change detection."""

from sheetbridge.client import SheetsClient
from sheetbridge.dataframe import (
    append_dataframe_rows,
    dataframe_to_worksheet,
    filter_dataframe_to_worksheet,
    worksheet_to_dataframe,
)
from sheetbridge.polling import (
    ChangeResult,
    SpreadsheetPoller,
    SpreadsheetState,
    create_poller,
)

__version__ = "0.1.0"

__all__ = [
    "SheetsClient",
    "worksheet_to_dataframe",
    "dataframe_to_worksheet",
    "append_dataframe_rows",
    "filter_dataframe_to_worksheet",
    "SpreadsheetState",
    "ChangeResult",
    "SpreadsheetPoller",
    "create_poller",
]
