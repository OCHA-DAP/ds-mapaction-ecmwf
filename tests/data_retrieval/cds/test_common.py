from src.data_retrieval.cds.common import get_dates


def test_get_dates_returns_correct_value():
    expected: str = (
        "2019-01-01/2019-02-01/2019-03-01/2019-04-01/2019-05-01/2019-06-01/2019-07-01/2019-08-01/2019-09-01/2019-10-01/2019-11-01/2019-12-01"  # noqa: E501
    )
    returned: str = get_dates(2019)

    assert expected == returned
