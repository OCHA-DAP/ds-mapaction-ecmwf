import os
from typing import List

from data_retrieval.cds.mars import download_ecmwf_mars
from data_retrieval.util import setup_output_path

OUTPUT_PATH: str = "~/Downloads/MARS_Chad_Forecast"

# see the example in notebooks/bounding-box-chad.ipynb
# on how to get the bounding box value
CHAD_BOUNDING_BOX: str = "23.6/13.4/7.3/24.1"


if __name__ == "__main__":
    output_path: str = os.path.expanduser(OUTPUT_PATH)
    setup_output_path(output_path)

    years: List[int] = list(range(1981, 2023))

    for year in years:
        file_name: str = f"chad_ecmwf_hres_seas5_{year}.grib"
        download_ecmwf_mars(year, output_path, file_name, CHAD_BOUNDING_BOX)
