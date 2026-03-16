# Changelog

All notable changes to sheetbridge will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of sheetbridge library
- `SheetsClient` class for Google Sheets authentication and access
- DataFrame sync operations:
  - `worksheet_to_dataframe()` - Read worksheets into pandas DataFrames
  - `dataframe_to_worksheet()` - Write DataFrames to worksheets
  - `append_dataframe_rows()` - Append DataFrame rows to existing worksheets
  - `filter_dataframe_to_worksheet()` - Filter and update worksheets
- Change detection and polling:
  - `SpreadsheetState` dataclass for tracking spreadsheet state
  - `ChangeResult` dataclass for change detection results
  - `SpreadsheetPoller` class for monitoring spreadsheet changes
  - `create_poller()` factory function for easy poller creation
- Support for service account authentication
- Configurable OAuth scopes for Sheets and Drive APIs
- Full type hints throughout the codebase
- 96%+ test coverage with pytest

## [0.1.0] - 2024-01-XX

### Added
- Initial release
- Google Sheets client with gspread integration
- DataFrame synchronization capabilities
- Change detection and polling support
- Comprehensive test suite
- Documentation (README.md, AGENTS.md)
