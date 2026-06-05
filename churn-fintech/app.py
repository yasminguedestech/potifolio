"""
Dashboard de Churn - Fintech Digital
Execute: python app.py
Acesse:  http://localhost:8050
"""

import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

# ── dados ──────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent
df   = pd.read_excel(BASE / "data/churn_dataset_final.xlsx", sheet_name="Clientes")
df_pred = pd.read_excel(BASE / "ml/outputs/predicoes_churn.xlsx", sheet_name="Probabilidades")
df_imp  = pd.read_excel(BASE / "ml/outputs/predicoes_churn.xlsx", sheet_name="Importancia_Vars")
df_met  = pd.read_excel(BASE / "ml/outputs/predicoes_churn.xlsx", sheet_name="Metricas_Modelos")
df_cm   = pd.read_excel(BASE / "ml/outputs/predicoes_churn.xlsx", sheet_name="Matriz_Confusao", index_col=0)

# ── paleta azul + roxo ─────────────────────────────────────────────────────
BG      = "#08071a"          # fundo quase preto com toque roxo
CARD_BG = "#100f2e"          # card azul-roxo escuro
BORDER  = "#2a2560"          # borda roxo-azulada sutil
RED     = "#f472b6"          # rosa-quente para alertas (combina com roxo)
GREEN   = "#38bdf8"          # azul-ciano para "positivo"
BLUE    = "#6366f1"          # índigo/roxo primário
YELLOW  = "#818cf8"          # lavanda para destaques secundários
PURPLE  = "#a78bfa"          # roxo vibrante para alto valor
TEXT    = "#ede9ff"          # texto branco-lilás
MUTED   = "#8b7ec8"          # roxo acinzentado para textos secundários

RISK_COLORS = {"Alto Risco": RED, "Médio Risco": YELLOW, "Baixo Risco": GREEN}
STATUS_COLORS = {"Cancelou": RED, "Ativo": GREEN}
SEG_COLORS = {"Alto Valor": PURPLE, "Médio Valor": BLUE, "Baixo Valor": MUTED}

PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT, family="Inter, sans-serif", size=12),
    margin=dict(t=40, b=40, l=40, r=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT)),
    xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, color=TEXT),
    yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER, color=TEXT),
)

def apply_layout(fig, **extra):
    layout = {**PLOT_LAYOUT, **extra}
    fig.update_layout(**layout)
    return fig

# ── helpers ────────────────────────────────────────────────────────────────
def fmt_brl(v):
    if v >= 1_000_000: return f"R$ {v/1_000_000:.1f}M"
    if v >= 1_000:     return f"R$ {v/1_000:.0f}K"
    return f"R$ {v:.0f}"

def kpi_card(title, value, sub=None, color=BLUE, icon=""):
    return dbc.Card([
        dbc.CardBody([
            html.P([icon, " ", title], className="mb-1",
                   style={"color": MUTED, "fontSize": "0.75rem", "textTransform": "uppercase",
                          "letterSpacing": "0.08em"}),
            html.H3(value, style={"color": color, "fontWeight": "700", "margin": "0"}),
            html.P(sub or "", style={"color": MUTED, "fontSize": "0.72rem", "margin": "0"}),
        ])
    ], style={"background": CARD_BG, "border": f"1px solid {BORDER}",
              "borderRadius": "10px", "height": "100%"})

# ── métricas globais ────────────────────────────────────────────────────────
total       = len(df)
cancelados  = df["Churn"].sum()
ativos      = total - cancelados
taxa_churn  = cancelados / total
rec_total   = df["Receita_Estimada"].sum()
rec_perdida = df[df["Churn"]==1]["Receita_Estimada"].sum()
rec_risco   = df[df["Nivel_Risco"]=="Alto Risco"]["Receita_Estimada"].sum()
ticket_med  = rec_total / total
tempo_med   = df["Tempo_Conta_Anos"].mean()

# ── app ────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.SLATE,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"
    ],
    suppress_callback_exceptions=True,
    title="Churn Dashboard — Fintech"
)

# ── sidebar ────────────────────────────────────────────────────────────────
PAGES = [
    ("01", "Visão Executiva",       "/"),
    ("02", "Perfil do Cliente",     "/perfil"),
    ("03", "Produtos Financeiros",  "/produtos"),
    ("04", "Receita & Segmentos",   "/receita"),
    ("05", "Score de Risco",        "/risco"),
    ("06", "Jornada do Cliente",    "/jornada"),
    ("07", "Simulador",             "/simulador"),
    ("08", "Modelo Preditivo",      "/modelo"),
    ("09", "Recomendações",         "/recomendacoes"),
]

def nav_link(num, label, href):
    return html.A([
        html.Span(num, style={"color": MUTED, "fontSize": "0.7rem", "minWidth": "22px"}),
        html.Span(label, style={"fontSize": "0.85rem"}),
    ], href=href, style={
        "display": "flex", "gap": "10px", "alignItems": "center",
        "padding": "10px 16px", "color": TEXT, "textDecoration": "none",
        "borderRadius": "8px", "transition": "background 0.15s",
    }, className="nav-link-item")

