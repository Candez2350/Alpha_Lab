import pandas as pd
import core.yf_setup as yf
import fundamentus
from datetime import datetime

class SelectionEngine:
    def __init__(self):
        # Definições de setores para exclusão na Magic Formula e inclusão no Momentum
        self.setor_bancos = 35
        self.setor_utils = 14
        self.setor_seguros = 38

    def get_magic_formula_ranking(self, top_n=6):
        """
        Filtra o mercado por ROIC e EV/EBIT, excluindo Financeiras e Utilities via Banco de Dados.
        """
        try:
            from core.db import engine
            query = "SELECT ticker, evebit, roic, liq2m, cotacao, setor FROM fundamentals"
            df = pd.read_sql(query, engine)
            
            if df.empty: return pd.DataFrame()
            
            # Filtros de Liquidez e Qualidade 
            df = df[df['liq2m'] > 1000000] # Liquidez > R$ 1M/dia 
            df = df[df['evebit'] > 0]       # EV/EBIT Positivo 
            df = df[df['roic'] > 0]         # ROIC Positivo 

            # Exclusão de Setores 
            df = df[~df['setor'].isin(['banco', 'util', 'seguro'])]

            # Remoção de Duplicatas (Mantém a mais líquida da mesma empresa) 
            df['base'] = df['ticker'].str[:4]
            df = df.sort_values('liq2m', ascending=False).drop_duplicates(subset='base', keep='first')

            # Cálculo dos Ranks 
            df['rank_ev_ebit'] = df['evebit'].rank(ascending=True)
            df['rank_roic'] = df['roic'].rank(ascending=False)
            df['magic_score'] = df['rank_ev_ebit'] + df['rank_roic']
            
            res = df.sort_values('magic_score').head(top_n)
            return res[['ticker', 'evebit', 'roic', 'magic_score', 'cotacao']]
        except Exception:
            return pd.DataFrame()

    def get_momentum_ranking(self, n_bancos=2, n_eletricas=2):
        """
        Captura a tendência de 12 meses e 3 meses em Bancos e Elétricas via Banco de Dados.
        """
        try:
            from core.db import engine, Fundamental, DailyPrice
            from sqlalchemy import select
            
            query_setores = select(Fundamental.ticker, Fundamental.setor).where(
                Fundamental.setor.in_(['banco', 'util'])
            )
            df_setores = pd.read_sql(query_setores, engine)
            
            bancos_garantidos = ['ITUB4', 'BBDC4', 'BBAS3', 'SANB11', 'BPAC11'] 
            
            if not df_setores.empty:
                utils_db = df_setores[df_setores['setor'] == 'util']['ticker'].tolist()
                bancos_db = df_setores[df_setores['setor'] == 'banco']['ticker'].tolist()
            else:
                utils_db = []
                bancos_db = []
            
            target_tickers = list(set(bancos_garantidos + utils_db + bancos_db))
            if not target_tickers: return pd.DataFrame()
            
            target_tickers_sa = [f"{t}.SA" for t in target_tickers]
            
            query_prices = select(DailyPrice.date, DailyPrice.ticker, DailyPrice.close).where(
                DailyPrice.ticker.in_(target_tickers_sa)
            ).order_by(DailyPrice.date.asc())
            
            df_prices = pd.read_sql(query_prices, engine)
            
            if df_prices.empty: return pd.DataFrame()
            
            data = df_prices.pivot(index='date', columns='ticker', values='close')
            data.index = pd.to_datetime(data.index)
            data = data.ffill().dropna(axis=1, how='all')

            momentum_results = []
            for ticker_sa in data.columns:
                ticker = ticker_sa.replace(".SA", "")
                serie = data[ticker_sa].dropna()
                
                if len(serie) < 252: continue
                
                # Retornos 12M e 3M
                p_atual = serie.iloc[-1]
                ret_12m = (p_atual / serie.iloc[-252]) - 1
                ret_3m = (p_atual / serie.iloc[-63]) - 1
                
                setor = "BANCO" if ticker in bancos_garantidos or ticker in bancos_db else "ELETRICA"
                
                momentum_results.append({
                    'ticker': ticker,
                    'setor': setor,
                    'preco': float(p_atual),
                    'ret_12m': float(ret_12m),
                    'ret_3m': float(ret_3m),
                    'score': float(ret_12m + ret_3m)
                })

            df_mom = pd.DataFrame(momentum_results)
            if df_mom.empty: return pd.DataFrame()
            
            # Seleção: N Melhores de cada setor 
            top_bancos = df_mom[df_mom['setor'] == "BANCO"].sort_values('score', ascending=False).head(n_bancos)
            top_utils = df_mom[df_mom['setor'] == "ELETRICA"].sort_values('score', ascending=False).head(n_eletricas)
            
            return pd.concat([top_bancos, top_utils])
        except Exception:
            return pd.DataFrame()

    def get_final_selection(self, n_mf=6, n_bancos=2, n_eletricas=2):
        """Une as duas estratégias para a API com parâmetros customizáveis."""
        df_mf = self.get_magic_formula_ranking(top_n=n_mf)
        df_mom = self.get_momentum_ranking(n_bancos=n_bancos, n_eletricas=n_eletricas)

        return {
            "magic_formula": df_mf.to_dict(orient='records'),
            "momentum": df_mom.to_dict(orient='records'),
            "updated_at": datetime.now().strftime("%d/%m/%Y %H:%M")
        }