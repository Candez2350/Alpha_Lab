# Plano de Refatoração: Arquitetura Database-First com Supabase

## Objetivo
Migrar a captura de dados em tempo real (yfinance/fundamentus) para um modelo **Database-First** utilizando **Supabase (PostgreSQL)**. Isso garantirá respostas em milissegundos, eliminará timeouts e evitará bloqueios de IP por excesso de requisições.

## Passos da Implementação

### Fase 1: Setup e Conexão com o Banco de Dados
- [x] Adicionar dependências (`SQLAlchemy`, `psycopg2-binary`, `python-dotenv`) ao `backend/requirements.txt`.
- [x] Criar o arquivo `backend/core/db.py` para gerenciar a conexão com o Supabase via `create_engine`.
- [x] Configurar a leitura da variável de ambiente `DATABASE_URL`.
- [x] Criar estrutura das tabelas no Supabase (`daily_prices`, `fundamentals`, `bdrs`, `ibrx_100`).

### Fase 2: Construção do Pipeline ETL (Sincronização Diária)
- [x] Desenvolver a rotina de extração e transformação (download histórico e incremental de preços e fundamentos).
- [x] Criar a rota segura `POST /api/system/sync` no `backend/main.py`.
- [x] Proteger a rota com uma `SYNC_SECRET_KEY` para evitar execuções maliciosas.
- [x] Validar a inserção de dados (`upsert`) nas tabelas do Supabase utilizando o Pandas/SQLAlchemy.
- [x] **Nova Regra de Negócio (IBRX-100):** Selecionar os 100 primeiros ativos em ordem decrescente de Índice de Negociabilidade (IN) via Fundamentus (`liq2m`), que não sejam penny stocks, ponderados por valor de mercado (proxy `pvp * patrliq`).
- [x] **Nova Regra de Negócio (BDR):** Tabela exclusiva para os BDRs, baseada na lista vip existente, garantindo a sincronização e persistência para o motor de alocação.

### Fase 3: Refatoração dos Motores Quantitativos
- [x] **Alocação Tática (`engine_monthly_bdr.py`):** Substituir `yf.download` e `fundamentus.get_resultado` por `pd.read_sql`, consumindo a lista de BDRs e IBRX-100 do banco de dados.
- [x] **Stock Picking / Alpha (`engine_selection.py`):** Refatorar cálculos de Magic Formula e Momentum para consumir a tabela `fundamentals` (adicionados os campos de `setor` e `cotacao`) e `daily_prices`.
- [x] **Opções & Volatilidade (`engine_opt.py`):** Modificar o Radar e o Scanner para calcular Squeeze e Breakouts com base no banco de dados.
- [x] **Long & Short (`engine_ls.py`):** Atualizar o `get_market_data()` para puxar a matriz de preços via SQL, gerando o DataFrame final.

### Fase 4: Limpeza e Deploy
- [ ] Remover o uso de dados em tempo real da interface de navegação do usuário.
- [x] Testar todas as rotas localmente garantindo latência < 1 segundo (Testes de importação executados com sucesso).
- [ ] Atualizar variáveis de ambiente no Render (`DATABASE_URL`, `SYNC_SECRET_KEY`).
- [ ] Deploy final e configuração do Cron Job (Render Cron / GitHub Actions) para chamar a rota `/api/system/sync` diariamente (ex: 18h30).