"""Regenera cv_yasmin_guedes.pdf com os 3 projetos atualizados."""
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
import os

W, H = A4  # 595.25 x 842

ML = 45    # margin left
MR = 45    # margin right
TW = W - ML - MR  # text width ~505

# ── Tentar registrar Times New Roman do sistema ──────────────
FONT_DIR = r"C:\Windows\Fonts"
try:
    pdfmetrics.registerFont(TTFont("TNR",      os.path.join(FONT_DIR, "times.ttf")))
    pdfmetrics.registerFont(TTFont("TNR-Bold", os.path.join(FONT_DIR, "timesbd.ttf")))
    pdfmetrics.registerFont(TTFont("TNR-It",   os.path.join(FONT_DIR, "timesi.ttf")))
    NORMAL = "TNR"
    BOLD   = "TNR-Bold"
    ITALIC = "TNR-It"
except Exception:
    NORMAL = "Times-Roman"
    BOLD   = "Times-Bold"
    ITALIC = "Times-Italic"


def draw_section_header(c, y, title):
    c.setFont(BOLD, 12)
    c.setFillColorRGB(0, 0, 0)
    c.drawString(ML, y, title)
    y -= 4
    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(0.8)
    c.line(ML, y, W - MR, y)
    return y - 4


def wrap_text(c, text, x, y, font, size, max_width, line_height):
    c.setFont(font, size)
    lines = simpleSplit(text, font, size, max_width)
    for line in lines:
        c.drawString(x, y, line)
        y -= line_height
    return y


def draw_bullet(c, text, x, y, indent=8, font=NORMAL, size=10, lh=13, max_w=None):
    if max_w is None:
        max_w = TW - (x - ML) - indent
    c.setFont(font, size)
    c.drawString(x, y, "•")
    lines = simpleSplit(text, font, size, max_w - indent)
    for i, line in enumerate(lines):
        c.drawString(x + indent + 2, y, line)
        y -= lh
    return y


def new_page(c):
    c.showPage()
    return H - 45


output = r"C:\Users\Yasmin Guedes\OneDrive\Documentos\project\portifolio\assets\cv_yasmin_guedes.pdf"
c = canvas.Canvas(output, pagesize=A4)

y = H - 38

# ── CABEÇALHO ────────────────────────────────────────────────
c.setFont(BOLD, 16)
c.drawCentredString(W / 2, y, "Yasmin Guedes")
y -= 18

c.setFont(NORMAL, 11)
c.drawCentredString(W / 2, y, "Analista de Dados Júnior | SQL · Python · Power BI")
y -= 13

c.setFont(NORMAL, 9)
c.drawCentredString(W / 2, y,
    "São Paulo/SP | (11) 95288-6949 | yasminguedstech@gmail.com | linkedin.com/in/yasmin-guedes-0101")
y -= 11
c.drawCentredString(W / 2, y, "github.com/yasminguedestech")
y -= 18

# ── RESUMO ───────────────────────────────────────────────────
y = draw_section_header(c, y, "Resumo")
y -= 4
resumo = (
    "Profissional da área de Dados e Produto, com base sólida em suporte administrativo, gestão de processos e "
    "operações. Possui experiência prática com controle, organização e análise de dados, monitoramento de indicadores "
    "e padronização de fluxos, utilizando metodologias ágeis (Scrum e Kanban). Desenvolve projetos com Python, SQL e "
    "Power BI para identificar oportunidades, apoiar decisões estratégicas e promover a melhoria contínua de processos."
)
y = wrap_text(c, resumo, ML, y, NORMAL, 10, TW, 13)
y -= 10

# ── HABILIDADES ──────────────────────────────────────────────
y = draw_section_header(c, y, "Habilidades")
y -= 5