sidebar = html.Div([
    html.Div([
        html.Div("💳", style={"fontSize": "1.8rem"}),
        html.Div([
            html.P("Churn Analytics", style={"margin": "0", "fontWeight": "700",
                                              "fontSize": "0.95rem", "color": TEXT}),
            html.P("Fintech Digital", style={"margin": "0", "fontSize": "0.72rem", "color": MUTED}),
        ])
    ], style={"display": "flex", "gap": "12px", "alignItems": "center",
              "padding": "20px 16px 16px", "borderBottom": f"1px solid {BORDER}"}),
    html.Nav([nav_link(n, l, h) for n, l, h in PAGES],
             style={"padding": "10px 8px", "display": "flex", "flexDirection": "column", "gap": "2px"}),
    html.Div([
        html.P("10.000 clientes · Kaggle", style={"color": MUTED, "fontSize": "0.7rem", "margin": "0"}),
        html.P("Bank Customer Churn", style={"color": MUTED, "fontSize": "0.7rem", "margin": "0"}),
    ], style={"padding": "16px", "borderTop": f"1px solid {BORDER}", "marginTop": "auto"}),
], style={
    "width": "220px", "minWidth": "220px", "background": CARD_BG,
    "borderRight": f"1px solid {BORDER}", "height": "100vh",
    "overflowY": "auto", "position": "fixed", "left": "0", "top": "0", "zIndex": "100",
    "display": "flex", "flexDirection": "column",
})

app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar,
    html.Div(id="page-content", style={
        "marginLeft": "220px", "background": BG, "minHeight": "100vh",
        "padding": "28px 32px", "color": TEXT,
    }),
], style={"fontFamily": "Inter, sans-serif", "background": BG})

# ══════════════════════════════════════════════════════════════════════════════
# PÁGINAS
# ══════════════════════════════════════════════════════════════════════════════

# ── P1: Visão Executiva ─────────────────────────────────────────────────────
def page_executiva():
    # Gráfico: Churn por país
    por_pais = df.groupby("Pais")["Churn"].agg(["sum","count"]).reset_index()
    por_pais["taxa"] = por_pais["sum"] / por_pais["count"] * 100
    fig_pais = go.Figure([
        go.Bar(name="Ativos",    x=por_pais["Pais"], y=por_pais["count"]-por_pais["sum"], marker_color=GREEN),
        go.Bar(name="Cancelados",x=por_pais["Pais"], y=por_pais["sum"], marker_color=RED),
    ])
    fig_pais.update_layout(barmode="stack", title="Clientes por País", **PLOT_LAYOUT)

    # Gráfico: Rosca status
    fig_rosca = go.Figure(go.Pie(
        labels=["Ativos","Cancelados"], values=[ativos, cancelados],
        hole=0.65, marker_colors=[GREEN, RED],
        textinfo="label+percent", textfont_color=TEXT,
    ))
    fig_rosca.update_layout(title="Status da Base", showlegend=False, **PLOT_LAYOUT)

    # Gráfico: Churn por cohort
    cohort_order = ["0-1 anos","2-3 anos","4-5 anos","6-7 anos","8+ anos"]
    coh = df.groupby("Cohort_Tempo", observed=True).apply(
        lambda x: pd.Series({"taxa": x["Churn"].mean()*100, "total": len(x)}), include_groups=False
    ).reindex(cohort_order).reset_index()
    fig_cohort = go.Figure([
        go.Scatter(x=coh["Cohort_Tempo"], y=coh["taxa"].round(1),
                   mode="lines+markers", line=dict(color=RED, width=3),
                   marker=dict(size=9, color=RED),
                   fill="tozeroy", fillcolor="rgba(248,81,73,0.10)", name="Taxa Churn %"),
    ])
    fig_cohort.update_layout(title="Taxa de Churn por Tempo de Conta", **PLOT_LAYOUT)
    fig_cohort.update_yaxes(title="Taxa Churn %")

    return html.Div([
        html.H2("Visão Executiva", style={"color": TEXT, "fontWeight": "700", "marginBottom": "6px"}),
        html.P("Saúde da base de clientes e impacto financeiro do churn",
               style={"color": MUTED, "marginBottom": "24px"}),

        dbc.Row([
            dbc.Col(kpi_card("Total de Clientes",  f"{total:,}",             color=BLUE, icon="👥"), md=2),
            dbc.Col(kpi_card("Clientes Ativos",     f"{ativos:,}",           color=GREEN, icon="✅"), md=2),
            dbc.Col(kpi_card("Cancelamentos",       f"{cancelados:,}",       color=RED, icon="⚠️"), md=2),
            dbc.Col(kpi_card("Taxa de Churn",       f"{taxa_churn:.1%}",     color=RED, icon="📉"), md=2),
            dbc.Col(kpi_card("Receita em Risco",    fmt_brl(rec_risco),      color=YELLOW, icon="💸"), md=2),
            dbc.Col(kpi_card("Receita Perdida",     fmt_brl(rec_perdida),    color=RED, icon="🔴"), md=2),
        ], className="mb-3 g-2"),

        dbc.Row([
            dbc.Col(kpi_card("Ticket Médio",              fmt_brl(ticket_med),        color=BLUE, icon="🎫"), md=3),
            dbc.Col(kpi_card("Tempo Médio de Permanência", f"{tempo_med:.1f} anos",   color=BLUE, icon="⏱️"), md=3),
            dbc.Col(kpi_card("Receita Total",             fmt_brl(rec_total),         color=GREEN, icon="💰"), md=3),
            dbc.Col(kpi_card("% Receita Perdida",         f"{rec_perdida/rec_total:.1%}", color=RED, icon="📊"), md=3),
        ], className="mb-4 g-2"),

        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_pais,   config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_rosca,  config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=3),
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.P("Receita Perdida", style={"color":MUTED,"fontSize":"0.75rem","textTransform":"uppercase"}),
                    html.H2(fmt_brl(rec_perdida), style={"color":RED,"fontWeight":"700"}),
                    html.Hr(style={"borderColor":BORDER}),
                    html.P("Receita em Alto Risco", style={"color":MUTED,"fontSize":"0.75rem","textTransform":"uppercase"}),
                    html.H3(fmt_brl(rec_risco), style={"color":YELLOW,"fontWeight":"700"}),
                    html.Hr(style={"borderColor":BORDER}),
                    html.P(f"{rec_risco/rec_total:.1%} da receita total está em risco",
                           style={"color":MUTED,"fontSize":"0.8rem"}),
                ])
            ], style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px","height":"100%"}), md=3),
        ], className="mb-3 g-2"),

        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_cohort, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=12),
        ], className="g-2"),
    ])

