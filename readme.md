# Candez Quant Platform

Candez Quant Platform é um Terminal de Inteligência Quantitativa desenvolvido para fornecer análises avançadas de mercado, englobando estratégias de arbitragem, precificação de opções e alocação tática de portfólio.

O sistema é dividido em duas partes principais: um **Backend** robusto construído com Python (FastAPI) para o processamento de modelos matemáticos e extração de dados financeiros, e um **Frontend** moderno feito em Next.js (React) para a visualização de dados e interação do usuário. 

Recentemente, a interface da plataforma foi reformulada com um **Design Claro (Light Theme)** minimalista e moderno, otimizado para plataformas financeiras utilizando a paleta `Slate` e detalhes em `Emerald`, garantindo uma leitura confortável de dados e alto contraste em tabelas e gráficos.

## 🏗 Arquitetura

- **Backend:** Python 3, FastAPI, Pandas, NumPy, yfinance, fundamentus, statsmodels, scipy.
- **Frontend:** Next.js 14+, React 19, TypeScript, TailwindCSS, Tremor (para gráficos e componentes de UI).

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
