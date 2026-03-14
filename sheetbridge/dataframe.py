"""DataFrame sync utilities for Google Sheets worksheets."""

import gspread
import pandas as pd


def worksheet_to_dataframe(worksheet: gspread.Worksheet) -> pd.DataFrame:
    """Convert a worksheet to a pandas DataFrame.

    Args:
        worksheet: gspread Worksheet object.

    Returns:
        DataFrame with worksheet data. First row is used as column names.
    """
    records = worksheet.get_all_records()
    return pd.DataFrame(records)


def dataframe_to_worksheet(
    worksheet: gspread.Worksheet,
    df: pd.DataFrame,
    include_index: bool = False,
) -> None:
    """Write a DataFrame to a worksheet, replacing all content.

    Args:
        worksheet: gspread Worksheet object to write to.
        df: pandas DataFrame to write.
        include_index: Whether to include the DataFrame index as first column.
    """
    # Prepare data with headers
    data = [df.columns.tolist()]
    if include_index:
        data = [[""] + df.columns.tolist()]
        for idx, row in df.iterrows():
            data.append([str(idx)] + row.tolist())
    else:
        data = [df.columns.tolist()]
        for row in df.itertuples(index=False, name=None):
            data.append(list(row))

    # Clear existing content
    worksheet.clear()

    # Write new content
    worksheet.update(
        data,
        raw=False,
    )


def append_dataframe_rows(
    worksheet: gspread.Worksheet,
    df: pd.DataFrame,
    include_header: bool = False,
) -> None:
    """Append DataFrame rows to the end of a worksheet.

    Args:
        worksheet: gspread Worksheet object.
        df: pandas DataFrame rows to append.
        include_header: Whether to include column headers (for empty worksheet).
    """
    data = []

    if include_header:
        data.append(df.columns.tolist())

    for row in df.itertuples(index=False, name=None):
        data.append(list(row))

    worksheet.append_rows(data, value_input_option="USER_ENTERED")


def filter_dataframe_to_worksheet(
    worksheet: gspread.Worksheet,
    df: pd.DataFrame,
    query_col: str,
    query_val: str,
) -> pd.DataFrame:
    """Filter a DataFrame by a column value and write filtered results.

    Args:
        worksheet: gspread Worksheet to write filtered data to.
        df: pandas DataFrame to filter.
        query_col: Column name to filter on.
        query_val: Value to match.

    Returns:
        Filtered DataFrame.
    """
    filtered = df[df[query_col] == query_val]
    dataframe_to_worksheet(worksheet, filtered, include_index=False)
    return filtered
