# 💬 Classificador de Feedbacks com IA

![Python](https://img.shields.io/badge/Python-3.10+-6366f1?style=flat&logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-Plotly-a78bfa?style=flat&logo=plotly&logoColor=white)
![NLP](https://img.shields.io/badge/Domínio-NLP%20%7C%20Product%20Analytics-f472b6?style=flat)
![Status](https://img.shields.io/badge/Status-Concluído-38bdf8?style=flat)

> Dashboard que classifica feedbacks de usuários por tema, sentimento e prioridade — automatizando a triagem que todo time de produto faz manualmente.

---

## Contexto

Times de produto recebem centenas de feedbacks por mês e passam horas triando manualmente. Este projeto simula um sistema de classificação automática que categoriza cada feedback por **tema** (UX, Performance, Funcionalidade…), **sentimento** (Positivo, Negativo, Neutro) e **prioridade de ação**.

---

## Dashboard — 4 Páginas

| # | Página | O que mostra |
|---|--------|--------------|
| 1 | **Visão Geral** | Volume total, NPS médio, sentimentos, volume mensal e feedbacks por canal |
| 2 | **Por Tema** | Volume por tema, NPS médio por tema e sentimento empilhado por categoria |
| 3 | **Análise de Sentimento** | Heatmap tema × sentimento, distribuição por plano e NPS por plano |
| 4 | **Plano de Ação** | Feedbacks críticos de alta prioridade com ação recomendada |

---

## Screenshots

![Visão Geral](docs/p1.png)
![Por Tema](docs/p2.png)
![Sentimento](docs/p3.png)
![Plano de Ação](docs/p4.png)

---

## Principais Resultados

- **800 feedbacks** classificados em 12 meses de análise
- **6 temas** identificados: UX/Design, Performance, Funcionalidade, Atendimento, Preço/Planos, Onboarding
- NPS médio de **7.2/10** — com queda consistente nos planos básicos
- Tema mais crítico: **Performance** — maior volume de negativos e mais alta prioridade
- Canal **E-mail** com NPS 20% superior à média geral

---

## Ferramentas Utilizadas

| Categoria | Ferramenta | Uso |
|-----------|-----------|-----|
| Linguagem | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) | Desenvolvimento completo |
| Dashboard | ![Dash](https://img.shields.io/badge/Dash-008DE4?style=flat&logo=plotly&logoColor=white) | Interface interativa web |
| Visualização | ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) | Gráficos e heatmaps |
| Dados | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white) | Análise e agrupamentos |
| Numérico | ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white) | Cálculos estatísticos |
| Estilo | ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white) | Layout responsivo |
| Dados | ![Excel](https://img.shields.io/badge/Excel-217346?style=flat&logo=microsoft-excel&logoColor=white) | Dataset de feedbacks |
| Versionamento | ![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white) | Controle de versão |
| Repositório | ![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white) | Hospedagem do projeto |

---

## Como Executar

```bash
pip install -r requirements.txt
python gerar_dados.py
python app.py
```

Acesse: **http://localhost:8054**

---

*Projeto desenvolvido para portfólio — simula o ambiente real de um time de produto gerenciando feedbacks de usuários com classificação automática por IA.*