skills = [
    ("Dados & Analytics:", "Python, SQL, Power BI, Pandas, Matplotlib, Business Intelligence, Análise Exploratória de Dados"),
    ("Produto & Processos:", "Monitoramento de Indicadores, Gestão por Processos, Scrum, Kanban, Lean, Kaizen"),
    ("Ferramentas:", "Excel, Google Workspace, Jira, Trello, ERP TOTVS, Pacote Office"),
]
for label, value in skills:
    c.setFont(BOLD, 10)
    c.drawString(ML, y, label)
    lbl_w = c.stringWidth(label, BOLD, 10)
    c.setFont(NORMAL, 10)
    lines = simpleSplit(" " + value, NORMAL, 10, TW - lbl_w)
    c.drawString(ML + lbl_w, y, lines[0])
    y -= 13
    for line in lines[1:]:
        c.drawString(ML + lbl_w + 4, y, line)
        y -= 13
y -= 5

# ── EXPERIÊNCIA ──────────────────────────────────────────────
y = draw_section_header(c, y, "Experiência Profissional")
y -= 5

# Secretaria
c.setFont(BOLD, 10)
c.drawString(ML, y, "Secretaria Municipal da Saúde de São Paulo")
c.setFont(NORMAL, 9)
c.drawRightString(W - MR, y, "São Paulo, SP")
y -= 13
c.setFont(BOLD, 10)
c.drawString(ML, y, "Estagiária de Qualidade Jr")
c.setFont(NORMAL, 9)
c.drawRightString(W - MR, y, "mar. 2025 – presente")
y -= 12
exp1 = [
    "Monitoramento e análise de indicadores operacionais.",
    "Controle e organização de dados para suporte à tomada de decisão.",
    "Estruturação, revisão e padronização de Procedimentos Operacionais Padrão (POPs).",
    "Utilização de Jira, Trello e Google Workspace para gestão de atividades e processos.",
    "Apoio à melhoria contínua por meio de práticas Lean e Kaizen.",
]
for bullet in exp1:
    y = draw_bullet(c, bullet, ML + 2, y, size=10, lh=13)
y -= 8

# Cofema
c.setFont(BOLD, 10)
c.drawString(ML, y, "Cofema Atacadista")
y -= 13
c.setFont(BOLD, 10)
c.drawString(ML, y, "Assistente Administrativo Jr")
c.setFont(NORMAL, 9)
c.drawRightString(W - MR, y, "out. 2020 – fev. 2022")
y -= 12
exp2 = [
    "Registro e atualização de informações no ERP TOTVS.",
    "Controle e organização de dados administrativos e comerciais.",
    "Elaboração de orçamentos e acompanhamento de solicitações comerciais.",
    "Atendimento ao cliente e suporte às operações internas.",
    "Apoio à comunicação entre áreas e otimização de fluxos de trabalho.",
]
for bullet in exp2:
    y = draw_bullet(c, bullet, ML + 2, y, size=10, lh=13)
y -= 8

# ── PROJETOS ─────────────────────────────────────────────────
y = draw_section_header(c, y, "Projetos Relevantes")
y -= 5

