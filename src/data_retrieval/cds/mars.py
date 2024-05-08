import os
from io import BytesIO
from typing import Any, Dict, Optional

import pandas as pd

from .common import download_mars, get_dates

DEFAULT_GRID: str = "0.4/0.4"
DEFAULT_FCMONTH: str = "1/2/3/4/5/6/7"

# 25 ensemble members for year <= 2016
ENSEMBLE_MEMBERS_25: str = "/".join([str(i) for i in range(25)])
# 51 ensemble members for year > 2016
ENSEMBLE_MEMBERS_51: str = "/".join([str(i) for i in range(51)])


def get_ensemble_numbers(year: int) -> str:
    number_use: str = (
        ENSEMBLE_MEMBERS_25 if year <= 2016 else ENSEMBLE_MEMBERS_51
    )
    return number_use


def get_country_bbox_df() -> pd.DataFrame:
    data_path: str = os.path.normpath(
        os.path.join(
            os.path.realpath(__file__),
            "..",
            "..",
            "static_data",
            "country_bbox.csv",
        )
    )
    df = pd.read_csv(data_path)
    return df


def get_ecmwf_mars_metadata(
    dates: int, bounding_box: str, numbers: str, fcmonth: str, grid: str
) -> Dict[str, Any]:
    ecmwf_mars_metadata: Dict[str, Any] = {
        "class": "od",
        "date": dates,
        "expver": "1",
        "fcmonth": fcmonth,
        "levtype": "sfc",
        "method": "1",
        "area": bounding_box,
        "grid": grid,
        "number": numbers,
        "origin": "ecmwf",
        "param": "228.172",
        "stream": "msmm",
        "system": "5",
        "time": "00:00:00",
        "type": "fcmean",
        "target": "output",
    }

    return ecmwf_mars_metadata


def download_ecmwf_mars(
    year: int,
    bounding_box: str,
    download_path: Optional[str] = None,
    file_name: Optional[str] = None,
    ensemble_numbers: Optional[str] = None,
    fcmonth: str = DEFAULT_FCMONTH,
    grid: str = DEFAULT_GRID,
) -> Optional[BytesIO]:
    numbers: str = (
        ensemble_numbers if ensemble_numbers else get_ensemble_numbers(year)
    )
    dates: str = get_dates(year)

    # Prepare metadata for the MARS request
    ecmwf_mars_metadata: Dict[str, Any] = get_ecmwf_mars_metadata(
        dates, bounding_box, numbers, fcmonth, grid
    )

    if download_path and file_name:
        file_path = os.path.join(download_path, file_name)
        download_mars(ecmwf_mars_metadata, file_path)
        print(f"Downloaded: {file_path}")
        return None
    else:
        # If file_path is not provided, download the data to memory
        data_stream = download_mars(ecmwf_mars_metadata)
        print("Data downloaded into memory")
        return data_stream
