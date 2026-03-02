Pokemon Analytics Platform
Plataforma de inteligência de dados voltada à análise estratégica de performance competitiva. O sistema consolida um pipeline de ETL (Extract, Transform, Load) robusto, persistência em banco de dados relacional e uma camada de visualização analítica para suporte à decisão em tempo real.

Stack Tecnológica
Linguagem: Python 3.11.9

Data Pipeline: Pandas, NumPy

Persistência: PostgreSQL, SQLAlchemy (ORM), Psycopg2

Interface: Streamlit

Segurança: Autenticação via JWT (JSON Web Tokens) com lógica de Refresh Token e retry automático

Core Engine
1. Pipeline de ETL e Observabilidade
O sistema implementa um fluxo de dados idempotente que garante a consistência entre a API de origem e o Data Warehouse:

Extração: Mecanismo de fetch com resiliência a falhas (implementação de retries para erros 429 e 401).

Transformação: Normalização de esquemas complexos, tratamento de tipos aninhados e cálculo de métricas derivadas (Win Rate, Weighted Score).

Carga: Operações de escrita otimizadas para garantir a integridade referencial e evitar duplicidade de registros.

2. Analytics & Business Intelligence
O dashboard processa volumes significativos de dados de combate para extrair:

Matriz de correlação de tipos e eficácia elementar.

Distribuição estatística de atributos base (HP, Attack, Defense, etc.).

Rankings de performance baseados em amostragem histórica de vitórias e frequência de uso.

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

Análise Crítica e Roadmap
Pontos Fortes
Modularização: A separação clara entre a camada de extração e a de visualização facilita a escalabilidade e a manutenção do código.

Resiliência de Rede: O tratamento nativo de rate limiting garante a continuidade do ETL mesmo sob restrições severas da API.

Carga Idempotente: O design assegura que múltiplas execuções do script de carga não gerem redundância no banco de dados.