# ── P2: Perfil do Cliente ──────────────────────────────────────────────────
def page_perfil():
    etaria_order = ["Até 25","26-35","36-45","46-55","56-65","65+"]
    et = df.groupby("Faixa_Etaria", observed=True).apply(
        lambda x: pd.Series({"taxa": x["Churn"].mean()*100, "total": len(x), "cancel": x["Churn"].sum()}), include_groups=False
    ).reindex(etaria_order).reset_index()
    fig_et = go.Figure([
        go.Bar(x=et["Faixa_Etaria"], y=et["total"]-et["cancel"], name="Ativos", marker_color=GREEN),
        go.Bar(x=et["Faixa_Etaria"], y=et["cancel"], name="Cancelados", marker_color=RED),
    ])
    fig_et.update_layout(barmode="stack", title="Churn por Faixa Etária", **PLOT_LAYOUT)

    gen = df.groupby("Genero")["Churn"].agg(["mean","count","sum"]).reset_index()
    gen["taxa"] = gen["mean"]*100
    fig_gen = go.Figure([
        go.Bar(x=gen["Genero"], y=gen["count"]-gen["sum"], name="Ativos", marker_color=GREEN),
        go.Bar(x=gen["Genero"], y=gen["sum"], name="Cancelados", marker_color=RED),
    ])
    fig_gen.update_layout(barmode="stack", title="Churn por Gênero", **PLOT_LAYOUT)

    sal_order = ["Até 50k","50k-100k","100k-150k","Acima 150k"]
    sal = df.groupby("Faixa_Salarial", observed=True).apply(
        lambda x: pd.Series({"taxa": x["Churn"].mean()*100, "cancel": x["Churn"].sum(), "total": len(x)}), include_groups=False
    ).reindex(sal_order).reset_index()
    fig_sal = go.Figure(go.Bar(
        x=sal["Faixa_Salarial"], y=sal["taxa"].round(1),
        marker_color=[RED if v > taxa_churn*100 else GREEN for v in sal["taxa"]],
        text=sal["taxa"].round(1).astype(str)+"%", textposition="outside",
    ))
    fig_sal.update_layout(title="Taxa de Churn por Faixa Salarial", **PLOT_LAYOUT)

    # Heatmap: Gênero x Faixa Etária
    heat = df.pivot_table(index="Genero", columns="Faixa_Etaria", values="Churn",
                          aggfunc="mean", observed=True) * 100
    heat = heat.reindex(columns=etaria_order)
    fig_heat = go.Figure(go.Heatmap(
        z=heat.values.round(1), x=heat.columns.tolist(), y=heat.index.tolist(),
        colorscale=[[0,"#12104a"],[0.5,"#6366f1"],[1,"#f472b6"]],
        text=heat.values.round(1), texttemplate="%{text}%",
        colorbar=dict(tickfont=dict(color=TEXT)),
    ))
    fig_heat.update_layout(title="Heatmap: Taxa Churn (Gênero × Faixa Etária)", **PLOT_LAYOUT)

    return html.Div([
        html.H2("Perfil do Cliente que Cancela", style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Características demográficas dos clientes com maior propensão ao cancelamento",
               style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_et,   config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_gen,  config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
        ], className="mb-3 g-2"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_sal,  config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_heat, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
        ], className="g-2"),
    ])

# ── P3: Produtos ───────────────────────────────────────────────────────────
def page_produtos():
    prods = df.groupby("Qtd_Produtos").apply(
        lambda x: pd.Series({"total":len(x),"cancel":x["Churn"].sum(),"taxa":x["Churn"].mean()*100}), include_groups=False
    ).reset_index()

    fig_prods = make_subplots(specs=[[{"secondary_y": True}]])
    fig_prods.add_trace(go.Bar(x=prods["Qtd_Produtos"], y=prods["total"]-prods["cancel"],
                               name="Ativos", marker_color=GREEN), secondary_y=False)
    fig_prods.add_trace(go.Bar(x=prods["Qtd_Produtos"], y=prods["cancel"],
                               name="Cancelados", marker_color=RED), secondary_y=False)
    fig_prods.add_trace(go.Scatter(x=prods["Qtd_Produtos"], y=prods["taxa"].round(1),
                                   mode="lines+markers", name="Taxa Churn %",
                                   line=dict(color=YELLOW, width=3), marker=dict(size=10)),
                        secondary_y=True)
    fig_prods.update_layout(barmode="stack", title="Churn por Quantidade de Produtos", **PLOT_LAYOUT)
    fig_prods.update_yaxes(title_text="Clientes", secondary_y=False, gridcolor=BORDER, color=TEXT)
    fig_prods.update_yaxes(title_text="Taxa Churn %", secondary_y=True, color=YELLOW)
    fig_prods.update_xaxes(title_text="Qtd. Produtos", color=TEXT, gridcolor=BORDER)

    ativo_stats = df.groupby("Membro_Ativo")["Churn"].agg(["mean","count","sum"]).reset_index()
    ativo_stats["taxa"] = ativo_stats["mean"]*100
    fig_ativo = go.Figure([
        go.Bar(x=ativo_stats["Membro_Ativo"], y=ativo_stats["count"]-ativo_stats["sum"],
               name="Ativos", marker_color=GREEN),
        go.Bar(x=ativo_stats["Membro_Ativo"], y=ativo_stats["sum"],
               name="Cancelados", marker_color=RED),
    ])
    fig_ativo.update_layout(barmode="stack", title="Churn por Atividade do Membro", **PLOT_LAYOUT)

    fig_scatter = px.scatter(
        df.sample(2000, random_state=42),
        x="Saldo", y="Salario_Estimado",
        color="Status_Churn",
        color_discrete_map=STATUS_COLORS,
        size="Qtd_Produtos",
        opacity=0.5,
        title="Saldo vs Salário (amostra 2.000 clientes)",
        labels={"Saldo":"Saldo (R$)","Salario_Estimado":"Salário (R$)","Status_Churn":"Status"},
    )
    fig_scatter.update_layout(**PLOT_LAYOUT)

    heat_pa = df.pivot_table(index="Qtd_Produtos", columns="Membro_Ativo",
                             values="Churn", aggfunc="mean") * 100
    fig_heat_pa = go.Figure(go.Heatmap(
        z=heat_pa.values.round(1), x=heat_pa.columns.tolist(), y=[str(i) for i in heat_pa.index],
        colorscale=[[0,"#12104a"],[0.5,"#6366f1"],[1,"#f472b6"]],
        text=heat_pa.values.round(1), texttemplate="%{text}%",
        colorbar=dict(tickfont=dict(color=TEXT)),
    ))
    fig_heat_pa.update_layout(title="Heatmap: Churn (Produtos × Atividade)", **PLOT_LAYOUT)

    return html.Div([
        html.H2("Uso de Produtos Financeiros", style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Como o uso de produtos influencia a retenção", style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_prods, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_ativo, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
        ], className="mb-3 g-2"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_scatter,  config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=8),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_heat_pa, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=4),
        ], className="g-2"),
    ])

