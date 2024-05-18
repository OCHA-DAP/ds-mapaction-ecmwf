import os
from io import BytesIO
from typing import Any, Dict, List, Optional

from .common import download_cds


# Function to create a single API request for the specified years,
# all months, and all leadtime months
def get_ecmwf_cds_metadata(
    years: List[int], months: List[int], leadtime_months: List[int]
) -> Dict[str, Any]:
    ecmwf_cds_metadata: Dict[str, Any] = {
        "product_type": "monthly_mean",
        "format": "grib",  # Format set to grib
        "originating_centre": "ecmwf",
        "system": "51",
        "variable": ["total_precipitation"],
        "year": [str(year) for year in years],
        "month": [f"{month:02d}" for month in months],
        "leadtime_month": [
            str(leadtime_month) for leadtime_month in leadtime_months
        ],
        # 'area' parameter removed to target the whole globe
    }

    return ecmwf_cds_metadata


def download_ecmwf_cds(
    years: List[int],
    months: List[int],
    leadtime_months: List[int],
    download_path: Optional[str] = None,
    file_name: Optional[str] = None,
) -> Optional[BytesIO]:
    retrieve_name = "seasonal-monthly-single-levels"
    metadata = get_ecmwf_cds_metadata(years, months, leadtime_months)

    if download_path and file_name:
        file_path = os.path.join(download_path, file_name)
        metadata["target"] = file_path
        download_cds(retrieve_name, metadata, file_path)
        return None
    else:
        return download_cds(retrieve_name, metadata)
