"""
Dicionários de tradução (inglês -> português) usados para exibição.

Importante: a tradução acontece apenas na camada de apresentação.
O dataset em disco (data/dataset.csv) permanece intacto, em inglês,
para preservar a reprodutibilidade e a compatibilidade com o
German Credit Data original.
"""

# Métricas estatísticas (usadas em groupby/agg e nos seletores da sidebar)
METRIC_LABELS = {
    "mean": "Média",
    "median": "Mediana",
    "std": "Desvio Padrão",
    "min": "Mínimo",
    "max": "Máximo",
    "count": "Quantidade",
}

# Nomes de colunas (após normalização feita em data_loader.normalize_column_names)
COLUMN_LABELS = {
    "Age_in_years": "Idade (anos)",
    "Credit_amount": "Valor do Crédito (€)",
    "Duration_in_months": "Duração do Empréstimo (meses)",
    "Purpose_of_the_credit": "Objetivo do Crédito",
    "Sex_&_Marital_Status": "Sexo e Estado Civil",
    "Housing": "Moradia",
    "Job": "Emprego",
    "Saving_accounts": "Conta Poupança",
    "Checking_account": "Conta Corrente",
    "Credit_history": "Histórico de Crédito",
    "Other_installment_plans_banks_stores": "Outros Planos de Parcelamento",
    "Number_of_existing_credits_at_this_bank": "Qtd. de Créditos Existentes (Neste Banco)",
    "Number_of_people_being_liable_to_provide_maintenance_for": "Número de Dependentes",
    "Telephone": "Telefone",
    "Foreign_worker": "Trabalhador Estrangeiro",
    "Status_of_existing_checking_account": "Classificação de Risco (Bom/Mau Pagador)",
    "Present_employment_years": "Tempo de Emprego (anos)",
    "personal_status": "Estado Civil / Status Pessoal",
    "Present_residence_since_X_years": "Tempo de Residência (anos)",
    "Status_of_savings_account_bonds": "Status da Poupança / Títulos",
    "Present_employment_years_": "Tempo de Emprego (anos)",
    "Installment_rate_in_percentage_of_disposable_income": "Taxa da Parcela (% da Renda)",
    "Other_debtors_guarantors": "Outros Devedores / Fiadores",
    "Property": "Propriedades / Bens",
}

# Valores categóricos. Agrupados por coluna de origem para facilitar manutenção
# (o dataframe é traduzido com um único dicionário "achatado" em tempo de execução,
# veja translations.flatten_value_translations()).
_CREDIT_HISTORY = {
    "critical/other existing credit": "Crítico / outros créditos existentes",
    "existing paid": "Créditos existentes quitados em dia",
    "delayed previously": "Atraso no passado",
    "no credits/all paid": "Sem créditos / tudo quitado",
    "all paid": "Tudo quitado",
}

_PURPOSE = {
    "radio/tv": "Rádio/TV",
    "education": "Educação",
    "furniture/equipment": "Móveis/Equipamentos",
    "new car": "Carro novo",
    "used car": "Carro usado",
    "business": "Negócios",
    "domestic appliance": "Eletrodomésticos",
    "repairs": "Reparos",
    "other": "Outro",
    "retraining": "Requalificação profissional",
}

_SAVINGS = {
    "no known savings": "Sem poupança conhecida",
    "<100": "Menos de €100",
    "100<=X<500": "Entre €100 e €500",
    "500<=X<1000": "Entre €500 e €1.000",
    ">=1000": "€1.000 ou mais",
}

_EMPLOYMENT_TIME = {
    "unemployed": "Desempregado",
    "<1": "Menos de 1 ano",
    "1<=X<4": "Entre 1 e 4 anos",
    "4<=X<7": "Entre 4 e 7 anos",
    ">=7": "7 anos ou mais",
}

_PERSONAL_STATUS = {
    "male single": "Homem solteiro",
    "female div/dep/mar": "Mulher divorciada/separada/casada",
    "male div/sep": "Homem divorciado/separado",
    "male mar/wid": "Homem casado/viúvo",
}

_DEBTORS = {
    "none": "Nenhum",
    "guarantor": "Fiador",
    "co applicant": "Coobrigado",
}

_PROPERTY = {
    "real estate": "Imóvel",
    "life insurance": "Seguro de vida",
    "no known property": "Sem bens conhecidos",
    "car": "Veículo",
}

_INSTALLMENT_PLANS = {
    "none": "Nenhum",
    "bank": "Banco",
    "stores": "Lojas",
}

_HOUSING = {
    "own": "Própria",
    "for free": "Cedida",
    "rent": "Alugada",
}

_JOB = {
    "skilled": "Qualificado",
    "unskilled resident": "Não qualificado (residente)",
    "high qualif/self emp/mgmt": "Alta qualificação / autônomo / gestor",
    "unemp/unskilled non res": "Desempregado / não qualificado (não residente)",
}

_YES_NO = {
    "yes": "Sim",
    "none": "Não",
    "no": "Não",
}

# A coluna "Status_of_existing_checking_account" contém, na prática, o
# rótulo de risco (ver config.TARGET_COLUMN e docs/METODOLOGIA.md).
_RISK = {
    "good": "Bom pagador",
    "bad": "Mau pagador",
}

VALUE_TRANSLATIONS_BY_COLUMN = {
    "Credit_history": _CREDIT_HISTORY,
    "Purpose_of_the_credit": _PURPOSE,
    "Status_of_savings_account_bonds": _SAVINGS,
    "Present_employment_years": _EMPLOYMENT_TIME,
    "personal_status": _PERSONAL_STATUS,
    "Other_debtors_guarantors": _DEBTORS,
    "Property": _PROPERTY,
    "Other_installment_plans_banks_stores": _INSTALLMENT_PLANS,
    "Housing": _HOUSING,
    "Job": _JOB,
    "Telephone": _YES_NO,
    "Foreign_worker": _YES_NO,
    "Status_of_existing_checking_account": _RISK,
}


def flatten_value_translations() -> dict:
    """
    Achata VALUE_TRANSLATIONS_BY_COLUMN num único dicionário {valor_en: valor_pt}.

    Usado com DataFrame.replace(), que substitui por valor (não por coluna).
    Mantido separado por coluna acima porque alguns valores em inglês (ex.: "none")
    aparecem em colunas diferentes com o mesmo significado, então o achatamento
    é seguro aqui — mas se um novo valor colidir com significado diferente,
    isso deve ser resolvido nesta função, não silenciosamente.
    """
    flat: dict = {}
    for column_dict in VALUE_TRANSLATIONS_BY_COLUMN.values():
        flat.update(column_dict)
    return flat