# ── P4: Receita & Segmentos ────────────────────────────────────────────────
def page_receita():
    seg_order = ["Alto Valor","Médio Valor","Baixo Valor"]
    seg = df.groupby("Segmento_Valor").apply(
        lambda x: pd.Series({
            "Receita Total": x["Receita_Estimada"].sum(),
            "Receita Perdida": x.loc[x["Churn"]==1,"Receita_Estimada"].sum(),
            "Clientes": len(x),
            "Cancelados": x["Churn"].sum(),
        }), include_groups=False
    ).reindex(seg_order).reset_index()
    seg["Taxa Churn %"] = (seg["Cancelados"]/seg["Clientes"]*100).round(1)

    fig_tree = go.Figure(go.Treemap(
        labels=seg["Segmento_Valor"].tolist() + ["Total"],
        parents=["Total","Total","Total",""],
        values=[seg["Receita Total"].sum()] + [0,0,0],
        branchvalues="total",
        marker_colors=[MUTED,BLUE,PURPLE,"rgba(0,0,0,0)"],
    ))
    # Treemap simples
    fig_tree = px.treemap(
        seg, path=["Segmento_Valor"], values="Receita Total",
        color="Taxa Churn %", color_continuous_scale=["#12104a","#6366f1","#f472b6"],
        title="Receita por Segmento de Valor",
    )
    fig_tree.update_layout(**PLOT_LAYOUT)

    fig_seg_bar = go.Figure([
        go.Bar(name="Receita Total",   x=seg["Segmento_Valor"], y=seg["Receita Total"],   marker_color=BLUE),
        go.Bar(name="Receita Perdida", x=seg["Segmento_Valor"], y=seg["Receita Perdida"], marker_color=RED),
    ])
    fig_seg_bar.update_layout(barmode="group", title="Receita Total vs Perdida por Segmento", **PLOT_LAYOUT)

    # Pareto
    df_sorted = df.sort_values("Receita_Estimada", ascending=False).reset_index(drop=True)
    df_sorted["cum_pct_clientes"] = (df_sorted.index + 1) / len(df_sorted) * 100
    df_sorted["cum_pct_receita"]  = df_sorted["Receita_Estimada"].cumsum() / df_sorted["Receita_Estimada"].sum() * 100
    sample = df_sorted[::10]
    fig_pareto = go.Figure([
        go.Scatter(x=sample["cum_pct_clientes"], y=sample["cum_pct_receita"],
                   mode="lines", line=dict(color=PURPLE, width=3), name="Receita Acumulada"),
        go.Scatter(x=[0,80,80], y=[0,80,0], mode="lines",
                   line=dict(color=YELLOW, dash="dash", width=1), name="Linha 80/20"),
    ])
    fig_pareto.update_layout(title="Curva de Pareto — Receita Acumulada",
                             xaxis_title="% Clientes", yaxis_title="% Receita", **PLOT_LAYOUT)

    churn_seg = go.Figure(go.Bar(
        x=seg["Segmento_Valor"], y=seg["Taxa Churn %"],
        marker_color=[RED if v > taxa_churn*100 else GREEN for v in seg["Taxa Churn %"]],
        text=seg["Taxa Churn %"].astype(str)+"%", textposition="outside",
    ))
    churn_seg.update_layout(title="Taxa de Churn por Segmento de Valor", **PLOT_LAYOUT)

    return html.Div([
        html.H2("Receita e Segmentação de Clientes", style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Identificação dos grupos com maior risco financeiro", style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_tree, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_seg_bar, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
        ], className="mb-3 g-2"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_pareto,  config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=churn_seg, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
        ], className="g-2"),
    ])

