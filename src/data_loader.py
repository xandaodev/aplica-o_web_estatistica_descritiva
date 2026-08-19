"""
Camada de dados (ETL): carregamento, normalização e tradução do dataset.

Este módulo é deliberadamente independente do Streamlit. Isso permite:
  1. Testar a lógica de ETL com pytest sem precisar de um servidor Streamlit.
  2. Reutilizar as mesmas funções em outros contextos (notebook, CLI, API).

O cache do Streamlit (st.cache_data) fica na camada de UI (app.py), que é
quem sabe que está rodando dentro de um app Streamlit.
"""

import re
from pathlib import Path

import pandas as pd

from src.translations import flatten_value_translations


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normaliza nomes de colunas para snake_case "seguro": remove espaços,
    barras e parênteses, que quebram o acesso via df.coluna e algumas
    fórmulas do statsmodels.

    Exemplo: "Other installment plans (banks/stores)" -> "Other_installment_plans_banks_stores"
    """
    df = df.copy()
    new_columns = []
    for col in df.columns:
        clean = col.strip()
        clean = re.sub(r"[()/]", " ", clean)   # remove parênteses e barras
        clean = re.sub(r"\s+", "_", clean)      # espaços -> underscore
        clean = clean.strip("_")
        new_columns.append(clean)
    df.columns = new_columns
    return df


def translate_categorical_values(df: pd.DataFrame) -> pd.DataFrame:
    """Traduz os valores categóricos em inglês para português (in-place lógico, retorna cópia)."""
    return df.replace(flatten_value_translations())


def load_and_clean_data(file_path: str | Path) -> pd.DataFrame:
    """
    Carrega o dataset de crédito bruto e aplica o pipeline de limpeza:
      1. Leitura do CSV.
      2. Normalização dos nomes de colunas.
      3. Tradução dos valores categóricos para português.

    O arquivo em disco nunca é alterado — a tradução acontece em memória,
    preservando a reprodutibilidade do dataset original (German Credit Data).

    Args:
        file_path: caminho para o dataset.csv.

    Returns:
        DataFrame limpo e traduzido, pronto para análise.

    Raises:
        FileNotFoundError: se o arquivo não existir.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Dataset não encontrado em '{file_path}'. "
            "Verifique se o arquivo está em data/dataset.csv."
        )

    df = pd.read_csv(file_path)
    df = normalize_column_names(df)
    df = translate_categorical_values(df)
    return df


def get_numeric_columns(df: pd.DataFrame) -> list[str]:
    """Retorna as colunas numéricas do DataFrame, exceto o identificador 'id'."""
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    return [c for c in numeric_cols if c.lower() != "id"]


def get_categorical_columns(df: pd.DataFrame) -> list[str]:
    """Retorna as colunas categóricas (texto) do DataFrame."""
    return df.select_dtypes(exclude="number").columns.tolist()
