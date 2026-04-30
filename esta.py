import streamlit as st
import pandas as pd
import plotly.express as px

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
    st.markdown(f"**Aluno:**  Alexandre Vital   |   UFSJ   |   ESTATÍSTICA E PROBABILIDADE ")
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
        
    # escolha dinâmica das medidas-resumo que irão compor a tabela estatística
    metricas_selecionadas = st.sidebar.multiselect(
        "Escolha as Medidas-Resumo",
        options=list(traducoes.keys()), 
        format_func=lambda x: traducoes[x],
        default=['mean', 'median', 'std', 'count']
    )

    # aplica o filtro ao dataframe mantendo apenas as categorias escolhidas
    df_filtrado = df[df['Purpose_of_the_credit'].isin(escolha)]

    # informacoes de topo divididas em 3 colunas para otimização do espaço na tela
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

    # respondendo à pergunta
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
    title="Dispersão: Idade vs Valor do Crédito",
    labels=dicionario_colunas 
)
    st.plotly_chart(fig_scatter, use_container_width=True)

    with st.expander("Interpretação do Gráfico (Insights)"):
        st.markdown("""
        * **Concentração Jovem:** Existe uma densidade muito alta de pedidos feitos por clientes entre 20 e 35 anos, gerando um aglomerado na parte esquerda do gráfico.
        * **Picos Isolados:** Embora a maioria dos pedidos de alto valor (acima de € 10.000) sejam para categorias específicas como "negócios" (business) ou "carros", vemos que a idade nesses picos varia bastante.
        * **Conclusão Inicial:** A idade, de forma isolada, não dita *exatamente* o valor do empréstimo (a dispersão é grande), mas dita fortemente a *frequência* das categorias solicitadas.
        """)
    st.markdown("---")

    # antes aqui só mostrava o histograma do perfil de idade, agora o usuário pode utilizar qualquer coluna do dataset
    # verificando automaticamente se é número ou texto, e criando um histograma ou gráfico de barras agrupado, de acordo com o que foi selecionado
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