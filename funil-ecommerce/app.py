"""
Funil de Conversão E-commerce Dashboard
Execute: python app.py → http://localhost:8055
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
df_funil = pd.read_excel(BASE / "data/funil_ecommerce.xlsx", sheet_name="Funil_Geral")
df_canal = pd.read_excel(BASE / "data/funil_ecommerce.xlsx", sheet_name="Por_Canal")
df_disp  = pd.read_excel(BASE / "data/funil_ecommerce.xlsx", sheet_name="Por_Dispositivo")
df_men   = pd.read_excel(BASE / "data/funil_ecommerce.xlsx", sheet_name="Mensal")
df_aband = pd.read_excel(BASE / "data/funil_ecommerce.xlsx", sheet_name="Motivos_Abandono")

BG="#08071a"; CARD_BG="#100f2e"; BORDER="#2a2560"
PINK="#f472b6"; CYAN="#38bdf8"; BLUE="#6366f1"
PURPLE="#a78bfa"; LAV="#818cf8"; TEXT="#ede9ff"; MUTED="#8b7ec8"
GREEN="#34d399"; YELLOW="#fbbf24"

CANAL_C={"Google Ads":BLUE,"Orgânico SEO":GREEN,"Instagram Ads":PINK,"E-mail":PURPLE,"Direto":CYAN}
DISP_C={"Desktop":BLUE,"Mobile":PINK,"Tablet":CYAN}

PLOT_LAYOUT=dict(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=TEXT,family="Inter, sans-serif",size=12),
    margin=dict(t=40,b=40,l=40,r=20),
    legend=dict(bgcolor="rgba(0,0,0,0)",font=dict(color=TEXT)),
    xaxis=dict(gridcolor=BORDER,zerolinecolor=BORDER,color=TEXT),
    yaxis=dict(gridcolor=BORDER,zerolinecolor=BORDER,color=TEXT))

def fmt_brl(v):
    if v>=1_000_000: return f"R$ {v/1_000_000:.1f}M"
    if v>=1_000: return f"R$ {v/1_000:.0f}K"
    return f"R$ {v:.0f}"

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
    suppress_callback_exceptions=True,title="Funil de Conversão")

PAGES=[("01","Funil Geral","/"),("02","Por Canal","/canal"),("03","Por Dispositivo","/dispositivo"),("04","Oportunidades","/oportunidades")]

sidebar=html.Div([
    html.Div([html.Div("🛒",style={"fontSize":"1.8rem"}),
        html.Div([html.P("Funil de Conversão",style={"margin":"0","fontWeight":"700","fontSize":"0.9rem","color":TEXT}),
                  html.P("E-commerce Analytics",style={"margin":"0","fontSize":"0.68rem","color":MUTED})])
    ],style={"display":"flex","gap":"12px","alignItems":"center","padding":"20px 16px 16px","borderBottom":f"1px solid {BORDER}"}),
    html.Nav([html.A([html.Span(n,style={"color":MUTED,"fontSize":"0.7rem","minWidth":"22px"}),html.Span(l,style={"fontSize":"0.82rem"})],
        href=h,style={"display":"flex","gap":"10px","alignItems":"center","padding":"10px 16px","color":TEXT,"textDecoration":"none","borderRadius":"8px"})
        for n,l,h in PAGES],style={"padding":"10px 8px","display":"flex","flexDirection":"column","gap":"2px"}),
    html.Div([html.P("45.000 visitas/mês",style={"color":MUTED,"fontSize":"0.68rem","margin":"0"})],
        style={"padding":"16px","borderTop":f"1px solid {BORDER}","marginTop":"auto"}),
],style={"width":"220px","minWidth":"220px","background":CARD_BG,"borderRight":f"1px solid {BORDER}",
    "height":"100vh","overflowY":"auto","position":"fixed","left":"0","top":"0","zIndex":"100","display":"flex","flexDirection":"column"})

app.layout=html.Div([dcc.Location(id="url"),sidebar,
    html.Div(id="page-content",style={"marginLeft":"220px","background":BG,"minHeight":"100vh","padding":"28px 32px","color":TEXT})],
    style={"fontFamily":"Inter, sans-serif","background":BG})

def page_funil():
    visitas=df_funil.iloc[0]["Usuarios"]
    compras=df_funil.iloc[-1]["Usuarios"]
    taxa=compras/visitas*100
    receita_mes=df_men["Receita"].mean()
    ticket=df_men["Ticket_Medio"].mean()

    # Funil visual
    fig_funil=go.Figure(go.Funnel(
        y=df_funil["Etapa"],x=df_funil["Usuarios"],
        textposition="inside",textinfo="value+percent initial",
        marker_color=[BLUE,LAV,PURPLE,PINK,PINK,PINK,PINK][:len(df_funil)],
        connector=dict(line=dict(color=BORDER,dash="dot",width=2))))
    fig_funil.update_layout(title="Funil de Conversão — Visão Geral",**PLOT_LAYOUT)

    # Drop-off por etapa
    drop=df_funil.dropna(subset=["Drop_Off_Pct"]).copy()
    fig_drop=go.Figure(go.Bar(
        x=drop["Etapa"],y=drop["Drop_Off_Pct"],
        marker_color=[PINK if v>40 else YELLOW if v>25 else CYAN for v in drop["Drop_Off_Pct"]],
        text=drop["Drop_Off_Pct"].astype(str)+"%",textposition="outside"))
    fig_drop.update_layout(title="Taxa de Drop-off por Etapa (%)",**PLOT_LAYOUT)

    # Evolução mensal
    fig_men=go.Figure([
        go.Scatter(x=df_men["Mes"],y=df_men["Taxa_Conversao"],mode="lines+markers",
            name="Taxa Conversão %",line=dict(color=CYAN,width=3),yaxis="y2"),
        go.Bar(x=df_men["Mes"],y=df_men["Receita"],name="Receita (R$)",marker_color=PURPLE,opacity=0.6),
    ])
    fig_men.update_layout(title="Receita e Taxa de Conversão Mensal",
        yaxis=dict(title="Receita (R$)",gridcolor=BORDER,color=TEXT),
        yaxis2=dict(title="Conversão %",overlaying="y",side="right",color=CYAN,gridcolor="rgba(0,0,0,0)"),
        **{k:v for k,v in PLOT_LAYOUT.items() if k not in ["yaxis"]})

    return html.Div([
        html.H2("Funil de Conversão",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Da visita à compra — onde o e-commerce está perdendo clientes",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(kpi("Visitas/mês",f"{visitas:,}","tráfego mensal",BLUE,"👀"),md=3),
            dbc.Col(kpi("Compras/mês",f"{compras:,}","pedidos concluídos",GREEN,"🛒"),md=3),
            dbc.Col(kpi("Taxa de Conversão",f"{taxa:.1f}%","do total de visitas",CYAN,"📊"),md=3),
            dbc.Col(kpi("Receita Média/mês",fmt_brl(receita_mes),"estimativa",PURPLE,"💰"),md=3),
        ],className="mb-4 g-2"),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_funil,config={"displayModeBar":False})),md=5),
            dbc.Col(card(dcc.Graph(figure=fig_drop,config={"displayModeBar":False})),md=7),
        ],className="mb-3 g-2"),
        dbc.Row([dbc.Col(card(dcc.Graph(figure=fig_men,config={"displayModeBar":False})),md=12)],className="g-2"),
    ])

def page_canal():
    final=df_canal[df_canal["Etapa"]=="Compra Finalizada"].sort_values("Taxa",ascending=False)
    fig_conv=go.Figure(go.Bar(x=final["Canal"],y=final["Taxa"],
        marker_color=[CANAL_C.get(c,MUTED) for c in final["Canal"]],
        text=final["Taxa"].astype(str)+"%",textposition="outside"))
    fig_conv.update_layout(title="Taxa de Conversão Final por Canal (%)",**PLOT_LAYOUT)

    canais_list=list(CANAL_C.keys())
    fig_comp=go.Figure()
    for canal in canais_list:
        sub=df_canal[df_canal["Canal"]==canal]
        fig_comp.add_trace(go.Scatter(x=sub["Etapa"],y=sub["Taxa"],mode="lines+markers",
            name=canal,line=dict(color=CANAL_C[canal],width=2),marker=dict(size=7)))
    fig_comp.update_layout(title="Comparação do Funil por Canal",**PLOT_LAYOUT)
    fig_comp.update_xaxes(tickangle=-20)

    return html.Div([
        html.H2("Análise por Canal",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Qual canal traz o tráfego com maior propensão de compra",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_conv,config={"displayModeBar":False})),md=5),
            dbc.Col(card(dcc.Graph(figure=fig_comp,config={"displayModeBar":False})),md=7),
        ],className="g-2"),
    ])

def page_dispositivo():
    final=df_disp[df_disp["Etapa"]=="Compra Finalizada"]
    fig_disp=go.Figure(go.Bar(x=final["Dispositivo"],y=final["Taxa"],
        marker_color=[DISP_C.get(d,MUTED) for d in final["Dispositivo"]],
        text=final["Taxa"].astype(str)+"%",textposition="outside"))
    fig_disp.update_layout(title="Taxa de Conversão Final por Dispositivo (%)",**PLOT_LAYOUT)

    fig_comp=go.Figure()
    for disp in ["Desktop","Mobile","Tablet"]:
        sub=df_disp[df_disp["Dispositivo"]==disp]
        fig_comp.add_trace(go.Scatter(x=sub["Etapa"],y=sub["Taxa"],mode="lines+markers",
            name=disp,line=dict(color=DISP_C[disp],width=3),marker=dict(size=8)))
    fig_comp.update_layout(title="Funil Comparativo por Dispositivo",**PLOT_LAYOUT)
    fig_comp.update_xaxes(tickangle=-20)

    mob_desk=df_disp[df_disp["Etapa"]=="Compra Finalizada"]
    mob=mob_desk[mob_desk["Dispositivo"]=="Mobile"]["Taxa"].values[0]
    desk=mob_desk[mob_desk["Dispositivo"]=="Desktop"]["Taxa"].values[0]

    return html.Div([
        html.H2("Análise por Dispositivo",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Mobile converte muito menos que Desktop — oportunidade de otimização",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([
            dbc.Col(kpi("Desktop",f"{desk}%","conversão final",GREEN,"🖥️"),md=4),
            dbc.Col(kpi("Mobile",f"{mob}%","conversão final",PINK,"📱"),md=4),
            dbc.Col(kpi("Gap Mobile vs Desktop",f"{desk-mob:.1f}pp","oportunidade",YELLOW,"⚠️"),md=4),
        ],className="mb-4 g-2"),
        dbc.Row([
            dbc.Col(card(dcc.Graph(figure=fig_disp,config={"displayModeBar":False})),md=5),
            dbc.Col(card(dcc.Graph(figure=fig_comp,config={"displayModeBar":False})),md=7),
        ],className="g-2"),
    ])

def page_oportunidades():
    # Maior drop-off
    drop=df_funil.dropna(subset=["Drop_Off_Pct"]).sort_values("Drop_Off_Pct",ascending=False)
    maior_drop=drop.iloc[0]

    fig_aband=go.Figure()
    for etapa in df_aband["Etapa"].unique():
        sub=df_aband[df_aband["Etapa"]==etapa]
        fig_aband.add_trace(go.Bar(name=etapa,x=sub["Motivo"],y=sub["Pct"],marker_color=BLUE))
    fig_aband.update_layout(barmode="group",title="Principais Motivos de Abandono por Etapa",**PLOT_LAYOUT)

    # Simulação: se melhorarmos o checkout
    visitas=df_funil.iloc[0]["Usuarios"]
    compras_atual=df_funil.iloc[-1]["Usuarios"]
    ticket=df_men["Ticket_Medio"].mean()
    receita_atual=compras_atual*ticket

    cenarios=[]
    for melhora in [5,10,15,20]:
        nova_taxa=(compras_atual/visitas)*(1+melhora/100)
        novas_compras=round(visitas*nova_taxa)
        nova_receita=novas_compras*ticket
        cenarios.append({"Melhora":f"+{melhora}% conversão","Compras":novas_compras,
            "Receita_Extra":round((nova_receita-receita_atual),2)})
    df_cen=pd.DataFrame(cenarios)

    fig_cen=go.Figure(go.Bar(x=df_cen["Melhora"],y=df_cen["Receita_Extra"],
        marker_color=[CYAN,BLUE,PURPLE,PINK],
        text=[fmt_brl(v) for v in df_cen["Receita_Extra"]],textposition="outside"))
    fig_cen.update_layout(title="Receita Extra por Melhoria na Conversão",**PLOT_LAYOUT)

    def rec_card(icon,titulo,problema,impacto,acao,cor):
        return dbc.Card([dbc.CardBody([
            html.Div([html.Span(icon,style={"fontSize":"1.5rem"}),
                html.H6(titulo,style={"color":TEXT,"fontWeight":"700","margin":"0","marginLeft":"10px"})],
                style={"display":"flex","alignItems":"center","marginBottom":"10px"}),
            html.Hr(style={"borderColor":BORDER,"margin":"8px 0"}),
            dbc.Row([
                dbc.Col([html.P("Problema",style={"color":MUTED,"fontSize":"0.7rem","margin":"0"}),html.P(problema,style={"color":TEXT,"fontSize":"0.82rem"})],md=4),
                dbc.Col([html.P("Impacto",style={"color":MUTED,"fontSize":"0.7rem","margin":"0"}),html.P(impacto,style={"color":cor,"fontSize":"0.82rem","fontWeight":"700"})],md=4),
                dbc.Col([html.P("Ação",style={"color":MUTED,"fontSize":"0.7rem","margin":"0"}),html.P(acao,style={"color":TEXT,"fontSize":"0.82rem"})],md=4),
            ]),
        ])],style={"background":CARD_BG,"border":f"1px solid {cor}44","borderLeft":f"4px solid {cor}","borderRadius":"10px","marginBottom":"12px"})

    return html.Div([
        html.H2("Oportunidades de Otimização",style={"color":TEXT,"fontWeight":"700","marginBottom":"6px"}),
        html.P("Onde melhorar o funil para aumentar a receita",style={"color":MUTED,"marginBottom":"24px"}),
        dbc.Row([dbc.Col(card(dcc.Graph(figure=fig_aband,config={"displayModeBar":False})),md=12)],className="mb-3 g-2"),
        dbc.Row([dbc.Col(card(dcc.Graph(figure=fig_cen,config={"displayModeBar":False})),md=12)],className="mb-4 g-2"),
        rec_card("🚨","Checkout → Cadastro: maior gargalo",
            "42% dos usuários abandonam no formulário de cadastro",
            f"Drop-off de {maior_drop['Drop_Off_Pct']:.0f}% — maior do funil",
            "Implementar login social (Google/Apple) e reduzir campos do formulário",PINK),
        rec_card("📱","Mobile com conversão 45% menor que Desktop",
            "Mobile representa 42% do tráfego mas converte muito menos",
            "Gap de 4.5pp vs Desktop — receita não capturada",
            "Otimizar checkout mobile, simplificar teclado e adicionar Apple/Google Pay",YELLOW),
        rec_card("🚀","E-mail com maior taxa de conversão",
            "Canal E-mail converte 13.8% vs 8.5% do Google Ads",
            "E-mail gera 62% mais compras por visita",
            "Aumentar budget de e-mail marketing e criar fluxos de carrinho abandonado",CYAN),
    ])

@app.callback(Output("page-content","children"),Input("url","pathname"))
def render(path):
    return {"/":page_funil,"/canal":page_canal,"/dispositivo":page_dispositivo,"/oportunidades":page_oportunidades}.get(path,page_funil)()

if __name__=="__main__":
    import webbrowser,threading
    threading.Timer(1.5,lambda:webbrowser.open("http://localhost:8055")).start()
    print("\n  Funil E-commerce: http://localhost:8055\n")
    app.run(debug=False,host="0.0.0.0",port=8055)
