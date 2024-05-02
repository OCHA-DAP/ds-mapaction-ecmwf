from io import BytesIO
from typing import Any, Dict, List

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
    years: List[int], months: List[int], leadtime_months: List[int]
) -> BytesIO:
    retrieve_name = "seasonal-monthly-single-levels"
    metadata = get_ecmwf_cds_metadata(years, months, leadtime_months)
    data_stream = download_cds(retrieve_name, metadata)
    return data_stream
