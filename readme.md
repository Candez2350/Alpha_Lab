# Candez Quant Platform

Candez Quant Platform é um Terminal de Inteligência Quantitativa desenvolvido para fornecer análises avançadas de mercado, englobando estratégias de arbitragem, precificação de opções e alocação tática de portfólio.

O sistema é dividido em duas partes principais: um **Backend** robusto construído com Python (FastAPI) para o processamento de modelos matemáticos e extração de dados financeiros, e um **Frontend** moderno feito em Next.js (React) para a visualização de dados e interação do usuário. 

Recentemente, a interface da plataforma foi reformulada com um **Design Claro (Light Theme)** minimalista e moderno, otimizado para plataformas financeiras utilizando a paleta `Slate` e detalhes em `Emerald`, garantindo uma leitura confortável de dados e alto contraste em tabelas e gráficos.

## 🏗 Arquitetura

A plataforma utiliza um modelo de processamento em batch (ETL) para garantir extrema performance e resiliência contra rate-limits das APIs financeiras (ex: Yahoo Finance):

- **Backend:** Python 3, FastAPI, Pandas, NumPy, yfinance, statsmodels.
- **Banco de Dados / Cache:** PostgreSQL (Supabase) via SQLAlchemy. Os algoritmos quantitativos são executados uma vez ao dia via **Cron Job** (rotina em background) gravando os rankings e métricas diretamente no banco de dados. Os endpoints da API apenas consultam estas tabelas instantaneamente, resultando em latência de milissegundos.
- **Frontend:** Next.js 14+, React 19, TypeScript, TailwindCSS, Tremor.

## 🚀 Funcionalidades e Telas Principais

A interface web contempla dashboards dedicados para cada um dos motores da plataforma:

### 1. Alocação Tática Mensal (`/`)
- Otimizador de portfólio via Programação Linear que distribui o capital focando em "Caixa Zerado". 
- Balanceia investimentos entre as ações mais líquidas do Brasil e um pool seleto de BDRs (Ações Internacionais), retornando as quantidades exatas de lotes a serem executados no mercado.

### 2. Long & Short - Arbitragem Estatística (`/arbitragem`)
- **Scanner Estatístico:** Varre o mercado em busca de pares cointegrados utilizando Testes de Dickey-Fuller Aumentado (ADF).
- **Métricas Avançadas:** Exibe os pares e suas propriedades diretamente na interface, calculando o Z-Score atual, o Half-Life (tempo médio de retorno à média em dias) e a robustez da cointegração para operações com Neutralidade Financeira.

### 3. Radar de Volatilidade e Breakouts (`/opcoes`)
- **Calculadora Black-Scholes e Gregas:** Base matemática robusta para as análises do módulo.
- **Scanner Geral (IBRX-100):** Varre automaticamente todos os ativos do índice em busca de distorções de volatilidade e formações gráficas explosivas, poupando horas de busca manual.
- **Monitoramento e Squeeze:** Monitora a volatilidade histórica (HV20 vs HV50) para um Ticker selecionado e detecta compressões de volatilidade (Squeeze) cruzando as Bandas de Bollinger com os Canais de Keltner. Útil para antecipar movimentos explosivos de preço.
- **Qullamaggie Breakout Engine:** Rastreia sistematicamente três setups cruciais de Swing Trade: Breakout Clássico (bandeiras com momentum prévio), Episodic Pivot (gaps de alta explosivos com volume atípico) e Parabolic Short (identificação de exaustão e topos).

### 4. Seleção Alpha (`/alpha`)
- **Magic Formula e Momentum:** Ranking completo (Stock Picking) para seleção de ativos combinando a Magic Formula (ROIC e EV/EBIT) e o Momentum (tendência de 12 e 3 meses). Permite ao usuário filtrar e especificar diretamente na interface a quantidade desejada de ações gerais, bancos e elétricas.

## 🛠 Instalação e Execução

### Backend (FastAPI)
1. Navegue até a pasta do backend:
   ```bash
   cd backend
   ```
2. Instale as dependências:
   ```bash
   pip install -r requeriments.txt
   ```
3. Inicie o servidor local (rodará na porta 8000):
   ```bash
   uvicorn main:app --reload
   ```

### Frontend (Next.js)
1. Navegue até a pasta do frontend:
   ```bash
   cd frontend
   ```
2. Instale as dependências (você pode usar npm, yarn, pnpm ou bun):
   ```bash
   npm install
   ```
3. Inicie o servidor de desenvolvimento (rodará na porta 3000):
   ```bash
   npm run dev
   ```

Acesse o sistema web através de `http://localhost:3000` e a documentação da API em `http://localhost:8000/docs`.

## ☁️ Deploy (Vercel & Render)

Com a nova arquitetura baseada em cron jobs diários e cache em banco de dados, siga as instruções abaixo para realizar o deploy em produção:

### 1. Render (Backend + Database)
O backend foi desenhado para ser hospedado no Render, garantindo a execução das análises quantitativas.
- **Banco de Dados:** Recomendamos usar o [Supabase](https://supabase.com) para obter um banco de dados PostgreSQL gratuito e de alta performance. Copie a `DATABASE_URL` (Connection String) e adicione nas variáveis de ambiente (*Environment Variables*) do Render.
- **Serviço Web:** Crie um *Web Service* no Render apontando para o seu repositório:
  - **Root Directory:** `backend`
  - **Build Command:** `pip install -r requirements.txt`
  - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Rotina Diária (Cron Job):** O banco precisa ser atualizado todos os dias após o fechamento do pregão.
  - Para acionar a rotina, o Vercel Cron chamará a rota segura `POST /api/system/cron`.
  - Configure uma variável de ambiente chamada `SYNC_SECRET_KEY` no Render com uma senha forte. Essa mesma senha será enviada pelo Vercel.
- **Atenção (Primeira Execução):** Quando o backend rodar pela primeira vez no Render, ele identificará que o banco está vazio e começará a baixar os dados e popular os rankings em background automaticamente (isso pode levar alguns minutos).

### 2. Vercel (Frontend + Gatilho Cron)
O Frontend em Next.js é perfeitamente integrado à Vercel.
- **Deploy do Frontend:** Importe o projeto no dashboard da Vercel e especifique o *Root Directory* como `frontend`. A Vercel configurará o Next.js automaticamente.
- **Variáveis de Ambiente:** Configure a variável `NEXT_PUBLIC_API_URL` com a URL pública do seu backend no Render (ex: `https://seu-backend.onrender.com/api`). Configure também a `SYNC_SECRET_KEY` com a mesma senha definida no Render.
- **Cron Job (Gatilho):** O repositório contém um arquivo `vercel.json` no frontend que agenda a execução diária. A função serverless em `frontend/app/api/cron/sync/route.ts` será disparada pela Vercel e fará o repasse (trigger) seguro chamando o endpoint do backend.
