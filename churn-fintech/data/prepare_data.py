"""
Prepara o dataset Bank Customer Churn para uso no Power BI.
Fonte: https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn

Instalar dependências:
    pip install pandas numpy scikit-learn openpyxl

Uso:
    python prepare_data.py
    → gera churn_dataset_final.xlsx na pasta data/
"""

import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).parent

# ---------------------------------------------------------------------------
# 1. Carregar dados brutos
# ---------------------------------------------------------------------------
# Baixe o CSV do Kaggle e coloque em data/raw/Churn_Modelling.csv
RAW_PATH = BASE_DIR / "raw" / "Churn_Modelling.csv"

if not RAW_PATH.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {RAW_PATH}\n"
        "Baixe em: https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn\n"
        "e coloque em data/raw/Churn_Modelling.csv"
    )

df = pd.read_csv(RAW_PATH)

# ---------------------------------------------------------------------------
# 2. Renomear colunas para português
# ---------------------------------------------------------------------------
df = df.rename(columns={
    "RowNumber":       "ID_Linha",
    "CustomerId":      "ID_Cliente",
    "Surname":         "Sobrenome",
    "CreditScore":     "Score_Credito",
    "Geography":       "Pais",
    "Gender":          "Genero",
    "Age":             "Idade",
    "Tenure":          "Tempo_Conta_Anos",
    "Balance":         "Saldo",
    "NumOfProducts":   "Qtd_Produtos",
    "HasCrCard":       "Tem_CartaoCredito",
    "IsActiveMember":  "Membro_Ativo",
    "EstimatedSalary": "Salario_Estimado",
    "Exited":          "Churn",
})

# ---------------------------------------------------------------------------
# 3. Limpeza e padronização
# ---------------------------------------------------------------------------
df["Genero"] = df["Genero"].map({"Male": "Masculino", "Female": "Feminino"})
df["Pais"] = df["Pais"].map({"France": "França", "Germany": "Alemanha", "Spain": "Espanha"})
df["Tem_CartaoCredito"] = df["Tem_CartaoCredito"].map({1: "Sim", 0: "Não"})
df["Membro_Ativo"] = df["Membro_Ativo"].map({1: "Sim", 0: "Não"})
df["Status_Churn"] = df["Churn"].map({1: "Cancelou", 0: "Ativo"})

# ---------------------------------------------------------------------------
# 4. Faixas etárias
# ---------------------------------------------------------------------------
bins_idade  = [0, 25, 35, 45, 55, 65, 120]
labels_idade = ["Até 25", "26-35", "36-45", "46-55", "56-65", "65+"]
df["Faixa_Etaria"] = pd.cut(df["Idade"], bins=bins_idade, labels=labels_idade, right=True)

# ---------------------------------------------------------------------------
# 5. Faixas salariais
# ---------------------------------------------------------------------------
bins_sal  = [0, 50_000, 100_000, 150_000, np.inf]
labels_sal = ["Até 50k", "50k-100k", "100k-150k", "Acima 150k"]
df["Faixa_Salarial"] = pd.cut(df["Salario_Estimado"], bins=bins_sal, labels=labels_sal, right=True)

# ---------------------------------------------------------------------------
# 6. Faixas de saldo
# ---------------------------------------------------------------------------
def classificar_saldo(s):
    if s == 0:
        return "Sem Saldo"
    elif s < 50_000:
        return "Baixo (< 50k)"
    elif s < 100_000:
        return "Médio (50k-100k)"
    elif s < 150_000:
        return "Alto (100k-150k)"
    else:
        return "Premium (> 150k)"

df["Faixa_Saldo"] = df["Saldo"].apply(classificar_saldo)

# ---------------------------------------------------------------------------
# 7. Segmentação de valor do cliente (receita potencial = saldo + salário/10)
# ---------------------------------------------------------------------------
df["Receita_Estimada"] = df["Saldo"] * 0.03 + df["Salario_Estimado"] * 0.01

