# Pokemon Analytics Platform

Dashboard interativo de análise estratégica de combates Pokémon com ETL automatizado e persistência em banco de dados.

## 🚀 Stack Tecnológico

- **Python 3.11.9** com SQLAlchemy + psycopg2
- **Streamlit** para dashboard interativo
- **API REST** com autenticação JWT
- **Pandas** + NumPy para transformação de dados

## 📊 O Que Faz

1. **ETL Automatizado**: Extrai 799 Pokémon e 47.943 combates da API, limpa, transforma e persiste em PostgreSQL
2. **Dashboard**: Visualiza win rates, correlações de tipos, rankings, distribuições de stats
3. **Análises**: Identifica estratégias de combate, Pokemon top performers, padrões de sucesso

## 🏗️ Arquitetura

```
src/
├── services/etl/          # Pipeline ETL completa
│   ├── data_extraction/   # Fetch da API com retry (429, 401)
│   ├── data_cleaning/     # Normalização, type splitting
│   ├── data_transformation/ # Cálculo de métricas (win_rate, weighted_score)
│   └── data_loading/      # Inserção idempotente no BD
├── app/
│   ├── streamlit_app.py   # Dashboard principal
│   └── ui/                # Componentes reutilizáveis
│       ├── renderers/     # Charts, cards, tables, insights
│       ├── sections/      # Seções do dashboard
│       └── utils/         # Helpers, constants, validation
├── repositories/          # Data access layer
├── database/              # Models SQLAlchemy
└── analytics/             # Serviços de análise
```

## 🔧 Setup & Execução

### Instalação
```bash
python -m venv .venv
.venv\Scripts\activate  
pip install -r requirements.txt
```

### ETL (Carregar dados)
```bash
python run_etl.py
```

### Dashboard
```bash
streamlit run src/app/streamlit_app.py
```

## ✅ Status de Qualidade dos Dados (01/03/2026)

| Métrica | Valor | Status |
|---------|-------|--------|
| **Duplicatas Pokemon** | 0 | ✅ Zero |
| **Duplicatas Combates** | 0 | ✅ Zero |
| **Integridade Referencial** | 100% | ✅ Válidas |
| **Completude** | 99.7% | ✅ Excelente |
| **Anomalias Lógicas** | 0 | ✅ Zero |

**Conclusão**: Dados aprovados para produção. Zero problemas críticos.

### Achados Menores

- **2 Pokemon com geração nula** (0.25%): Dados faltantes na API, sem impacto nas análises
- **16 Pokemon sem combates** (2%): Normal - novos ou raros. Monitorar periodicamente

Autenticação JWT com refresh automático em caso de expiração. Retry automático em rate limit (429).

