import pandas as pd
import numpy as np
from gspread import Worksheet

HEADER_RANGE = "A11:T11"
END_ROW = "299"
START_ROW = "14"

class SheetAssumptionViolated(Exception):
    pass

def validate_sheet(sheet: Worksheet) -> None:
    # Worksheet is passed in as an arg
    # Check if the header row is where we expect it to be
    header_row = get_header_row(sheet, HEADER_RANGE)

    header_error_msg = validate_header(header_row) 
    if header_error_msg is not None:
       raise SheetAssumptionViolated(header_error_msg)

    order_error_msg = validate_order(header_row)
    if order_error_msg is not None:
        raise SheetAssumptionViolated(order_error_msg)
    
    col_val_error_msg = validate_col_val(sheet)
    if col_val_error_msg is not None:
        raise SheetAssumptionViolated(col_val_error_msg)
    # Check if the columns we expect to exist are there

    # Check if the order is as expected

    # Spot check critical columns to see if values are what we think they are

def get_header_row(sheet:Worksheet, cell_range) -> str:
    return sheet.get_values(cell_range)[0]

def validate_header(expected_header) -> str | None:
    """
    :param Worksheet: a gspread worksheet object containing one circuit of tasks
    :param cell_range: the A-notation range of where the header should be

    Return a string with missing columns, if they exist

    Only a subset of hard-coded expected columns; could be expanded.
    """

    #     get_values returns a list of lists, which is a list of the values in each row.
    missing_column_names = []
    for expected_column in ["STATUS", "PROJECTED HOURS", "SQUIRT BOOM", "Full Address"]:
        if expected_column not in expected_header:
            print(f"{expected_column} not in the header range")
        if expected_column.lower() not in [header_val.lower() for header_val in expected_header]:
            missing_column_names.append(expected_column)
    if missing_column_names != []:
        return f"{missing_column_names} not in the header range, even in constant case"
    
def validate_order(header_row) -> str:
   status = header_row[0]
   full_address = header_row[3]
   projected_hours = header_row[9]
   squirt_boom = header_row[13]
   columns =[status, full_address, projected_hours, squirt_boom]
   expected_column_names = ["STATUS", "Full Address", "PROJECTED HOURS", "SQUIRT BOOM"]
   if expected_column_names != columns:
       return "Columns out of order"

def validate_col_val(sheet: Worksheet)-> str:
    #spot check critical columns, maybe add full_address later

    status_col_unjoined = sheet.get_values("A"+START_ROW+":""A"+END_ROW)
    projected_hours_col_unjoined = sheet.get_values("J"+START_ROW+":""J"+END_ROW)
    status_column = []
    for item in status_col_unjoined:
        status_column.append(item[0])
    projected_hours = []
    for item in projected_hours_col_unjoined:
        projected_hours.append(item[0])

    status_bad_cells = []
    projected_hours_bad_cells = []

    for count, val in enumerate(status_column, 14):
        if val not in ['Done', 'Not Started', 'In Process']:
            status_bad_cells.append('A'+str(count))

    for count, val in enumerate(projected_hours, 14):
        try: 
            val = float(val)
            if val>20 or val==0:
                projected_hours_bad_cells.append('J'+str(count))
        except ValueError:
            projected_hours_bad_cells.append('J'+str(count))

    all_bad_cells = [status_bad_cells, projected_hours_bad_cells]
    if all_bad_cells != [[],[]]:
        return f"Unexpected values in {all_bad_cells}"