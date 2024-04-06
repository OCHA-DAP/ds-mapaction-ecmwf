from typing import Any, Dict

import cdsapi
import pandas as pd
from ecmwfapi import ECMWFService


def get_dates(year: int) -> str:
    start_date = pd.to_datetime(f"{year}-01-01")
    end_date = pd.to_datetime(f"{year}-12-01")

    # Generate a sequence of monthly dates
    date_range = pd.date_range(start=start_date, end=end_date, freq="MS")

    # Convert the date range to a list of formatted strings
    date_strings = (
        date_range.to_series()
        .apply(lambda date: date.strftime("%Y-%m-%d"))
        .to_list()
    )

    # Join the list of formatted strings into a single string with "/"
    dates: str = "/".join(date_strings)

    return dates


def download_cds(name: str, metadata: Dict[str, Any], file_path: str):
    client = cdsapi.Client()

    client.retrieve(
        name,
        metadata,
        file_path,
    )

    print(f"Downloaded: {file_path}")


def download_mars(metadata: Dict[str, Any], file_path: str):
    server = ECMWFService("mars")

    server.execute(
        metadata,
        file_path,
    )

    print(f"Downloaded: {file_path}")
