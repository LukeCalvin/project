import pandas as pd
from gspread import Worksheet

def validate_sheet(sheet: Worksheet) -> None:
    # Check if the header row is where we expect it to be

    # Check if the columns we expect to exist are there

    # Check if the order is as expected

    # Spot check critical columns to see if values are what we think they are
