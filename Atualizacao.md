# Plano de Atualização: Processamento Batch e Cache em Banco de Dados

## 1. Visão Geral e Arquitetura

Este plano visa refatorar a arquitetura atual do **Candez Quant Platform** migrando os cálculos on-the-fly (feitos durante a requisição do usuário) para um processo batch diário (Cron Job às 23:30). Os resultados de cada motor (Alpha, Long & Short, Opções, Alocação) serão pré-calculados e salvos em tabelas no banco de dados. O Frontend consumirá os dados de forma instantânea através de simples consultas (`SELECT`) no banco.

### Vantagens (Análise Crítica)
- **Fim dos Bloqueios (Rate Limits):** Resolve definitivamente os problemas listados no `problema.md`. O yfinance será consultado de forma controlada apenas uma vez ao dia, fora do horário de pregão.
- **Performance Extrema (Frontend):** O tempo de resposta da API cairá de vários segundos para milissegundos, melhorando drasticamente a experiência do usuário.
- **Escalabilidade e Limpeza de Dados:** As tabelas de ranking terão seus dados sobrescritos diariamente (`TRUNCATE` ou deleção em massa antes do insert), evitando o inchaço do banco de dados (bloat). A flexibilidade para exibir 5 ou 50 ativos será feita via `LIMIT` na query SQL.

### Revisão do Módulo de Opções
Foi identificado que **1 única tabela de ranking** é suficiente para o módulo de Opções. 
Ao rodar a análise de volatilidade (HV20, HV50, Squeeze) e setups Qullamaggie para todos os ativos do IBRX-100 no backup diário, podemos salvar tudo na tabela `options_analysis`. 
- O endpoint do **Scanner** filtrará os ativos com `squeeze_on = True` ou `qullamaggie_status` ativo.
- O endpoint do **Radar de Volatilidade** de um ativo específico fará um simples `SELECT` nessa mesma tabela buscando pelo `ticker`.
- *(Nota: O endpoint de precificação Black-Scholes continua dinâmico pois depende dos parâmetros (Strike, DTE) que o usuário digita na hora).*

---

## 2. Checklist de Implementação (Auto Ticável)

### Fase 1: Atualização do Banco de Dados (Modelagem)
- [x] Criar tabela `rank_alpha_selection`: Armazenará a seleção baseada na Magic Formula e Momentum (campos: ticker, roic, evebit, momentum, setor, rank_final).
- [x] Criar tabela `rank_long_short`: Armazenará os pares cointegrados encontrados (campos: par, zscore, half_life, adf_pvalue, status_cointegracao, rentabilidade_estimada, etc).
- [x] Criar tabela `rank_options_analysis`: Armazenará métricas de volatilidade e setups para cada ticker (campos: ticker, hv20, hv50, vol_status, squeeze_on, direction, qullamaggie_status, momentum_60d, is_ep, is_parabolic).
- [x] Criar tabela `rank_monthly_allocation`: Armazenará os pesos e sugestão de carteira (campos: ticker, peso_sugerido, tipo_ativo (BR/BDR)).
- [x] Atualizar o arquivo `backend/core/db.py` com os novos modelos SQLAlchemy (Classes Base) e gerar a migração/criação das tabelas.

### Fase 2: Construção da Rotina de Processamento (Cron Job / Backup)
- [x] Criar arquivo `backend/core/cron_jobs.py` (ou adaptar `sync_etl.py`) para orquestrar a rotina diária.
- [x] Implementar função para limpar as tabelas de ranking (`DELETE FROM tabela`).
- [x] Implementar execução do motor de **Alpha Selection** e salvar os top N resultados em `rank_alpha_selection`.
- [x] Implementar execução do motor de **Long & Short** (varredura do IBRX-100) e salvar os pares validados em `rank_long_short`.
- [x] Implementar execução do motor de **Opções** (Volatilidade e Breakouts) para o IBRX-100 e salvar em `rank_options_analysis`.
- [x] Implementar execução do motor de **Alocação Mensal** e salvar o baseline em `rank_monthly_allocation`.
- [x] Testar a rotina completa localmente para validar a gravação no banco de dados.

### Fase 3: Refatoração dos Endpoints da API (Consumo Rápido)
- [x] Refatorar `GET /api/selection/magic-momentum`: Modificar para ler a tabela `rank_alpha_selection`, aplicando filtros (`LIMIT n_mf`, `n_bancos`, `n_eletricas`).
- [x] Refatorar `GET /api/selection/monthly-portfolio`: Modificar para ler a tabela `rank_monthly_allocation` e apenas multiplicar o peso sugerido pelo `capital` informado pelo usuário.
- [x] Refatorar `GET /api/strategy/long-short/scan`: Modificar para ler os pares salvos na tabela `rank_long_short` e apenas recalcular o rateio de lote para o capital informado.
- [x] Refatorar `GET /api/options/scan`: Modificar para ler a tabela `rank_options_analysis` ordenando por `momentum_60d` onde `squeeze_on` ou breakouts sejam verdadeiros.
- [x] Refatorar `GET /api/options/vol-radar`: Modificar para ler os dados pré-calculados na tabela `rank_options_analysis` para o ticker requisitado.

### Fase 4: Frontend e Deploy
- [x] Ajustar o Frontend (`frontend/services/api.ts` e páginas) se o formato do JSON retornado tiver alguma mudança (geralmente não deve ter, mantendo o contrato da API).
- [x] Adicionar/Agendar o gatilho da rotina diária (23:30) no backend (via `APScheduler`, rota protegida chamada por um Cron do Render/Vercel ou serviço de mensageria).
- [x] Validar todos os módulos no navegador para garantir que a transição ocorra de forma fluida.
- [x] Corrigido erro 500 no `vol-radar` alterando para retorno 404 quando o ativo não possuir análise na base de dados.
- [x] Corrigido o filtro de Scanner do IBRX-100 para listar corretamente apenas os ativos com Squeeze ou setups do Qullamaggie ativos/formando.
- [x] Corrigido a exibição de NaN no Momentum da Seleção Alpha, removendo a coluna "Retorno 12M" que não é mais cacheada, além de forçar conversão correta do Score no Cronjob.
- [x] Refatorado Design: Adicionado efeito visual Gradiente + Glow no logo "Alpha Lab" e criada uma Landing Page interativa como nova tela de Início (`/`).
- [x] Responsividade Completa: A aplicação agora é 100% responsiva (Mobile First), com a Navbar lateral se transformando dinamicamente em uma "Bottom Navigation Bar" em celulares.