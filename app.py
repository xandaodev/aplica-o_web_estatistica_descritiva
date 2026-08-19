"""
Credit Risk Analytics — Dashboard de Análise Estatística de Crédito.

Este arquivo é a camada de UI (Streamlit) e deve conter apenas orquestração:
layout, widgets e chamadas às camadas de dados (src.data_loader), estatística
(src.stats_models), risco (src.risk_analysis), insights (src.insights) e
visualização (src.visualizations). A lógica de negócio não deve viver aqui.
"""

import pandas as pd
import streamlit as st

from src import config
from src.data_loader import get_categorical_columns, get_numeric_columns, load_and_clean_data
from src.formatting import format_currency_pt_br, format_int_pt_br
from src.insights import age_credit_amount_correlation, median_credit_amount_gap_by_risk, top_purpose_by_volume
from src.risk_analysis import (
    BAD_LABEL,
    default_rate_by_category,
    highest_risk_segment,
    numeric_profile_by_risk,
    overall_default_rate,
)
from src.stats_models import fit_credit_amount_models, fit_num_credits_models
from src.translations import COLUMN_LABELS, METRIC_LABELS
from src.visualizations import (
    age_vs_credit_scatter,
    correlation_heatmap,
    credit_amount_boxplot,
    default_rate_bar,
    dynamic_distribution,
    numeric_by_risk_boxplot,
    purpose_share_pie,
)

PURPOSE_COL = "Purpose_of_the_credit"
CREDIT_AMOUNT_COL = "Credit_amount"
AGE_COL = "Age_in_years"
DURATION_COL = "Duration_in_months"

st.set_page_config(page_title=config.PAGE_TITLE, page_icon=config.PAGE_ICON, layout="wide")

CUSTOM_CSS = """
<style>
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 14px 16px 8px 16px;
    }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem; opacity: 0.75; }
    .block-container { padding-top: 2rem; }
</style>
"""


@st.cache_data
def _load_data() -> pd.DataFrame:
    """Wrapper com cache do Streamlit em torno da função pura de ETL (src.data_loader)."""
    return load_and_clean_data(config.DATASET_PATH)


def render_header() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
    st.title(f"{config.PAGE_ICON} Credit Risk Analytics")
    st.markdown(
        "Análise exploratória e inferencial de risco de crédito bancário, com base numa "
        "adaptação do dataset **German Credit Data**. Objetivo: entender o perfil dos "
        "solicitantes, o que diferencia bons e maus pagadores, e como a idade se relaciona "
        "com o valor e a finalidade do crédito solicitado."
    )

    with st.expander("ℹ️ Sobre este projeto e os dados"):
        st.markdown(
            """
            **Origem dos dados:** adaptação do clássico *German Credit Data*, com 1.000
            solicitações de crédito de um banco alemão, incluindo variáveis demográficas,
            financeiras e de histórico bancário.

            **Metodologia completa** (perguntas de pesquisa, modelos estatísticos e
            limitações conhecidas) disponível em `docs/METODOLOGIA.md`, no repositório.

            ---
            Projeto desenvolvido por **Alexandre Vital** para a disciplina de Estatística e
            Probabilidade (UFSJ, prof. Davi Butturi Alvim) e posteriormente refatorado como
            projeto de portfólio em análise de dados.
            """
        )
    st.markdown("---")


def render_sidebar_filters(df: pd.DataFrame) -> list[str]:
    st.sidebar.header("🛠️ Filtros")
    st.sidebar.caption("Os filtros abaixo afetam as abas *Visão Geral*, *Perfil* e *Análise de Risco*.")

    objetivos_disponiveis = df[PURPOSE_COL].unique().tolist()
    selecionar_todos = st.sidebar.checkbox("Selecionar Todos os Objetivos", value=True)
    default = objetivos_disponiveis if selecionar_todos else []
    escolha = st.sidebar.multiselect("Filtrar por Objetivo do Crédito", objetivos_disponiveis, default=default)

    st.session_state["metricas_selecionadas"] = st.sidebar.multiselect(
        "Medidas-Resumo da tabela",
        options=list(METRIC_LABELS.keys()),
        format_func=lambda x: METRIC_LABELS[x],
        default=config.DEFAULT_SUMMARY_METRICS,
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Os modelos estatísticos (aba *Modelos*) sempre usam a base completa, "
        "independente destes filtros, para preservar poder estatístico."
    )
    return escolha