# ── P5: Score de Risco ─────────────────────────────────────────────────────
def page_risco():
    risk_cnt = df["Nivel_Risco"].value_counts().reindex(["Alto Risco","Médio Risco","Baixo Risco"])
    fig_rosca = go.Figure(go.Pie(
        labels=risk_cnt.index, values=risk_cnt.values, hole=0.60,
        marker_colors=[RED, YELLOW, GREEN],
        textinfo="label+percent", textfont_color=TEXT,
    ))
    fig_rosca.update_layout(title="Distribuição por Nível de Risco", showlegend=False, **PLOT_LAYOUT)

    risk_rec = df.groupby("Nivel_Risco")["Receita_Estimada"].sum().reindex(["Alto Risco","Médio Risco","Baixo Risco"])
    fig_rec_risco = go.Figure(go.Bar(
        x=risk_rec.index, y=risk_rec.values,
        marker_color=[RED, YELLOW, GREEN],
        text=[fmt_brl(v) for v in risk_rec.values], textposition="outside",
    ))
    fig_rec_risco.update_layout(title="Receita por Nível de Risco", **PLOT_LAYOUT)

    # Validação: churn real vs nível de risco
    val = df.groupby("Nivel_Risco")["Churn"].mean().reindex(["Alto Risco","Médio Risco","Baixo Risco"]) * 100
    fig_val = go.Figure(go.Bar(
        x=val.index, y=val.values.round(1),
        marker_color=[RED, YELLOW, GREEN],
        text=val.values.round(1).astype(str)+"%", textposition="outside",
    ))
    fig_val.update_layout(title="Taxa de Churn Real por Nível de Risco (Validação)", **PLOT_LAYOUT)

    # Top clientes críticos
    top = df[df["Nivel_Risco"]=="Alto Risco"].nlargest(20, "Score_Risco")[[
        "ID_Cliente","Idade","Pais","Saldo","Qtd_Produtos","Membro_Ativo",
        "Score_Risco","Segmento_Valor","Receita_Estimada"
    ]].copy()
    top["Saldo"] = top["Saldo"].apply(lambda x: f"R$ {x:,.0f}")
    top["Receita_Estimada"] = top["Receita_Estimada"].apply(lambda x: f"R$ {x:,.2f}")

    tabela = dash_table.DataTable(
        data=top.to_dict("records"),
        columns=[{"name": c, "id": c} for c in top.columns],
        style_table={"overflowX":"auto"},
        style_cell={"backgroundColor":CARD_BG,"color":TEXT,"border":f"1px solid {BORDER}",
                    "fontFamily":"Inter","fontSize":"0.8rem","padding":"8px"},
        style_header={"backgroundColor":"#1c2128","color":TEXT,"fontWeight":"700",
                      "border":f"1px solid {BORDER}"},
        style_data_conditional=[
            {"if":{"column_id":"Score_Risco"},"color":RED,"fontWeight":"700"},
        ],
        page_size=10,
    )

    pct_alto = df[df["Nivel_Risco"]=="Alto Risco"]["Receita_Estimada"].sum() / rec_total

    return html.Div([
        html.H2("Score de Risco de Churn", style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Classificação de clientes por probabilidade de cancelamento",
               style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(kpi_card("Clientes em Alto Risco",
                             f"{df[df['Nivel_Risco']=='Alto Risco'].shape[0]:,}",
                             f"{df[df['Nivel_Risco']=='Alto Risco'].shape[0]/total:.1%} da base",
                             RED, "🔴"), md=3),
            dbc.Col(kpi_card("Receita em Alto Risco", fmt_brl(rec_risco),
                             f"{pct_alto:.1%} da receita total", RED, "💸"), md=3),
            dbc.Col(kpi_card("Score Médio (Cancelados)",
                             f"{df[df['Churn']==1]['Score_Risco'].mean():.0f}",
                             "vs {:.0f} nos ativos".format(df[df['Churn']==0]['Score_Risco'].mean()),
                             YELLOW, "📊"), md=3),
            dbc.Col(kpi_card("Clientes em Baixo Risco",
                             f"{df[df['Nivel_Risco']=='Baixo Risco'].shape[0]:,}",
                             f"{df[df['Nivel_Risco']=='Baixo Risco'].shape[0]/total:.1%} da base",
                             GREEN, "🟢"), md=3),
        ], className="mb-4 g-2"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_rosca,    config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=4),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_rec_risco,config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=4),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_val,      config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=4),
        ], className="mb-3 g-2"),
        dbc.Card([
            dbc.CardBody([
                html.H6("Top 20 Clientes em Alto Risco", style={"color":TEXT,"marginBottom":"12px"}),
                tabela,
            ])
        ], style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}),
    ])

# ── P6: Jornada ────────────────────────────────────────────────────────────
def page_jornada():
    cohort_order = ["0-1 anos","2-3 anos","4-5 anos","6-7 anos","8+ anos"]
    coh = df.groupby("Cohort_Tempo", observed=True).apply(
        lambda x: pd.Series({
            "total": len(x), "cancelados": x["Churn"].sum(),
            "taxa": x["Churn"].mean()*100,
            "retencao": (1-x["Churn"].mean())*100,
        }), include_groups=False
    ).reindex(cohort_order).reset_index()

    fig_linha = go.Figure([
        go.Scatter(x=coh["Cohort_Tempo"], y=coh["taxa"].round(1),
                   mode="lines+markers", line=dict(color=RED,width=3),
                   marker=dict(size=9), name="Taxa Churn %",
                   fill="tozeroy", fillcolor="rgba(248,81,73,0.10)"),
    ])
    fig_linha.update_layout(title="Taxa de Churn por Cohort de Tempo", **PLOT_LAYOUT)

    fig_ret = go.Figure([
        go.Scatter(x=coh["Cohort_Tempo"], y=coh["retencao"].round(1),
                   mode="lines+markers", line=dict(color=GREEN,width=3),
                   marker=dict(size=9), name="Taxa Retenção %",
                   fill="tozeroy", fillcolor="rgba(63,185,80,0.10)"),
    ])
    fig_ret.update_layout(title="Curva de Retenção por Cohort", **PLOT_LAYOUT)

    # Heatmap: cohort x produtos
    heat_cp = df.pivot_table(index="Cohort_Tempo", columns="Qtd_Produtos",
                             values="Churn", aggfunc="mean", observed=True) * 100
    heat_cp = heat_cp.reindex(cohort_order)
    fig_heat = go.Figure(go.Heatmap(
        z=heat_cp.values.round(1), x=[str(c)+" prod." for c in heat_cp.columns],
        y=heat_cp.index.tolist(),
        colorscale=[[0,"#12104a"],[0.5,"#6366f1"],[1,"#f472b6"]],
        text=heat_cp.values.round(1), texttemplate="%{text}%",
        colorbar=dict(tickfont=dict(color=TEXT)),
    ))
    fig_heat.update_layout(title="Heatmap: Churn por Cohort × Qtd. Produtos", **PLOT_LAYOUT)

    tempo_medio = df[df["Churn"]==1]["Meses_Ate_Cancelamento"].mean()

    return html.Div([
        html.H2("Jornada do Cliente", style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Em qual momento da jornada ocorre o maior volume de cancelamentos",
               style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(kpi_card("Tempo Médio até Cancelamento",
                             f"{tempo_medio:.0f} meses", "desde a abertura da conta", YELLOW, "⏱️"), md=4),
            dbc.Col(kpi_card("Cohort com Maior Churn",
                             coh.loc[coh["taxa"].idxmax(),"Cohort_Tempo"],
                             f"{coh['taxa'].max():.1f}% de cancelamento", RED, "⚠️"), md=4),
            dbc.Col(kpi_card("Cohort com Menor Churn",
                             coh.loc[coh["taxa"].idxmin(),"Cohort_Tempo"],
                             f"{coh['taxa'].min():.1f}% de cancelamento", GREEN, "✅"), md=4),
        ], className="mb-4 g-2"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_linha, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_ret,   config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
        ], className="mb-3 g-2"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_heat, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=12),
        ], className="g-2"),
    ])

