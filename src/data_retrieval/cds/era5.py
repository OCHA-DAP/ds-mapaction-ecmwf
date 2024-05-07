import os
from io import BytesIO
from typing import Any, Dict, List, Optional

from .common import download_cds


def get_era5_cds_metadata(
    years: List[int], months: List[int], file_type: str
) -> Dict[str, Any]:
    era5_cds_metadata: Dict[str, Any] = {
        "product_type": "monthly_averaged_reanalysis",
        "variable": "total_precipitation",
        "year": [str(year) for year in years],
        "month": [f"{month:02d}" for month in months],
        "time": "00:00",
        "format": file_type,
    }

    return era5_cds_metadata


def download_era5_cds(
    years: List[int],
    months: List[int],
    file_name: str,
    download_path: Optional[str] = None,
) -> Optional[BytesIO]:
    retrieve_name = "reanalysis-era5-single-levels-monthly-means"
    file_type = file_name.split(".")[
        -1
    ]  # Assumes file_name includes an extension

    # Prepare metadata with appropriate file type
    era5_cds_metadata = get_era5_cds_metadata(years, months, file_type)

    if download_path:
        # Construct the full file path if a download path is specified
        file_path = os.path.join(download_path, file_name)
        download_cds(retrieve_name, era5_cds_metadata, file_path)
        print(f"Downloaded: {file_path}")
    else:
        # No file path specified, return data as BytesIO object
        data_stream = download_cds(retrieve_name, era5_cds_metadata)
        print("Data downloaded into memory")
        return data_stream
