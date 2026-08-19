"""
Camada de estatística inferencial.

Concentra o ajuste dos modelos de regressão e os testes de diagnóstico
que antes ficavam misturados com o código de interface no app.py.

Modelos incluídos:
  - OLS simples e polinomial (grau 2) para o Valor do Crédito (variável contínua).
  - Poisson simples e polinomial (grau 2) para o Nº de Créditos Existentes (contagem).

Cada modelo é acompanhado de um diagnóstico:
  - OLS: teste de normalidade dos resíduos (Jarque-Bera).
  - Poisson: razão de dispersão (Pearson Chi2 / graus de liberdade), que indica
    se a premissa "média == variância" do Poisson está sendo violada
    (superdispersão).
"""

from dataclasses import dataclass

import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.stats.api as sms

AGE_COL = "Age_in_years"
CREDIT_AMOUNT_COL = "Credit_amount"
NUM_CREDITS_COL = "Number_of_existing_credits_at_this_bank"

# Acima deste valor, consideramos que há superdispersão relevante no modelo de Poisson.
DISPERSION_ALERT_THRESHOLD = 1.2
# Abaixo deste p-valor, rejeitamos a hipótese de normalidade dos resíduos (Jarque-Bera).
NORMALITY_ALPHA = 0.05


@dataclass
class OLSDiagnostic:
    """Resultado de um modelo OLS já com o diagnóstico de normalidade calculado."""

    label: str
    formula: str
    result: "smf.ols"
    aic: float
    age_pvalue: float
    age_sq_pvalue: float | None
    jarque_bera_pvalue: float

    @property
    def residuals_are_normal(self) -> bool:
        return self.jarque_bera_pvalue >= NORMALITY_ALPHA


@dataclass
class PoissonDiagnostic:
    """Resultado de um modelo de Poisson já com a razão de dispersão calculada."""

    label: str
    formula: str
    result: "smf.poisson"
    aic: float
    age_pvalue: float
    age_sq_pvalue: float | None
    dispersion_ratio: float

    @property
    def has_overdispersion(self) -> bool:
        return self.dispersion_ratio > DISPERSION_ALERT_THRESHOLD


def _jarque_bera_pvalue(ols_result) -> float:
    """Extrai o p-valor do teste de Jarque-Bera para os resíduos de um modelo OLS."""
    return sms.jarque_bera(ols_result.resid)[1]


def _poisson_dispersion_ratio(poisson_result) -> float:
    """
    Calcula a razão de dispersão de Pearson: soma dos resíduos de Pearson ao
    quadrado dividida pelos graus de liberdade dos resíduos. Valor ideal: ~1.0.
    """
    return float(sum(poisson_result.resid_pearson**2) / poisson_result.df_resid)


def fit_credit_amount_models(df: pd.DataFrame) -> tuple[OLSDiagnostic, OLSDiagnostic]:
    """
    Ajusta os dois modelos para o Valor do Crédito: linear simples e polinomial (Idade²).

    Returns:
        (modelo_simples, modelo_quadratico)
    """
    formula_simple = f"{CREDIT_AMOUNT_COL} ~ {AGE_COL}"
    formula_quad = f"{CREDIT_AMOUNT_COL} ~ {AGE_COL} + I({AGE_COL}**2)"

    result_simple = smf.ols(formula_simple, data=df).fit()
    result_quad = smf.ols(formula_quad, data=df).fit()

    simple = OLSDiagnostic(
        label="Regressão Linear Simples",
        formula="Valor ~ Idade",
        result=result_simple,
        aic=result_simple.aic,
        age_pvalue=result_simple.pvalues.get(AGE_COL, float("nan")),
        age_sq_pvalue=None,
        jarque_bera_pvalue=_jarque_bera_pvalue(result_simple),
    )
    quad = OLSDiagnostic(
        label="Regressão Polinomial (Idade²)",
        formula="Valor ~ Idade + Idade²",
        result=result_quad,
        aic=result_quad.aic,
        age_pvalue=result_quad.pvalues.get(AGE_COL, float("nan")),
        age_sq_pvalue=result_quad.pvalues.get(f"I({AGE_COL} ** 2)", float("nan")),
        jarque_bera_pvalue=_jarque_bera_pvalue(result_quad),
    )
    return simple, quad


def fit_num_credits_models(df: pd.DataFrame) -> tuple[PoissonDiagnostic, PoissonDiagnostic]:
    """
    Ajusta os dois modelos de Poisson para o Nº de Créditos Existentes: simples
    e polinomial (Idade²).

    Returns:
        (modelo_simples, modelo_quadratico)
    """
    formula_simple = f"{NUM_CREDITS_COL} ~ {AGE_COL}"
    formula_quad = f"{NUM_CREDITS_COL} ~ {AGE_COL} + I({AGE_COL}**2)"

    result_simple = smf.poisson(formula_simple, data=df).fit(disp=0)
    result_quad = smf.poisson(formula_quad, data=df).fit(disp=0)

    simple = PoissonDiagnostic(
        label="Poisson Simples",
        formula="Nº Empréstimos ~ Idade",
        result=result_simple,
        aic=result_simple.aic,
        age_pvalue=result_simple.pvalues.get(AGE_COL, float("nan")),
        age_sq_pvalue=None,
        dispersion_ratio=_poisson_dispersion_ratio(result_simple),
    )
    quad = PoissonDiagnostic(
        label="Poisson Polinomial (Idade²)",
        formula="Nº Empréstimos ~ Idade + Idade²",
        result=result_quad,
        aic=result_quad.aic,
        age_pvalue=result_quad.pvalues.get(AGE_COL, float("nan")),
        age_sq_pvalue=result_quad.pvalues.get(f"I({AGE_COL} ** 2)", float("nan")),
        dispersion_ratio=_poisson_dispersion_ratio(result_quad),
    )
    return simple, quad
