import os
from typing import Any, Dict, List

from cds.common import download_cds


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
    years: List[int], months: List[int], download_path: str, file_name: str
):
    retrieve_name: str = "reanalysis-era5-single-levels-monthly-means"
    file_path: str = os.path.join(download_path, file_name)
    file_type: str = file_name.split(".")[-1]

    era5_cds_metadata: Dict[str, Any] = get_era5_cds_metadata(
        years, months, file_type
    )

    download_cds(retrieve_name, era5_cds_metadata, file_path)
