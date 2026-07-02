import streamlit as st
import pandas as pd
import plotly.express as px
import statsmodels.formula.api as smf
import statsmodels.stats.api as sms 
import numpy as np 

# configuração e carregamento inicial da página
st.set_page_config(page_title="Estatística UFSJ - Crédito", layout="wide")

# armazena os dados em cache para não recarregar o arquivo csv a cada interação do usuário
@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv")
    # limpando nomes das colunas
    df.columns = [col.replace(' ', '_').replace('/', '_').replace('(', '_').replace(')', '') for col in df.columns]
    
    # substitui todos os valores em inglês pelos de português em todo o dataframe de uma vez só
    df = df.replace(dicionario_valores)
    
    return df

# traduzindo as métricas para exibição na tabela
traducoes = {
    'mean': 'Média',
    'median': 'Mediana',
    'std': 'Desvio Padrão',
    'min': 'Mínimo',
    'max': 'Máximo',
    'count': 'Quantidade'
}

# dicionário para traduzir a interface 
# garante que os dados sejam apresentados em português sem alterar a estrutura do arquivo csv original
dicionario_colunas = {
    'Age_in_years': 'Idade (anos)',
    'Credit_amount': 'Valor do Crédito (€)',
    'Duration_in_months': 'Duração do Empréstimo (meses)',
    'Purpose_of_the_credit': 'Objetivo do Crédito',
    'Sex_&_Marital_Status': 'Sexo e Estado Civil',
    'Housing': 'Moradia',
    'Job': 'Emprego',
    'Saving_accounts': 'Conta Poupança',
    'Checking_account': 'Conta Corrente',
    'Credit_history': 'Histórico de Crédito',
    
    'Other_installment_plans_(banks/stores)': 'Outros Planos de Parcelamento',
    'Other_installment_plans__banks_stores_': 'Outros Planos de Parcelamento', 
    'Number_of_existing_credits_at_this_bank': 'Qtd. de Créditos Existentes (Neste Banco)',
    'Number_of_people_being_liable_to_provide_maintenance_for': 'Número de Dependentes',
    'Telephone': 'Telefone',
    'Foreign_worker': 'Trabalhador Estrangeiro',
    'Status_of_existing_checking_account': 'Status da Conta Corrente',
    'Present_employment_since': 'Tempo no Emprego Atual',
    'Installment_rate_in_percentage_of_disposable_income': 'Taxa da Parcela (% da Renda)',
    'Present_residence_since': 'Tempo na Residência Atual',
    'Property': 'Propriedades / Bens',
    'Other_debtors_/_guarantors': 'Outros Devedores / Fiadores',
    'Risk': 'Risco de Crédito',

    'Status_of_savings_account_bonds': 'Status da Poupança / Títulos',
    'Present_employment_years': 'Tempo de Emprego (anos)',
    'personal_status': 'Estado Civil / Status Pessoal',
    'Present_residence_since_X_years': 'Tempo de Residência (anos)',
    
    'Status_of_savings_account/bonds': 'Status da Poupança / Títulos',
    'Present_employment(years)': 'Tempo de Emprego (anos)'
}

# dicionário para traduzir os dados internos das categorias
dicionario_valores = {
    'skilled': 'Qualificado',
    'unskilled resident': 'Não qualificado (Residente)',
    'high qualif/self emp/mgmt': 'Alta qualificação / Autônomo',
    'unemp/unskilled non res': 'Desempregado / Não qualificado (Não res.)',
    
    'radio/tv': 'Rádio/TV',
    'education': 'Educação',
    'furniture/equipment': 'Móveis/Equipamentos',
    'car': 'Carro',
    'business': 'Negócios',
    'domestic appliances': 'Eletrodomésticos',
    'repairs': 'Reparos',
    'vacation/others': 'Férias/Outros'
    
}

