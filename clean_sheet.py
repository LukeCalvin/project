import gspread
import pandas as pd
from google.auth import default

COLNAME_REPLACEMENTS = {" ": "_", "/": "", "#": "no", "__": "_"}
# last two are temporary, need to ask what X and blank mean
VALUE_REPLACEMENTS = {"Not Started": False, "Done": True, "In Process": False, "X": 1.25, "": 1.25}


def clean_data(circuit):
    credentials, _ = default(scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.Client(auth=credentials)

    url = "https://docs.google.com/spreadsheets/d/1M__pvslmhMRkXCl-7DEPc0PzvKj6qlgfc8antAd9hgI/edit#gid=223128104"
    # sandbox_url = "https://docs.google.com/spreadsheets/d/1Mab3WIIMxUuFdjzayu1kYBbeIf_-fsLI89vgx9GPKho/edit#gid=223128104
    HEADER_RANGE = "A11:U11"

    wb = client.open_by_url(url)
    first_circuit = wb.worksheet(circuit)

    # Step 1: bring in the data & clean up

    colnames = first_circuit.get_values(HEADER_RANGE)

    colnames = colnames[0]

    raw = pd.DataFrame(
        first_circuit.get_values(
            "A14:T700",
        ),
        columns=colnames[:-1],
    )

    for start, replacement in COLNAME_REPLACEMENTS.items():
        munged_columns = [x.lower().replace(start, replacement) for x in raw.columns]
    raw.columns = munged_columns
    raw = raw.rename(columns={"squirt_boom": "requires_squirt_boom", "status": "is_complete"}).astype(
        {"requires_squirt_boom": bool}
    )

    data = raw.loc[
        :,
        [
            "full_address",
            "projected_hours",
            "requires_squirt_boom",
            "status",
        ],
    ].astype({"requires_squirt_boom": int})
    data = {data.replace(start, replacement) for start, replacement in VALUE_REPLACEMENTS.items()}
    orig_data = (
        raw.loc[
            :,
            [
                "site_no",
                "address",
                "work_description",
                "owner_phone_comments",
                "no_parks",
                "nbw",
                "projected_hours",
                "flagging",
                "requires_squirt_boom",
                "merge",
                "notes",
                "also_clear_for",
                "status",
            ],
        ]
        .replace("Not Started", False)
        .replace("Done", True)
        .replace("In Process", False)
        .replace("Hold/ Change in Contract", True)
    )

    data = data[~data["status"]]  # changes data to only sites that aren't completed
    orig_data = orig_data[~orig_data["status"]]
    return data, orig_data
