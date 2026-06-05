# Guia de Configuração — Dashboard de Churn Fintech no Power BI

## 1. Preparação dos dados

### 1.1 Baixar o dataset
1. Acesse: https://www.kaggle.com/datasets/radheshyamkollipara/bank-customer-churn
2. Baixe `Churn_Modelling.csv`
3. Coloque em `data/raw/Churn_Modelling.csv`

### 1.2 Executar o script de preparação
```bash
cd data
pip install pandas numpy openpyxl scikit-learn xgboost
python prepare_data.py
```
→ Gera `data/churn_dataset_final.xlsx`

### 1.3 Executar o modelo preditivo
```bash
cd ml
python modelo_churn.py
```
→ Gera `ml/outputs/predicoes_churn.xlsx`

---

## 2. Importar para o Power BI

1. Abrir Power BI Desktop
2. **Obter Dados > Excel**
3. Selecionar `data/churn_dataset_final.xlsx`
   - Importar aba: **Clientes** (tabela principal)
   - Importar aba: **Resumo_Segmentos**
   - Importar aba: **Curva_Retencao**
4. Selecionar `ml/outputs/predicoes_churn.xlsx`
   - Importar aba: **Probabilidades** → renomear para `Predicoes`
   - Importar aba: **Importancia_Vars**
   - Importar aba: **Metricas_Modelos**

---

## 3. Modelo de dados (relacionamentos)

```
Clientes[ID_Cliente] → Predicoes[ID_Cliente]   (1:1)
```

---

## 4. Criar medidas DAX

1. No painel Campos, clique com botão direito em **Clientes > Nova medida**
2. Cole cada bloco dos arquivos `.dax` de `dax/`
3. Organize em pastas de exibição (ex: "Pág 1 - Executiva")

### Medidas essenciais a criar primeiro (todas as páginas dependem delas):
- `Total de Clientes`
- `Clientes Cancelados`
- `Taxa de Churn %`
- `Receita Total`
- `Receita Perdida por Churn`

---

## 5. Parâmetros do Simulador (Página 7)

**Modelagem > Novo Parâmetro > Campo numérico**

| Parâmetro | Mín | Máx | Incremento | Padrão |
|-----------|-----|-----|------------|--------|
| Redução de Churn % | 0.01 | 0.30 | 0.01 | 0.05 |
| Custo de Retenção por Cliente (R$) | 50 | 500 | 50 | 150 |

---

## 6. Tema e cores sugeridas

| Elemento | Cor |
|----------|-----|
| Fundo principal | `#0F1117` (dark) ou `#FFFFFF` (light) |
| Destaque primário | `#E63946` (vermelho churn) |
| Destaque positivo | `#2DC653` (verde retenção) |
| Neutro | `#457B9D` (azul dados) |
| Alto Risco | `#E63946` |
| Médio Risco | `#F4A261` |
| Baixo Risco | `#2DC653` |

Para aplicar: **Exibir > Temas > Personalizar tema atual**

---

## 7. Layout página por página

### Página 1 — Visão Executiva
- **Fila 1:** 5 cartões KPI (Total Clientes | Ativos | Cancelados | Taxa Churn % | Receita em Risco)
- **Fila 2:** Gráfico de colunas agrupadas (Ativos vs Cancelados por País) + Gráfico de rosca (Status Churn)
- **Fila 3:** Gráfico de área (Churn por Cohort_Tempo) + Cartão grande (Receita Perdida por Churn)

### Página 2 — Perfil do Cliente
- **Filtros:** Segmentadores de Gênero, País, Faixa Etária
- **Gráficos:** Barras horizontais (Churn por Faixa Etária) + Matriz heatmap (Gênero x Faixa Etária) + Barras (Churn por País) + Barras (Churn por Faixa Salarial)

### Página 3 — Produtos
- **KPIs:** Taxa Churn Membros Inativos vs Ativos
- **Gráficos:** Colunas (Clientes por Qtd Produtos + linha Taxa Churn sobreposta) + Scatter (Saldo vs Salário, cor=Status_Churn)

### Página 4 — Receita e Segmentação
- **Treemap:** Receita por Segmento_Valor
- **Barras:** Receita Perdida por Segmento
- **Linha Pareto:** Receita acumulada
- **Cartões:** Alto Valor Cancelados + % Alto Valor Perdido

### Página 5 — Score de Risco
- **Rosca:** Distribuição por Nivel_Risco
- **Barras:** Receita por Nivel_Risco
- **Tabela:** Top 50 clientes (Score_Risco DESC, filtro Alto Risco)
- **Medidor:** % Receita em Alto Risco

### Página 6 — Jornada do Cliente
- **Linha:** Taxa Churn por Cohort_Tempo
- **Área:** Taxa Retenção por Cohort
- **Matriz heatmap:** Cohort_Tempo x Qtd_Produtos
- **Cartão:** Tempo Médio até Cancelamento

### Página 7 — Simulador
- **Slicers:** Parâmetros (Redução %, Custo/Cliente)
- **Cartões KPI:** Clientes Salvos | Receita Recuperada | Custo Campanha | ROI
- **Tabela comparativa:** Cenários 5% / 10% / 15%
- **Gráfico de barras:** Receita Recuperada por cenário

### Página 8 — Modelo Preditivo
- **Cartões:** Accuracy | Precision | Recall | F1-Score
- **Barras horizontais:** Importância das Variáveis (Importancia_Vars)
- **Gráfico de dispersão / distribuição:** Prob_Churn por Nivel_Risco_ML
- **Tabela:** Matriz de confusão (da aba Matriz_Confusao)

### Página 9 — Recomendações
- Use visual de **Smart Narrative** ou caixas de texto formatadas
- 5 cards de recomendação, cada um com:
  - Título do problema
  - Medida de impacto (receita em risco)
  - Ação recomendada
  - Ícone de prioridade (🔴 Alta / 🟡 Média / 🟢 Baixa)

---

## 8. Publicar no Power BI Service

1. **Arquivo > Publicar > Power BI**
2. Selecionar workspace
3. Configurar **atualização agendada** se necessário (não aplicável para dados estáticos do Kaggle)
4. Copiar link para adicionar ao portfólio
