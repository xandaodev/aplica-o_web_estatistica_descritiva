import pytest

from src.config import DATASET_PATH, TARGET_COLUMN
from src.data_loader import load_and_clean_data
from src.risk_analysis import default_rate_by_category
from src.visualizations import (
    age_vs_credit_scatter,
    correlation_heatmap,
    credit_amount_boxplot,
    default_rate_bar,
    dynamic_distribution,
    numeric_by_risk_boxplot,
    purpose_share_pie,
)


@pytest.fixture(scope="module")
def df():
    return load_and_clean_data(DATASET_PATH)


def test_purpose_share_pie_builds_figure(df):
    fig = purpose_share_pie(df)
    assert fig.data


def test_credit_amount_boxplot_builds_figure(df):
    fig = credit_amount_boxplot(df)
    assert fig.data


def test_age_vs_credit_scatter_builds_figure(df):
    fig = age_vs_credit_scatter(df)
    assert fig.data


@pytest.mark.parametrize("column", ["Age_in_years", "Housing", "Job"])
def test_dynamic_distribution_builds_figure_for_numeric_and_categorical(df, column):
    fig = dynamic_distribution(df, column)
    assert fig.data


def test_default_rate_bar_builds_figure(df):
    rate_table = default_rate_by_category(df, "Housing")
    fig = default_rate_bar(rate_table, "Housing")
    assert fig.data


def test_numeric_by_risk_boxplot_builds_figure(df):
    fig = numeric_by_risk_boxplot(df, "Age_in_years", TARGET_COLUMN)
    assert fig.data


def test_correlation_heatmap_builds_figure(df):
    fig = correlation_heatmap(df, ["Age_in_years", "Credit_amount", "Duration_in_months"])
    assert fig.data
