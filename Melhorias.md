# Crítica Arquitetural e Roadmap de Melhorias (Alpha Lab)

Este documento apresenta uma análise crítica e construtiva da atual arquitetura do **Candez Quant Platform (Alpha Lab)**, juntamente com um roadmap de melhorias, novos módulos e funcionalidades para transformar o sistema em um Terminal Quantitativo de nível institucional.

---

## 1. Crítica à Arquitetura Atual

A transição recente para processamento em Batch (Cronjobs) e Cache em Banco de Dados (PostgreSQL/Supabase) resolveu o principal gargalo de performance e rate-limits. No entanto, para escalar o sistema, os seguintes pontos merecem atenção:

* **Orquestração de Tarefas (Backend):** Atualmente, o processamento diário roda em uma simples `Thread` do Python disparada por um endpoint HTTP (`/api/system/cron`). Para um sistema em produção real, caso uma etapa falhe (ex: o Yahoo Finance caia no meio do download), o sistema inteiro falha silenciosamente.
  * *Solução:* Implementar um sistema de filas de mensageria como **Celery + Redis** ou **Apache Airflow** para gerenciar os jobs, permitindo tentativas de repetição (retries) automáticas.
* **Dependência do Yahoo Finance:** O `yfinance` é ótimo para MVP, mas é instável e propenso a bloqueios e dados sujos (splits/dividendos não ajustados corretamente).
  * *Solução:* Integrar provedores de dados financeiros profissionais (ex: AlphaVantage, Tiingo, ou scraping direto da B3/CVM).
* **Gestão de Estado (Frontend):** O React está utilizando chamadas diretas com `useEffect` e `useState`.
  * *Solução:* Adotar bibliotecas como **React Query (TanStack Query)** para fazer o cache inteligente dos dados no navegador, evitando que o usuário baixe os mesmos rankings se trocar de aba e voltar.
* **Calculadora Black-Scholes:** Hoje, cada cálculo exige um ping no backend. Como a fórmula de Black-Scholes é estritamente matemática, ela poderia ser reescrita 100% em TypeScript no Frontend, gerando resultados instantâneos conforme o usuário digita (zero latência).

---

## 2. Novos Módulos e Funcionalidades (Roadmap)

### 📈 Módulo de Backtesting (O Santo Graal)
Nenhuma plataforma Quant está completa sem backtesting.
* **Simulador Histórico:** Permitir que o usuário teste a *Magic Formula* ou estratégias de *Momentum* nos últimos 5 ou 10 anos para ver qual seria o retorno comparado ao IBOV.
* **Gráficos de Drawdown e Sharpe Ratio:** Exibir métricas de risco real das carteiras montadas.

### ⚖️ Evolução do Long & Short (Arbitragem)
O scanner atual encontra os pares e exibe na tabela.
* **Visualização Gráfica do Spread:** Ao clicar em um par, abrir um gráfico mostrando o histórico do Spread e do Z-Score cruzando as bandas de +2 e -2 desvios padrões.
* **Acompanhamento de Posição:** Permitir que o usuário "salve" um par que ele entrou, e o sistema calcule o lucro/prejuízo (PnL) em tempo real conforme o Spread converge para a média.

### 🛡️ Gestão de Risco e Alocação Avançada
O otimizador atual foca em "Caixa Zerado" (Programação Linear).
* **Fronteira Eficiente de Markowitz:** Evoluir o motor para considerar a *Covariância* e *Correlação* entre os ativos. O sistema não deve apenas comprar o que sobrou no caixa, mas montar uma carteira que minimize o risco para um dado nível de retorno esperado.

### 📉 Evolução do Módulo de Opções
* **Payoff Charts (Gráficos de Lucro/Prejuízo):** Desenhar o gráfico de Payoff (aquela linha torta mostrando onde a opção dá lucro ou prejuízo no vencimento).
* **Estruturas Complexas:** Permitir a montagem de estratégias com múltiplas "pernas" (Travas de Alta/Baixa, Iron Condor, Straddle) e calcular as Gregas da estrutura inteira, não apenas da opção individual.

### 🔐 Autenticação e Personalização (SaaS)
* **Login de Usuários:** Integrar o **NextAuth** ou **Supabase Auth**.
* **Watchlists e Alertas:** Permitir que o usuário crie uma lista de ativos e receba um e-mail ou alerta no painel quando um *Squeeze* ou *Breakout* do Qullamaggie for ativado em um de seus ativos favoritos.

---

## 3. UI / UX (Experiência do Usuário)

* **Modo Escuro (Dark Mode):** Traders e quants amam interfaces escuras. O Tailwind já suporta nativamente, bastaria mapear as cores `dark:` nos componentes atuais.
* **Gráficos Interativos:** Substituir tabelas estáticas de preços por bibliotecas como o **Lightweight Charts (TradingView)** para exibir os Candlesticks diretamente na plataforma quando o usuário clica em um ticker no Scanner.
* **Exportação de Dados:** Botão simples de "Exportar para CSV/Excel" nas tabelas de Long & Short e Seleção Alpha, permitindo que o usuário brinque com os dados em suas próprias planilhas.

---

## Resumo da Visão
O **Alpha Lab** possui um esqueleto formidável. A atual arquitetura resolve o peso computacional, o que abre as portas para escalar o Frontend livremente. O próximo grande salto transformacional para a plataforma é a inclusão de **Gráficos Visuais de Dados (DataViz)** e um **Módulo de Backtest**, que transformarão a ferramenta de um "Scanner Diário" em uma plataforma de pesquisa quantitativa completa.