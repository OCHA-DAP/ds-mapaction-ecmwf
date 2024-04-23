import argparse
import os
from typing import List

import pandas as pd
from cds.ecmwf import download_ecmwf_cds
from cds.era5 import download_era5_cds
from cds.mars import download_ecmwf_mars, get_country_bbox_df
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
parser_mars.add_argument(
    "iso",
    help="Country ISO code. See docs for the list of supported countries",
)


def get_cds_ecmwf():
    logger.info("Downloading Copernicus CDS data of ECMWF global forecast..")
    file_name: str = "ecmwf_forecast_global_all_years.grib"
    output_path: str = os.path.expanduser("~/Downloads/ecmwf_global_forecast")
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
        "era5_total_precipitation_global_1981_2023_all_months.grib"
    )
    output_path: str = os.path.expanduser("~/Downloads/era5_global_data")
    setup_output_path(output_path)

    # Define the years and months for the single request
    # From 1981 to 2023 try extra 2024 next time
    years: List[int] = list(range(1981, 2024))

    # All months
    months: List[int] = list(range(1, 13))

    # Download the data for the entire globe with a single request
    download_era5_cds(years, months, output_path, file_name)


def get_mars(iso: str):
    static_df: pd.DataFrame = get_country_bbox_df()
    country_df: pd.DataFrame = static_df[static_df["iso"].isin([iso.upper()])]

    if country_df.empty:
        logger.error(
            f"{iso} is not a valid ISO code. See the docs for the list supported counbtries"  # noqa: E501
        )
        return

    if len(country_df) > 1:
        logger.error(
            "Internal Error: multiple countries selected by same ISO!"
        )
        return

    country_name: str = country_df.iloc[0]["name_en"]
    country_path_name: str = country_name.replace(" ", "_").lower()
    country_bbox: str = country_df.iloc[0]["bbox"]

    logger.info(f"Downloading ECMWF MARS data of {country_name} forecast..")
    output_path: str = os.path.expanduser(
        f"~/Downloads/mars_{country_path_name}_forecast"
    )
    setup_output_path(output_path)

    years: List[int] = list(range(1981, 2023))

    for year in years:
        file_name: str = f"{country_path_name}_ecmwf_hres_seas5_{year}.grib"
        print(file_name)
        download_ecmwf_mars(year, output_path, file_name, country_bbox)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.command == "cds":
        if args.type == "ecmwf":
            get_cds_ecmwf()

        elif args.type == "era5":
            get_cds_era5()

    elif args.command == "mars":
        get_mars(args.iso)