projetos = [
    {
        "titulo": "Retenção de Motoristas — Contexto 99",
        "tech": "Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter Notebook",
        "desc": "Análise de dados focada em identificar os principais fatores de churn de motoristas em plataformas de ride hailing, gerando insumos para ações de retenção.",
        "bullets": [
            "Dataset com 1.200 registros e 9 variáveis: cidade, engajamento, avaliação, ganho e cancelamentos.",
            "Ganho semanal abaixo de R$ 500 identificado como principal driver de saída da plataforma.",
            "Primeiros 6 meses apontados como período crítico; bônus como alavanca eficaz de retenção.",
        ],
    },
    {
        "titulo": "Customer Health Score — Dashboard SaaS",
        "tech": "Python, Dash, Plotly, Pandas, NumPy, Bootstrap",
        "desc": "Dashboard interativo para identificação proativa de clientes SaaS em risco de churn, consolidando métricas de engajamento, satisfação, suporte e financeiro.",
        "bullets": [
            "500 clientes analisados; 14,6% classificados em risco, representando R$ 79K de MRR sob ameaça.",
            "Modelo ponderado: engajamento (40%), satisfação (30%), suporte (20%) e financeiro (10%).",
            "Top 20 clientes críticos exibidos com recomendações de ação para equipes de Customer Success.",
        ],
    },
    {
        "titulo": "Knowledge Analytics — Mapeamento de Dúvidas e IA",
        "tech": "Python, Dash, Plotly, Pandas, NumPy, Bootstrap",
        "desc": "Dashboard operacional que identifica dúvidas internas recorrentes em empresas, estimando impacto financeiro e oportunidades de automação com IA.",
        "bullets": [
            "Análise de 3.500 solicitações/ano revelando 7.106 horas consumidas em respostas duplicadas.",
            "\"Acessos e Senhas\" identificado como categoria mais frequente (22%), com 95% de potencial de automação.",
            "Economia estimada em R$ 309K/ano; ROI de R$ 181K em 6 meses com investimento de R$ 15K.",
        ],
    },
]

for proj in projetos:
    # Verificar espaço — se menos de 90pt, nova página
    if y < 100:
        y = new_page(c)

    c.setFont(BOLD, 10)
    c.drawString(ML, y, proj["titulo"])
    y -= 13
    c.setFont(ITALIC, 9)
    c.drawString(ML, y, "Tecnologias: " + proj["tech"])
    y -= 12
    y = wrap_text(c, proj["desc"], ML, y, NORMAL, 10, TW, 13)
    for bullet in proj["bullets"]:
        y = draw_bullet(c, bullet, ML + 2, y, size=10, lh=13)
    y -= 8

# ── PAGE 2 ───────────────────────────────────────────────────
y = new_page(c)

# Formação
y = draw_section_header(c, y, "Formação Acadêmica")
y -= 5
c.setFont(BOLD, 10)
c.drawString(ML, y, "Universidade Cidade de São Paulo (UNICID)")
c.setFont(NORMAL, 9)
c.drawRightString(W - MR, y, "mar. 2023 – dez. 2026")
y -= 13
c.setFont(NORMAL, 10)
c.drawString(ML, y, "Bacharelado em Biomedicina — cursando 8º semestre")
y -= 18

# Certificações
y = draw_section_header(c, y, "Certificações")
y -= 5
certs = [
    "Power BI Completo – Do Básico ao Avançado · Udemy · João Paulo de Lira · 10h · Mai/2026",
    "Ferramentas para um Product Owner · Udemy · Leonardo Adonis, SquadHub Academy · 8,5h · Mai/2026",
    "Customer Success na Prática · Udemy · 2h · Mai/2026",
    "Python 101 for Data Science · IBM (International Business Machines) · 10h · Mai/2026",
    "Nano Course Big Data & Analytics · FIAP · 60h · Mai/2026",
    "Nano Course DevOps & Agile Culture · FIAP · 60h · Jun/2026",
    "Business Intelligence (BI) · FIAP · 40h · Mai/2026",
    "Criar Relatórios Eficazes no Power BI · Microsoft · 40h · Mai/2026",
    "Fundamentos da Gestão por Processos · FGV · 14h · Mai/2026",
    "Kanban e Ferramentas Ágeis de Gestão de Projetos · FGV · 5h · Mai/2026",
    "Power BI com IA · Rocketseat · 6h · Jun/2026",
    "Understanding Data Engineering · DataCamp · 2h · Jun/2026",
]
for cert in certs:
    y = draw_bullet(c, cert, ML + 2, y, size=10, lh=13)
y -= 10

# Idiomas
y = draw_section_header(c, y, "Idiomas")
y -= 7
c.setFont(NORMAL, 10)
c.drawString(ML, y, "Português – Nativo          Inglês – Intermediário")

c.save()
print("CV gerado em:", output)