try:
    df = load_data()
    
    st.title("Dashboard de Crédito: Análise Estatística")
    st.markdown(f"**Aluno:** Alexandre Vital   |   UFSJ   |   ESTATÍSTICA E PROBABILIDADE ")
    st.markdown(f"Professor: Davi Butturi Alvim")
    st.markdown("---")

    # contextualizacao dos dados iniciais
    with st.expander("Contextualização e Objetivo da Análise (Clique para expandir)", expanded=False):
        st.markdown("""
        **História dos Dados:**
        Este conjunto de dados é uma adaptação do clássico *German Credit Data*. Ele contém informações demográficas, financeiras e de histórico bancário de 1.000 solicitantes de crédito de um banco alemão. Ele é amplamente utilizado para entender padrões de risco e concessão de crédito.
        
        **Pergunta de Interesse:**
        > *Qual é o perfil demográfico e financeiro dos clientes que solicitam os maiores volumes de crédito, e como a idade do solicitante influencia o valor e a finalidade do empréstimo solicitado?*
        """)
    st.markdown("---")

    # barra lateral (filtros e ui melhorada)
    st.sidebar.header("🛠️ Configurações e Filtros")
    
    # extrai todos os valores unicos da coluna de objetivo para criar as opcoes do filtro
    objetivos_disponiveis = df['Purpose_of_the_credit'].unique().tolist()
    
    # botão para selecionar ou remover todos rapidamente, melhorando a experiencia do usuario
    selecionar_todos = st.sidebar.checkbox("Selecionar Todos os Objetivos", value=True)
    
    # define o estado inicial do filtro com base no checkbox
    if selecionar_todos:
        escolha = st.sidebar.multiselect("Filtrar Objetivos", objetivos_disponiveis, default=objetivos_disponiveis)
    else:
        escolha = st.sidebar.multiselect("Filtrar Objetivos", objetivos_disponiveis, default=[])
        
    metricas_selecionadas = st.sidebar.multiselect(
        "Escolha as Medidas-Resumo",
        options=list(traducoes.keys()), 
        format_func=lambda x: traducoes[x],
        default=['mean', 'median', 'std', 'count']
    )

    # aplica o filtro ao dataframe mantendo apenas as categorias escolhidas
    df_filtrado = df[df['Purpose_of_the_credit'].isin(escolha)]

    if df_filtrado.empty:
        st.warning("Por favor, selecione ao menos um objetivo de crédito para visualizar os dados.")
        st.stop()

    # informacoes de topo
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Pedidos", len(df_filtrado))
    col2.metric("Média de Valor", f"€ {df_filtrado['Credit_amount'].mean():.2f}")
    col3.metric("Idade Média", f"{df_filtrado['Age_in_years'].mean():.1f} anos")
    st.markdown("---")

    # distribuição e dispersão
    st.subheader("Distribuição e Dispersão (Insights Iniciais)")
    
    # renderiza dois graficos um do lado do outro para analise comparativa inicial
    c_left, c_right = st.columns(2)
    with c_left:
        st.markdown("**Participação por Objetivo de Crédito**")
        fig_pizza = px.pie(df_filtrado, names='Purpose_of_the_credit', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel, labels=dicionario_colunas)
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with c_right:
        st.markdown("**Boxplot: Dispersão e Outliers de Valores**")
        fig_box = px.box(df_filtrado, x='Purpose_of_the_credit', y='Credit_amount', color='Purpose_of_the_credit', labels=dicionario_colunas)
        st.plotly_chart(fig_box, use_container_width=True)

    # tabela estatística
    st.subheader("Resumo Estatístico Dinâmico")
    if metricas_selecionadas:
        # agrupa os dados filtrados pela categoria e aplica as funcoes estatisticas escolhidas na barra lateral
        resumo = df_filtrado.groupby('Purpose_of_the_credit')['Credit_amount'].agg(metricas_selecionadas)
        resumo = resumo.rename(columns=traducoes)
        resumo.index.name = "Objetivo do Crédito"
        st.dataframe(resumo.style.format("{:.2f}").background_gradient(cmap='Blues'), use_container_width=True)
    else:
        st.warning("Selecione ao menos uma métrica na barra lateral.")
    st.markdown("---")

    # respondendo à pergunta visualmente
    st.subheader("A quantidade de empréstimo por categoria muda de acordo com a idade?")
    st.markdown("O Gráfico de Dispersão abaixo nos permite cruzar a Idade do cliente com o Valor solicitado, buscando correlações visuais.")
    
    fig_scatter = px.scatter(
        df_filtrado, 
        x='Age_in_years', 
        y='Credit_amount', 
        color='Purpose_of_the_credit',
        opacity=0.7,
        marginal_y="violin",
        marginal_x="histogram",
        trendline="ols", # adiciona a linha de regressão visual
        title="Dispersão: Idade vs Valor do Crédito (com Linhas de Tendência)",
        labels=dicionario_colunas 
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown("---")


    # ESTATÍSTICA INFERENCIAL - REGRESSÕES E DIAGNÓSTICOS (NOVO)

    
    st.subheader("🔬 Análise Inferencial: Regressões, Efeitos Não-Lineares e Diagnósticos")
    st.markdown("Evolução dos modelos: Passando da regressão simples para polinomial (Idade²) e diagnosticando a validade antes de confiar no P-valor.")

    import numpy as np #necessário para a transformação quadrática

    #cria abas para separar bem os 4 modelos exigidos
    tab1, tab2 = st.tabs(["1. Valor do Empréstimo (Regressão Linear)", "2. Número de Empréstimos (Regressão de Poisson)"])

    with tab1:
        st.markdown("### Variável Alvo: Valor do Empréstimo (Contínua)")
        col_m1, col_m2 = st.columns(2)
        
        # Modelo 1: OLS simples
        modelo_valor_simples = smf.ols('Credit_amount ~ Age_in_years', data=df).fit()
        # Modelo 2: OLS polinomial (quadrático)
        modelo_valor_quad = smf.ols('Credit_amount ~ Age_in_years + I(Age_in_years**2)', data=df).fit()

        with col_m1:
            st.info("**Modelo 1: Regressão Linear Simples**")
            st.markdown("Fórmula: `Valor ~ Idade`")
            st.metric("P-Valor (Idade)", f"{modelo_valor_simples.pvalues.get('Age_in_years', 1):.4f}")
            st.metric("Critério AIC (Menor é melhor)", f"{modelo_valor_simples.aic:.1f}")
        
        with col_m2:
            st.success("**Modelo 2: Regressão Polinomial (Idade²)**")
            st.markdown("Fórmula: `Valor ~ Idade + Idade²`")
            st.metric("P-Valor (Idade²)", f"{modelo_valor_quad.pvalues.get('I(Age_in_years ** 2)', 1):.4f}")
            st.metric("Critério AIC (Menor é melhor)", f"{modelo_valor_quad.aic:.1f}")
        
        st.markdown("#### Diagnóstico dos Modelos (OLS):")
        st.write(f"- **Comparação (AIC):** O modelo com menor AIC se ajusta melhor à realidade. AIC Simples: {modelo_valor_simples.aic:.1f} vs AIC Quadrático: {modelo_valor_quad.aic:.1f}.")
        # Teste de Normalidade dos Resíduos (Jarque-Bera)
        jb_pvalue = sms.jarque_bera(modelo_valor_quad.resid)[1]
        st.write(f"- **Normalidade dos Resíduos (Jarque-Bera p-value):** {jb_pvalue:.4e}")
        if jb_pvalue < 0.05:
            st.error("ALERTA DE DIAGNÓSTICO: O p-valor do Jarque-Bera é menor que 0.05. Os resíduos não são normais. Logo, os P-valores da Idade acima não são 100% confiáveis (o modelo falhou na premissa da Normalidade).")
        else:
            st.success("DIAGNÓSTICO OK: Resíduos normais, podemos confiar no P-Valor das idades.")

    with tab2:
        st.markdown("### Variável Alvo: Número de Empréstimos (Contagem Discreta)")
        col_m3, col_m4 = st.columns(2)

        # Modelo 3: poisson simples
        modelo_qtd_simples = smf.poisson('Number_of_existing_credits_at_this_bank ~ Age_in_years', data=df).fit(disp=0)
        # Modelo 4: poisson polinomial (Quadrático)
        modelo_qtd_quad = smf.poisson('Number_of_existing_credits_at_this_bank ~ Age_in_years + I(Age_in_years**2)', data=df).fit(disp=0)

        with col_m3:
            st.info("**Modelo 3: Regressão de Poisson Simples**")
            st.markdown("Fórmula: `N° Empréstimos ~ Idade`")
            st.metric("P-Valor (Idade)", f"{modelo_qtd_simples.pvalues.get('Age_in_years', 1):.4f}")
            st.metric("Critério AIC", f"{modelo_qtd_simples.aic:.1f}")
        
        with col_m4:
            st.success("**Modelo 4: Regressão de Poisson Polinomial**")
            st.markdown("Fórmula: `N° Empréstimos ~ Idade + Idade²`")
            st.metric("P-Valor (Idade²)", f"{modelo_qtd_quad.pvalues.get('I(Age_in_years ** 2)', 1):.4f}")
            st.metric("Critério AIC", f"{modelo_qtd_quad.aic:.1f}")
            
        st.markdown("#### Diagnóstico dos Modelos (Poisson):")
        st.write("- Na regressão de Poisson, a média deve ser igual à variância. Avaliamos isso pelo teste de Superdispersão (Pearson Chi2 / Graus de Liberdade). O valor ideal é 1.0.")
        
        dispersao_simples = sum(modelo_qtd_simples.resid_pearson**2) / modelo_qtd_simples.df_resid
        dispersao_quad = sum(modelo_qtd_quad.resid_pearson**2) / modelo_qtd_quad.df_resid
        
        st.write(f"- Dispersão Modelo Simples: **{dispersao_simples:.3f}**")
        st.write(f"- Dispersão Modelo Quadrático: **{dispersao_quad:.3f}**")
        
        if dispersao_quad > 1.2:
            st.error("ALERTA DE DIAGNÓSTICO: Existe Superdispersão (> 1.2). O modelo de Poisson clássico está falhando em capturar a variância dos dados. O ideal seria evoluir para uma Regressão Binomial Negativa para que os P-Valores fossem confiáveis.")
        else:
            st.success("DIAGNÓSTICO OK: O modelo de Poisson não apresenta superdispersão severa. A premissa está razoavelmente válida.")
            
    st.markdown("---")







    # exploração dinâmica
    st.subheader("🔄 Exploração Dinâmica (Usando todos os dados)")
    st.markdown("Selecione qualquer variável do dataset para visualizar como ela se comporta no nosso conjunto filtrado.")
    
    # pega todas as colunas do dataset
    colunas_disponiveis = df.columns.tolist()
    
    # remove o id da lista de opcoes pois nao possui valor analitico
    if 'id' in colunas_disponiveis:
        colunas_disponiveis.remove('id')
        
    # cria o selectbox com todas as colunas, deixando a idade como padrão ao abrir
    # o format_func utiliza o dicionario para exibir os nomes traduzidos na interface dinamicamente
    var_x = st.selectbox(
        "Selecione a Variável para análise:", 
        colunas_disponiveis, 
        index=colunas_disponiveis.index('Age_in_years'),
        format_func=lambda x: dicionario_colunas.get(x, x)
    )
    
    # logica condicional: verifica o tipo de dado da coluna selecionada para definir o tipo de grafico adequado
    if pd.api.types.is_numeric_dtype(df[var_x]):
        fig_dinamico = px.histogram(df_filtrado, x=var_x, color='Purpose_of_the_credit', barmode='overlay', title=f"Distribuição de {dicionario_colunas.get(var_x, var_x)}", labels=dicionario_colunas)
    else:
        fig_dinamico = px.histogram(df_filtrado, x=var_x, color='Purpose_of_the_credit', barmode='group', title=f"Contagem por {dicionario_colunas.get(var_x, var_x)}", labels=dicionario_colunas)
        
    st.plotly_chart(fig_dinamico, use_container_width=True)

except Exception as e:
    st.error(f"Erro: Verifique se 'dataset.csv' está na pasta. Detalhe: {e}")