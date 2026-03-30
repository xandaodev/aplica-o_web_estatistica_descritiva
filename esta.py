import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração e Carregamento
st.set_page_config(page_title="Estatística UFSJ - Crédito", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv")
    df.columns = [col.replace(' ', '_') for col in df.columns]
    return df

# traduzindo as métricas
traducoes = {
    'mean': 'Média',
    'median': 'Mediana',
    'std': 'Desvio Padrão',
    'min': 'Mínimo',
    'max': 'Máximo',
    'count': 'Quantidade'
}

try:
    df = load_data()
    
    st.title("Dashboard de Crédito: Análise Estatística")
    st.markdown(f"**Aluno:**  Alexandre Vital   |   UFSJ   |   ESTATÍSTICA E PROBABILIDADE ")
    st.markdown(f"Professor: Davi Butturi Alvim")
    st.markdown("---")

    # Barra Lateral
    st.sidebar.header("Configurações")
    objetivos = df['Purpose_of_the_credit'].unique()
    escolha = st.sidebar.multiselect("Filtrar Objetivos", objetivos, default=objetivos[:3])
    
    # escolha de medidas-resumo 
    metricas_selecionadas = st.sidebar.multiselect(
        "Escolha as Medidas-Resumo",
        options=list(traducoes.keys()), 
        format_func=lambda x: traducoes[x],
        default=['mean', 'median', 'std', 'count']
    )

    df_filtrado = df[df['Purpose_of_the_credit'].isin(escolha)]

    # informaçoes de topo
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Pedidos", len(df_filtrado))
    col2.metric("Média de Valor", f"€ {df_filtrado['Credit_amount'].mean():.2f}")
    col3.metric("Idade Média", f"{df_filtrado['Age_in_years'].mean():.1f} anos")
    st.markdown("---")

    # distribuição e dispersão
    c_left, c_right = st.columns(2)
    with c_left:
        st.subheader("Participação por Objetivo")
        fig_pizza = px.pie(df_filtrado, names='Purpose_of_the_credit', hole=0.4)
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with c_right:
        st.subheader("Boxplot: Dispersão de Valores")
        fig_box = px.box(df_filtrado, x='Purpose_of_the_credit', y='Credit_amount', color='Purpose_of_the_credit')
        st.plotly_chart(fig_box, use_container_width=True)

    # tabela estatística
    st.subheader("Resumo Estatístico Dinâmico")
    if metricas_selecionadas:
        resumo = df_filtrado.groupby('Purpose_of_the_credit')['Credit_amount'].agg(metricas_selecionadas)
        resumo = resumo.rename(columns=traducoes)
        resumo.index.name = "Objetivo do Crédito"
        st.dataframe(resumo.style.format("{:.2f}").background_gradient(cmap='Blues'), use_container_width=True)
    else:
        st.warning("Selecione ao menos uma métrica na barra lateral.")

    # perfil de idade
    st.subheader("Perfil de Idade")
    fig_hist = px.histogram(df_filtrado, x='Age_in_years', color='Purpose_of_the_credit', barmode='overlay')
    st.plotly_chart(fig_hist, use_container_width=True)

except Exception as e:
    st.error(f"Erro: Verifique se 'dataset.csv' está na pasta. Detalhe: {e}")