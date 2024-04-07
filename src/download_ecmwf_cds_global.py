"""ECMWF forecast global CDS"""

import os
from typing import List

from data_retrieval.cds.ecmwf import download_ecmwf_cds
from data_retrieval.util import setup_output_path

OUTPUT_PATH: str = "~/Downloads/ECMWF_Global_Forecast"


if __name__ == "__main__":
    file_name: str = "ecmwf_forecast_global_all_years.grib"
    download_path: str = os.path.expanduser(OUTPUT_PATH)
    setup_output_path(download_path)

    # Utilizing the specific range of available years you've provided
    # Updated to include 1981 through 2023
    available_years: List[int] = list(range(1981, 2024))

    months: List[int] = list(range(1, 13))

    # Adjusting for all available lead times
    # Assuming these are all the lead times available
    leadtime_months: List[int] = list(range(1, 7))

    # Download all years, months, and leadtime months
    download_ecmwf_cds(
        available_years, months, leadtime_months, download_path, file_name
    )
