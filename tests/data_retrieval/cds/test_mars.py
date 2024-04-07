from typing import Any, Dict

from src.data_retrieval.cds.mars import get_ecmwf_mars_metadata


def test_get_ecmwf_mars_metadata_returns_correct_value():
    dates: str = "2019-01-01/2019-02-01/2019-03-01"
    bounding_box: str = "22.2/7.7/9.9/22.2"
    numbers: str = "0/1/2/3/4/5/6/7/8"
    fcmonth: str = "1/2/3"
    grid: str = "1.0/1.0"

    expected: Dict[str, Any] = {
        "class": "od",
        "date": "2019-01-01/2019-02-01/2019-03-01",
        "expver": "1",
        "fcmonth": "1/2/3",
        "levtype": "sfc",
        "method": "1",
        "area": "22.2/7.7/9.9/22.2",
        "grid": "1.0/1.0",
        "number": "0/1/2/3/4/5/6/7/8",
        "origin": "ecmwf",
        "param": "228.172",
        "stream": "msmm",
        "system": "5",
        "time": "00:00:00",
        "type": "fcmean",
        "target": "output",
    }

    returned: Dict[str, Any] = get_ecmwf_mars_metadata(
        dates, bounding_box, numbers, fcmonth, grid
    )

    assert expected == returned
