import argparse
from io import BytesIO
from typing import List

import pandas as pd
from azure_blob_utils import load_env_vars, upload_stream
from cds.ecmwf import download_ecmwf_cds
from cds.era5 import download_era5_cds
from cds.mars import download_ecmwf_mars, get_country_bbox_df
from util import get_logger

sas_token, container_name, storage_account = load_env_vars()

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
    blob_path = "/raw/glb/ecmwf/ecmwf-monthly-seasonalforecast-1981-2023.grib"

    # Utilizing the specific range of available years you've provided
    # Updated to include 1981 through 2023
    available_years: List[int] = list(range(1981, 2023))

    months: List[int] = list(range(1, 13))

    # Adjusting for all available lead times
    # Assuming these are all the lead times available
    leadtime_months: List[int] = list(range(1, 7))

    # Download all years, months, and leadtime months
    data_stream = download_ecmwf_cds(available_years, months, leadtime_months)
    upload_stream(
        sas_token, container_name, storage_account, data_stream, blob_path
    )


def get_cds_era5():
    logger.info(
        "Downloading Copernicus CDS data of ERA5 total precipitation.."
    )
    file_name: str = (
        "era5_total_precipitation_global_1981_2023_all_months.grib"
    )
    blob_path = "/raw/glb/era5/era5-total-precipitation-1981-2023.grib"

    # Define the years and months for the single request
    years: List[int] = list(range(1981, 2024))
    months: List[int] = list(range(1, 13))

    # Download the data for the entire globe with a single request
    data_stream = download_era5_cds(years, months, file_name)

    # Define the blob path for upload

    # Upload the data to the cloud
    upload_stream(
        sas_token, container_name, storage_account, data_stream, blob_path
    )


def upload_to_cloud(
    data_streams,
    sas_token,
    container_name,
    storage_account,
    country_name,
    years,
):
    for year, data_stream in zip(years, data_streams):

        filename = (
            f"{country_name.lower().replace(' ', '_')}_forecast_{year}.grib"
        )
        blob_path = f"/raw/{country_name}/mars/{filename}"

        upload_stream(
            sas_token, container_name, storage_account, data_stream, blob_path
        )


def get_mars(iso: str):
    logger.info(f"Retrieving data for ISO code: {iso}")
    static_df: pd.DataFrame = get_country_bbox_df()
    country_df: pd.DataFrame = static_df[static_df["iso"].isin([iso.upper()])]

    if country_df.empty:
        error_msg = (
            f"{iso} is not a valid ISO code. "
            "Please refer to the supported countries list."
        )
        logger.error(error_msg)
        return

    if len(country_df) > 1:
        error_msg = "Internal error: multiple entries for the same ISO code!"
        logger.error(error_msg)
        return

    country_name: str = country_df.iloc[0]["name_en"]
    country_bbox: str = country_df.iloc[0]["bbox"]

    logger.info(f"Downloading ECMWF MARS data for {country_name}...")

    # Defining the period of years to download
    years: List[int] = list(range(1981, 1983))

    # List to hold data streams
    data_streams: List[BytesIO] = []

    for year in years:
        logger.info(f"Processing data for the year: {year}")
        data_stream = download_ecmwf_mars(year, country_bbox)
        data_streams.append(data_stream)

    upload_to_cloud(
        data_streams,
        sas_token,
        container_name,
        storage_account,
        country_name,
        years,
    )

    return data_streams


if __name__ == "__main__":
    args = parser.parse_args()

    if args.command == "cds":
        if args.type == "ecmwf":
            get_cds_ecmwf()

        elif args.type == "era5":
            get_cds_era5()

    elif args.command == "mars":
        get_mars(args.iso)
