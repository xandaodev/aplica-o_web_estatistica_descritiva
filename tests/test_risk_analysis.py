import pytest

from src.config import DATASET_PATH, TARGET_COLUMN
from src.data_loader import load_and_clean_data
from src.risk_analysis import (
    BAD_LABEL,
    GOOD_LABEL,
    default_rate_by_category,
    highest_risk_segment,
    numeric_profile_by_risk,
    overall_default_rate,
)


@pytest.fixture(scope="module")
def df():
    return load_and_clean_data(DATASET_PATH)


def test_overall_default_rate_is_a_valid_percentage(df):
    rate = overall_default_rate(df)
    assert 0 <= rate <= 100


def test_overall_default_rate_empty_df_returns_zero(df):
    empty = df.iloc[0:0]
    assert overall_default_rate(empty) == 0.0


def test_target_column_only_has_expected_labels(df):
    assert set(df[TARGET_COLUMN].unique()) == {GOOD_LABEL, BAD_LABEL}


def test_default_rate_by_category_sorted_descending(df):
    table = default_rate_by_category(df, "Housing")
    rates = table["Taxa de Inadimplência (%)"].tolist()
    assert rates == sorted(rates, reverse=True)


def test_default_rate_by_category_preserves_total_count(df):
    table = default_rate_by_category(df, "Housing")
    assert table["Quantidade"].sum() == len(df)


def test_highest_risk_segment_respects_min_sample_size(df):
    table = default_rate_by_category(df, "Housing")
    result = highest_risk_segment(table, "Housing", min_sample_size=10_000)
    # Nenhuma categoria de Housing tem 10.000 observações (dataset tem 1.000 linhas).
    assert result is None


def test_highest_risk_segment_returns_tuple_when_available(df):
    table = default_rate_by_category(df, "Housing")
    result = highest_risk_segment(table, "Housing", min_sample_size=1)
    assert result is not None
    segment, rate = result
    assert isinstance(segment, str)
    assert 0 <= rate <= 100


def test_numeric_profile_by_risk_has_both_labels(df):
    profile = numeric_profile_by_risk(df, "Age_in_years")
    assert set(profile.index) == {GOOD_LABEL, BAD_LABEL}
