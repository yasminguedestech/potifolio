"""
Gera dataset de funil de conversão para e-commerce.
Execute: python gerar_dados.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent
np.random.seed(42)

etapas = ["Visita","Produto Visto","Adicionou ao Carrinho","Iniciou Checkout","Cadastro","Pagamento","Compra Finalizada"]
conversao_base = [1.000, 0.620, 0.380, 0.220, 0.128, 0.095, 0.078]

canais = {
    "Google Ads":    [1.00, 0.65, 0.40, 0.24, 0.14, 0.10, 0.085],
    "Orgânico SEO":  [1.00, 0.58, 0.35, 0.20, 0.12, 0.09, 0.074],
    "Instagram Ads": [1.00, 0.70, 0.42, 0.25, 0.13, 0.10, 0.082],
    "E-mail":        [1.00, 0.75, 0.50, 0.32, 0.20, 0.16, 0.138],
    "Direto":        [1.00, 0.60, 0.38, 0.22, 0.14, 0.10, 0.083],
}

dispositivos = {
    "Desktop": [1.00, 0.65, 0.42, 0.26, 0.16, 0.12, 0.100],
    "Mobile":  [1.00, 0.58, 0.32, 0.17, 0.09, 0.07, 0.055],
    "Tablet":  [1.00, 0.62, 0.38, 0.22, 0.13, 0.10, 0.082],
}

VISITAS_MES = 45000

# Funil geral
funil_geral = pd.DataFrame({
    "Etapa": etapas,
    "Usuarios": [round(VISITAS_MES * c) for c in conversao_base],
    "Taxa_Conversao": [round(c*100,1) for c in conversao_base],
})
funil_geral["Drop_Off"] = funil_geral["Usuarios"].shift(1) - funil_geral["Usuarios"]
funil_geral["Drop_Off_Pct"] = (funil_geral["Drop_Off"] / funil_geral["Usuarios"].shift(1) * 100).round(1)
funil_geral["Taxa_Etapa"] = (funil_geral["Usuarios"] / funil_geral["Usuarios"].shift(1) * 100).round(1)

# Funil por canal
rows_canal = []
for canal, taxas in canais.items():
    visitas = round(VISITAS_MES * {"Google Ads":0.35,"Orgânico SEO":0.25,"Instagram Ads":0.20,"E-mail":0.12,"Direto":0.08}[canal])
    for i, (etapa, taxa) in enumerate(zip(etapas, taxas)):
        rows_canal.append({"Canal": canal, "Etapa": etapa, "Usuarios": round(visitas*taxa), "Taxa": round(taxa*100,1)})
df_canal = pd.DataFrame(rows_canal)

# Funil por dispositivo
rows_disp = []
for disp, taxas in dispositivos.items():
    visitas = round(VISITAS_MES * {"Desktop":0.45,"Mobile":0.42,"Tablet":0.13}[disp])
    for i, (etapa, taxa) in enumerate(zip(etapas, taxas)):
        rows_disp.append({"Dispositivo": disp, "Etapa": etapa, "Usuarios": round(visitas*taxa), "Taxa": round(taxa*100,1)})
df_disp = pd.DataFrame(rows_disp)

# Evolução mensal
meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
rows_mensal = []
for mes in meses:
    var = np.random.uniform(-0.02, 0.05)
    visitas = round(VISITAS_MES * (1 + var + np.random.uniform(-0.1,0.1)))
    compras = round(visitas * (0.078 + np.random.uniform(-0.01, 0.02)))
    ticket = round(np.random.uniform(180, 350), 2)
    rows_mensal.append({
        "Mes": mes, "Visitas": visitas, "Compras": compras,
        "Taxa_Conversao": round(compras/visitas*100, 2),
        "Receita": round(compras * ticket, 2),
        "Ticket_Medio": ticket,
    })
df_mensal = pd.DataFrame(rows_mensal)

# Abandono por etapa (simulação de motivos)
abandono = pd.DataFrame([
    {"Etapa": "Produto Visto → Carrinho",    "Motivo": "Preço alto",             "Pct": 35},
    {"Etapa": "Produto Visto → Carrinho",    "Motivo": "Sem interesse suficiente","Pct": 28},
    {"Etapa": "Produto Visto → Carrinho",    "Motivo": "Produto indisponível",    "Pct": 17},
    {"Etapa": "Produto Visto → Carrinho",    "Motivo": "Outros",                  "Pct": 20},
    {"Etapa": "Carrinho → Checkout",         "Motivo": "Só estava comparando",    "Pct": 42},
    {"Etapa": "Carrinho → Checkout",         "Motivo": "Frete alto",              "Pct": 30},
    {"Etapa": "Carrinho → Checkout",         "Motivo": "Outros",                  "Pct": 28},
    {"Etapa": "Checkout → Cadastro",         "Motivo": "Formulário longo",        "Pct": 45},
    {"Etapa": "Checkout → Cadastro",         "Motivo": "Sem login social",        "Pct": 32},
    {"Etapa": "Checkout → Cadastro",         "Motivo": "Outros",                  "Pct": 23},
    {"Etapa": "Cadastro → Pagamento",        "Motivo": "Parcelamento insuficiente","Pct": 38},
    {"Etapa": "Cadastro → Pagamento",        "Motivo": "Falta de confiança",      "Pct": 25},
    {"Etapa": "Cadastro → Pagamento",        "Motivo": "Método não aceito",       "Pct": 22},
    {"Etapa": "Cadastro → Pagamento",        "Motivo": "Outros",                  "Pct": 15},
])

out = BASE / "data" / "funil_ecommerce.xlsx"
with pd.ExcelWriter(out, engine="openpyxl") as w:
    funil_geral.to_excel(w, sheet_name="Funil_Geral", index=False)
    df_canal.to_excel(w, sheet_name="Por_Canal", index=False)
    df_disp.to_excel(w, sheet_name="Por_Dispositivo", index=False)
    df_mensal.to_excel(w, sheet_name="Mensal", index=False)
    abandono.to_excel(w, sheet_name="Motivos_Abandono", index=False)

print(f"Dataset: {out}")
print(f"Visitas/mês: {VISITAS_MES:,}")
print(f"Compras/mês: {round(VISITAS_MES*0.078):,}")
print(f"Taxa de conversão geral: 7.8%")
print(f"Maior drop-off: Checkout → Cadastro (42%)")
