# 🛒 Análise de Funil de Conversão — E-commerce

![Python](https://img.shields.io/badge/Python-3.10+-6366f1?style=flat&logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-Plotly-a78bfa?style=flat&logo=plotly&logoColor=white)
![E-commerce](https://img.shields.io/badge/Domínio-E--commerce%20Analytics-34d399?style=flat)
![Status](https://img.shields.io/badge/Status-Concluído-38bdf8?style=flat)

> Dashboard interativo que mapeia cada etapa do funil de conversão de um e-commerce — identificando gargalos, comparando canais e dispositivos, e simulando o impacto financeiro de melhorias.

---

## Contexto

A empresa percebia queda nas vendas mas não sabia onde os usuários abandonavam. A análise mapeou cada etapa do funil — da visita à compra finalizada — e identificou que **42% dos usuários abandonam no formulário de cadastro**, o maior gargalo de todo o processo.

---

## Dashboard — 4 Páginas

| # | Página | O que mostra |
|---|--------|--------------|
| 1 | **Funil Geral** | Funil visual completo, drop-off por etapa e receita + conversão mensal |
| 2 | **Por Canal** | Taxa de conversão final por canal e comparação do funil entre canais |
| 3 | **Por Dispositivo** | Conversão Desktop vs Mobile vs Tablet com gap de oportunidade |
| 4 | **Oportunidades** | Motivos de abandono, simulador de receita extra e recomendações priorizadas |

---

## Screenshots

![Funil Geral](docs/p1.png)
![Por Canal](docs/p2.png)
![Por Dispositivo](docs/p3.png)
![Oportunidades](docs/p4.png)

---

## Principais Resultados

- **45.000 visitas/mês** — taxa de conversão final de **2.8%**
- Maior drop-off: etapa de **cadastro** com **42% de abandono**
- **Mobile converte 45% menos** que Desktop — gap de 4.5 pontos percentuais
- Canal **E-mail** converte 62% mais por visita do que Google Ads
- Simulador mostra que **+10% na conversão** = R$ 38K de receita extra/mês

---

## Ferramentas Utilizadas

| Categoria | Ferramenta | Uso |
|-----------|-----------|-----|
| Linguagem | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) | Desenvolvimento completo |
| Dashboard | ![Dash](https://img.shields.io/badge/Dash-008DE4?style=flat&logo=plotly&logoColor=white) | Interface interativa web |
| Visualização | ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) | Funil, scatter e barras |
| Dados | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white) | Análise do funil por segmento |
| Numérico | ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white) | Cálculos de taxa e projeções |
| Estilo | ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white) | Layout responsivo |
| Dados | ![Excel](https://img.shields.io/badge/Excel-217346?style=flat&logo=microsoft-excel&logoColor=white) | Datasets do funil por canal/dispositivo |
| Versionamento | ![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white) | Controle de versão |
| Repositório | ![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white) | Hospedagem do projeto |

---

## Como Executar

```bash
pip install -r requirements.txt
python gerar_dados.py
python app.py
```

Acesse: **http://localhost:8055**

---

*Projeto desenvolvido para portfólio — simula o ambiente real de um time de growth/e-commerce analisando e otimizando o funil de conversão.*