# ── P7: Simulador ──────────────────────────────────────────────────────────
def page_simulador():
    receita_media = df[df["Churn"]==1]["Receita_Estimada"].mean()

    def calcular(reducao_pct, custo_cliente):
        salvos = round(cancelados * reducao_pct / 100)
        recuperada = salvos * receita_media
        custo = salvos * custo_cliente
        roi = (recuperada - custo) / custo * 100 if custo > 0 else 0
        payback = custo / (recuperada / 12) if recuperada > 0 else 0
        return salvos, recuperada, custo, roi, payback

    cenarios_df = pd.DataFrame([
        {"Redução": f"{p}%", **dict(zip(
            ["Clientes Salvos","Receita Recuperada","Custo","ROI %","Payback (meses)"],
            [round(calcular(p,150)[0]), calcular(p,150)[1], calcular(p,150)[2],
             round(calcular(p,150)[3],1), round(calcular(p,150)[4],1)]
        ))} for p in [5,10,15,20,25]
    ])

    fig_cenarios = go.Figure([
        go.Bar(name="Receita Recuperada",
               x=cenarios_df["Redução"], y=cenarios_df["Receita Recuperada"], marker_color=GREEN),
        go.Bar(name="Custo da Campanha",
               x=cenarios_df["Redução"], y=cenarios_df["Custo"], marker_color=YELLOW),
    ])
    fig_cenarios.update_layout(barmode="group", title="Receita Recuperada vs Custo por Cenário", **PLOT_LAYOUT)

    fig_roi = go.Figure(go.Bar(
        x=cenarios_df["Redução"], y=cenarios_df["ROI %"],
        marker_color=[GREEN if v > 0 else RED for v in cenarios_df["ROI %"]],
        text=cenarios_df["ROI %"].astype(str)+"%", textposition="outside",
    ))
    fig_roi.update_layout(title="ROI por Cenário de Redução de Churn", **PLOT_LAYOUT)

    return html.Div([
        html.H2("Simulador de Cenários", style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Avalie o impacto financeiro de diferentes estratégias de retenção",
               style={"color":MUTED,"marginBottom":"24px"}),

        dbc.Card([dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Label("Redução de Churn (%)", style={"color":MUTED,"fontSize":"0.8rem"}),
                    dcc.Slider(id="sl-reducao", min=1, max=30, step=1, value=10,
                               marks={i:{"label":f"{i}%","style":{"color":MUTED}} for i in [1,5,10,15,20,25,30]},
                               tooltip={"placement":"bottom","always_visible":True}),
                ], md=6),
                dbc.Col([
                    html.Label("Custo por Cliente Retido (R$)", style={"color":MUTED,"fontSize":"0.8rem"}),
                    dcc.Slider(id="sl-custo", min=50, max=500, step=50, value=150,
                               marks={i:{"label":f"R${i}","style":{"color":MUTED}} for i in [50,150,250,350,500]},
                               tooltip={"placement":"bottom","always_visible":True}),
                ], md=6),
            ])
        ])], style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px","marginBottom":"20px"}),

        dbc.Row(id="sim-kpis", className="mb-4 g-2"),

        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_cenarios, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_roi,      config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
        ], className="g-2"),
    ])

