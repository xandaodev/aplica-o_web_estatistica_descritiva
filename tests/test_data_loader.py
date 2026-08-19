import pandas as pd
import pytest

from src.config import DATASET_PATH
from src.data_loader import (
    get_categorical_columns,
    get_numeric_columns,
    load_and_clean_data,
    normalize_column_names,
    translate_categorical_values,
)


@pytest.fixture(scope="module")
def df():
    return load_and_clean_data(DATASET_PATH)


def test_load_and_clean_data_returns_dataframe(df):
    assert isinstance(df, pd.DataFrame)
    assert not df.empty


def test_load_and_clean_data_has_expected_row_count(df):
    # O German Credit Data (e esta adaptação) tem 1.000 solicitantes.
    assert len(df) == 1000


def test_load_and_clean_data_raises_for_missing_file(tmp_path):
    missing_file = tmp_path / "nao_existe.csv"
    with pytest.raises(FileNotFoundError):
        load_and_clean_data(missing_file)


def test_normalize_column_names_removes_special_characters():
    df_raw = pd.DataFrame(columns=["Other installment plans (banks/stores)", "Age in years"])
    normalized = normalize_column_names(df_raw)
    assert "Other_installment_plans_banks_stores" in normalized.columns
    assert "Age_in_years" in normalized.columns
    for col in normalized.columns:
        assert "(" not in col and ")" not in col and "/" not in col and " " not in col


def test_translate_categorical_values_translates_known_value():
    df_raw = pd.DataFrame({"Housing": ["own", "rent"]})
    translated = translate_categorical_values(df_raw)
    assert "Própria" in translated["Housing"].values
    assert "Alugada" in translated["Housing"].values


def test_get_numeric_columns_excludes_id(df):
    numeric_cols = get_numeric_columns(df)
    assert "id" not in [c.lower() for c in numeric_cols]
    assert "Credit_amount" in numeric_cols
    assert "Age_in_years" in numeric_cols


def test_get_categorical_columns_excludes_numeric(df):
    categorical_cols = get_categorical_columns(df)
    assert "Credit_amount" not in categorical_cols
    assert "Purpose_of_the_credit" in categorical_cols


def test_dataset_has_no_missing_values_after_cleaning(df):
    # Falha alto e cedo caso o dataset original venha a ganhar valores ausentes:
    # a tradução via .replace() propagaria NaN silenciosamente para colunas
    # com valores fora dos dicionários de tradução.
    assert df.isna().sum().sum() == 0
