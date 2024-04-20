import os
from typing import Any, Dict, Optional

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
    download_path: str,
    file_name: str,
    bounding_box: str,
    ensemble_numbers: Optional[str] = None,
    fcmonth: str = DEFAULT_FCMONTH,
    grid: str = DEFAULT_GRID,
):
    numbers: str = (
        ensemble_numbers if ensemble_numbers else get_ensemble_numbers(year)
    )
    dates: str = get_dates(year)
    file_path: str = os.path.join(download_path, file_name)

    ecmwf_mars_metadata: Dict[str, Any] = get_ecmwf_mars_metadata(
        dates, bounding_box, numbers, fcmonth, grid
    )

    download_mars(ecmwf_mars_metadata, file_path)
