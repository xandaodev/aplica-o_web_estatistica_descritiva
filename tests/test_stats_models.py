import pytest

from src.config import DATASET_PATH
from src.data_loader import load_and_clean_data
from src.stats_models import (
    DISPERSION_ALERT_THRESHOLD,
    NORMALITY_ALPHA,
    fit_credit_amount_models,
    fit_num_credits_models,
)


@pytest.fixture(scope="module")
def df():
    return load_and_clean_data(DATASET_PATH)


def test_fit_credit_amount_models_returns_two_models(df):
    simples, quad = fit_credit_amount_models(df)
    assert simples.label != quad.label
    assert simples.age_sq_pvalue is None
    assert quad.age_sq_pvalue is not None


def test_credit_amount_models_have_valid_pvalues(df):
    simples, quad = fit_credit_amount_models(df)
    for model in (simples, quad):
        assert 0 <= model.age_pvalue <= 1
        assert model.aic > 0


def test_credit_amount_jarque_bera_flag_matches_alpha(df):
    _, quad = fit_credit_amount_models(df)
    assert quad.residuals_are_normal == (quad.jarque_bera_pvalue >= NORMALITY_ALPHA)


def test_fit_num_credits_models_returns_two_models(df):
    simples, quad = fit_num_credits_models(df)
    assert simples.dispersion_ratio > 0
    assert quad.dispersion_ratio > 0


def test_num_credits_overdispersion_flag_matches_threshold(df):
    simples, _ = fit_num_credits_models(df)
    assert simples.has_overdispersion == (simples.dispersion_ratio > DISPERSION_ALERT_THRESHOLD)