# ── P8: Modelo Preditivo ───────────────────────────────────────────────────
def page_modelo():
    # Métricas
    rf_row = df_met[df_met["Modelo"]=="Random Forest"].iloc[0]

    fig_imp = go.Figure(go.Bar(
        x=df_imp["Importancia_Pct"].head(8),
        y=df_imp["Variavel_PT"].head(8) if "Variavel_PT" in df_imp.columns else df_imp["Variavel"].head(8),
        orientation="h", marker_color=BLUE,
        text=df_imp["Importancia_Pct"].head(8).round(1).astype(str)+"%",
        textposition="outside",
    ))
    fig_imp.update_layout(title="Importância das Variáveis — Random Forest", **PLOT_LAYOUT)
    fig_imp.update_yaxes(autorange="reversed")

    # Distribuição de probabilidade
    hist_data = df_pred["Prob_Churn"]
    fig_hist = go.Figure([
        go.Histogram(x=df_pred[df_pred["Churn"]==0]["Prob_Churn"], nbinsx=20,
                     name="Ativo", marker_color=GREEN, opacity=0.7),
        go.Histogram(x=df_pred[df_pred["Churn"]==1]["Prob_Churn"], nbinsx=20,
                     name="Cancelou", marker_color=RED, opacity=0.7),
    ])
    fig_hist.update_layout(barmode="overlay", title="Distribuição de Probabilidade de Churn",
                           xaxis_title="Probabilidade (%)", **PLOT_LAYOUT)

    # Matriz de confusão
    fig_cm = go.Figure(go.Heatmap(
        z=df_cm.values, x=df_cm.columns.tolist(), y=df_cm.index.tolist(),
        colorscale=[[0,"#12104a"],[1,"#f472b6"]],
        text=df_cm.values, texttemplate="%{text}",
        textfont=dict(size=20, color=TEXT),
        colorbar=dict(tickfont=dict(color=TEXT)),
    ))
    fig_cm.update_layout(title="Matriz de Confusão — Random Forest", **PLOT_LAYOUT)

    # Comparação de modelos
    fig_modelos = go.Figure()
    metricas_cols = ["Accuracy","Precision","Recall","F1-Score","ROC-AUC"]
    colors = [BLUE, GREEN, YELLOW]
    for i, row in df_met.iterrows():
        fig_modelos.add_trace(go.Bar(
            name=row["Modelo"],
            x=metricas_cols,
            y=[row[m] for m in metricas_cols],
            marker_color=colors[i % len(colors)],
        ))
    fig_modelos.update_layout(barmode="group", title="Comparação de Modelos de ML", **PLOT_LAYOUT)
    fig_modelos.update_yaxes(range=[0, 1])

    return html.Div([
        html.H2("Modelo Preditivo de Churn", style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Machine Learning para antecipar clientes com risco de cancelamento",
               style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(kpi_card("Accuracy",  f"{rf_row['Accuracy']:.1%}",  "Random Forest", BLUE,   "🎯"), md=3),
            dbc.Col(kpi_card("Precision", f"{rf_row['Precision']:.1%}", "Random Forest", BLUE,   "🔍"), md=3),
            dbc.Col(kpi_card("Recall",    f"{rf_row['Recall']:.1%}",    "Random Forest", YELLOW, "📡"), md=3),
            dbc.Col(kpi_card("F1-Score",  f"{rf_row['F1-Score']:.1%}",  "Random Forest", GREEN,  "⭐"), md=3),
        ], className="mb-4 g-2"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_imp,     config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_hist,    config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=6),
        ], className="mb-3 g-2"),
        dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_cm,      config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=5),
            dbc.Col(dbc.Card(dcc.Graph(figure=fig_modelos, config={"displayModeBar":False}),
                             style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}), md=7),
        ], className="g-2"),
    ])