def render_kpis(df_filtrado: pd.DataFrame) -> None:
    col1, col2, col3, col4, col5 = st.columns(5)

    total_pedidos = len(df_filtrado)
    valor_total = df_filtrado[CREDIT_AMOUNT_COL].sum()
    ticket_medio = df_filtrado[CREDIT_AMOUNT_COL].mean()
    idade_media = df_filtrado[AGE_COL].mean()
    taxa_inadimplencia = overall_default_rate(df_filtrado)

    col1.metric("Total de Pedidos", format_int_pt_br(total_pedidos))
    col2.metric("Valor Total Solicitado", format_currency_pt_br(valor_total))
    col3.metric("Ticket Médio", format_currency_pt_br(ticket_medio))
    col4.metric("Idade Média", f"{idade_media:.1f} anos")
    col5.metric("Taxa de Inadimplência", f"{taxa_inadimplencia:.1f}%")
    st.markdown("---")


def render_overview_tab(df_filtrado: pd.DataFrame, metricas_selecionadas: list[str]) -> None:
    render_kpis(df_filtrado)

    st.subheader("Distribuição e Dispersão")
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("**Participação por Objetivo de Crédito**")
        st.plotly_chart(purpose_share_pie(df_filtrado), use_container_width=True)
    with c_right:
        st.markdown("**Dispersão e Outliers de Valores por Objetivo**")
        st.plotly_chart(credit_amount_boxplot(df_filtrado), use_container_width=True)

    top_purpose, share = top_purpose_by_volume(df_filtrado)
    top_purpose_label = COLUMN_LABELS.get(top_purpose, top_purpose)
    st.info(
        f"💡 **Insight:** *{top_purpose}* concentra **{share:.1f}%** do volume total de "
        f"crédito solicitado no recorte atual — o maior peso entre os objetivos filtrados."
    )
    st.markdown("---")

    st.subheader("Resumo Estatístico Dinâmico")
    if not metricas_selecionadas:
        st.warning("Selecione ao menos uma métrica na barra lateral.")
    else:
        resumo = df_filtrado.groupby(PURPOSE_COL)[CREDIT_AMOUNT_COL].agg(metricas_selecionadas)
        resumo = resumo.rename(columns=METRIC_LABELS)
        resumo.index.name = "Objetivo do Crédito"
        st.dataframe(resumo.style.format("{:.2f}").background_gradient(cmap="Blues"), use_container_width=True)


def render_profile_tab(df: pd.DataFrame, df_filtrado: pd.DataFrame) -> None:
    st.subheader("Idade x Valor do Crédito")
    st.markdown(
        "Cruzamento entre a idade do solicitante e o valor pedido, com a linha de "
        "tendência (regressão OLS) e as distribuições marginais de cada eixo."
    )
    st.plotly_chart(age_vs_credit_scatter(df_filtrado), use_container_width=True)

    corr = age_credit_amount_correlation(df_filtrado)
    strength = "fraca" if abs(corr) < 0.2 else "moderada" if abs(corr) < 0.5 else "forte"
    direction = "positiva" if corr > 0 else "negativa"
    st.info(
        f"💡 **Insight:** a correlação entre idade e valor do crédito no recorte atual é "
        f"**{corr:.2f}** — uma associação linear **{strength}** e **{direction}**. Isso sugere "
        f"que, sozinha, a idade explica pouco do valor solicitado (por isso testamos modelos "
        f"não lineares na aba *Modelos Estatísticos*)."
    )
    st.markdown("---")

    st.subheader("Correlação entre Variáveis Numéricas")
    numeric_cols = get_numeric_columns(df_filtrado)
    default_selection = [c for c in [AGE_COL, CREDIT_AMOUNT_COL, DURATION_COL] if c in numeric_cols]
    selected_numeric = st.multiselect(
        "Variáveis para o mapa de correlação:",
        numeric_cols,
        default=default_selection or numeric_cols[:4],
        format_func=lambda x: COLUMN_LABELS.get(x, x),
    )
    if len(selected_numeric) >= 2:
        st.plotly_chart(correlation_heatmap(df_filtrado, selected_numeric), use_container_width=True)
    else:
        st.warning("Selecione ao menos duas variáveis para calcular a correlação.")
    st.markdown("---")

    st.subheader("🔄 Exploração Dinâmica")
    st.markdown("Selecione qualquer variável do dataset para visualizar seu comportamento no recorte filtrado.")
    colunas_disponiveis = [c for c in df.columns.tolist() if c.lower() != "id"]
    default_index = colunas_disponiveis.index(AGE_COL) if AGE_COL in colunas_disponiveis else 0
    var_x = st.selectbox(
        "Variável:",
        colunas_disponiveis,
        index=default_index,
        format_func=lambda x: COLUMN_LABELS.get(x, x),
    )
    st.plotly_chart(dynamic_distribution(df_filtrado, var_x), use_container_width=True)


