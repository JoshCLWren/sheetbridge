# Repository Guidelines

## Project Overview
sheetbridge is a Python library that provides a convenient bridge between Google Sheets and Python applications. It wraps `gspread` with DataFrame synchronization and change detection capabilities, making it easy to read from and write to Google Sheets using pandas DataFrames.

## Project Structure & Module Organization
The main package code lives in the `sheetbridge` directory with the following modules:
- `__init__.py` - Package exports and version
- `client.py` - SheetsClient for authentication and spreadsheet access
- `dataframe.py` - DataFrame sync operations (read/write/filter/append)
- `polling.py` - Change detection and polling functionality

Tooling metadata (`pyproject.toml`, `uv.lock`) defines project dependencies. Tests are in the `tests/` directory with mirrored structure.

## Build, Test, and Development Commands
- `source .venv/bin/activate`: activate the virtual environment (do this once per session).
- `uv sync --all-extras`: install dependencies via uv (including dev and drive extras).
- `pytest`: run tests.
- `make pytest`: run the test suite with coverage.
- `make lint`: run ruff and pyright type checking.

## Getting Started
When working on sheetbridge:
1. Run `uv sync --all-extras` to install all dependencies
2. Run `source .venv/bin/activate` to activate the virtual environment
3. Review the code in `sheetbridge/` to understand the architecture
4. Run `pytest` to verify all tests pass
5. Make your changes and run `make lint` before committing

## Git Worktrees (Parallel Work)
Use git worktrees to work on multiple features in parallel without branch conflicts:
- Create a branch per feature: `git switch -c feature/short-description`
- Add a worktree: `git worktree add ../sheetbridge-<slug> feature/short-description`
- Work only in that worktree for the feature; run tests there.
- Keep the branch updated: `git fetch` then `git rebase origin/main` (or merge).
- When merged, remove it: `git worktree remove ../sheetbridge-<slug>`
- Clean stale refs: `git worktree prune`
- WIP limit: 3 features total in progress across all worktrees.

## Test Coverage Requirements
- Current target: 96% coverage threshold (configured in `pyproject.toml`)
- Always run `pytest --cov=sheetbridge --cov-report=term-missing` to check missing coverage
- When touching logic or input handling, ensure tests are added to maintain coverage
- Strategies for increasing coverage:
  - Add tests for error handling paths (e.g., invalid credentials, network failures)
  - Add tests for edge cases in DataFrame operations (empty DataFrames, NaN values)
  - Add tests for polling edge cases (rapid changes, large spreadsheets)
  - Add integration tests with mock Google Sheets responses

## Coding Style & Naming Conventions
Follow standard PEP 8 spacing (4 spaces, 100-character soft wrap) and favor descriptive snake_case for functions and variables. The codebase uses:
- Type hints throughout (no `Any` types allowed)
- Dataclasses for typed data containers (e.g., `SpreadsheetState`, `ChangeResult`)
- Async/await for I/O operations where applicable
- Explicit error handling with custom exceptions where appropriate
- Clear function names that describe their purpose (e.g., `worksheet_to_dataframe`)

Ruff configuration (from `pyproject.toml`):
- Line length: 100 characters
- Python version: 3.13
- Enabled rules: E, F, I, N, UP, B, C4, D, ANN401
- Ignored: D203, D213, E501
- Code comments are discouraged - prefer clear code and commit messages

## Pre-commit Hook
A pre-commit hook is installed in `.git/hooks/pre-commit` that automatically runs:
- Check for type/linter ignores in staged files
- Run the shared lint script (`scripts/lint.sh`)

The lint script runs:
- Python compilation check
- Ruff linting
- Any type usage check (ruff ANN401 rule)
- Pyright type checking

The hook will block commits containing `# type: ignore`, `# noqa`, `# ruff: ignore`, or `# pylint: ignore`.

To test the hook manually: `make githook` or `bash scripts/lint.sh`

## Code Quality Standards
- Run linting after each change:
  - `make lint` or `bash scripts/lint.sh`
- Use specific types instead of `Any` in type annotations (ruff ANN401 rule)
- Run tests when you touch logic or input handling:
  - `pytest`
- Always write a regression test when fixing a bug.
- If you break something while fixing it, fix both in the same PR.
- Do not use in-line comments to disable linting or type checks.
- Do not narrate your code with comments; prefer clear code and commit messages.

## Style Guidelines
- Keep helpers explicit and descriptive (snake_case), and annotate public functions with precise types.
- Avoid shell-specific shortcuts; prefer Python APIs and `pathlib.Path` helpers.
- When adding new DataFrame operations, follow existing patterns in `dataframe.py`.
- When adding new polling features, follow existing patterns in `polling.py`.
- Use f-strings for string formatting, not `.format()` or `%`.
- Prefer context managers for resource management (e.g., file handles, connections).

## Branch Workflow
- Always create a feature branch from `main` before making changes:
  - `git checkout -b feature-name`
  - Use descriptive names like `fix-auth-error` or `add-batch-update`
- Push the feature branch to create a pull request
- After your PR is merged, update your local `main`:
  - `git checkout main`
  - `git pull`
  - Delete the merged branch: `git branch -d feature-name`

## Testing Guidelines
- Automated tests live in `tests/` and run with `python -m pytest` (or `make pytest`).
- When adding tests, keep `pytest` naming like `test_worksheet_to_dataframe`.
- Always use appropriate fixtures from `conftest.py` for testing dependencies.
- Mock external API calls (gspread, Google Sheets API) to avoid hitting rate limits.
- Use parametrized tests for testing multiple scenarios with similar logic.
- Test error conditions: invalid credentials, missing worksheets, malformed data.

## Testing Specifics for sheetbridge
- **Client tests**: Mock gspread.authorize and test authentication flows
- **DataFrame tests**: Use sample DataFrames to test round-trip operations
- **Polling tests**: Mock time.sleep for interval testing, simulate spreadsheet changes
- **Integration tests**: Test full workflows from client init to data sync
- Always clean up test resources (close connections, delete temporary files)

## Commit & Pull Request Guidelines
- Use imperative, component-scoped commit messages (e.g., "Add batch update support for DataFrames")
- Bundle related changes per commit
- PR summary should describe user impact and testing performed
- For new features, include usage examples in the PR description
- For bug fixes, include reproduction steps and verification
- When changing public API, update relevant docstrings and README examples

## Architecture Patterns
- **Authentication**: Service account credentials via google-auth, wrapped in SheetsClient
- **Data Access**: All Google Sheets operations go through gspread library
- **DataFrame Sync**: Two-way sync between pandas DataFrames and Google Sheets worksheets
- **Change Detection**: Stateful polling with diff detection for spreadsheet changes
- **Error Handling**: Explicit exceptions for API errors, auth failures, and data validation

## Dependencies
- **gspread**: Python wrapper for Google Sheets API
- **google-auth**: Service account authentication
- **pandas**: DataFrame operations and data manipulation
- **pytest**: Testing framework
- **ruff**: Linting and formatting
- **pyright**: Static type checking

## Release Notes
- Maintain CHANGELOG.md with each release
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Document breaking changes in release notes
- Include migration guides for major version bumps
