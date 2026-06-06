"""
Feedback Classifier Dashboard
Execute: python app.py → http://localhost:8054
"""
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

BASE = Path(__file__).parent
df   = pd.read_excel(BASE / "data/feedbacks.xlsx", sheet_name="Feedbacks")
dmen = pd.read_excel(BASE / "data/feedbacks.xlsx", sheet_name="Mensal")

BG="#08071a"; CARD_BG="#100f2e"; BORDER="#2a2560"
PINK="#f472b6"; CYAN="#38bdf8"; BLUE="#6366f1"
PURPLE="#a78bfa"; LAV="#818cf8"; TEXT="#ede9ff"; MUTED="#8b7ec8"
GREEN="#34d399"; YELLOW="#fbbf24"

SENT_C={"Positivo":CYAN,"Negativo":PINK,"Neutro":LAV}
PRIO_C={"Alta":PINK,"Média":CYAN,"Baixa":MUTED}
TEMA_C={"UX/Design":PURPLE,"Performance":PINK,"Funcionalidade":BLUE,
        "Atendimento":GREEN,"Preço/Planos":YELLOW,"Onboarding":CYAN}

PLOT_LAYOUT=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT,family="Inter, sans-serif",size=12),
    margin=dict(t=40,b=40,l=40,r=20),
    legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=TEXT)),
    xaxis=dict(gridcolor=BORDER,zerolinecolor=BORDER,color=TEXT),
    yaxis=dict(gridcolor=BORDER,zerolinecolor=BORDER,color=TEXT))