def render_risk_tab(df_filtrado: pd.DataFrame) -> None:
    st.subheader("⚠️ Quem são os maus pagadores?")
    st.markdown(
        "Esta aba usa o rótulo de risco identificado na coluna de status da conta corrente "
        "(que, na prática, indica se o solicitante é um bom ou mau pagador — "
        "veja `docs/METODOLOGIA.md`) para segmentar a inadimplência por perfil."
    )

    taxa_geral = overall_default_rate(df_filtrado)
    good_median, bad_median, gap_pct = median_credit_amount_gap_by_risk(df_filtrado)

    col1, col2, col3 = st.columns(3)
    col1.metric("Taxa de Inadimplência Geral", f"{taxa_geral:.1f}%")
    col2.metric("Crédito Mediano — Bons Pagadores", format_currency_pt_br(good_median))
    col3.metric("Crédito Mediano — Maus Pagadores", format_currency_pt_br(bad_median))

    if pd.notna(gap_pct):
        comparativo = "maior" if gap_pct > 0 else "menor"
        st.info(
            f"💡 **Insight:** maus pagadores pedem um valor mediano **{abs(gap_pct):.1f}% "
            f"{comparativo}** do que bons pagadores no recorte atual. Isso é evidência inicial "
            f"de que o valor solicitado, sozinho, também é um sinal de risco a considerar."
        )
    st.markdown("---")

    st.subheader("Taxa de Inadimplência por Categoria")
    categorical_cols = [c for c in get_categorical_columns(df_filtrado) if c != config.TARGET_COLUMN]
    default_cat = "Credit_history" if "Credit_history" in categorical_cols else categorical_cols[0]
    category_column = st.selectbox(
        "Segmentar por:",
        categorical_cols,
        index=categorical_cols.index(default_cat),
        format_func=lambda x: COLUMN_LABELS.get(x, x),
    )

    rate_table = default_rate_by_category(df_filtrado, category_column)
    st.plotly_chart(default_rate_bar(rate_table, category_column), use_container_width=True)

    highlight = highest_risk_segment(rate_table, category_column)
    if highlight:
        segment, rate = highlight
        st.info(
            f"💡 **Insight:** dentro das categorias com amostra suficiente (≥ 20 solicitantes), "
            f"**{segment}** tem a maior taxa de inadimplência: **{rate:.1f}%**, "
            f"{'acima' if rate > taxa_geral else 'abaixo'} da média geral de {taxa_geral:.1f}%."
        )
    st.markdown("---")

    st.subheader("Perfil Numérico: Bons x Maus Pagadores")
    numeric_cols = get_numeric_columns(df_filtrado)
    default_numeric = AGE_COL if AGE_COL in numeric_cols else numeric_cols[0]
    numeric_column = st.selectbox(
        "Comparar variável:",
        numeric_cols,
        index=numeric_cols.index(default_numeric),
        format_func=lambda x: COLUMN_LABELS.get(x, x),
        key="risk_numeric_col",
    )
    c_left, c_right = st.columns([2, 1])
    with c_left:
        st.plotly_chart(
            numeric_by_risk_boxplot(df_filtrado, numeric_column, config.TARGET_COLUMN),
            use_container_width=True,
        )
    with c_right:
        profile = numeric_profile_by_risk(df_filtrado, numeric_column)
        st.dataframe(profile.style.format("{:.1f}"), use_container_width=True)


