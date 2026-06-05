"""
Modelo Preditivo de Churn — Página 8 do Dashboard
Treina Random Forest, XGBoost e Regressão Logística e exporta:
  - probabilidades de churn por cliente (para o Power BI)
  - importância das variáveis
  - métricas de avaliação

Dependências:
    pip install pandas numpy scikit-learn xgboost openpyxl matplotlib seaborn

Uso:
    python modelo_churn.py
    → gera ml/outputs/predicoes_churn.xlsx
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR.parent / "data" / "churn_dataset_final.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Carregar dados
# ---------------------------------------------------------------------------
df = pd.read_excel(DATA_PATH, sheet_name="Clientes")

# ---------------------------------------------------------------------------
# 2. Feature engineering
# ---------------------------------------------------------------------------
features = [
    "Score_Credito", "Idade", "Tempo_Conta_Anos", "Saldo",
    "Qtd_Produtos", "Salario_Estimado", "Score_Risco",
    "Tem_CartaoCredito", "Membro_Ativo", "Genero", "Pais"
]

target = "Churn"

df_model = df[features + [target, "ID_Cliente"]].copy()

# Encode categóricas
le = LabelEncoder()
for col in ["Tem_CartaoCredito", "Membro_Ativo", "Genero", "Pais"]:
    df_model[col] = le.fit_transform(df_model[col].astype(str))

X = df_model[features]
y = df_model[target]

# ---------------------------------------------------------------------------
# 3. Split treino/teste
# ---------------------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled  = scaler.transform(X_test)

# ---------------------------------------------------------------------------
# 4. Modelos
# ---------------------------------------------------------------------------
modelos = {
    "Random Forest": RandomForestClassifier(
        n_estimators=200, max_depth=8, min_samples_leaf=10,
        class_weight="balanced", random_state=42, n_jobs=-1
    ),
    "Regressão Logística": LogisticRegression(
        C=1.0, max_iter=500, class_weight="balanced", random_state=42
    ),
}

try:
    from xgboost import XGBClassifier
    modelos["XGBoost"] = XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, scale_pos_weight=3,
        random_state=42, eval_metric="logloss", verbosity=0
    )
except ImportError:
    print("⚠ XGBoost não instalado — pulando esse modelo.")

# ---------------------------------------------------------------------------
# 5. Treinar e avaliar
# ---------------------------------------------------------------------------
resultados = []
melhor_modelo = None
melhor_f1 = 0
melhor_nome = ""

for nome, modelo in modelos.items():
    X_tr = X_train_scaled if nome == "Regressão Logística" else X_train
    X_te = X_test_scaled  if nome == "Regressão Logística" else X_test

    modelo.fit(X_tr, y_train)
    y_pred = modelo.predict(X_te)
    y_prob = modelo.predict_proba(X_te)[:, 1]

    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec  = recall_score(y_test, y_pred)
    f1   = f1_score(y_test, y_pred)
    auc  = roc_auc_score(y_test, y_prob)

    resultados.append({
        "Modelo":     nome,
        "Accuracy":   round(acc,  4),
        "Precision":  round(prec, 4),
        "Recall":     round(rec,  4),
        "F1-Score":   round(f1,   4),
        "ROC-AUC":    round(auc,  4),
    })

    if f1 > melhor_f1:
        melhor_f1     = f1
        melhor_modelo = modelo
        melhor_nome   = nome

    print(f"\n{'='*40}\n{nome}")
    print(classification_report(y_test, y_pred, target_names=["Ativo", "Cancelou"]))

# ---------------------------------------------------------------------------
# 6. Probabilidades para TODOS os clientes (Power BI)
# ---------------------------------------------------------------------------
X_all = X.copy()
X_all_in = X_all if melhor_nome != "Regressão Logística" else scaler.transform(X_all)
probs = melhor_modelo.predict_proba(X_all_in)[:, 1]

df_output = df_model[["ID_Cliente"]].copy()
df_output["Prob_Churn"]    = (probs * 100).round(2)
df_output["Previsao_Churn"] = (probs >= 0.5).astype(int)
df_output["Nivel_Risco_ML"] = pd.cut(
    probs,
    bins=[0, 0.33, 0.60, 1.0],
    labels=["Baixo Risco", "Médio Risco", "Alto Risco"]
)

# Junta com dados originais para contexto
cols_contexto = ["ID_Cliente", "Score_Credito", "Idade", "Saldo",
                 "Qtd_Produtos", "Membro_Ativo", "Segmento_Valor", "Churn"]
df_final = df[cols_contexto].merge(df_output, on="ID_Cliente")
df_final = df_final.sort_values("Prob_Churn", ascending=False)

# ---------------------------------------------------------------------------
# 7. Importância das variáveis
# ---------------------------------------------------------------------------
if hasattr(melhor_modelo, "feature_importances_"):
    importances = pd.DataFrame({
        "Variavel":    features,
        "Importancia": melhor_modelo.feature_importances_,
    }).sort_values("Importancia", ascending=False)
    importances["Importancia_Pct"] = (
        importances["Importancia"] / importances["Importancia"].sum() * 100
    ).round(2)
else:
    coef = np.abs(melhor_modelo.coef_[0])
    importances = pd.DataFrame({
        "Variavel":    features,
        "Importancia": coef / coef.sum(),
    }).sort_values("Importancia", ascending=False)
    importances["Importancia_Pct"] = (importances["Importancia"] * 100).round(2)

# ---------------------------------------------------------------------------
# 8. Matriz de confusão
# ---------------------------------------------------------------------------
X_te_in = X_test_scaled if melhor_nome == "Regressão Logística" else X_test
y_pred_best = melhor_modelo.predict(X_te_in)
cm = confusion_matrix(y_test, y_pred_best)
df_cm = pd.DataFrame(
    cm,
    index=["Real: Ativo", "Real: Cancelou"],
    columns=["Previsto: Ativo", "Previsto: Cancelou"]
)

# ---------------------------------------------------------------------------
# 9. Exportar tudo para Excel (Power BI lê direto)
# ---------------------------------------------------------------------------
output_file = OUTPUT_DIR / "predicoes_churn.xlsx"
with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    df_final.to_excel(writer,      sheet_name="Probabilidades",  index=False)
    importances.to_excel(writer,   sheet_name="Importancia_Vars", index=False)
    pd.DataFrame(resultados).to_excel(writer, sheet_name="Metricas_Modelos", index=False)
    df_cm.to_excel(writer,         sheet_name="Matriz_Confusao")

print(f"\n✅ Outputs exportados: {output_file}")
print(f"   Melhor modelo: {melhor_nome} (F1={melhor_f1:.4f})")
print(f"\nTop 5 variáveis mais importantes:")
print(importances.head(5).to_string(index=False))
