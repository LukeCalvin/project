import pandas as pd
import numpy as np
from gspread import Worksheet

HEADER_RANGE = "A11:T11"
class SheetAssumptionViolated(Exception):
    pass

def validate_sheet(sheet: Worksheet) -> None:
    # Worksheet is passed in as an arg
    # Check if the header row is where we expect it to be
    error_msg1 = validate_header(sheet, HEADER_RANGE) 
    if error_msg1 is not None:
       raise SheetAssumptionViolated(error_msg1)

    error_msg2 = validate_order(sheet)
    if error_msg2 is not None:
        raise SheetAssumptionViolated(error_msg2)
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
    for expected_column in ["STATUS", "PROJECTED HOURS", "SQUIRT BOOM", "Full Address"]:
        if expected_column not in expected_header:
            print(f"{expected_column} not in the header range")
        if expected_column.lower() not in [header_val.lower() for header_val in expected_header]:
            missing_column_names.append(expected_column)
    if missing_column_names != []:
        return f"{missing_column_names} not in the header range, even in constant case"
    
def validate_order(sheet: Worksheet):
   status = sheet.get_values("A11")
   full_address = sheet.get_values("D11")
   projected_hours = sheet.get_values("J11")
   squirt_boom = sheet.get_values("N11")
   columns = status[0]+full_address[0]+projected_hours[0]+squirt_boom[0]
   expected_column_names = ["STATUS", "Full Address", "PROJECTED HOURS", "SQUIRT BOOM"]
   if expected_column_names != columns:
       return "Columns out of order"

def validate_col_val(sheet: Worksheet, cell_range: str):
    pass