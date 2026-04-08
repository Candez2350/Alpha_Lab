import pandas as pd
import core.yf_setup as yf
import fundamentus
import math
from datetime import datetime

class MonthlyBdrEngine:
    def __init__(self):
        # Pool mestre de BDRs extraído do seu script original 
        self.bdrs_pool = [
            'S1TX34.SA', 'W1DC34.SA', 'MUTC34.SA', 'J2BL34.SA', 'T1EL34.SA', 'HPQB34.SA', 'DELL34.SA',
            'AVGO34.SA', 'QCOM34.SA', 'A1MD34.SA', 'ITLC34.SA', 'TSMC34.SA', 'SMCI34.SA', 'NVDC34.SA',
            'M2PM34.SA', 'S1BS34.SA', 'G1FI34.SA', 'AURA33.SA', 'N1EM34.SA', 'VALE34.SA', 'RIO34.SA', 'FCXO34.SA',
            'MSFT34.SA', 'AAPL34.SA', 'AMZO34.SA', 'GOGL34.SA', 'M1TA34.SA', 'P2LT34.SA', 'SSFO34.SA', 'ADBE34.SA', 'ORCL34.SA',
            'W2YF34.SA', 'MELI34.SA', 'NIKE34.SA', 'MCDC34.SA', 'COCA34.SA', 'PEPB34.SA', 'LILY34.SA', 'N1VO34.SA', 'TSLA34.SA'
        ]

    def get_top_br_stocks(self):
        """Busca as ações BR mais líquidas via Fundamentus."""
        try:
            df = fundamentus.get_resultado()
            df.columns = [col.replace('.', '').replace('/', '').lower() for col in df.columns]
            # Filtro de liquidez > 500k/dia 
            df = df[df['liq2m'] > 500000] 
            df = df.sort_values(by='liq2m', ascending=False).head(100)
            
            # Filtra apenas ações ordinárias, preferenciais e units (3, 4, 11) 
            tickers = [f"{t}.SA" for t in df.index if t[-1] in ['3', '4', '11'] and not t.endswith('34') and t != 'AURA33']
            return tickers
        except Exception:
            return []

    def calculate_momentum_score(self, tickers, tipo, top_n=5):
        """Calcula o Momentum Triplo (12M, 3M, 1M) e checa SMA200."""
        if not tickers: return pd.DataFrame()
        
        try:
            data = yf.download(tickers, period="2y", progress=False)['Close']
            data = data.ffill().dropna(axis=1, how='all')
            
            scores = []
            for ticker in data.columns:
                serie = data[ticker].dropna()
                if len(serie) < 252: continue
                
                atual = serie.iloc[-1]
                # Retornos: 12 meses, 3 meses e 1 mês 
                r12 = (atual / serie.iloc[-252]) - 1
                r3 = (atual / serie.iloc[-63]) - 1
                r1 = (atual / serie.iloc[-21]) - 1
                
                sma200 = serie.iloc[-200:].mean()
                tendencia = "ALTA" if atual > sma200 else "BAIXA"
                
                scores.append({
                    'ticker': ticker.replace('.SA', ''),
                    'tipo': tipo,
                    'preco': float(atual),
                    'r12': r12, 'r3': r3, 'r1': r1,
                    'tendencia': tendencia
                })
                
            df = pd.DataFrame(scores)
            # Ranking: Soma dos Ranks de 12M, 3M e 1M 
            df['rank_score'] = df['r12'].rank(ascending=False) + \
                               df['r3'].rank(ascending=False) + \
                               df['r1'].rank(ascending=False)
            
            # Penalidade para ativos em tendência de baixa (abaixo da média 200)
            df.loc[df['tendencia'] == 'BAIXA', 'rank_score'] += 200
            return df.sort_values('rank_score').head(top_n)
        except Exception:
            return pd.DataFrame()

    def optimize_allocation(self, df_portfolio, capital_total):
        """Distribui o capital focando em caixa zerado e pesos percentuais."""
        df = df_portfolio.copy()
        n_ativos = len(df)
        if n_ativos == 0: return {}

        alocacao_base = capital_total / n_ativos
        
        # Cálculo de quantidades inteiras 
        df['qtd'] = df['preco'].apply(lambda p: math.floor(alocacao_base / p))
        df['financeiro'] = df['qtd'] * df['preco']
        
        # Lógica de reinvestimento da sobra para caixa zerado 
        sobra = capital_total - df['financeiro'].sum()
        while sobra > df['preco'].min():
            ativos_compraveis = df[df['preco'] <= sobra]
            if ativos_compraveis.empty: break
            
            # Prioriza reinvestir no ativo mais barato para zerar o caixa mais rápido 
            idx_alocar = ativos_compraveis['preco'].idxmin()
            df.at[idx_alocar, 'qtd'] += 1
            df.at[idx_alocar, 'financeiro'] += df.at[idx_alocar, 'preco']
            sobra -= df.at[idx_alocar, 'preco']
        
        # Cálculo da composição percentual real final
        total_alocado = df['financeiro'].sum()
        df['participacao_pct'] = (df['financeiro'] / total_alocado * 100).round(2)
            
        return {
            "ativos": df.to_dict(orient='records'),
            "resumo": {
                "capital_solicitado": capital_total,
                "total_investido": round(total_alocado, 2),
                "caixa_restante": round(capital_total - total_alocado, 2),
                "num_ativos": n_ativos
            }
        }

    def get_monthly_portfolio(self, capital, n_ativos_br=5, n_ativos_bdr=5):
        """Gera a carteira final unificada com os parâmetros do usuário."""
        br_picks = self.calculate_momentum_score(self.get_top_br_stocks(), "AÇÃO BR", top_n=n_ativos_br)
        bdr_picks = self.calculate_momentum_score(self.bdrs_pool, "BDR USA", top_n=n_ativos_bdr)
        
        portfolio_raw = pd.concat([br_picks, bdr_picks], ignore_index=True)
        return self.optimize_allocation(portfolio_raw, capital)