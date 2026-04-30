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

    # contextualizacao
    with st.expander("Contextualização e Objetivo da Análise (Clique para expandir)", expanded=False):
        st.markdown("""
        **História dos Dados:**
        Este conjunto de dados é uma adaptação do clássico *German Credit Data*. Ele contém informações demográficas, financeiras e de histórico bancário de 1.000 solicitantes de crédito de um banco alemão. Ele é amplamente utilizado para entender padrões de risco e concessão de crédito.
        
        **Pergunta de Interesse:**
        > *Qual é o perfil demográfico e financeiro dos clientes que solicitam os maiores volumes de crédito, e como a idade do solicitante influencia o valor e a finalidade do empréstimo solicitado?*
        """)
    st.markdown("---")

    # barra lateral (filtros e UI melhorada)
    st.sidebar.header("🛠️ Configurações e Filtros")
    objetivos_disponiveis = df['Purpose_of_the_credit'].unique().tolist()
    
    # botão para selecionar/remover todos rapidamente
    selecionar_todos = st.sidebar.checkbox("Selecionar Todos os Objetivos", value=True)
    
    if selecionar_todos:
        escolha = st.sidebar.multiselect("Filtrar Objetivos", objetivos_disponiveis, default=objetivos_disponiveis)
    else:
        escolha = st.sidebar.multiselect("Filtrar Objetivos", objetivos_disponiveis, default=[])
        
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
    st.subheader("📈 Distribuição e Dispersão (Insights Iniciais)")
    
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("**Participação por Objetivo de Crédito**")
        fig_pizza = px.pie(df_filtrado, names='Purpose_of_the_credit', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with c_right:
        st.markdown("**Boxplot: Dispersão e Outliers de Valores**")
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

    # RESPONDENDO À PERGUNTA
    st.subheader("A quantidade de empréstimo por categoria muda de acordo com a idade?")
    st.markdown("O Gráfico de Dispersão abaixo nos permite cruzar a Idade do cliente com o Valor solicitado, buscando correlações.")
    
    fig_scatter = px.scatter(
        df_filtrado, 
        x='Age_in_years', 
        y='Credit_amount', 
        color='Purpose_of_the_credit',
        opacity=0.7,
        marginal_y="violin",
        marginal_x="histogram",
        title="Dispersão: Idade vs Valor do Crédito"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    with st.expander("Interpretação do Gráfico (Insights)"):
        st.markdown("""
        * **Concentração Jovem:** Existe uma densidade muito alta de pedidos feitos por clientes entre 20 e 35 anos, gerando um aglomerado na parte esquerda do gráfico.
        * **Picos Isolados:** Embora a maioria dos pedidos de alto valor (acima de € 10.000) sejam para categorias específicas como "negócios" (business) ou "carros", vemos que a idade nesses picos varia bastante.
        * **Conclusão Inicial:** A idade, de forma isolada, não dita *exatamente* o valor do empréstimo (a dispersão é grande), mas dita fortemente a *frequência* das categorias solicitadas.
        """)
    st.markdown("---")

    # perfil de idade
    st.subheader("Perfil de Idade")
    fig_hist = px.histogram(df_filtrado, x='Age_in_years', color='Purpose_of_the_credit', barmode='overlay')
    st.plotly_chart(fig_hist, use_container_width=True)

except Exception as e:
    st.error(f"Erro: Verifique se 'dataset.csv' está na pasta. Detalhe: {e}")