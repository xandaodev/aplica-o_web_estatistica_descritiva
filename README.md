# 📊 Credit Risk Analytics

Dashboard interativo de análise exploratória e inferencial de risco de
crédito, construído em **Python + Streamlit**, com base numa adaptação do
clássico dataset **German Credit Data**.

Projeto desenvolvido originalmente para a disciplina de Estatística e
Probabilidade (UFSJ) e posteriormente refatorado para seguir boas práticas
de engenharia de software: separação de camadas, tipagem, testes
automatizados e documentação.

## ✨ Funcionalidades

- **Dashboard em abas**: Visão Geral, Perfil & Correlações, Análise de
  Risco e Modelos Estatísticos — cada uma com um objetivo analítico claro,
  em vez de um scroll único.
- **Insights narrativos calculados em tempo real**: cada gráfico principal
  vem acompanhado de uma frase de interpretação (ex.: força da correlação,
  categoria de maior risco, diferença de ticket entre bons e maus
  pagadores) — recalculada a cada filtro aplicado, nunca um texto fixo.
- **Análise de risco de crédito**: a coluna de status da conta corrente do
  dataset original contém, na prática, o rótulo de risco do solicitante
  (bom/mau pagador — achado documentado em `docs/METODOLOGIA.md`). A partir
  disso, o dashboard calcula taxa de inadimplência geral e por segmento
  (moradia, histórico de crédito, emprego etc.), com destaque para
  categorias de maior risco (respeitando um tamanho mínimo de amostra).
- **KPIs da carteira**: total de pedidos, valor total solicitado, ticket
  médio, idade média e taxa de inadimplência, recalculados dinamicamente.
- **Exploração dinâmica**: o usuário escolhe qualquer variável do dataset
  e o dashboard renderiza automaticamente o gráfico mais adequado
  (histograma sobreposto para variáveis numéricas, barras agrupadas para
  categóricas).
- **Visualizações**: dispersão com marginais (violino + histograma) e linha
  de tendência OLS, boxplots para outliers, mapa de correlação entre
  variáveis numéricas, gráfico de pizza de participação por objetivo.
- **Estatística inferencial**: 4 modelos de regressão (OLS simples e
  polinomial para valor do crédito; Poisson simples e polinomial para
  número de créditos existentes), cada um com diagnóstico automático das
  premissas estatísticas (normalidade dos resíduos via Jarque-Bera;
  superdispersão via razão de Pearson).
- **ETL com tradução**: os dados originais permanecem em inglês no CSV
  (reprodutibilidade), mas são traduzidos para português em tempo de
  execução para exibição.
- **Tema escuro customizado**, com paleta de cores consistente entre todos
  os gráficos (Plotly) e os componentes nativos do Streamlit.

## 🏗️ Arquitetura

O projeto é dividido em camadas para manter a lógica de negócio
independente da interface — o que também torna o código testável sem
precisar rodar um servidor Streamlit:

```
app.py                 → Camada de UI: orquestra abas, widgets e layout do Streamlit
src/
├── config.py           → Paths e constantes centralizadas
├── data_loader.py       → ETL: leitura, normalização e tradução (puro, sem Streamlit)
├── translations.py      → Dicionários de tradução (colunas, valores, métricas)
├── stats_models.py      → Ajuste de modelos estatísticos e diagnósticos
├── risk_analysis.py     → Taxa de inadimplência geral e por segmento
├── insights.py          → Números usados nos textos narrativos (correlações, gaps etc.)
├── visualizations.py    → Construção dos gráficos Plotly (funções puras, tema escuro)
└── formatting.py        → Formatação de números/moeda no padrão pt-BR
tests/                  → Testes automatizados (pytest) para cada camada
docs/
└── METODOLOGIA.md       → Discussão estatística detalhada e limitações
data/
└── dataset.csv          → Dataset (German Credit Data adaptado)
.streamlit/
└── config.toml          → Tema escuro customizado
```

**Regra geral:** `app.py` não deve conter lógica de ETL, estatística ou
construção de gráfico — apenas chama funções de `src/` e organiza o layout.
Isso permite, por exemplo, reaproveitar os modelos estatísticos em um
notebook ou script de linha de comando sem precisar do Streamlit.

## 🚀 Como executar

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd credit-risk-analytics

# 2. Crie um ambiente virtual (recomendado)
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode o dashboard
streamlit run app.py
```

O app abre em `http://localhost:8501`.

## ✅ Testes

O projeto tem testes automatizados para as camadas de dados, estatística e
visualização:

```bash
pytest
```

```bash
# Com relatório de cobertura
pytest --cov=src
```

## 🚀 Tecnologias

- **Python 3.10+**
- **Streamlit** — interface web e interatividade
- **Pandas** — ETL e manipulação de dados
- **Plotly Express** — gráficos interativos
- **statsmodels** — regressão OLS e Poisson, testes de diagnóstico
- **pytest** — testes automatizados

## 📖 Metodologia

A discussão estatística completa — perguntas de pesquisa, modelos usados,
critérios de diagnóstico e limitações conhecidas (incluindo uma
inconsistência de nomenclatura encontrada no dataset original) — está em
[`docs/METODOLOGIA.md`](docs/METODOLOGIA.md).

## 🗺️ Possíveis evoluções

- [ ] Treinar um modelo de classificação (ex.: regressão logística) para
      prever a probabilidade de inadimplência, além das taxas descritivas
      já calculadas na aba de risco.
- [ ] Ajustar automaticamente um modelo Binomial Negativo quando houver
      superdispersão significativa no modelo de Poisson.
- [ ] Adicionar modelo multivariado (idade + tempo de emprego + moradia) para
      reduzir viés de variável omitida.
- [ ] Exportar o resumo estatístico filtrado para CSV/Excel direto da UI.
- [ ] Deploy no Streamlit Community Cloud com link público.

## 👤 Autor

**Alexandre Vital** — Estatística e Probabilidade, UFSJ
Professor: Davi Butturi Alvim

## 📄 Licença

Distribuído sob a licença MIT. Veja [`LICENSE`](LICENSE) para mais detalhes.
