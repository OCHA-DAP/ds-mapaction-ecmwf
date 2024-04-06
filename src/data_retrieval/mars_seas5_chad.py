import os

from cds.mars import download_ecmwf_mars
from util import setup_output_path

OUTPUT_PATH: str = "~/Downloads/MARS_Chad_Forecast"

# see the example in notebooks/bounding-box-chad.ipynb
# on how to get the bounding box value
CHAD_BOUNDING_BOX: str = "23.6/13.4/7.3/24.1"


if __name__ == "__main__":
    year: int = 2022
    file_name: str = "chad_ecmwf_hres_seas5_{year}.grib"

    output_path: str = os.path.expanduser(OUTPUT_PATH)
    setup_output_path(output_path)

    download_ecmwf_mars(year, output_path, file_name, CHAD_BOUNDING_BOX)
