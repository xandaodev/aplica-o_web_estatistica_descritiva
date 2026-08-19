"""
Camada de insights.

Cada texto narrativo exibido ao lado de um gráfico no dashboard ("o que este
gráfico mostra") é montado a partir de um número calculado aqui — nunca
escrito à mão diretamente no app.py. Isso evita a armadilha comum de um
dashboard "storytelling" ficar com afirmações desatualizadas assim que o
usuário aplica um filtro diferente: o texto é recalculado junto com o gráfico.
"""

import pandas as pd

from src.config import TARGET_COLUMN
from src.risk_analysis import BAD_LABEL, GOOD_LABEL

AGE_COL = "Age_in_years"
CREDIT_AMOUNT_COL = "Credit_amount"
PURPOSE_COL = "Purpose_of_the_credit"


def age_credit_amount_correlation(df: pd.DataFrame) -> float:
    """Correlação de Pearson entre idade e valor do crédito solicitado."""
    return float(df[AGE_COL].corr(df[CREDIT_AMOUNT_COL]))


def top_purpose_by_volume(df: pd.DataFrame) -> tuple[str, float]:
    """
    Objetivo de crédito com maior volume total solicitado, e sua
    participação (%) sobre o total.
    """
    totals = df.groupby(PURPOSE_COL)[CREDIT_AMOUNT_COL].sum().sort_values(ascending=False)
    top_purpose = totals.index[0]
    share = float(totals.iloc[0] / totals.sum() * 100)
    return top_purpose, share


def median_credit_amount_gap_by_risk(df: pd.DataFrame) -> tuple[float, float, float]:
    """
    Mediana do valor do crédito entre bons e maus pagadores, e a diferença
    percentual do grupo de maus pagadores em relação ao de bons pagadores.
    """
    medians = df.groupby(TARGET_COLUMN)[CREDIT_AMOUNT_COL].median()
    good = float(medians.get(GOOD_LABEL, float("nan")))
    bad = float(medians.get(BAD_LABEL, float("nan")))
    gap_pct = float((bad - good) / good * 100) if good else float("nan")
    return good, bad, gap_pct