def kpi(title,value,sub=None,color=BLUE,icon=""):
    return dbc.Card([dbc.CardBody([
        html.P([icon," ",title],style={"color":MUTED,"fontSize":"0.72rem","textTransform":"uppercase","letterSpacing":"0.08em","marginBottom":"4px"}),
        html.H3(value,style={"color":color,"fontWeight":"700","margin":"0"}),
        html.P(sub or "",style={"color":MUTED,"fontSize":"0.72rem","margin":"0"}),
    ])],style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px","height":"100%"})

def card(children):
    return dbc.Card(children,style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"})

app=dash.Dash(__name__,
    external_stylesheets=[dbc.themes.SLATE,"https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"],
    suppress_callback_exceptions=True,title="Feedback Classifier")

PAGES=[("01","Visão Geral","/"),("02","Por Tema","/temas"),("03","Análise de Sentimento","/sentimento"),("04","Ações","/acoes")]

sidebar=html.Div([
    html.Div([html.Div("💬",style={"fontSize":"1.8rem"}),
        html.Div([html.P("Feedback Classifier",style={"margin":"0","fontWeight":"700","fontSize":"0.9rem","color":TEXT}),
                  html.P("Classificação com IA",style={"margin":"0","fontSize":"0.68rem","color":MUTED})])
    ],style={"display":"flex","gap":"12px","alignItems":"center","padding":"20px 16px 16px","borderBottom":f"1px solid {BORDER}"}),
    html.Nav([html.A([html.Span(n,style={"color":MUTED,"fontSize":"0.7rem","minWidth":"22px"}),html.Span(l,style={"fontSize":"0.82rem"})],
        href=h,style={"display":"flex","gap":"10px","alignItems":"center","padding":"10px 16px","color":TEXT,"textDecoration":"none","borderRadius":"8px"})
        for n,l,h in PAGES],style={"padding":"10px 8px","display":"flex","flexDirection":"column","gap":"2px"}),
    html.Div([html.P("800 feedbacks · 12 meses",style={"color":MUTED,"fontSize":"0.68rem","margin":"0"})],
        style={"padding":"16px","borderTop":f"1px solid {BORDER}","marginTop":"auto"}),
],style={"width":"220px","minWidth":"220px","background":CARD_BG,"borderRight":f"1px solid {BORDER}",
    "height":"100vh","overflowY":"auto","position":"fixed","left":"0","top":"0","zIndex":"100","display":"flex","flexDirection":"column"})

app.layout=html.Div([dcc.Location(id="url"),sidebar,
    html.Div(id="page-content",style={"marginLeft":"220px","background":BG,"minHeight":"100vh","padding":"28px 32px","color":TEXT})],
    style={"fontFamily":"Inter, sans-serif","background":BG})

def page_geral():
    pos=(df["Sentimento"]=="Positivo").sum()
    neg=(df["Sentimento"]=="Negativo").sum()
    nps=df["NPS"].mean()

    fig_sent=go.Figure(go.Pie(labels=["Positivo","Negativo","Neutro"],
        values=[(df["Sentimento"]==s).sum() for s in ["Positivo","Negativo","Neutro"]],
        hole=0.6,marker_colors=[CYAN,PINK,LAV],textinfo="label+percent",textfont_color=TEXT))
    fig_sent.update_layout(title="Distribuição de Sentimentos",showlegend=False,**PLOT_LAYOUT)

    fig_vol=go.Figure([
        go.Bar(x=dmen["Mes"],y=dmen["Positivos"],name="Positivos",marker_color=CYAN,opacity=0.85),
        go.Bar(x=dmen["Mes"],y=dmen["Negativos"],name="Negativos",marker_color=PINK,opacity=0.85),
    ])
    fig_vol.update_layout(barmode="group",title="Volume Mensal por Sentimento",**PLOT_LAYOUT)

    fig_nps=go.Figure(go.Scatter(x=dmen["Mes"],y=dmen["NPS_Medio"].round(1),
        mode="lines+markers",line=dict(color=PURPLE,width=3),marker=dict(size=8),
        fill="tozeroy",fillcolor="rgba(167,139,250,0.10)"))
    fig_nps.update_layout(title="NPS Médio Mensal",yaxis=dict(range=[0,10]),**PLOT_LAYOUT)

    canal=df["Canal"].value_counts().reset_index()
    fig_canal=go.Figure(go.Bar(x=canal["Canal"],y=canal["count"],
        marker_color=[BLUE,PURPLE,CYAN,PINK,LAV],text=canal["count"],textposition="outside"))
    fig_canal.update_layout(title="Feedbacks por Canal",**PLOT_LAYOUT)

    return html.Div([
        html.H2("Visão Geral dos Feedbacks",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("800 feedbacks classificados por tema, sentimento e prioridade",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(kpi("Total Feedbacks",f"{len(df):,}","em 12 meses",BLUE,"💬"),md=3),
            dbc.Col(kpi("Positivos",f"{pos}",f"{pos/len(df):.1%} do total",CYAN,"😊"),md=3),
            dbc.Col(kpi("Negativos",f"{neg}",f"{neg/len(df):.1%} do total",PINK,"😞"),md=3),
            dbc.Col(kpi("NPS Médio",f"{nps:.1f}","/10 — média geral",PURPLE,"⭐"),md=3),
        ],className="mb-4 g-2"),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_sent,config={"displayModeBar":False})),md=4),
            dbc.Col(card(dcc.Graph(figure=fig_vol,config={"displayModeBar":False})),md=8),
        ],className="mb-3 g-2"),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_nps,config={"displayModeBar":False})),md=6),
            dbc.Col(card(dcc.Graph(figure=fig_canal,config={"displayModeBar":False})),md=6),
        ],className="g-2"),
    ])

