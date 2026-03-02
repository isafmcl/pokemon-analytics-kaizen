# Pokemon Analytics Platform

Plataforma de inteligência para análise estratégica de performance competitiva. Integra pipeline ETL resiliente, persistência em PostgreSQL e dashboard analítico para suporte à decisão.

## Stack Tecnológica

* **Linguagem:** Python 3.11.9
* **Pipeline:** Pandas, NumPy, Pydantic
* **Database:** PostgreSQL, SQLAlchemy (ORM)
* **Interface:** Streamlit
* **Segurança:** JWT Auth (Refresh Token) & Retry Logic (429/401)

## Core Engine

### 1. ETL & Observabilidade
* **Resiliência:** Fetch com retries e tratamento de rate limit.
* **Transformação:** Normalização de schemas e cálculo de métricas (Win Rate, Weighted Score).
* **Idempotência:** Carga otimizada para garantir integridade referencial e zero duplicidade.

### 2. Analytics
* Matrizes de correlação de tipos e eficácia.
* Distribuição estatística de atributos base.
* Rankings de performance baseados em amostragem histórica.

## 3.Instalação do Ambiente

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou .venv\Scripts\activate no Windows
pip install -r requirements.txt

## 4.Inicialização do Sistema

# 1. Executar o Pipeline de Dados
python run_etl.py

# 2. Iniciar o Dashboard
streamlit run src/app/streamlit_app.py

## 5.Análise Crítica
Diferenciais: Design modular que separa a lógica de ingestão da camada de visualização; resiliência nativa contra instabilidades de rede e APIs externas.

## 6.Roadmap: 
Containerização via Docker para padronização de ambiente e implementação de logs estruturados para monitoramento de saúde do pipeline em produção.
