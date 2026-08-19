# Metodologia

Este documento detalha as decisões estatísticas e de engenharia de dados por
trás do dashboard, complementando o `README.md` (que foca em "como rodar").

## 1. Dataset

O dataset é uma adaptação do **German Credit Data** (Statlog), amplamente
usado em estudos de risco de crédito. Contém **1.000 observações** e **20
variáveis** (demográficas, financeiras e de histórico bancário), mais um
identificador `id`.

### 1.1. Observação sobre nomenclatura de colunas

Durante a refatoração, identificamos que a coluna `Status_of_existing_checking_account`
**não contém** o status da conta corrente (como o nome sugere), mas sim os
valores `good` / `bad` — ou seja, funciona como a variável de **risco de
crédito** (o alvo/target clássico do German Credit Data, normalmente chamado
de `Risk` ou `Class`).

Optamos por **não renomear a coluna silenciosamente**, para não mascarar uma
inconsistência real do arquivo de dados fornecido. Em vez disso:

- Documentamos o problema aqui e em `src/config.py` (`TARGET_COLUMN`).
- Traduzimos o rótulo de exibição para "Classificação de Risco (Bom/Mau
  Pagador)" em `src/translations.py`, refletindo o conteúdo real da coluna.
- Os valores `good`/`bad` são traduzidos para "Bom pagador" / "Mau pagador".

Isso é citado propositalmente como exemplo do tipo de inconsistência que
qualquer pipeline de dados real deve validar antes de seguir para modelagem.

## 2. Pipeline de ETL (`src/data_loader.py`)

1. **Leitura** do CSV bruto (`data/dataset.csv`), mantido em inglês para
   preservar a reprodutibilidade em relação ao German Credit Data original.
2. **Normalização de nomes de coluna**: espaços, parênteses e barras são
   convertidos para `snake_case` seguro (ex.: `"Other installment plans
   (banks/stores)"` → `Other_installment_plans_banks_stores`), o que evita
   quebras em fórmulas do `statsmodels` (que usa `patsy` e é sensível a
   caracteres especiais em nomes de variável).
3. **Tradução de valores categóricos**: os valores em inglês são traduzidos
   para português em memória, via `DataFrame.replace()`. O arquivo em disco
   nunca é alterado.

Essas três etapas são funções puras (sem dependência do Streamlit), o que
permite testá-las isoladamente — ver `tests/test_data_loader.py`.

## 3. Perguntas de pesquisa

1. Qual o perfil demográfico e financeiro dos solicitantes que pedem os
   maiores volumes de crédito?
2. Como a idade influencia o valor do crédito solicitado?
3. A relação entre idade e valor do crédito é melhor descrita por uma reta ou
   por uma curva (efeito não linear)?
4. O número de créditos já existentes no banco varia com a idade, e esse
   efeito seria mais bem modelado como uma contagem (Poisson) do que como
   uma variável contínua?

## 4. Modelos estatísticos (`src/stats_models.py`)

### 4.1. Valor do crédito (variável contínua) — Regressão OLS

| Modelo | Fórmula |
|---|---|
| Simples | `Credit_amount ~ Age_in_years` |
| Polinomial | `Credit_amount ~ Age_in_years + I(Age_in_years**2)` |

**Comparação:** feita pelo critério de informação de Akaike (AIC) — menor é
melhor.

**Diagnóstico:** teste de **Jarque-Bera** para normalidade dos resíduos. Se o
p-valor for menor que 0.05, a premissa de normalidade dos resíduos é
rejeitada, e os p-valores dos coeficientes (incluindo o de Idade) deixam de
ser totalmente confiáveis — mesmo que estatisticamente "significativos" à
primeira vista.

### 4.2. Número de créditos existentes (variável de contagem) — Regressão de Poisson

| Modelo | Fórmula |
|---|---|
| Simples | `Number_of_existing_credits_at_this_bank ~ Age_in_years` |
| Polinomial | `Number_of_existing_credits_at_this_bank ~ Age_in_years + I(Age_in_years**2)` |

**Diagnóstico:** razão de dispersão de Pearson (soma dos resíduos de Pearson
ao quadrado dividida pelos graus de liberdade). O valor ideal é próximo de
1.0, pois a Poisson assume que média e variância são iguais
(*equidispersão*). Valores acima de **1.2** (limiar definido em
`DISPERSION_ALERT_THRESHOLD`) indicam superdispersão — sinal de que um
modelo Binomial Negativo seria mais adequado.

## 5. Análise de risco (`src/risk_analysis.py`)

Com a identificação da coluna de risco (seção 1.1), o dashboard passou a
calcular, na aba **Análise de Risco**:

- **Taxa de inadimplência geral** e **por segmento** (moradia, histórico de
  crédito, emprego, objetivo do crédito etc.), com o tamanho de amostra de
  cada categoria exibido lado a lado com a taxa — uma taxa "alta" calculada
  sobre 5 observações não tem o mesmo peso que uma calculada sobre 500.
- **Destaque da categoria de maior risco**, mas apenas entre categorias com
  amostra mínima confiável (`MIN_SAMPLE_SIZE_FOR_HIGHLIGHT = 20`), para
  evitar apontar uma categoria pequena como "mais arriscada" só por acaso
  amostral.
- **Comparação de perfil numérico** (idade, valor do crédito, duração etc.)
  entre bons e maus pagadores, via boxplot e tabela de média/mediana.

Essa análise é **descritiva**, não preditiva: não há um modelo de
classificação de risco treinado — apenas segmentação e comparação de
grupos. Um passo natural de evolução seria treinar um classificador (ex.:
regressão logística) para estimar a probabilidade de inadimplência de um
novo solicitante — ver "Possíveis evoluções" no `README.md`.

## 6. Insights narrativos (`src/insights.py`)

Os textos de interpretação exibidos ao lado dos gráficos (ex.: força da
correlação idade x valor, objetivo de crédito com maior volume) **não são
textos fixos**: são montados a partir de números recalculados a cada
filtro aplicado pelo usuário, usando funções puras e testadas
isoladamente. Isso evita a armadilha comum de um dashboard "storytelling"
ficar com uma afirmação desatualizada assim que o recorte de dados muda.

## 7. Limitações conhecidas

- **Escopo do filtro:** os modelos de regressão usam o dataset completo, não
  o recorte filtrado na barra lateral — isso é intencional (mais poder
  estatístico), e está documentado no docstring de
  `app.render_inferential_section`.
- **Causalidade:** os modelos descrevem associação, não causalidade. A idade
  provavelmente atua como *proxy* de outras variáveis (tempo de emprego,
  estabilidade financeira) não incluídas nos modelos univariados aqui
  apresentados.
- **Superdispersão não corrigida:** quando detectada, o dashboard apenas
  alerta sobre o problema — não ajusta automaticamente um modelo Binomial
  Negativo. Isso é proposto como próximo passo (ver `README.md`).
- **Tradução parcial:** o dicionário de tradução cobre os valores conhecidos
  no dataset atual; um valor novo e desconhecido simplesmente permanece em
  inglês (comportamento padrão do `DataFrame.replace()`), em vez de falhar
  silenciosamente.