def page_temas():
    tema_cnt=df["Tema"].value_counts().reset_index()
    fig_tema=go.Figure(go.Bar(x=tema_cnt["Tema"],y=tema_cnt["count"],
        marker_color=[TEMA_C.get(t,MUTED) for t in tema_cnt["Tema"]],
        text=tema_cnt["count"],textposition="outside"))
    fig_tema.update_layout(title="Volume por Tema",**PLOT_LAYOUT)

    # Sentimento por tema
    pivot=df.groupby(["Tema","Sentimento"]).size().unstack(fill_value=0).reset_index()
    fig_stack=go.Figure()
    for sent,color in [("Positivo",CYAN),("Neutro",LAV),("Negativo",PINK)]:
        if sent in pivot.columns:
            fig_stack.add_trace(go.Bar(name=sent,x=pivot["Tema"],y=pivot[sent],marker_color=color))
    fig_stack.update_layout(barmode="stack",title="Sentimento por Tema",**PLOT_LAYOUT)

    # NPS médio por tema
    nps_tema=df.groupby("Tema")["NPS"].mean().sort_values(ascending=False).reset_index()
    fig_nps_tema=go.Figure(go.Bar(x=nps_tema["Tema"],y=nps_tema["NPS"].round(1),
        marker_color=[TEMA_C.get(t,MUTED) for t in nps_tema["Tema"]],
        text=nps_tema["NPS"].round(1),textposition="outside"))
    fig_nps_tema.update_layout(title="NPS Médio por Tema",**PLOT_LAYOUT)

    return html.Div([
        html.H2("Análise por Tema",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Quais temas concentram mais feedbacks e qual o sentimento em cada área",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_tema,config={"displayModeBar":False})),md=6),
            dbc.Col(card(dcc.Graph(figure=fig_nps_tema,config={"displayModeBar":False})),md=6),
        ],className="mb-3 g-2"),
        dbc.Row([dbc.Col(card(dcc.Graph(figure=fig_stack,config={"displayModeBar":False})),md=12)],className="g-2"),
    ])

def page_sentimento():
    # Heatmap: tema x sentimento (%)
    heat=df.groupby(["Tema","Sentimento"]).size().unstack(fill_value=0)
    heat_pct=(heat.div(heat.sum(axis=1),axis=0)*100).round(1)
    fig_heat=go.Figure(go.Heatmap(
        z=heat_pct.values,x=heat_pct.columns.tolist(),y=heat_pct.index.tolist(),
        colorscale=[[0,"#12104a"],[0.5,"#6366f1"],[1,"#f472b6"]],
        text=heat_pct.values.round(1),texttemplate="%{text}%",
        colorbar=dict(tickfont=dict(color=TEXT))))
    fig_heat.update_layout(title="% de Sentimento por Tema",**PLOT_LAYOUT)

    # Por plano
    plano=df.groupby(["Plano","Sentimento"]).size().unstack(fill_value=0).reset_index()
    fig_plano=go.Figure()
    for sent,color in [("Positivo",CYAN),("Neutro",LAV),("Negativo",PINK)]:
        if sent in plano.columns:
            fig_plano.add_trace(go.Bar(name=sent,x=plano["Plano"],y=plano[sent],marker_color=color))
    fig_plano.update_layout(barmode="group",title="Sentimento por Plano",**PLOT_LAYOUT)

    # NPS por plano
    nps_plano=df.groupby("Plano")["NPS"].mean().reset_index()
    fig_nps_p=go.Figure(go.Bar(x=nps_plano["Plano"],y=nps_plano["NPS"].round(1),
        marker_color=[PURPLE,BLUE,CYAN],text=nps_plano["NPS"].round(1),textposition="outside"))
    fig_nps_p.update_layout(title="NPS por Plano",**PLOT_LAYOUT)

    return html.Div([
        html.H2("Análise de Sentimento",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Distribuição de sentimentos por tema, plano e canal",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([dbc.Col(card(dcc.Graph(figure=fig_heat,config={"displayModeBar":False})),md=12)],className="mb-3 g-2"),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_plano,config={"displayModeBar":False})),md=7),
            dbc.Col(card(dcc.Graph(figure=fig_nps_p,config={"displayModeBar":False})),md=5),
        ],className="g-2"),
    ])

