# sheetbridge

[![CI Status](https://github.com/JoshCLWren/sheetbridge/workflows/CI/badge.svg)](https://github.com/JoshCLWren/sheetbridge/actions)

A Python library that provides a convenient bridge between Google Sheets and Python applications, wrapping `gspread` with DataFrame synchronization and change detection capabilities.

## Features

- **Google Sheets Integration**: Simple authentication and API access via service account credentials
- **DataFrame Synchronization**: Read worksheets into pandas DataFrames and write DataFrames back to sheets
- **Change Detection**: Monitor spreadsheets for changes with polling support
- **Batch Operations**: Efficiently append and filter data to/from worksheets
- **Type Safety**: Full type hints throughout the codebase
- **Test Coverage**: 96%+ test coverage with pytest

## Quick Start

```bash
# Clone the repository
git clone https://github.com/JoshCLWren/sheetbridge.git
cd sheetbridge

# Install dependencies
uv sync --all-extras

# Activate the virtual environment (do this once per session)
source .venv/bin/activate

# Run tests
pytest

# Use in your Python code
python -c "import sheetbridge; print(sheetbridge.__version__)"
```

## Installation

```bash
# From PyPI (when published)
pip install sheetbridge

# Or install with Google Drive API support
pip install sheetbridge[drive]
```

## Usage

### Basic Authentication

```python
from sheetbridge import SheetsClient

# Initialize with service account credentials
client = SheetsClient(credentials_path="path/to/service-account.json")

# Open a spreadsheet by ID
spreadsheet = client.open_spreadsheet("1BxiMVs0XRA5nFMdKvBdBZjGMUUqptbfs74NYvQE")

# Or by title
spreadsheet = client.open_spreadsheet_by_title("My Spreadsheet")

# Access a specific worksheet
worksheet = client.get_worksheet("spreadsheet_id", "Sheet1")
```

### DataFrame Operations

```python
from sheetbridge import SheetsClient, worksheet_to_dataframe, dataframe_to_worksheet
import pandas as pd

client = SheetsClient(credentials_path="service-account.json")

# Read worksheet into DataFrame
df = worksheet_to_dataframe(worksheet)
print(df.head())

# Write DataFrame to worksheet (replaces existing data)
df = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie"],
    "Age": [25, 30, 35],
    "City": ["NYC", "LA", "Chicago"]
})
dataframe_to_worksheet(df, worksheet)
```

### Batch Operations

```python
from sheetbridge import append_dataframe_rows, filter_dataframe_to_worksheet

# Append new rows to existing worksheet
new_data = pd.DataFrame({
    "Name": ["David", "Eve"],
    "Age": [28, 32],
    "City": ["Boston", "Seattle"]
})
append_dataframe_rows(new_data, worksheet)

# Filter DataFrame to worksheet (update rows based on criteria)
filtered_df = df[df["Age"] > 30]
filter_dataframe_to_worksheet(filtered_df, worksheet)
```

### Change Detection & Polling

```python
from sheetbridge import create_poller

# Create a poller for monitoring spreadsheet changes
poller = create_poller(
    credentials_path="service-account.json",
    spreadsheet_id="your-spreadsheet-id",
    poll_interval_seconds=30
)

# Check for changes
result = poller.check_for_changes()
if result.has_changes:
    print(f"Changes detected: {result.changes}")
    print(f"Previous state: {result.previous_state}")
    print(f"Current state: {result.current_state}")
```

## Development Workflow

### First Time Setup

```bash
# Install dependencies
uv sync --all-extras

# Activate the virtual environment
source .venv/bin/activate
```

### Daily Development

```bash
# Run tests
pytest

# Run tests with coverage report
pytest --cov-report=term-missing

# Run linting
make lint

# Format code with ruff
ruff format .
```

### Make Commands

- `make lint` - Run all linting checks (ruff + pyright)
- `make pytest` - Run the test suite
- `make venv` - Create virtual environment
- `make sync` - Install/update dependencies

## Project Structure

```
sheetbridge/
├── sheetbridge/              # Main package
│   ├── __init__.py          # Package exports
│   ├── client.py            # SheetsClient for authentication
│   ├── dataframe.py         # DataFrame sync operations
│   └── polling.py           # Change detection and polling
├── tests/                   # Test suite
│   ├── conftest.py         # pytest fixtures
│   ├── test_client.py      # Client tests
│   ├── test_dataframe.py   # DataFrame tests
│   └── test_polling.py     # Polling tests
├── .github/
│   └── workflows/ci.yml    # CI pipeline
├── scripts/
│   └── lint.sh            # Linting script
├── pyproject.toml         # Project configuration
├── uv.lock               # Dependency lockfile
└── README.md             # This file
```

## Testing

The project uses pytest with coverage reporting:

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_client.py

# Run with coverage
pytest --cov=sheetbridge --cov-report=html
```

**Coverage requirement**: Minimum 96% (configured in pyproject.toml)

## Code Quality

### Linting

The project uses ruff for fast Python linting:

```bash
# Run linter
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Format code
ruff format .
```

### Type Checking

Pyright provides static type checking:

```bash
# Run type checker
pyright .
```

### Pre-commit Hook

A pre-commit hook is installed automatically that runs:
- Python compilation check
- Ruff linting
- Any type usage check (disallows `Any` type)
- Pyright type checking

The hook will block commits with issues. To test manually:

```bash
make githook
```

## Authentication Setup

To use sheetbridge, you need a Google Cloud service account:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Sheets API
4. Enable the Google Drive API (optional, for some operations)
5. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Grant it "Editor" role on your spreadsheets
6. Create a service account key:
   - Click on the service account
   - Go to "Keys" tab
   - Click "Add Key" > "Create New Key"
   - Download as JSON
7. Share your spreadsheet with the service account email

## Tech Stack

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Language** | Python 3.13+ | Type hints throughout |
| **Package Manager** | uv | Fast, modern |
| **Sheets API** | gspread | Python wrapper for Google Sheets API |
| **Authentication** | google-auth | Service account authentication |
| **Data Manipulation** | pandas | DataFrame operations |
| **Testing** | pytest | 96%+ coverage enforced |
| **Linting** | ruff | Fast formatter + linter |
| **Type Checking** | pyright | Static analysis |

## API Reference

### SheetsClient

Main client for authentication and spreadsheet access.

**Methods:**
- `__init__(credentials_path, scopes=None)` - Initialize client
- `open_spreadsheet(spreadsheet_id)` - Open spreadsheet by ID
- `open_spreadsheet_by_title(title)` - Open spreadsheet by title
- `get_worksheet(spreadsheet_id, worksheet_title)` - Get worksheet

### DataFrame Functions

- `worksheet_to_dataframe(worksheet)` - Convert worksheet to DataFrame
- `dataframe_to_worksheet(df, worksheet)` - Write DataFrame to worksheet
- `append_dataframe_rows(df, worksheet)` - Append DataFrame rows
- `filter_dataframe_to_worksheet(df, worksheet)` - Filter and update

### Polling Functions

- `create_poller(credentials_path, spreadsheet_id, poll_interval_seconds)` - Create poller
- `SpreadsheetPoller.check_for_changes()` - Check for changes
- `SpreadsheetState` - State container
- `ChangeResult` - Change detection result

## Configuration

### Python Version

Default is Python 3.13. To change:

1. Update `requires-python` in `pyproject.toml`
2. Update `target-version` in `pyproject.toml`
3. Update `.python-version` file
4. Recreate venv: `rm -rf .venv && uv venv`

### Coverage Threshold

Set in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
addopts = ["--cov-fail-under=96"]
```

### Lint Rules

Configure in `pyproject.toml` under `[tool.ruff]`:

```toml
[tool.ruff]
line-length = 100
target-version = "py313"
```

## CI/CD

GitHub Actions runs on every push to main and on pull requests:
- **Lint job**: Runs ruff and pyright
- **Tests job**: Runs pytest with coverage

View pipeline status in the Actions tab of the repository.

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `pytest`
5. Run linting: `make lint`
6. Commit with conventional commits
7. Push and create a pull request

## License

MIT License - see LICENSE file for details

## Credits

Created by Josh Wren

## Related

- [gspread Documentation](https://docs.gspread.org/)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [pandas Documentation](https://pandas.pydata.org/docs/)
