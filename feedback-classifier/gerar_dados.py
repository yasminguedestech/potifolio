"""
Gera dataset de feedbacks de usuários para o classificador.
Execute: python gerar_dados.py
"""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).parent
np.random.seed(42)

feedbacks_por_tema = {
    "UX/Design": {
        "sentimento": ["positivo","negativo","neutro"],
        "peso": [0.3, 0.4, 0.3],
        "textos_pos": [
            "Interface muito intuitiva, adorei o novo layout",
            "Design clean e moderno, fácil de navegar",
            "A tela ficou bem organizada, muito melhor que antes",
            "Visual bonito e profissional",
        ],
        "textos_neg": [
            "O botão de salvar é difícil de encontrar",
            "Muitos cliques para chegar onde preciso",
            "A fonte está muito pequena, difícil de ler",
            "Confuso demais, não sei onde estão as funcionalidades",
            "Interface antiga e pouco intuitiva",
        ],
        "textos_neu": [
            "O design é ok, nada especial",
            "Interface funcional mas poderia melhorar",
        ],
    },
    "Performance": {
        "sentimento": ["positivo","negativo","neutro"],
        "peso": [0.25, 0.50, 0.25],
        "textos_pos": [
            "Muito rápido, carrega em segundos",
            "Sem travamentos, excelente desempenho",
        ],
        "textos_neg": [
            "App trava com frequência ao abrir relatórios",
            "Carregamento lento demais, perco tempo esperando",
            "Fica lento quando tenho muitos dados abertos",
            "Sistema caiu 3 vezes hoje, muito frustrante",
            "A busca demora mais de 10 segundos para responder",
        ],
        "textos_neu": [
            "Performance aceitável para o que preciso",
            "Às vezes demora um pouco mas funciona",
        ],
    },
    "Funcionalidade": {
        "sentimento": ["positivo","negativo","neutro"],
        "peso": [0.35, 0.35, 0.30],
        "textos_pos": [
            "O novo filtro avançado resolve exatamente o que eu precisava",
            "Exportar para Excel funcionou perfeitamente",
            "Integração com o Slack salvou horas do meu dia",
            "O relatório automático é excelente",
        ],
        "textos_neg": [
            "Não consigo importar arquivos CSV com mais de 10MB",
            "Falta integração com o Google Sheets",
            "Não há como editar em massa, preciso fazer um por um",
            "A função de busca não encontra itens antigos",
        ],
        "textos_neu": [
            "As funcionalidades atendem o básico",
            "Cumpre o prometido, sem grandes diferenciais",
        ],
    },
    "Atendimento": {
        "sentimento": ["positivo","negativo","neutro"],
        "peso": [0.45, 0.35, 0.20],
        "textos_pos": [
            "Suporte resolveu meu problema em menos de 1 hora",
            "Atendimento excelente, muito prestativo",
            "Chat ao vivo muito eficiente",
        ],
        "textos_neg": [
            "Esperei 3 dias por uma resposta do suporte",
            "O chatbot não entendeu minha dúvida e não me conectou a um humano",
            "Respostas genéricas que não resolvem o problema",
        ],
        "textos_neu": [
            "Atendimento dentro do esperado",
            "Demorou um pouco mas resolveu",
        ],
    },
    "Preço/Planos": {
        "sentimento": ["positivo","negativo","neutro"],
        "peso": [0.20, 0.55, 0.25],
        "textos_pos": [
            "Custo-benefício excelente para o que oferece",
            "Plano empresarial vale cada centavo",
        ],
        "textos_neg": [
            "Muito caro para o que entrega, concorrentes cobram menos",
            "Cobram por funcionalidades que deveriam ser básicas",
            "Reajuste de preço sem aviso prévio foi absurdo",
            "O plano básico é muito limitado para uso profissional",
        ],
        "textos_neu": [
            "Preço compatível com o mercado",
            "Poderia ter um plano intermediário",
        ],
    },
    "Onboarding": {
        "sentimento": ["positivo","negativo","neutro"],
        "peso": [0.40, 0.35, 0.25],
        "textos_pos": [
            "Tutorial inicial muito claro e objetivo",
            "Consegui usar o sistema sem precisar de ajuda",
        ],
        "textos_neg": [
            "Sem tutorial, tive que descobrir tudo sozinho",
            "Documentação desatualizada confundiu mais do que ajudou",
            "Primeiro acesso muito confuso",
        ],
        "textos_neu": [
            "Onboarding básico, cumpre o mínimo",
        ],
    },
}

N = 800
rows = []
temas = list(feedbacks_por_tema.keys())
pesos_tema = [0.22, 0.18, 0.25, 0.15, 0.12, 0.08]

datas = pd.date_range("2024-01-01", "2024-12-31", periods=N)
canais = np.random.choice(["App Store","Google Play","NPS Interno","Suporte","Site"], N, p=[0.25,0.20,0.30,0.15,0.10])
planos = np.random.choice(["Starter","Growth","Enterprise"], N, p=[0.45,0.35,0.20])

for i in range(N):
    tema = np.random.choice(temas, p=pesos_tema)
    info = feedbacks_por_tema[tema]
    sent = np.random.choice(info["sentimento"], p=info["peso"])
    key = f"textos_{sent[:3]}"
    texto = np.random.choice(info[key])
    nps = {"positivo": np.random.randint(8,11), "neutro": np.random.randint(6,9), "negativo": np.random.randint(1,7)}[sent]
    prioridade = "Alta" if sent == "negativo" and tema in ["Performance","Funcionalidade"] else \
                 "Média" if sent in ["negativo","neutro"] else "Baixa"
    rows.append({
        "ID": i+1,
        "Data": datas[i].strftime("%Y-%m-%d"),
        "Mes": datas[i].strftime("%b/%Y"),
        "Canal": canais[i],
        "Plano": planos[i],
        "Texto": texto,
        "Tema": tema,
        "Sentimento": sent.capitalize(),
        "NPS": nps,
        "Prioridade": prioridade,
        "Acao": "Corrigir bug / melhorar" if sent=="negativo" else "Replicar em outras áreas" if sent=="positivo" else "Monitorar",
    })

df = pd.DataFrame(rows)

# Resumo mensal
mensal = df.groupby("Mes").agg(
    Total=("ID","count"),
    Positivos=("Sentimento", lambda x: (x=="Positivo").sum()),
    Negativos=("Sentimento", lambda x: (x=="Negativo").sum()),
    NPS_Medio=("NPS","mean"),
).round(1).reset_index()

out = BASE / "data" / "feedbacks.xlsx"
with pd.ExcelWriter(out, engine="openpyxl") as w:
    df.to_excel(w, sheet_name="Feedbacks", index=False)
    mensal.to_excel(w, sheet_name="Mensal", index=False)

print(f"Dataset: {out}")
print(f"Total feedbacks: {N}")
print(f"Positivos: {(df['Sentimento']=='Positivo').sum()} | Negativos: {(df['Sentimento']=='Negativo').sum()}")
print(f"NPS médio: {df['NPS'].mean():.1f}")
