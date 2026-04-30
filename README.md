# 🏦 Dashboard de Análise de Crédito - Estatística UFSJ

Este projeto foi desenvolvido como parte da disciplina de Estatística e Probabilidade na **Universidade Federal de São João del-Rei (UFSJ)**.

## 📊 Sobre o Projeto
O objetivo é fornecer uma ferramenta interativa para análise exploratória de dados de crédito bancário, utilizando uma adaptação do clássico dataset *German Credit Data*. O dashboard permite visualizar a dispersão de valores, o perfil financeiro/demográfico dos tomadores e extrair medidas-resumo customizáveis, buscando correlações (como a influência da idade no valor do empréstimo).

## ✨ Funcionalidades Adicionadas
* **Exploração Dinâmica:** O usuário pode selecionar qualquer variável do dataset (Moradia, Emprego, Histórico de Crédito, etc.) e o sistema renderiza automaticamente o gráfico mais adequado (Histograma sobreposto para dados numéricos ou Barras agrupadas para dados categóricos).
* **Tradução de Dados (Processo de ETL):** As colunas e os dados categóricos originais em inglês são mantidos intactos no arquivo `.csv` para reprodutibilidade, mas são traduzidos *on-the-fly* (em tempo de execução) para o português utilizando dicionários do Pandas e do Plotly.
* **Visualizações Avançadas:** Utilização de Gráficos de Dispersão com representações marginais (violino e histograma), Boxplots para análise de outliers e Gráficos de Pizza.
* **Filtros Otimizados:** Interface melhorada com *checkbox* para manipulação rápida de categorias ("Selecionar Todos").

## 🚀 Tecnologias Utilizadas
* **Python 3.x**
* **Streamlit** (Interface Web e Interatividade)
* **Pandas** (Manipulação de Dados, ETL e Medidas-Resumo)
* **Plotly Express** (Gráficos Interativos)

## 🛠️ Como executar
1. Instale as dependências: 
```bash
pip install -r requirements.txt

2. Execute o app: `streamlit run esta.py`