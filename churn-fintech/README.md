# 💳 Análise e Previsão de Churn em Fintech: Estratégias de Retenção Baseadas em Dados

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat&logo=python)
![Dash](https://img.shields.io/badge/Dash-Plotly-6366f1?style=flat&logo=plotly)
![Machine Learning](https://img.shields.io/badge/ML-Random%20Forest%20%7C%20XGBoost-a78bfa?style=flat)
![Status](https://img.shields.io/badge/Status-Concluído-38bdf8?style=flat)

> Dashboard executivo interativo com 9 páginas analíticas, Machine Learning integrado e simulação de cenários financeiros para redução de churn em uma fintech digital.

---

## 📌 Contexto do Negócio

Uma fintech digital identificou um aumento no cancelamento de clientes (churn), impactando diretamente sua receita e crescimento. Este projeto analisa os fatores que influenciam a saída dos clientes, classifica perfis de risco e propõe ações estratégicas baseadas em dados para aumentar a retenção.

**Dataset:** Bank Customer Churn — 10.000 clientes com variáveis demográficas, comportamentais e financeiras.

---

## 🎯 Objetivos

- Identificar os principais fatores relacionados ao churn
- Descobrir perfis de clientes com maior risco de cancelamento
- Estimar o impacto financeiro da perda de clientes
- Criar indicadores preditivos para antecipar cancelamentos
- Apoiar decisões estratégicas de retenção e aumento de receita

---

## 📊 Páginas do Dashboard

| # | Página | Descrição |
|---|--------|-----------|
| 1 | **Visão Executiva** | KPIs gerais, receita perdida, evolução do churn por cohort |
| 2 | **Perfil do Cliente** | Análise demográfica — faixa etária, gênero, país, salário |
| 3 | **Produtos Financeiros** | Como o uso de produtos impacta a retenção |
| 4 | **Receita & Segmentos** | Treemap, Pareto 80/20, segmentação Alto/Médio/Baixo Valor |
| 5 | **Score de Risco** | Classificação 🔴🟡🟢, ranking dos 20 clientes mais críticos |
| 6 | **Jornada do Cliente** | Curva de retenção, cohort analysis, momento ideal de intervenção |
| 7 | **Simulador de Cenários** | ROI de estratégias de retenção com parâmetros interativos |
| 8 | **Modelo Preditivo** | RF, XGBoost, Regressão Logística — importância de variáveis e matriz de confusão |
| 9 | **Recomendações** | 5 ações estratégicas com impacto financeiro quantificado |

---

## 🖥️ Screenshots

### Visão Executiva
![Visão Executiva](docs/p1_executiva.png)

### Perfil do Cliente
![Perfil](docs/p2_perfil.png)

### Score de Risco
![Score de Risco](docs/p5_risco.png)

### Simulador de Cenários
![Simulador](docs/p7_simulador.png)

### Modelo Preditivo
![Modelo](docs/p8_modelo.png)

### Recomendações Estratégicas
![Recomendações](docs/p9_recomendacoes.png)

---

## 🤖 Modelo de Machine Learning

| Modelo | Accuracy | Precision | Recall | F1-Score | ROC-AUC |
|--------|----------|-----------|--------|----------|---------|
| Random Forest | 65.9% | 57.9% | 67.0% | 62.1% | 71.6% |
| XGBoost | 57.1% | 49.1% | 81.9% | 61.4% | 69.1% |
| Regressão Logística | 64.7% | 56.7% | 65.0% | 60.6% | 69.9% |

**Variáveis mais importantes:** Qtd. Produtos · Score de Risco · País · Idade · Membro Ativo

---

## 💡 Principais Insights

- **41.8%** de taxa de churn — R$ 8.6M em receita perdida
- Clientes com **1 produto** têm churn ~2× maior que clientes com 2+ produtos
- **Membros inativos** são o maior fator de risco isolado (57% de churn)
- Faixa etária **46-55 anos** concentra a maior proporção de cancelamentos
- Uma redução de **10% no churn** preservaria ~R$ 860K e geraria ROI de 1.271%
- **30.5%** dos clientes estão classificados como Alto Risco, concentrando R$ 4.4M em receita

---

## 🚀 Como Executar

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/churn-fintech.git
cd churn-fintech

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Gere os dados e treine o modelo
python gerar_tudo.py

# 4. Suba o dashboard
python app.py
```

Acesse: **http://localhost:8050**

---

## 🗂️ Estrutura do Projeto

```
churn-fintech/
├── app.py                    # Dashboard principal (Dash + Plotly)
├── gerar_tudo.py             # Geração de dados + treinamento do modelo
├── data/
│   └── churn_dataset_final.xlsx
├── ml/
│   └── outputs/
│       └── predicoes_churn.xlsx
├── docs/
│   └── *.png                 # Screenshots das páginas
└── dax/                      # Medidas DAX para versão Power BI
```

---

## 🛠️ Stack

- **Python** — pandas, numpy, scikit-learn, XGBoost
- **Visualização** — Plotly, Dash, Dash Bootstrap Components
- **Machine Learning** — Random Forest, XGBoost, Regressão Logística
- **Dataset** — [Bank Customer Churn — Kaggle](https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn)

---

## 📎 Sobre o Projeto

Projeto desenvolvido para portfólio de análise de dados, simulando um cenário corporativo real de uma fintech digital. Abrange desde a análise exploratória e segmentação financeira até Machine Learning e recomendações estratégicas orientadas a negócio.
