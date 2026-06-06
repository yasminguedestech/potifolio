"""
RICE Prioritization Dashboard
Execute: python app.py → http://localhost:8053
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
df    = pd.read_excel(BASE / "data/rice_dashboard.xlsx", sheet_name="Features")
dfh   = pd.read_excel(BASE / "data/rice_dashboard.xlsx", sheet_name="Historico")

BG=   "#08071a"; CARD_BG="#100f2e"; BORDER="#2a2560"
PINK= "#f472b6"; CYAN= "#38bdf8";  BLUE= "#6366f1"
PURPLE="#a78bfa"; LAV="#818cf8";   TEXT="#ede9ff"; MUTED="#8b7ec8"
GREEN="#34d399";  YELLOW="#fbbf24"

STATUS_C={"Backlog":MUTED,"Em andamento":CYAN,"Concluído":GREEN}
PRIO_C={"Alta":PINK,"Média":CYAN,"Baixa":MUTED}

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
    suppress_callback_exceptions=True,title="RICE Dashboard")

PAGES=[("01","Ranking RICE","/"),("02","Análise de Fatores","/fatores"),("03","Roadmap","/roadmap"),("04","Simulador","/simulador")]

sidebar=html.Div([
    html.Div([html.Div("🎯",style={"fontSize":"1.8rem"}),
        html.Div([html.P("RICE Prioritization",style={"margin":"0","fontWeight":"700","fontSize":"0.9rem","color":TEXT}),
                  html.P("Product Backlog",style={"margin":"0","fontSize":"0.68rem","color":MUTED})])
    ],style={"display":"flex","gap":"12px","alignItems":"center","padding":"20px 16px 16px","borderBottom":f"1px solid {BORDER}"}),
    html.Nav([html.A([html.Span(n,style={"color":MUTED,"fontSize":"0.7rem","minWidth":"22px"}),html.Span(l,style={"fontSize":"0.82rem"})],
        href=h,style={"display":"flex","gap":"10px","alignItems":"center","padding":"10px 16px","color":TEXT,"textDecoration":"none","borderRadius":"8px"})
        for n,l,h in PAGES],style={"padding":"10px 8px","display":"flex","flexDirection":"column","gap":"2px"}),
    html.Div([html.P("20 features · 4 sprints",style={"color":MUTED,"fontSize":"0.68rem","margin":"0"})],
        style={"padding":"16px","borderTop":f"1px solid {BORDER}","marginTop":"auto"}),
],style={"width":"220px","minWidth":"220px","background":CARD_BG,"borderRight":f"1px solid {BORDER}",
    "height":"100vh","overflowY":"auto","position":"fixed","left":"0","top":"0","zIndex":"100","display":"flex","flexDirection":"column"})

app.layout=html.Div([dcc.Location(id="url"),sidebar,
    html.Div(id="page-content",style={"marginLeft":"220px","background":BG,"minHeight":"100vh","padding":"28px 32px","color":TEXT})],
    style={"fontFamily":"Inter, sans-serif","background":BG})

def page_ranking():
    # Barras horizontais — top 15 por RICE
    top=df.head(15)
    fig_rice=go.Figure(go.Bar(y=top["Feature"],x=top["RICE_Score"],orientation="h",
        marker_color=[PRIO_C.get(p,MUTED) for p in top["Prioridade"]],
        text=top["RICE_Score"].astype(int),textposition="outside"))
    fig_rice.update_layout(title="Ranking RICE — Top 15 Features",**PLOT_LAYOUT)
    fig_rice.update_yaxes(autorange="reversed")

    # Pizza por status
    sc=df["Status"].value_counts().reset_index()
    fig_status=go.Figure(go.Pie(labels=sc["Status"],values=sc["count"],hole=0.6,
        marker_colors=[STATUS_C.get(s,MUTED) for s in sc["Status"]],
        textinfo="label+percent",textfont_color=TEXT))
    fig_status.update_layout(title="Features por Status",showlegend=False,**PLOT_LAYOUT)

    # Scatter: Effort vs RICE
    fig_scatter=px.scatter(df,x="Effort",y="RICE_Score",color="Categoria",size="Reach",
        hover_name="Feature",title="Esforço vs RICE Score",
        labels={"Effort":"Esforço (semanas)","RICE_Score":"RICE Score"})
    fig_scatter.update_layout(**PLOT_LAYOUT)

    # Tabela completa
    tabela=dash_table.DataTable(
        data=df[["Rank","Feature","Categoria","Reach","Impact","Confidence","Effort","RICE_Score","Prioridade","Status"]].to_dict("records"),
        columns=[{"name":c,"id":c} for c in ["Rank","Feature","Categoria","Reach","Impact","Confidence","Effort","RICE_Score","Prioridade","Status"]],
        style_table={"overflowX":"auto"},
        style_cell={"backgroundColor":CARD_BG,"color":TEXT,"border":f"1px solid {BORDER}","fontFamily":"Inter","fontSize":"0.8rem","padding":"8px"},
        style_header={"backgroundColor":"#1c1a4a","color":TEXT,"fontWeight":"700","border":f"1px solid {BORDER}"},
        style_data_conditional=[
            {"if":{"filter_query":'{Prioridade} = "Alta"'},"color":PINK,"fontWeight":"700"},
            {"if":{"filter_query":'{Prioridade} = "Média"'},"color":CYAN},
            {"if":{"column_id":"RICE_Score"},"fontWeight":"700"},
        ],
        sort_action="native",page_size=10)

    return html.Div([
        html.H2("Ranking RICE",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Priorize features automaticamente com Reach × Impact × Confidence ÷ Effort",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(kpi("Total Features",f"{len(df)}","no backlog",BLUE,"📋"),md=3),
            dbc.Col(kpi("Alta Prioridade",f"{(df['Prioridade']=='Alta').sum()}","RICE > 6.000",PINK,"🔴"),md=3),
            dbc.Col(kpi("Em Andamento",f"{(df['Status']=='Em andamento').sum()}","features ativas",CYAN,"⚡"),md=3),
            dbc.Col(kpi("Score Máximo",f"{df['RICE_Score'].max():,.0f}","feature #1",PURPLE,"🏆"),md=3),
        ],className="mb-4 g-2"),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_rice,config={"displayModeBar":False})),md=8),
            dbc.Col(card(dcc.Graph(figure=fig_status,config={"displayModeBar":False})),md=4),
        ],className="mb-3 g-2"),
        dbc.Row([dbc.Col(card(dcc.Graph(figure=fig_scatter,config={"displayModeBar":False})),md=12)],className="mb-3 g-2"),
        dbc.Card([dbc.CardBody([html.H6("Todas as Features",style={"color":TEXT,"marginBottom":"12px"}),tabela])],
            style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px"}),
    ])

def page_fatores():
    fig_r=go.Figure(go.Bar(x=df["Feature"].head(10),y=df["Reach"].head(10),marker_color=BLUE,name="Reach"))
    fig_r.update_layout(title="Reach por Feature (Top 10)",**PLOT_LAYOUT)
    fig_r.update_xaxes(tickangle=-30)

    cat=df.groupby("Categoria")["RICE_Score"].mean().sort_values(ascending=False).reset_index()
    fig_cat=go.Figure(go.Bar(x=cat["Categoria"],y=cat["RICE_Score"].round(0),
        marker_color=PURPLE,text=cat["RICE_Score"].round(0).astype(int),textposition="outside"))
    fig_cat.update_layout(title="RICE Médio por Categoria",**PLOT_LAYOUT)

    fig_heatmap=go.Figure(go.Heatmap(
        z=[df["Reach"].head(10).tolist(),df["Impact"].head(10).tolist(),
           df["Confidence"].head(10).tolist()],
        x=df["Feature"].head(10).tolist(),
        y=["Reach","Impact","Confidence"],
        colorscale=[[0,"#12104a"],[0.5,"#6366f1"],[1,"#f472b6"]],
        colorbar=dict(tickfont=dict(color=TEXT))))
    fig_heatmap.update_layout(title="Heatmap de Fatores RICE",**PLOT_LAYOUT)
    fig_heatmap.update_xaxes(tickangle=-30)

    return html.Div([
        html.H2("Análise de Fatores",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Como cada fator (R·I·C·E) contribui para o score final",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_r,config={"displayModeBar":False})),md=6),
            dbc.Col(card(dcc.Graph(figure=fig_cat,config={"displayModeBar":False})),md=6),
        ],className="mb-3 g-2"),
        dbc.Row([dbc.Col(card(dcc.Graph(figure=fig_heatmap,config={"displayModeBar":False})),md=12)],className="g-2"),
    ])

def page_roadmap():
    status_order=["Em andamento","Backlog","Concluído"]
    colors={"Em andamento":CYAN,"Backlog":LAVANDA if False else LAV,"Concluído":GREEN}
    fig=go.Figure()
    for i,(_, row) in enumerate(df.head(12).iterrows()):
        fig.add_trace(go.Bar(
            name=row["Status"],x=[row["Semanas_Est"]],y=[row["Feature"]],
            orientation="h",marker_color=STATUS_C.get(row["Status"],MUTED),
            showlegend=i<3,legendgroup=row["Status"],
            text=f"{row['Semanas_Est']}s",textposition="inside"))
    fig.update_layout(barmode="stack",title="Roadmap — Estimativa de Semanas (Top 12)",**PLOT_LAYOUT)
    fig.update_yaxes(autorange="reversed")

    evo=dfh.groupby(["Sprint","Feature"])["Score"].mean().reset_index()
    top5=df.head(5)["Feature"].tolist()
    fig_evo=go.Figure()
    for feat in top5:
        sub=evo[evo["Feature"]==feat]
        fig_evo.add_trace(go.Scatter(x=sub["Sprint"],y=sub["Score"],mode="lines+markers",name=feat,line=dict(width=2)))
    fig_evo.update_layout(title="Evolução do Score por Sprint (Top 5)",**PLOT_LAYOUT)

    return html.Div([
        html.H2("Roadmap & Evolução",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Planejamento de entregas e histórico de score por sprint",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([dbc.Col(card(dcc.Graph(figure=fig,config={"displayModeBar":False})),md=12)],className="mb-3 g-2"),
        dbc.Row([dbc.Col(card(dcc.Graph(figure=fig_evo,config={"displayModeBar":False})),md=12)],className="g-2"),
    ])

def page_simulador():
    return html.Div([
        html.H2("Simulador RICE",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Ajuste os parâmetros e veja o score recalculado em tempo real",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Card([dbc.CardBody([
            dbc.Row([
                dbc.Col([html.Label("Reach (usuários/mês)",style={"color":MUTED,"fontSize":"0.8rem"}),
                    dcc.Slider(id="sl-reach",min=500,max=10000,step=500,value=5000,
                        marks={i:{"label":f"{i//1000}K","style":{"color":MUTED}} for i in range(0,11000,2000)},
                        tooltip={"placement":"bottom","always_visible":True})],md=6),
                dbc.Col([html.Label("Impact (0.25=mínimo, 3=máximo)",style={"color":MUTED,"fontSize":"0.8rem"}),
                    dcc.Slider(id="sl-impact",min=0.25,max=3,step=0.25,value=2,
                        marks={v:{"label":str(v),"style":{"color":MUTED}} for v in [0.25,0.5,1,2,3]},
                        tooltip={"placement":"bottom","always_visible":True})],md=6),
            ],className="mb-3"),
            dbc.Row([
                dbc.Col([html.Label("Confidence (%)",style={"color":MUTED,"fontSize":"0.8rem"}),
                    dcc.Slider(id="sl-conf",min=10,max=100,step=5,value=80,
                        marks={i:{"label":f"{i}%","style":{"color":MUTED}} for i in [10,25,50,75,100]},
                        tooltip={"placement":"bottom","always_visible":True})],md=6),
                dbc.Col([html.Label("Effort (semanas-pessoa)",style={"color":MUTED,"fontSize":"0.8rem"}),
                    dcc.Slider(id="sl-effort",min=1,max=10,step=1,value=2,
                        marks={i:{"label":f"{i}s","style":{"color":MUTED}} for i in range(1,11)},
                        tooltip={"placement":"bottom","always_visible":True})],md=6),
            ]),
        ])],style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"10px","marginBottom":"20px"}),
        dbc.Row(id="sim-rice-kpis",className="mb-4 g-2"),
        dbc.Row([dbc.Col(card(dcc.Graph(id="fig-rice-sim",config={"displayModeBar":False})),md=12)],className="g-2"),
    ])

@app.callback(Output("page-content","children"),Input("url","pathname"))
def render(path):
    return {"/":page_ranking,"/fatores":page_fatores,"/roadmap":page_roadmap,"/simulador":page_simulador}.get(path,page_ranking)()

@app.callback(
    Output("sim-rice-kpis","children"),Output("fig-rice-sim","figure"),
    Input("sl-reach","value"),Input("sl-impact","value"),Input("sl-conf","value"),Input("sl-effort","value"))
def update_sim(reach,impact,conf,effort):
    score=round((reach*impact*conf)/effort,1)
    rank=int((df["RICE_Score"]>score).sum())+1
    prio="Alta" if score>6000 else "Média" if score>3000 else "Baixa"
    cor=PINK if prio=="Alta" else CYAN if prio=="Média" else MUTED
    kpis=[
        dbc.Col(kpi("RICE Score",f"{score:,.0f}","calculado",cor,"🎯"),md=3),
        dbc.Col(kpi("Posição no Ranking",f"#{rank}",f"de {len(df)} features",PURPLE,"📊"),md=3),
        dbc.Col(kpi("Prioridade",prio,"classificação",cor,"🏷️"),md=3),
        dbc.Col(kpi("Duração Estimada",f"{effort*2} semanas","para entrega",CYAN,"⏱️"),md=3),
    ]
    scores_comp=df["RICE_Score"].tolist()+[score]
    labels=df["Feature"].tolist()+["◀ Sua Feature"]
    colors_comp=[PRIO_C.get(p,MUTED) for p in df["Prioridade"].tolist()]+[YELLOW]
    fig=go.Figure(go.Bar(y=labels,x=scores_comp,orientation="h",marker_color=colors_comp,
        text=[f"{s:,.0f}" for s in scores_comp],textposition="outside"))
    fig.update_layout(title="Comparação com o Backlog Atual",**PLOT_LAYOUT)
    fig.update_yaxes(autorange="reversed")
    return kpis,fig

if __name__=="__main__":
    import webbrowser,threading
    threading.Timer(1.5,lambda:webbrowser.open("http://localhost:8053")).start()
    print("\n  RICE Dashboard: http://localhost:8053\n")
    app.run(debug=False,host="0.0.0.0",port=8053)
