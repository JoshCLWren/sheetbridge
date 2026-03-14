"""Google Sheets client with gspread integration."""


import gspread
from google.oauth2.service_account import Credentials


class SheetsClient:
    """Client for interacting with Google Sheets via gspread.

    Wraps gspread authentication and provides methods to open sheets
    and access worksheets.
    """

    def __init__(
        self,
        credentials_path: str,
        scopes: list[str] | None = None,
    ) -> None:
        """Initialize SheetsClient with service account credentials.

        Args:
            credentials_path: Path to service account JSON file.
            scopes: List of OAuth scopes. Defaults to Sheets and Drive APIs.
        """
        if scopes is None:
            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive",
            ]

        self.creds = Credentials.from_service_account_file(
            credentials_path, scopes=scopes
        )
        self.client = gspread.authorize(self.creds)

    def open_spreadsheet(self, spreadsheet_id: str) -> gspread.Spreadsheet:
        """Open a spreadsheet by ID.

        Args:
            spreadsheet_id: Google Sheets ID.

        Returns:
            gspread.Spreadsheet object.
        """
        return self.client.open_by_key(spreadsheet_id)

    def open_spreadsheet_by_title(self, title: str) -> gspread.Spreadsheet:
        """Open a spreadsheet by title.

        Args:
            title: Spreadsheet title.

        Returns:
            gspread.Spreadsheet object.
        """
        return self.client.open(title)

    def get_worksheet(
        self, spreadsheet_id: str, worksheet_title: str
    ) -> gspread.Worksheet:
        """Get a specific worksheet from a spreadsheet.

        Args:
            spreadsheet_id: Google Sheets ID.
            worksheet_title: Worksheet title (sheet name).

        Returns:
            gspread.Worksheet object.
        """
        spreadsheet = self.open_spreadsheet(spreadsheet_id)
        return spreadsheet.worksheet(worksheet_title)