percentis = df["Receita_Estimada"].quantile([0.33, 0.66])
def segmento_valor(v):
    if v >= percentis[0.66]:
        return "Alto Valor"
    elif v >= percentis[0.33]:
        return "Médio Valor"
    else:
        return "Baixo Valor"

df["Segmento_Valor"] = df["Receita_Estimada"].apply(segmento_valor)

# ---------------------------------------------------------------------------
# 8. Score de risco de churn (regra de negócio)
# ---------------------------------------------------------------------------
def calcular_score_risco(row):
    score = 0
    # Tempo de conta curto → risco
    if row["Tempo_Conta_Anos"] <= 2:
        score += 25
    elif row["Tempo_Conta_Anos"] <= 4:
        score += 10
    # Saldo zero → risco
    if row["Saldo"] == 0:
        score += 20
    # Inativo → risco alto
    if row["Membro_Ativo"] == "Não":
        score += 30
    # Poucos produtos → risco
    if row["Qtd_Produtos"] == 1:
        score += 15
    elif row["Qtd_Produtos"] >= 3:
        score -= 10  # mais produtos = mais engajado
    # Idade intermediária → tendência de churn
    if 40 <= row["Idade"] <= 60:
        score += 10
    return max(0, min(100, score))

df["Score_Risco"] = df.apply(calcular_score_risco, axis=1)

def classificar_risco(s):
    if s >= 60:
        return "Alto Risco"
    elif s >= 30:
        return "Médio Risco"
    else:
        return "Baixo Risco"

df["Nivel_Risco"] = df["Score_Risco"].apply(classificar_risco)

# ---------------------------------------------------------------------------
# 9. Tempo estimado até cancelamento (simulado para curva de retenção)
# ---------------------------------------------------------------------------
np.random.seed(42)
df["Meses_Ate_Cancelamento"] = np.where(
    df["Churn"] == 1,
    (df["Tempo_Conta_Anos"] * 12 * np.random.uniform(0.5, 1.0, len(df))).astype(int),
    np.nan
)

# ---------------------------------------------------------------------------
# 10. Cohort por tempo de conta
# ---------------------------------------------------------------------------
def cohort_tempo(t):
    if t <= 1:
        return "0-1 anos"
    elif t <= 3:
        return "2-3 anos"
    elif t <= 5:
        return "4-5 anos"
    elif t <= 7:
        return "6-7 anos"
    else:
        return "8+ anos"

df["Cohort_Tempo"] = df["Tempo_Conta_Anos"].apply(cohort_tempo)

# ---------------------------------------------------------------------------
# 11. Exportar
# ---------------------------------------------------------------------------
OUTPUT = BASE_DIR / "churn_dataset_final.xlsx"

with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="Clientes", index=False)

    # Tabela de métricas por segmento
    resumo = df.groupby("Segmento_Valor").agg(
        Total_Clientes=("ID_Cliente", "count"),
        Cancelados=("Churn", "sum"),
        Receita_Total=("Receita_Estimada", "sum"),
        Receita_Perdida=("Receita_Estimada", lambda x: x[df.loc[x.index, "Churn"] == 1].sum()),
    ).reset_index()
    resumo["Taxa_Churn"] = resumo["Cancelados"] / resumo["Total_Clientes"]
    resumo.to_excel(writer, sheet_name="Resumo_Segmentos", index=False)

    # Tabela para curva de retenção
    retencao = (
        df[df["Churn"] == 1]
        .groupby("Cohort_Tempo")
        .agg(Cancelados=("Churn", "sum"))
        .reset_index()
    )
    retencao.to_excel(writer, sheet_name="Curva_Retencao", index=False)

print(f"✅ Dataset exportado: {OUTPUT}")
print(f"   Total de registros: {len(df):,}")
print(f"   Colunas: {len(df.columns)}")
print(f"   Taxa de churn: {df['Churn'].mean():.1%}")
