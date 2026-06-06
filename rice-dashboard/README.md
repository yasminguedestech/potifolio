# 🎯 Dashboard de Priorização RICE

![Python](https://img.shields.io/badge/Python-3.10+-6366f1?style=flat&logo=python&logoColor=white)
![Dash](https://img.shields.io/badge/Dash-Plotly-a78bfa?style=flat&logo=plotly&logoColor=white)
![Produto](https://img.shields.io/badge/Domínio-Product%20Analytics-38bdf8?style=flat)
![Status](https://img.shields.io/badge/Status-Concluído-38bdf8?style=flat)

> Dashboard interativo que aplica o framework RICE para ranquear features automaticamente — unindo visão de produto com tomada de decisão baseada em dados.

---

## Contexto

Times de produto frequentemente enfrentam o dilema de **o que construir primeiro**. O framework RICE (Reach, Impact, Confidence, Effort) resolve isso com um score numérico objetivo. Este dashboard transforma um backlog de 20 features em um ranking visual e acionável.

---

## Fórmula RICE

```
RICE Score = (Reach × Impact × Confidence) ÷ Effort
```

| Fator | Descrição |
|-------|-----------|
| **Reach** | Quantos usuários serão impactados por mês |
| **Impact** | Grau de impacto na vida do usuário (0.25 a 3) |
| **Confidence** | Nível de certeza sobre as estimativas (%) |
| **Effort** | Semanas-pessoa necessárias para entregar |

---

## Dashboard — 4 Páginas

| # | Página | O que mostra |
|---|--------|--------------|
| 1 | **Ranking RICE** | Top 15 features, status, scatter esforço vs score e tabela completa |
| 2 | **Análise de Fatores** | Reach por feature, RICE médio por categoria e heatmap R·I·C |
| 3 | **Roadmap** | Estimativa de semanas por feature e evolução do score por sprint |
| 4 | **Simulador** | Ajuste R·I·C·E em tempo real e compare com o backlog atual |

---

## Screenshots

![Ranking RICE](docs/p1.png)
![Análise de Fatores](docs/p2.png)
![Roadmap](docs/p3.png)
![Simulador](docs/p4.png)

---

## Principais Resultados

- **20 features** ranqueadas com score RICE automatizado
- Feature #1 com score **9.600** — impacto máximo, esforço mínimo
- **4 sprints** mapeados no roadmap com estimativa de entrega
- Simulador permite testar qualquer combinação de parâmetros em tempo real

---

## Ferramentas Utilizadas

| Categoria | Ferramenta | Uso |
|-----------|-----------|-----|
| Linguagem | ![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white) | Desenvolvimento completo |
| Dashboard | ![Dash](https://img.shields.io/badge/Dash-008DE4?style=flat&logo=plotly&logoColor=white) | Interface interativa web |
| Visualização | ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white) | Gráficos e charts |
| Dados | ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas&logoColor=white) | Manipulação do backlog |
| Numérico | ![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white) | Cálculo do score RICE |
| Estilo | ![Bootstrap](https://img.shields.io/badge/Bootstrap-7952B3?style=flat&logo=bootstrap&logoColor=white) | Layout responsivo |
| Dados | ![Excel](https://img.shields.io/badge/Excel-217346?style=flat&logo=microsoft-excel&logoColor=white) | Dataset do backlog |
| Versionamento | ![Git](https://img.shields.io/badge/Git-F05032?style=flat&logo=git&logoColor=white) | Controle de versão |
| Repositório | ![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white) | Hospedagem do projeto |

---

## Como Executar

```bash
pip install -r requirements.txt
python gerar_dados.py
python app.py
```

Acesse: **http://localhost:8053**

---

*Projeto desenvolvido para portfólio — simula o ambiente real de um time de produto priorizando um backlog com o framework RICE.*
