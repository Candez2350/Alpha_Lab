import pandas as pd
import yfinance as yf
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
        Filtra o mercado por ROIC e EV/EBIT, excluindo Financeiras e Utilities.
        Baseado em Magic Formula.py e tbt.py.
        """
        try:
            # 1. Coleta e Padronização 
            df = fundamentus.get_resultado()
            df.columns = [col.replace('.', '').replace('/', '').lower() for col in df.columns]
            
            # 2. Filtros de Liquidez e Qualidade 
            df = df[df['liq2m'] > 1000000] # Liquidez > R$ 1M/dia 
            df = df[df['evebit'] > 0]       # EV/EBIT Positivo 
            df = df[df['roic'] > 0]         # ROIC Positivo 

            # 3. Exclusão de Setores 
            excluir_ids = [self.setor_bancos, self.setor_utils, self.setor_seguros]
            tickers_excluir = []
            for s_id in excluir_ids:
                try: tickers_excluir.extend(fundamentus.list_papel_setor(s_id))
                except: pass
            df = df[~df.index.isin(tickers_excluir)]

            # 4. Remoção de Duplicatas (Mantém a mais líquida da mesma empresa) 
            df['base'] = df.index.str[:4]
            df = df.sort_values('liq2m', ascending=False).drop_duplicates(subset='base', keep='first')

            # 5. Cálculo dos Ranks 
            df['rank_ev_ebit'] = df['evebit'].rank(ascending=True)
            df['rank_roic'] = df['roic'].rank(ascending=False)
            df['magic_score'] = df['rank_ev_ebit'] + df['rank_roic']
            
            # Retorna o DataFrame ordenado com os dados relevantes para o front-end
            res = df.sort_values('magic_score').head(top_n)
            return res[['evebit', 'roic', 'magic_score', 'cotacao']].reset_index().rename(columns={'index': 'ticker', 'papel': 'ticker'})
        except Exception:
            return pd.DataFrame()

    def get_momentum_ranking(self, n_bancos=2, n_eletricas=2):
        """
        Captura a tendência de 12 meses e 3 meses em Bancos e Elétricas.
        Baseado em tbt.py e momentum.py.
        """
        try:
            # 1. Listas de Setores Específicos
            bancos_garantidos = ['ITUB4', 'BBDC4', 'BBAS3', 'SANB11', 'BPAC11'] 
            try:
                setor_utils = fundamentus.list_papel_setor(self.setor_utils)
            except:
                setor_utils = []
            
            target_tickers = list(set(bancos_garantidos + setor_utils))
            
            # 2. Download de Dados
            data = yf.download([t + ".SA" for t in target_tickers], period="14mo", progress=False)['Close']
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
                
                setor = "BANCO" if ticker in bancos_garantidos else "ELETRICA"
                
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