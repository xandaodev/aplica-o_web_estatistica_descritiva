"""
Camada de análise de risco.

Centraliza toda a lógica de negócio que usa a variável de risco (rótulo
'Bom pagador' / 'Mau pagador', hospedada na coluna `TARGET_COLUMN` — ver
docs/METODOLOGIA.md para o histórico de como essa coluna foi identificada).

Mantido como funções puras (sem Streamlit) para ser testável isoladamente
e reutilizável fora do dashboard, se necessário.
"""

import pandas as pd

from src.config import TARGET_COLUMN

GOOD_LABEL = "Bom pagador"
BAD_LABEL = "Mau pagador"

# Abaixo deste tamanho de amostra, uma taxa de inadimplência "recorde" numa
# categoria é estatisticamente pouco confiável (ex.: 1 mau pagador em 2
# observações vira "50% de inadimplência"). Usado para não destacar outliers
# de amostra pequena como se fossem achados robustos.
MIN_SAMPLE_SIZE_FOR_HIGHLIGHT = 20


def overall_default_rate(df: pd.DataFrame) -> float:
    """Taxa geral (%) de maus pagadores na amostra fornecida."""
    if df.empty:
        return 0.0
    return float((df[TARGET_COLUMN] == BAD_LABEL).mean() * 100)


def default_rate_by_category(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Taxa de inadimplência (%) por categoria de `column`, com o tamanho da
    amostra de cada categoria, ordenada da maior para a menor taxa.
    """
    rate = (
        df.groupby(column)[TARGET_COLUMN]
        .apply(lambda s: (s == BAD_LABEL).mean() * 100)
        .rename("Taxa de Inadimplência (%)")
    )
    count = df.groupby(column).size().rename("Quantidade")
    table = pd.concat([rate, count], axis=1).reset_index()
    return table.sort_values("Taxa de Inadimplência (%)", ascending=False, ignore_index=True)


def highest_risk_segment(
    rate_table: pd.DataFrame,
    category_column: str,
    min_sample_size: int = MIN_SAMPLE_SIZE_FOR_HIGHLIGHT,
) -> tuple[str, float] | None:
    """
    Retorna (categoria, taxa) da categoria com maior inadimplência entre as
    que têm amostra mínima confiável. `rate_table` já deve vir ordenada de
    forma decrescente (ver default_rate_by_category).
    """
    reliable = rate_table[rate_table["Quantidade"] >= min_sample_size]
    if reliable.empty:
        return None
    top_row = reliable.iloc[0]
    return top_row[category_column], top_row["Taxa de Inadimplência (%)"]


def numeric_profile_by_risk(df: pd.DataFrame, numeric_column: str) -> pd.DataFrame:
    """Compara média, mediana e tamanho de amostra de `numeric_column` entre bons e maus pagadores."""
    profile = df.groupby(TARGET_COLUMN)[numeric_column].agg(["mean", "median", "count"])
    return profile.rename(columns={"mean": "Média", "median": "Mediana", "count": "Quantidade"})
