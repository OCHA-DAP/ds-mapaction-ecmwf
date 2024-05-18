import os
import tempfile
from io import BytesIO
from typing import Any, Dict, Optional

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


def download_cds(
    name: str, metadata: Dict[str, Any], file_path: Optional[str] = None
) -> Optional[BytesIO]:  # noqa: E501
    client = cdsapi.Client()

    if file_path:
        # Save directly to the specified path
        client.retrieve(name, metadata, file_path)
        print(f"Downloaded locally: {file_path}")
        return None
    else:
        # Use a temporary file for in-memory operations
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            client.retrieve(name, metadata, tmp.name)
            tmp.seek(0)  # Rewind to read content
            data = BytesIO(tmp.read())

        os.unlink(tmp.name)
        print("Downloaded in memory and ready for further processing")
        return data


def download_mars(
    metadata: Dict[str, Any], file_path: Optional[str] = None
) -> Optional[BytesIO]:  # noqa: E501
    server = ECMWFService("mars")

    if file_path:
        # Download directly to the specified file path
        server.execute(metadata, file_path)
        print(f"Downloaded locally: {file_path}")
        return None
    else:
        # Use a temporary file to handle the
        # download and return a BytesIO object
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            server.execute(metadata, tmp.name)
            tmp.seek(0)  # Rewind the file to read its content
            data = BytesIO(tmp.read())

        os.unlink(tmp.name)  # Delete the temporary file after reading
        data.seek(0)  # Rewind the BytesIO object for further use
        print("Downloaded data to memory")
        return data