# ── P9: Recomendações ──────────────────────────────────────────────────────
def page_recomendacoes():
    def rec_card(prioridade, cor, titulo, problema, impacto, acao, metrica_label, metrica_valor):
        return dbc.Card([dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.Span(prioridade, style={
                        "background": cor, "color": "#000", "borderRadius": "20px",
                        "padding": "3px 12px", "fontSize": "0.7rem", "fontWeight": "700"
                    }),
                    html.H5(titulo, style={"color": TEXT, "marginTop": "10px", "fontWeight": "700"}),
                ], md=8),
                dbc.Col([
                    html.P(metrica_label, style={"color": MUTED, "fontSize": "0.72rem", "margin": "0"}),
                    html.H4(metrica_valor, style={"color": cor, "fontWeight": "700", "margin": "0"}),
                ], md=4, style={"textAlign": "right"}),
            ]),
            html.Hr(style={"borderColor": BORDER, "margin": "10px 0"}),
            dbc.Row([
                dbc.Col([html.P("Problema", style={"color": MUTED, "fontSize": "0.7rem", "margin": "0"}),
                         html.P(problema, style={"color": TEXT, "fontSize": "0.85rem"})], md=4),
                dbc.Col([html.P("Impacto", style={"color": MUTED, "fontSize": "0.7rem", "margin": "0"}),
                         html.P(impacto, style={"color": TEXT, "fontSize": "0.85rem"})], md=4),
                dbc.Col([html.P("Recomendação", style={"color": MUTED, "fontSize": "0.7rem", "margin": "0"}),
                         html.P(acao, style={"color": TEXT, "fontSize": "0.85rem"})], md=4),
            ]),
        ])], style={"background": CARD_BG, "border": f"1px solid {cor}33",
                    "borderLeft": f"4px solid {cor}", "borderRadius": "10px", "marginBottom": "14px"})

    taxa_1p  = df[df["Qtd_Produtos"]==1]["Churn"].mean()
    rec_1p   = df[(df["Qtd_Produtos"]==1)&(df["Churn"]==1)]["Receita_Estimada"].sum()
    taxa_in  = df[df["Membro_Ativo"]=="Não"]["Churn"].mean()
    rec_in   = df[(df["Membro_Ativo"]=="Não")&(df["Churn"]==1)]["Receita_Estimada"].sum()
    taxa_46  = df[df["Faixa_Etaria"]=="46-55"]["Churn"].mean()
    rec_46   = df[(df["Faixa_Etaria"]=="46-55")&(df["Churn"]==1)]["Receita_Estimada"].sum()
    taxa_av  = df[df["Segmento_Valor"]=="Alto Valor"]["Churn"].mean()
    rec_av   = df[(df["Segmento_Valor"]=="Alto Valor")&(df["Churn"]==1)]["Receita_Estimada"].sum()
    taxa_new = df[df["Tempo_Conta_Anos"]<=2]["Churn"].mean()
    rec_new  = df[(df["Tempo_Conta_Anos"]<=2)&(df["Churn"]==1)]["Receita_Estimada"].sum()

    return html.Div([
        html.H2("Recomendações Estratégicas", style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Transformando dados em ações práticas para aumentar a retenção",
               style={"color":MUTED,"marginBottom":"8px"}),
        dbc.Row([
            dbc.Col(kpi_card("Potencial Total de Retenção",
                             fmt_brl(rec_1p+rec_in+rec_46+rec_av+rec_new),
                             "soma das 5 oportunidades identificadas", GREEN, "💡"), md=4),
            dbc.Col(kpi_card("Maior Alavanca Individual", "Membros Inativos",
                             f"taxa de churn: {taxa_in:.1%}", RED, "🎯"), md=4),
            dbc.Col(kpi_card("Clientes Prioritários",
                             f"{df[(df['Nivel_Risco']=='Alto Risco')&(df['Segmento_Valor']=='Alto Valor')].shape[0]:,}",
                             "Alto Risco + Alto Valor", PURPLE, "⭐"), md=4),
        ], className="mb-4 g-2"),

        rec_card("PRIORIDADE ALTA", RED,
            "Cross-sell para clientes com 1 produto",
            f"Clientes com 1 produto têm taxa de churn de {taxa_1p:.1%} — quase o dobro da média.",
            f"{fmt_brl(rec_1p)} em receita perdida por este grupo no período.",
            "Criar campanha de cross-sell personalizada com oferta de segundo produto com benefício exclusivo nos primeiros 3 meses.",
            "Receita em Risco", fmt_brl(rec_1p)),

        rec_card("PRIORIDADE ALTA", RED,
            "Reengajamento de membros inativos",
            f"Membros inativos cancelam {taxa_in:.1%} do tempo — {(taxa_in/taxa_churn-1):.0%} acima da média.",
            f"{fmt_brl(rec_in)} em receita perdida por inatividade.",
            "Programa de reativação com benefícios progressivos: cashback na 1ª transação, pontos bônus e acesso a produto premium.",
            "Receita em Risco", fmt_brl(rec_in)),

        rec_card("PRIORIDADE MÉDIA", YELLOW,
            "Retenção proativa da faixa 46-55 anos",
            f"Clientes entre 46-55 anos têm churn de {taxa_46:.1%}, concentrando grande volume de cancelamentos.",
            f"{fmt_brl(rec_46)} em receita potencial perdida neste segmento.",
            "Oferecer produtos financeiros de perfil conservador (previdência, CDB de longo prazo) alinhados ao momento de vida desta faixa.",
            "Receita em Risco", fmt_brl(rec_46)),

        rec_card("PRIORIDADE ALTA", PURPLE,
            "Programa VIP para clientes de Alto Valor",
            f"Clientes de Alto Valor têm taxa de churn de {taxa_av:.1%} — inaceitável para quem gera mais receita.",
            f"{fmt_brl(rec_av)} em receita de alto valor em risco de cancelamento.",
            "Criar gerente de relacionamento dedicado, SLA de atendimento preferencial e revisão trimestral de portfólio.",
            "Receita em Risco", fmt_brl(rec_av)),

        rec_card("PRIORIDADE MÉDIA", YELLOW,
            "Onboarding reforçado nos primeiros 2 anos",
            f"Clientes novos (0-2 anos) apresentam churn de {taxa_new:.1%} — janela crítica de abandono.",
            f"{fmt_brl(rec_new)} perdidos em clientes nos primeiros 2 anos.",
            "Jornada de onboarding de 90 dias com milestones, tutoriais de produtos e check-in automático no 6º e 12º mês.",
            "Receita em Risco", fmt_brl(rec_new)),
    ])

# ══════════════════════════════════════════════════════════════════════════════
# CALLBACKS
# ══════════════════════════════════════════════════════════════════════════════

@app.callback(Output("page-content","children"), Input("url","pathname"))
def render(path):
    routes = {
        "/":             page_executiva,
        "/perfil":       page_perfil,
        "/produtos":     page_produtos,
        "/receita":      page_receita,
        "/risco":        page_risco,
        "/jornada":      page_jornada,
        "/simulador":    page_simulador,
        "/modelo":       page_modelo,
        "/recomendacoes":page_recomendacoes,
    }
    fn = routes.get(path, page_executiva)
    return fn()

@app.callback(
    Output("sim-kpis","children"),
    Input("sl-reducao","value"),
    Input("sl-custo","value"),
)
def update_sim(reducao, custo_cliente):
    receita_media = df[df["Churn"]==1]["Receita_Estimada"].mean()
    salvos    = round(cancelados * reducao / 100)
    recuperada = salvos * receita_media
    custo     = salvos * custo_cliente
    roi       = (recuperada - custo) / custo * 100 if custo > 0 else 0
    payback   = custo / (recuperada / 12) if recuperada > 0 else 0
    nova_taxa = taxa_churn * (1 - reducao/100)

    return [
        dbc.Col(kpi_card("Clientes Salvos",         f"{salvos:,}", f"redução de {reducao}%", GREEN, "✅"), md=3),
        dbc.Col(kpi_card("Receita Recuperada",       fmt_brl(recuperada), "estimativa anual", GREEN, "💰"), md=3),
        dbc.Col(kpi_card("Custo da Campanha",        fmt_brl(custo), f"R$ {custo_cliente}/cliente", YELLOW, "💸"), md=3),
        dbc.Col(kpi_card("ROI da Campanha",          f"{roi:.0f}%",
                          f"Payback em {payback:.1f} meses",
                          GREEN if roi > 0 else RED, "📈"), md=3),
    ]

# ──────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import webbrowser, threading
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:8050")).start()
    print("\n" + "="*50)
    print("  Dashboard de Churn — Fintech Digital")
    print("  Acesse: http://localhost:8050")
    print("="*50 + "\n")
    app.run(debug=False, host="0.0.0.0", port=8050)
