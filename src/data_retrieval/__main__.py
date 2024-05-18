import argparse
import os
from typing import Optional

from azure_blob_utils import load_env_vars, upload_stream
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
parser_cds.add_argument(
    "--local", help="Local directory path to save files", type=str
)
parser_cds.add_argument(
    "--upload",
    help="Flag to upload data to cloud instead of saving locally",
    action="store_true",
)

parser_mars.add_argument(
    "iso",
    help="Country ISO code. See docs for the list of supported countries",
)
parser_mars.add_argument(
    "--local", help="Local directory path to save files", type=str
)
parser_mars.add_argument(
    "--upload",
    help="Flag to upload data to cloud instead of saving locally",
    action="store_true",
)


def get_cds_ecmwf(local_path: Optional[str] = None, upload: bool = False):
    logger.info("Downloading Copernicus CDS data of ECMWF global forecast...")

    # Define parameters 1981 to 2024 or 1982 to test
    available_years = list(range(1981, 2024))
    months = list(range(1, 13))
    leadtime_months = list(range(1, 7))

    # Default path if no local_path is provided and not uploading
    if not local_path and not upload:
        local_path = os.path.expanduser("~/Downloads/ecmwf_global_forecast")

    if local_path:
        # Local download
        file_name = "ecmwf_forecast_global_all_years.grib"
        setup_output_path(local_path)
        download_ecmwf_cds(
            available_years, months, leadtime_months, local_path, file_name
        )
    elif upload:
        sas_token, container_name, storage_account = load_env_vars()
        # Upload to cloud, handle the stream
        data_stream = download_ecmwf_cds(
            available_years, months, leadtime_months
        )
        blob_path = (
            "/raw/glb/ecmwf/ecmwf-monthly-seasonalforecast-1981-2023.grib"
        )
        upload_stream(
            sas_token, container_name, storage_account, data_stream, blob_path
        )
    else:
        logger.error(
            "No valid operation specified. Please provide a local path or set upload to True."  # noqa: E501
        )


def get_cds_era5(local_path: Optional[str] = None, upload: bool = False):
    logger.info(
        "Downloading Copernicus CDS data of ERA5 total precipitation.."
    )
    file_name = "era5_total_precipitation_global_1981_2023_all_months.grib"

    # Define the years and months for the single request
    years = list(range(1981, 2024))
    months = list(range(1, 13))

    # Default path if no local_path is provided and not uploading
    if not local_path and not upload:
        local_path = os.path.expanduser("~/Downloads/era5_global_data")

    if local_path and not upload:
        # Download data to a local path
        setup_output_path(local_path)
        download_era5_cds(years, months, file_name, download_path=local_path)
    elif upload and not local_path:
        sas_token, container_name, storage_account = load_env_vars()
        # Download data into memory and upload to cloud
        data_stream = download_era5_cds(years, months, file_name)
        blob_path = "/raw/glb/era5/era5-total-precipitation-1981-2023.grib"
        upload_stream(
            sas_token, container_name, storage_account, data_stream, blob_path
        )
    else:
        logger.error(
            "No valid operation specified. Please provide a local path or set upload to True."  # noqa: E501
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


def get_mars(iso: str, local_path: Optional[str] = None, upload: bool = False):
    logger.info(f"Retrieving data for ISO code: {iso}")
    static_df = get_country_bbox_df()
    country_df = static_df[static_df["iso"].isin([iso.upper()])]

    if country_df.empty:
        logger.error(
            f"{iso} is not a valid ISO code. Please refer to the supported countries list."  # noqa: E501
        )
        return

    if len(country_df) > 1:
        logger.error("Internal error: multiple entries for the same ISO code!")
        return

    country_name = country_df.iloc[0]["name_en"]
    country_bbox = country_df.iloc[0]["bbox"]
    logger.info(f"Downloading ECMWF MARS data for {country_name}...")

    # Default path if no local_path is provided and not uploading
    if not local_path and not upload:
        local_path = os.path.expanduser(
            f"~/Downloads/mars_{country_name.replace(' ', '_').lower()}_forecast"  # noqa: E501
        )

    # Defining the period of years to download 1981 to 2023 or 1982 to test
    years = list(range(1981, 2023))

    if local_path and not upload:
        setup_output_path(local_path)
        for year in years:
            file_name = f"{country_name.replace(' ', '_').lower()}_ecmwf_hres_seas5_{year}.grib"  # noqa: E501
            download_ecmwf_mars(
                year,
                country_bbox,
                download_path=local_path,
                file_name=file_name,
            )
    elif upload and not local_path:
        sas_token, container_name, storage_account = load_env_vars()
        # List to hold data streams if uploading
        data_streams = []
        for year in years:
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
    else:
        logger.error(
            "Invalid configuration. Use either --local [path], --upload, or none to use the default path."  # noqa: E501
        )


if __name__ == "__main__":
    args = parser.parse_args()

    if args.command == "cds":
        if args.type == "ecmwf":
            get_cds_ecmwf(local_path=args.local, upload=args.upload)
        elif args.type == "era5":
            get_cds_era5(local_path=args.local, upload=args.upload)

    elif args.command == "mars":
        get_mars(args.iso, local_path=args.local, upload=args.upload)
