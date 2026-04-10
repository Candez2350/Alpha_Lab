# Plano de Refatoração: Arquitetura Database-First com Supabase

## Background & Motivação
A arquitetura atual busca dados em tempo real no Yahoo Finance e Fundamentus a cada requisição do usuário. Essa abordagem resulta em gargalos de performance (timeouts na Vercel), bloqueios de IP (Rate Limits e Invalid Crumbs do Yahoo Finance) e exaustão dos recursos do servidor Render. 
A transição para um modelo **Database-First** armazenará as cotações históricas e fundamentos no **Supabase (PostgreSQL)**, permitindo que os motores quantitativos da plataforma consumam dados estruturados em milissegundos e não dependam da internet externa durante a navegação do usuário.

## Escopo & Impacto
- **Camada de Extração (ETL):** Criação de uma rota ou script seguro para atualizar a base de dados (sincronização incremental e histórica).
- **Camada de Conexão:** Implementação de conexão ao Supabase via `SQLAlchemy`, tirando vantagem da velocidade nativa do Pandas com `pd.read_sql()`.
- **Motores Quantitativos:** Alteração total das funções de captura em:
  - `engine_ls.py` (Arbitragem)
  - `engine_opt.py` (Volatilidade e Breakouts)
  - `engine_selection.py` (Stock Picking / Alpha)
  - `engine_monthly_bdr.py` (Alocação Tática)
  - `yf_setup.py` (Aposentado para requisições em tempo real e transformado em pipeline de atualização diária).

## Plano de Implementação

### Fase 1: Setup do Supabase e Modelagem do Banco (`backend/core/db.py`)
1. Instalar dependências no `requirements.txt`: `SQLAlchemy` e `psycopg2-binary`.
2. Configurar a engine de conexão (`create_engine`) consumindo a variável de ambiente `DATABASE_URL`.
3. Criar tabelas no banco de dados para suportar:
   - `daily_prices`: `ticker` (str), `date` (date), `close` (float), `high` (float), `low` (float), `open` (float), `volume` (float).
   - `fundamentals`: `ticker` (str), `roic` (float), `evebit` (float), `liq2m` (float), etc.

### Fase 2: Pipeline de Sincronização (ETL)
1. Criar um novo endpoint seguro em `main.py`: `POST /api/system/sync`.
2. Essa rota será protegida por uma `SYNC_SECRET_KEY` configurada no ambiente.
3. A lógica do pipeline irá:
   - Baixar o histórico do `yfinance` para o IBRX-100 e BDRs dinamicamente (1 ou 2 anos iniciais, depois incremental).
   - Inserir/Atualizar os dados (`upsert`) na tabela `daily_prices` do Supabase usando operações SQL otimizadas pelo Pandas.
   - Baixar os dados do Fundamentus e atualizar a tabela `fundamentals`.
4. Essa rota poderá ser chamada via Render Cron Jobs ou GitHub Actions 1 vez ao dia (ex: 18h30).

### Fase 3: Refatoração dos Motores
1. **Long & Short (`engine_ls.py`):** Modificar `get_market_data()` para realizar `SELECT date, ticker, close FROM daily_prices WHERE ticker IN (...) AND date >= ...` com pivotamento direto para DataFrames.
2. **Opções (`engine_opt.py`):** Alterar os scanners para rodar em cima do `SELECT` de preços e máximas/mínimas do banco de dados, sem abrir sessões HTTP.
3. **Stock Picking & BDRs (`engine_selection.py`, `engine_monthly_bdr.py`):** Substituir chamadas ao Fundamentus por consultas na tabela `fundamentals` e cálculos de Momentum baseados nos preços do Supabase.

### Fase 4: Testes Locais e Deploy
1. Configurar `DATABASE_URL` (Supabase connection string) local e testar o endpoint de Sync.
2. Homologar as rotas da API (`/api/options/scan`, etc.) verificando a queda drástica de latência (esperado < 1 segundo).
3. Atualizar as variáveis de ambiente no painel do Render e Vercel e aplicar deploy.

## Alternativas Consideradas
- **Web Scraping Contínuo com Cache:** Já provou ser frágil devido a restrições e mudanças anti-bot do Yahoo Finance.
- **Worker/Scheduler Interno no FastAPI:** Descartado pois consome recursos vitais e pode escalar incorretamente no Render. Um Endpoint acionado por Cron externo (serverless) é mais resiliente.
- **Conexão via SDK REST do Supabase:** Descartado em favor do **SQLAlchemy**, pois o SDK REST retorna JSONs que demandam custos de CPU para virar DataFrames, enquanto o `SQLAlchemy` traduz resultados SQL para Pandas de forma binária e ultrarrápida.

## Validação & Migração
1. **Validação:** Rodaremos a API de forma mista temporariamente ou como branch separada até que o ETL prove popular a base de dados com 100% de sucesso.
2. **Rollback:** Caso a arquitetura Supabase encontre latência de rede não prevista, retornamos o commit que contém a versão otimizada em memória construída recentemente.