def page_acoes():
    alta=df[df["Prioridade"]=="Alta"].groupby("Tema").agg(
        Feedbacks=("ID","count"), NPS_Medio=("NPS","mean")).round(1).reset_index()
    fig_alta=go.Figure(go.Bar(x=alta["Tema"],y=alta["Feedbacks"],
        marker_color=[TEMA_C.get(t,MUTED) for t in alta["Tema"]],
        text=alta["Feedbacks"],textposition="outside"))
    fig_alta.update_layout(title="Feedbacks de Alta Prioridade por Tema",**PLOT_LAYOUT)

    tabela=dash_table.DataTable(
        data=df[df["Prioridade"]=="Alta"].head(30)[["Data","Canal","Plano","Tema","Sentimento","Texto","Prioridade","Acao"]].to_dict("records"),
        columns=[{"name":c,"id":c} for c in ["Data","Canal","Plano","Tema","Sentimento","Texto","Prioridade","Acao"]],
        style_table={"overflowX":"auto"},
        style_cell={"backgroundColor":CARD_BG,"color":TEXT,"border":f"1px solid {BORDER}",
            "fontFamily":"Inter","fontSize":"0.8rem","padding":"8px","whiteSpace":"normal","maxWidth":"300px"},
        style_header={"backgroundColor":"#1c1a4a","color":TEXT,"fontWeight":"700","border":f"1px solid {BORDER}"},
        style_data_conditional=[
            {"if":{"column_id":"Sentimento","filter_query":'{Sentimento} = "Negativo"'},"color":PINK},
            {"if":{"column_id":"Prioridade"},"color":PINK,"fontWeight":"700"},
            {"if":{"column_id":"Acao"},"color":CYAN},
        ],
        page_size=10)

    prio_cnt=df["Prioridade"].value_counts().reset_index()
    fig_prio=go.Figure(go.Pie(labels=prio_cnt["Prioridade"],values=prio_cnt["count"],hole=0.6,
        marker_colors=[PRIO_C.get(p,MUTED) for p in prio_cnt["Prioridade"]],
        textinfo="label+percent",textfont_color=TEXT))
    fig_prio.update_layout(title="Distribuição por Prioridade",showlegend=False,**PLOT_LAYOUT)

    return html.Div([
        html.H2("Plano de Ação",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Feedbacks críticos que exigem ação imediata do time de produto",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(kpi("Alta Prioridade",f"{(df['Prioridade']=='Alta').sum()}","ação imediata",PINK,"🚨"),md=3),
            dbc.Col(kpi("Média Prioridade",f"{(df['Prioridade']=='Média').sum()}","monitorar",CYAN,"📋"),md=3),
            dbc.Col(kpi("Tema Crítico",df[df["Prioridade"]=="Alta"]["Tema"].value_counts().index[0],"mais reclamado",PINK,"⚠️"),md=3),
            dbc.Col(kpi("NPS Crítico",f"{df[df['Prioridade']=='Alta']['NPS'].mean():.1f}","/10 nas alta prio",PINK,"📉"),md=3),
        ],className="mb-4 g-2"),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_alta,config={"displayModeBar":False})),md=8),
            dbc.Col(card(dcc.Graph(figure=fig_prio,config={"displayModeBar":False})),md=4),
        ],className="mb-3 g-2"),
        dbc.Card([dbc.CardBody([
            html.H6("Feedbacks de Alta Prioridade — Ação Imediata",style={"color":PINK,"marginBottom":"12px"}),
            tabela])],
            style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}),
    ])

@app.callback(Output("page-content","children"),Input("url","pathname"))
def render(path):
    return {"/":page_geral,"/temas":page_temas,"/sentimento":page_sentimento,"/acoes":page_acoes}.get(path,page_geral)()

if __name__=="__main__":
    import webbrowser,threading
    threading.Timer(1.5,lambda:webbrowser.open("http://localhost:8054")).start()
    print("\n  Feedback Classifier: http://localhost:8054\n")
    app.run(debug=False,host="0.0.0.0",port=8054)
