import pytest

from src.config import DATASET_PATH
from src.data_loader import load_and_clean_data
from src.insights import age_credit_amount_correlation, median_credit_amount_gap_by_risk, top_purpose_by_volume


@pytest.fixture(scope="module")
def df():
    return load_and_clean_data(DATASET_PATH)


def test_age_credit_amount_correlation_is_valid_range(df):
    corr = age_credit_amount_correlation(df)
    assert -1 <= corr <= 1


def test_top_purpose_by_volume_returns_known_purpose(df):
    purpose, share = top_purpose_by_volume(df)
    assert purpose in df["Purpose_of_the_credit"].unique()
    assert 0 < share <= 100


def test_median_credit_amount_gap_by_risk_returns_three_finite_values(df):
    good, bad, gap_pct = median_credit_amount_gap_by_risk(df)
    assert good > 0
    assert bad > 0
    assert gap_pct == pytest.approx((bad - good) / good * 100)