def render_models_tab(df: pd.DataFrame) -> None:
    """
    Usa o dataset completo (não o filtrado pela sidebar), de propósito: os
    modelos precisam da maior amostra disponível para estimativas mais
    estáveis. Ver aviso na barra lateral.
    """
    st.subheader("🔬 Regressões, Efeitos Não-Lineares e Diagnósticos")
    st.markdown(
        "Evolução dos modelos: da regressão simples para a polinomial (Idade²), "
        "com diagnóstico das premissas antes de confiar no p-valor."
    )

    tab1, tab2 = st.tabs(
        ["1. Valor do Empréstimo (Regressão Linear)", "2. Número de Empréstimos (Regressão de Poisson)"]
    )

    with tab1:
        st.markdown("### Variável Alvo: Valor do Empréstimo (Contínua)")
        simples, quad = fit_credit_amount_models(df)
        col_m1, col_m2 = st.columns(2)

        with col_m1:
            st.info(f"**Modelo 1: {simples.label}**")
            st.markdown(f"Fórmula: `{simples.formula}`")
            st.metric("P-Valor (Idade)", f"{simples.age_pvalue:.4f}")
            st.metric("Critério AIC (menor é melhor)", f"{simples.aic:.1f}")

        with col_m2:
            st.success(f"**Modelo 2: {quad.label}**")
            st.markdown(f"Fórmula: `{quad.formula}`")
            st.metric("P-Valor (Idade²)", f"{quad.age_sq_pvalue:.4f}")
            st.metric("Critério AIC (menor é melhor)", f"{quad.aic:.1f}")

        st.markdown("#### Diagnóstico dos Modelos (OLS)")
        st.write(
            f"- **Comparação (AIC):** o modelo com menor AIC se ajusta melhor aos dados. "
            f"Simples: {simples.aic:.1f} vs. Quadrático: {quad.aic:.1f}."
        )
        st.write(f"- **Normalidade dos Resíduos (Jarque-Bera p-valor):** {quad.jarque_bera_pvalue:.4e}")
        if quad.residuals_are_normal:
            st.success("DIAGNÓSTICO OK: resíduos normais, os p-valores das idades são confiáveis.")
        else:
            st.error(
                "ALERTA DE DIAGNÓSTICO: p-valor do Jarque-Bera abaixo de 0.05. Os resíduos não "
                "são normais, então os p-valores da Idade acima não são 100% confiáveis "
                "(o modelo falhou na premissa de normalidade)."
            )

    with tab2:
        st.markdown("### Variável Alvo: Número de Empréstimos (Contagem Discreta)")
        simples, quad = fit_num_credits_models(df)
        col_m3, col_m4 = st.columns(2)

        with col_m3:
            st.info(f"**Modelo 3: {simples.label}**")
            st.markdown(f"Fórmula: `{simples.formula}`")
            st.metric("P-Valor (Idade)", f"{simples.age_pvalue:.4f}")
            st.metric("Critério AIC", f"{simples.aic:.1f}")

        with col_m4:
            st.success(f"**Modelo 4: {quad.label}**")
            st.markdown(f"Fórmula: `{quad.formula}`")
            st.metric("P-Valor (Idade²)", f"{quad.age_sq_pvalue:.4f}")
            st.metric("Critério AIC", f"{quad.aic:.1f}")

        st.markdown("#### Diagnóstico dos Modelos (Poisson)")
        st.write(
            "- Na regressão de Poisson, a média deve ser igual à variância. Avaliamos isso pela "
            "razão de dispersão de Pearson (Pearson Chi² / graus de liberdade). O valor ideal é 1.0."
        )
        st.write(f"- Dispersão Modelo Simples: **{simples.dispersion_ratio:.3f}**")
        st.write(f"- Dispersão Modelo Quadrático: **{quad.dispersion_ratio:.3f}**")

        if quad.has_overdispersion:
            st.error(
                "ALERTA DE DIAGNÓSTICO: há superdispersão (> 1.2). O Poisson clássico está "
                "falhando em capturar a variância dos dados. O ideal seria evoluir para uma "
                "Regressão Binomial Negativa para que os p-valores fossem confiáveis."
            )
        else:
            st.success("DIAGNÓSTICO OK: sem superdispersão severa. A premissa está razoavelmente válida.")


def main() -> None:
    try:
        df = _load_data()
    except FileNotFoundError as exc:
        st.error(f"Erro ao carregar os dados: {exc}")
        st.stop()
        return

    render_header()
    escolha = render_sidebar_filters(df)
    df_filtrado = df[df[PURPOSE_COL].isin(escolha)]

    if df_filtrado.empty:
        st.warning("Por favor, selecione ao menos um objetivo de crédito para visualizar os dados.")
        st.stop()
        return

    tab_overview, tab_profile, tab_risk, tab_models = st.tabs(
        ["📈 Visão Geral", "🧑‍🤝‍🧑 Perfil & Correlações", "⚠️ Análise de Risco", "🔬 Modelos Estatísticos"]
    )

    with tab_overview:
        render_overview_tab(df_filtrado, st.session_state.get("metricas_selecionadas", []))
    with tab_profile:
        render_profile_tab(df, df_filtrado)
    with tab_risk:
        render_risk_tab(df_filtrado)
    with tab_models:
        render_models_tab(df)


if __name__ == "__main__":
    main()
