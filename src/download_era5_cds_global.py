import os
from typing import List

from data_retrieval.cds.era5 import download_era5_cds
from data_retrieval.util import setup_output_path

OUTPUT_PATH: str = "~/Downloads/ERA5_Global_Data"


if __name__ == "__main__":
    file_name: str = (
        "ERA5_total_precipitation_global_1981_2023_all_months.grib"
    )
    output_path: str = os.path.expanduser(OUTPUT_PATH)
    setup_output_path(output_path)

    # Define the years and months for the single request
    # From 1981 to 2023 try extra 2024 next time
    years: List[int] = list(range(1981, 2024))

    # All months
    months: List[int] = list(range(1, 13))

    # Download the data for the entire globe with a single request
    download_era5_cds(years, months, output_path, file_name)
