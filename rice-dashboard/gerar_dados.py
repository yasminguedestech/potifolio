"""
Gera dataset para o Dashboard de Priorização RICE.
Execute: python gerar_dados.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent
np.random.seed(42)

features = [
    # (nome, categoria, reach, impact, confidence, effort, status)
    ("Login com Google/Apple",         "Auth",        8000, 3, 90, 1, "Backlog"),
    ("Notificações push personalizadas","Engajamento", 6500, 3, 80, 2, "Backlog"),
    ("Dashboard analítico do usuário",  "Analytics",   4000, 3, 70, 3, "Em andamento"),
    ("Modo offline",                    "Performance", 3000, 2, 60, 5, "Backlog"),
    ("Integração com Slack",            "Integrações", 2500, 2, 75, 2, "Backlog"),
    ("Gamificação — badges",            "Engajamento", 5000, 2, 65, 3, "Backlog"),
    ("Exportar relatório PDF",          "Relatórios",  3500, 2, 85, 1, "Concluído"),
    ("Onboarding interativo",           "UX",          7000, 3, 80, 2, "Em andamento"),
    ("Filtros avançados",               "UX",          4500, 2, 90, 1, "Concluído"),
    ("API pública",                     "Integrações", 1500, 3, 50, 8, "Backlog"),
    ("Suporte a múltiplos idiomas",     "Global",      5000, 2, 70, 4, "Backlog"),
    ("Tela de busca global",            "UX",          6000, 2, 85, 2, "Backlog"),
    ("Autenticação 2FA",                "Segurança",   4000, 3, 95, 1, "Concluído"),
    ("Histórico de atividades",         "Analytics",   3000, 1, 80, 2, "Backlog"),
    ("Templates prontos",               "Produtividade",5500,3, 75, 3, "Em andamento"),
    ("Modo escuro",                     "UX",          7500, 1, 95, 1, "Concluído"),
    ("Comentários em tempo real",       "Colaboração", 4000, 3, 65, 4, "Backlog"),
    ("Widget para mobile",              "Mobile",      3500, 2, 60, 5, "Backlog"),
    ("Relatório semanal automático",    "Relatórios",  4500, 2, 80, 2, "Backlog"),
    ("Permissões granulares",           "Segurança",   2000, 2, 85, 3, "Backlog"),
]

rows = []
for nome, cat, reach, impact, conf, effort, status in features:
    rice = round((reach * impact * conf) / effort, 1)
    rows.append({
        "Feature":    nome,
        "Categoria":  cat,
        "Reach":      reach,
        "Impact":     impact,
        "Confidence": conf,
        "Effort":     effort,
        "RICE_Score": rice,
        "Status":     status,
        "Votos_Time": np.random.randint(1, 12),
        "Semanas_Est": effort * 2,
    })

df = pd.DataFrame(rows).sort_values("RICE_Score", ascending=False).reset_index(drop=True)
df["Rank"] = df.index + 1
df["Prioridade"] = pd.cut(df["RICE_Score"],
    bins=[0, 3000, 6000, 99999],
    labels=["Baixa", "Média", "Alta"])

# Histórico simulado (como o score evoluiu nas últimas 4 sprints)
historico = []
for _, row in df.iterrows():
    base = row["RICE_Score"]
    for sprint in range(1, 5):
        historico.append({
            "Feature": row["Feature"],
            "Sprint":  f"Sprint {sprint}",
            "Score":   max(0, round(base * np.random.uniform(0.75, 1.1), 1))
        })
df_hist = pd.DataFrame(historico)

out = BASE / "data" / "rice_dashboard.xlsx"
with pd.ExcelWriter(out, engine="openpyxl") as w:
    df.to_excel(w, sheet_name="Features", index=False)
    df_hist.to_excel(w, sheet_name="Historico", index=False)

print(f"Dataset gerado: {out}")
print(f"Total features: {len(df)}")
print(f"Top RICE: {df.iloc[0]['Feature']} ({df.iloc[0]['RICE_Score']:,.0f})")
print(f"Alta prioridade: {(df['Prioridade']=='Alta').sum()}")
