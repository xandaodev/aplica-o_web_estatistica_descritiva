"""
Camada de visualização: funções puras que recebem um DataFrame e devolvem
uma figura Plotly pronta para ser exibida (com st.plotly_chart na camada de UI).

Manter a construção dos gráficos aqui, fora do app.py, facilita:
  - Reaproveitar os mesmos gráficos em outro contexto (ex.: exportar para PDF).
  - Testar que as figuras são geradas sem erro para diferentes fatias de dados.

Todas as figuras usam o template `plotly_dark` com fundo transparente, para
se integrar ao tema escuro definido em `.streamlit/config.toml`.
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.risk_analysis import BAD_LABEL, GOOD_LABEL
from src.translations import COLUMN_LABELS

PURPOSE_COL = "Purpose_of_the_credit"
CREDIT_AMOUNT_COL = "Credit_amount"
AGE_COL = "Age_in_years"

# Paleta com bom contraste sobre fundo escuro (o "Pastel" padrão do Plotly
# fica apagado em dark mode).
CATEGORY_COLORWAY = [
    "#38BDF8",  # azul céu (cor primária do tema)
    "#A78BFA",  # roxo
    "#34D399",  # verde
    "#FBBF24",  # âmbar
    "#F472B6",  # rosa
    "#60A5FA",  # azul
    "#FB923C",  # laranja
    "#2DD4BF",  # teal
    "#F87171",  # vermelho suave
    "#C084FC",  # lilás
]

GOOD_COLOR = "#34D399"
BAD_COLOR = "#F87171"
RISK_COLOR_MAP = {GOOD_LABEL: GOOD_COLOR, BAD_LABEL: BAD_COLOR}
# Escala contínua verde -> âmbar -> vermelho para taxas de inadimplência.
RISK_COLOR_SCALE = ["#34D399", "#FBBF24", "#F87171"]


def _apply_dark_theme(fig: "go.Figure") -> "go.Figure":
    """Aplica o template escuro e fundo transparente, padronizando todas as figuras do app."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=CATEGORY_COLORWAY,
        font=dict(color="#E6EDF3"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(t=60, b=40, l=40, r=20),
    )
    return fig


def purpose_share_pie(df: pd.DataFrame) -> "go.Figure":
    """Gráfico de pizza com a participação de cada objetivo de crédito."""
    fig = px.pie(
        df,
        names=PURPOSE_COL,
        hole=0.45,
        color_discrete_sequence=CATEGORY_COLORWAY,
        labels=COLUMN_LABELS,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return _apply_dark_theme(fig)


def credit_amount_boxplot(df: pd.DataFrame) -> "go.Figure":
    """Boxplot do valor do crédito por objetivo, para identificar outliers e dispersão."""
    fig = px.box(
        df,
        x=PURPOSE_COL,
        y=CREDIT_AMOUNT_COL,
        color=PURPOSE_COL,
        color_discrete_sequence=CATEGORY_COLORWAY,
        labels=COLUMN_LABELS,
    )
    fig.update_layout(showlegend=False)
    return _apply_dark_theme(fig)


def age_vs_credit_scatter(df: pd.DataFrame) -> "go.Figure":
    """Dispersão Idade x Valor do Crédito, com marginais e linha de tendência OLS."""
    fig = px.scatter(
        df,
        x=AGE_COL,
        y=CREDIT_AMOUNT_COL,
        color=PURPOSE_COL,
        opacity=0.75,
        marginal_y="violin",
        marginal_x="histogram",
        trendline="ols",
        color_discrete_sequence=CATEGORY_COLORWAY,
        labels=COLUMN_LABELS,
    )
    return _apply_dark_theme(fig)


def dynamic_distribution(df: pd.DataFrame, column: str) -> "go.Figure":
    """
    Histograma da variável escolhida dinamicamente pelo usuário.
    Sobreposto se numérica, agrupado se categórica.
    """
    label = COLUMN_LABELS.get(column, column)
    is_numeric = pd.api.types.is_numeric_dtype(df[column])

    fig = px.histogram(
        df,
        x=column,
        color=PURPOSE_COL,
        barmode="overlay" if is_numeric else "group",
        title=f"{'Distribuição de' if is_numeric else 'Contagem por'} {label}",
        color_discrete_sequence=CATEGORY_COLORWAY,
        labels=COLUMN_LABELS,
    )
    return _apply_dark_theme(fig)


def default_rate_bar(rate_table: pd.DataFrame, category_column: str) -> "go.Figure":
    """
    Gráfico de barras horizontais com a taxa de inadimplência (%) por
    categoria, ordenado da maior para a menor taxa e colorido numa escala
    verde -> vermelho.
    """
    label = COLUMN_LABELS.get(category_column, category_column)
    fig = px.bar(
        rate_table.sort_values("Taxa de Inadimplência (%)"),
        x="Taxa de Inadimplência (%)",
        y=category_column,
        orientation="h",
        color="Taxa de Inadimplência (%)",
        color_continuous_scale=RISK_COLOR_SCALE,
        text="Taxa de Inadimplência (%)",
        labels={**COLUMN_LABELS, category_column: label},
        hover_data={"Quantidade": True},
    )
    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_layout(coloraxis_showscale=False, yaxis_title=label)
    return _apply_dark_theme(fig)


def numeric_by_risk_boxplot(df: pd.DataFrame, numeric_column: str, target_column: str) -> "go.Figure":
    """Compara a distribuição de uma variável numérica entre bons e maus pagadores."""
    label = COLUMN_LABELS.get(numeric_column, numeric_column)
    fig = px.box(
        df,
        x=target_column,
        y=numeric_column,
        color=target_column,
        color_discrete_map=RISK_COLOR_MAP,
        labels={**COLUMN_LABELS, numeric_column: label},
    )
    fig.update_layout(showlegend=False, xaxis_title="", yaxis_title=label)
    return _apply_dark_theme(fig)


def correlation_heatmap(df: pd.DataFrame, numeric_columns: list[str]) -> "go.Figure":
    """Mapa de calor de correlação (Pearson) entre variáveis numéricas."""
    corr = df[numeric_columns].corr()
    display_labels = [COLUMN_LABELS.get(c, c) for c in numeric_columns]
    fig = px.imshow(
        corr.values,
        x=display_labels,
        y=display_labels,
        color_continuous_scale="RdBu_r",
        zmin=-1,
        zmax=1,
        text_auto=".2f",
        aspect="auto",
    )
    fig.update_layout(coloraxis_showscale=True)
    return _apply_dark_theme(fig)
