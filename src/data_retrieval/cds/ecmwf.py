import os
from io import BytesIO
from typing import Any, Dict, List, Optional

from .common import download_cds


# Function to create a single API request for the specified years,
# all months, and all leadtime months
def get_ecmwf_cds_metadata(
    years: List[int],
    months: List[int],
    leadtime_months: List[int],
    format: str = "grib",
) -> Dict[str, Any]:
    ecmwf_cds_metadata: Dict[str, Any] = {
        "product_type": "monthly_mean",
        "format": format,
        "originating_centre": "ecmwf",
        "system": "51",
        "variable": ["total_precipitation"],
        "year": [str(year) for year in years],
        "month": [f"{month:02d}" for month in months],
        "leadtime_month": [
            str(leadtime_month) for leadtime_month in leadtime_months
        ],
    }

    return ecmwf_cds_metadata


def download_ecmwf_cds(
    years: List[int],
    months: List[int],
    leadtime_months: List[int],
    download_path: Optional[str] = None,
    format: str = "grib",
    file_name: Optional[str] = None,
) -> Optional[BytesIO]:
    retrieve_name = "seasonal-monthly-single-levels"
    metadata = get_ecmwf_cds_metadata(years, months, leadtime_months, format)

    if download_path and file_name:
        if format == "grib":
            file_path = os.path.join(download_path, file_name)
            metadata["target"] = file_path
            download_cds(retrieve_name, metadata, file_path)
            print(f"Downloaded {file_name} to {file_path}")
        else:
            for year in years:
                for leadtime_month in leadtime_months:
                    netcdf_file_name = f"ecmwf_global_forecast_{year}_lt{leadtime_month}.{format}"  # noqa: E501
                    file_path = os.path.join(download_path, netcdf_file_name)
                    metadata["target"] = file_path
                    download_cds(retrieve_name, metadata, file_path)
                    print(f"Downloaded {netcdf_file_name} to {file_path}")
        return None
    else:
        # If no file path is provided, handle the download in memory
        return download_cds(retrieve_name, metadata)
