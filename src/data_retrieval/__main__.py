import argparse
import os
from typing import List

from cds.ecmwf import download_ecmwf_cds
from cds.era5 import download_era5_cds
from cds.mars import download_ecmwf_mars
from util import get_logger, setup_output_path

logger = get_logger(__name__)


parser = argparse.ArgumentParser(
    description="Download data from ECMWF MARS and Copernicus CDS"
)
subparsers = parser.add_subparsers(
    dest="command", required=True, help="Data stores"
)

parser_cds = subparsers.add_parser("cds", help="Copernicus CDS")
parser_mars = subparsers.add_parser("mars", help="ECMWF MARS")

parser_cds.add_argument("type", choices=["ecmwf", "era5"], help="Data types")


def get_cds_ecmwf():
    logger.info("Downloading Copernicus CDS data of ECMWF global forecast..")
    file_name: str = "ecmwf_forecast_global_all_years.grib"
    output_path: str = os.path.expanduser("~/Downloads/ECMWF_Global_Forecast")
    setup_output_path(output_path)

    # Utilizing the specific range of available years you've provided
    # Updated to include 1981 through 2023
    available_years: List[int] = list(range(1981, 2024))

    months: List[int] = list(range(1, 13))

    # Adjusting for all available lead times
    # Assuming these are all the lead times available
    leadtime_months: List[int] = list(range(1, 7))

    # Download all years, months, and leadtime months
    download_ecmwf_cds(
        available_years, months, leadtime_months, output_path, file_name
    )


def get_cds_era5():
    logger.info(
        "Downloading Copernicus CDS data of ERA5 total precipitation.."
    )
    file_name: str = (
        "ERA5_total_precipitation_global_1981_2023_all_months.grib"
    )
    output_path: str = os.path.expanduser("~/Downloads/ERA5_Global_Data")
    setup_output_path(output_path)

    # Define the years and months for the single request
    # From 1981 to 2023 try extra 2024 next time
    years: List[int] = list(range(1981, 2024))

    # All months
    months: List[int] = list(range(1, 13))

    # Download the data for the entire globe with a single request
    download_era5_cds(years, months, output_path, file_name)


def get_mars():
    logger.info("Downloading ECMWF MARS data of Chad forecast..")
    output_path: str = os.path.expanduser("~/Downloads/MARS_Chad_Forecast")
    setup_output_path(output_path)

    # see the example in notebooks/bounding-box-chad.ipynb
    # on how to get the bounding box value
    chad_bbox: str = "23.6/13.4/7.3/24.1"

    logger.info(output_path)
    logger.info(chad_bbox)

    years: List[int] = list(range(1981, 2023))

    for year in years:
        file_name: str = f"chad_ecmwf_hres_seas5_{year}.grib"
        download_ecmwf_mars(year, output_path, file_name, chad_bbox)


if __name__ == "__main__":
    args = parser.parse_args()
    print(args)

    if args.command == "cds":
        if args.type == "ecmwf":
            get_cds_ecmwf()

        elif args.type == "era5":
            get_cds_era5()

    elif args.command == "mars":
        get_mars()
