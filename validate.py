import pandas as pd
from gspread import Worksheet

HEADER_RANGE = 'A11:T11'

def validate_sheet(sheet: Worksheet) -> None:
    pass
    # Check if the header row is where we expect it to be
    error_msg = validate_header(sheet,HEADER_RANGE)
    if error_msg is not None:
        raise ValueError(error_msg)

    # Check if the columns we expect to exist are there

    # Check if the order is as expected

    # Spot check critical columns to see if values are what we think they are

def validate_header(sheet: Worksheet, cell_range: str) -> str | None:
    """
    :param Worksheet: a gspread worksheet object containing one circuit of tasks
    :param cell_range: the A-notation range of where the header should be
    
    Return a string with missing columns, if they exist

    Only a subset of hard-coded expected columns; could be expanded.
    """
    
#     get_values returns a list of lists, which is a list of the values in each row. 
    expected_header = sheet.get_values(cell_range)[0]
    missing_column_names = []
    for expected_column in ['PROJECTED HOURS','SQUIRT BOOM', 'Full Address']:
        if expected_column not in expected_header:
            print(f"{expected_column} not in the header range")
            if expected_column.lower() not in [header_val.lower() for header_val in expected_header]:
                missing_column_names.append(expected_column)
    if missing_column_names != []:
        return f"{missing_column_names} not in the header range, even in constant case"
