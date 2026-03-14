"""Change detection utilities for Google Sheets."""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime

import gspread


@dataclass
class SpreadsheetState:
    """Represents the state of a spreadsheet for change detection.

    Attributes:
        spreadsheet_id: Google Sheets ID.
        revision_id: Last known revision ID (if available).
        checksum: Hash of worksheet data for change detection.
        modified_time: ISO timestamp of last modification.
        checked_at: When this state was last checked.
    """

    spreadsheet_id: str
    revision_id: str | None = None
    checksum: str | None = None
    modified_time: str | None = None
    checked_at: str | None = None


@dataclass
class ChangeResult:
    """Result of a change detection check.

    Attributes:
        has_changed: Whether the spreadsheet has changed since last check.
        old_state: Previous state (if any).
        new_state: Current state.
        changes: List of worksheet titles that changed.
    """

    has_changed: bool
    old_state: SpreadsheetState | None
    new_state: SpreadsheetState
    changes: list[str] = field(default_factory=list)


class SpreadsheetPoller:
    """Polls Google Sheets for changes using multiple detection methods.

    Supports detection via:
    - Drive API modifiedTime
    - Worksheet data checksums
    - Revision IDs (if available)
    """

    def __init__(self, client: gspread.Client) -> None:
        """Initialize poller with gspread client.

        Args:
            client: Authenticated gspread client.
        """
        self.client = client
        self._states: dict[str, SpreadsheetState] = {}

    def calculate_checksum(self, spreadsheet: gspread.Spreadsheet) -> str:
        """Calculate checksum of all worksheet data.

        Args:
            spreadsheet: gspread Spreadsheet object.

        Returns:
            SHA256 hash of all worksheet data.
        """
        data = []
        for worksheet in spreadsheet.worksheets():
            records = worksheet.get_all_records()
            data.append(
                {
                    "title": worksheet.title,
                    "rows": len(records),
                    "hash": hashlib.sha256(
                        json.dumps(records, sort_keys=True).encode()
                    ).hexdigest()[:16],
                }
            )

        combined = json.dumps(data, sort_keys=True)
        return hashlib.sha256(combined.encode()).hexdigest()

    def get_modified_time(self, spreadsheet: gspread.Spreadsheet) -> str | None:
        """Get last modified time from Drive API.

        Args:
            spreadsheet: gspread Spreadsheet object.

        Returns:
            ISO timestamp of last modification, or None if unavailable.
        """
        try:
            from googleapiclient.discovery import build  # type: ignore[import]

            creds = self.client.auth  # type: ignore[attr-defined]
            drive_service = build("drive", "v3", credentials=creds)
            drive_file = (
                drive_service.files().get(fileId=spreadsheet.id, fields="modifiedTime").execute()
            )
            return drive_file.get("modifiedTime")
        except Exception:
            return None

    def register(
        self,
        spreadsheet_id: str,
        state: SpreadsheetState | None = None,
    ) -> SpreadsheetState:
        """Register a spreadsheet for polling.

        Args:
            spreadsheet_id: Google Sheets ID.
            state: Initial state (optional, will be fetched if not provided).

        Returns:
            Current state of the spreadsheet.
        """
        if spreadsheet_id in self._states:
            return self._states[spreadsheet_id]

        if state is None:
            spreadsheet = self.client.open_by_key(spreadsheet_id)
            checksum = self.calculate_checksum(spreadsheet)
            modified_time = self.get_modified_time(spreadsheet)
            state = SpreadsheetState(
                spreadsheet_id=spreadsheet_id,
                checksum=checksum,
                modified_time=modified_time,
                checked_at=datetime.now(UTC).isoformat(),
            )

        self._states[spreadsheet_id] = state
        return state

    def check_for_changes(
        self,
        spreadsheet_id: str,
        use_checksum: bool = True,
        use_modified_time: bool = True,
    ) -> ChangeResult:
        """Check if a spreadsheet has changed since last check.

        Args:
            spreadsheet_id: Google Sheets ID.
            use_checksum: Whether to compare checksums (slower but accurate).
            use_modified_time: Whether to check Drive API modifiedTime.

        Returns:
            ChangeResult with has_changed flag and current state.
        """
        old_state = self._states.get(spreadsheet_id)
        spreadsheet = self.client.open_by_key(spreadsheet_id)

        new_checksum = None
        new_modified_time = None
        changes: list[str] = []

        if use_checksum:
            new_checksum = self.calculate_checksum(spreadsheet)

        if use_modified_time:
            new_modified_time = self.get_modified_time(spreadsheet)

        new_state = SpreadsheetState(
            spreadsheet_id=spreadsheet_id,
            checksum=new_checksum,
            modified_time=new_modified_time,
            checked_at=datetime.now(UTC).isoformat(),
        )

        if old_state is None:
            self._states[spreadsheet_id] = new_state
            return ChangeResult(
                has_changed=True,
                old_state=None,
                new_state=new_state,
                changes=[],
            )

        has_changed = False

        if use_checksum and old_state.checksum != new_checksum:
            has_changed = True
            changes = self._detect_worksheet_changes(spreadsheet, old_state)

        if use_modified_time and old_state.modified_time != new_modified_time and not has_changed:
            has_changed = True

        self._states[spreadsheet_id] = new_state

        return ChangeResult(
            has_changed=has_changed,
            old_state=old_state,
            new_state=new_state,
            changes=changes,
        )

    def _detect_worksheet_changes(
        self,
        spreadsheet: gspread.Spreadsheet,
        old_state: SpreadsheetState,
    ) -> list[str]:
        """Detect which worksheets have changed.

        Args:
            spreadsheet: gspread Spreadsheet object.
            old_state: Previous state with old checksum info.

        Returns:
            List of worksheet titles that changed.
        """
        changed_worksheets: list[str] = []
        for worksheet in spreadsheet.worksheets():
            try:
                records = worksheet.get_all_records()
                current_hash = hashlib.sha256(
                    json.dumps(records, sort_keys=True).encode()
                ).hexdigest()[:16]
                if old_state.checksum:
                    old_hash = old_state.checksum
                    if current_hash not in old_hash:
                        changed_worksheets.append(worksheet.title)
            except Exception:
                changed_worksheets.append(worksheet.title)

        return changed_worksheets

    def get_state(self, spreadsheet_id: str) -> SpreadsheetState | None:
        """Get the current state for a registered spreadsheet.

        Args:
            spreadsheet_id: Google Sheets ID.

        Returns:
            Current state, or None if not registered.
        """
        return self._states.get(spreadsheet_id)

    def clear_state(self, spreadsheet_id: str) -> None:
        """Clear stored state for a spreadsheet.

        Args:
            spreadsheet_id: Google Sheets ID.
        """
        self._states.pop(spreadsheet_id, None)

    def clear_all_states(self) -> None:
        """Clear all stored states."""
        self._states.clear()


def create_poller(credentials_path: str) -> SpreadsheetPoller:
    """Create a SpreadsheetPoller with default authentication.

    Args:
        credentials_path: Path to service account JSON file.

    Returns:
        Configured SpreadsheetPoller instance.
    """
    import gspread
    from google.oauth2.service_account import Credentials

    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(credentials_path, scopes=scopes)
    client = gspread.authorize(creds)
    return SpreadsheetPoller(client)
