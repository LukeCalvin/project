import gspread
import pandas as pd


def clean_data():
    client = gspread.service_account(
        filename="/Users/lukehakso/kemp/project/jobtracker.json"
    )

    url = "https://docs.google.com/spreadsheets/d/1M__pvslmhMRkXCl-7DEPc0PzvKj6qlgfc8antAd9hgI/edit#gid=223128104"
    sandbox_url = "https://docs.google.com/spreadsheets/d/1Mab3WIIMxUuFdjzayu1kYBbeIf_-fsLI89vgx9GPKho/edit#gid=223128104"

    HEADER_RANGE = "A11:T11"

    wb = client.open_by_url(sandbox_url)

    # Step 1: bring in the data & clean up

    first_circuit = wb.get_worksheet_by_id(223128104)

    from gspread import Worksheet

    colnames = first_circuit.get_values(HEADER_RANGE)

    colnames = colnames[0]

    raw = pd.DataFrame(
        first_circuit.get_values(
            "A14:T500",
        ),
        columns=colnames[:-1],
    )

    # list comprehension
    munged_columns = [
        x.lower()
        .replace(" ", "_")
        .replace("/", "")
        .replace("#", "no")
        .replace("__", "_")
        for x in raw.columns
    ]
    raw.columns = munged_columns
    raw = raw.rename(columns={"squirt_boom": "requires_squirt_boom"}).astype(
        {"requires_squirt_boom": bool}
    )

    df = raw.assign(unique_id=range(raw.shape[0]))
    data = df.loc[
        :, ["unique_id", "full_address", "projected_hours", "requires_squirt_boom"]
    ].astype({"requires_squirt_boom": int})
    return data
