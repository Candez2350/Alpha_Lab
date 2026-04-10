import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from itertools import combinations
import core.yf_setup as yf

class LongShortEngine:
    def __init__(self):
        # Janelas de teste para garantir que a cointegração não é "sorte"
        self.janelas = [140, 200, 250]
        self.min_confianca = 0.95 # p-value < 0.05

    def get_market_data(self, tickers):
        """Busca dados históricos do Supabase para o universo selecionado."""
        from core.db import engine, DailyPrice
        from sqlalchemy import select
        tickers_sa = [t + ".SA" if not t.endswith(".SA") else t for t in tickers]
        
        if not tickers_sa:
            return pd.DataFrame()
            
        query = select(DailyPrice.date, DailyPrice.ticker, DailyPrice.close).where(
            DailyPrice.ticker.in_(tickers_sa)
        ).order_by(DailyPrice.date.asc())
        
        df = pd.read_sql(query, engine)
        
        if df.empty:
            return pd.DataFrame()
            
        df = df.pivot(index='date', columns='ticker', values='close')
        df.index = pd.to_datetime(df.index)

        # Garante que temos pelo menos 250 dias de dados (maior janela)
        df = df.tail(260).ffill().bfill().dropna(axis=1) # Remove ativos que não têm histórico completo no período
        return df

    def calcular_metricas(self, serie_y, serie_x):
        """Executa a regressão OLS, ADF e calcula Half-Life."""
        df_par = pd.concat([serie_y, serie_x], axis=1).dropna()
        if len(df_par) < 100: return None
        
        y = np.log(df_par.iloc[:, 0])
        x = np.log(df_par.iloc[:, 1])
        
        try:
            # OLS (Regressão Linear) 
            model = sm.OLS(y, sm.add_constant(x)).fit()
            beta = model.params.iloc[1]
            residuos = model.resid
            
            # ADF (Teste de Dickey-Fuller para Estacionaridade) - Otimizado para velocidade
            p_val = adfuller(residuos, maxlag=1, autolag=None)[1]
            
            # Z-Score (Distorção atual vs Média Histórica) 
            res_mean = residuos.mean()
            res_std = residuos.std()
            z_score = (residuos.iloc[-1] - res_mean) / res_std
            
            # Z-Score Histórico (Últimos 7 dias)
            history_z_score = [(r - res_mean) / res_std for r in residuos.tail(7)]
            
            # Half-Life (Tempo médio de retorno à média) 
            res_lag = residuos.shift(1).bfill()
            ret = (residuos - res_lag).bfill()
            hl_model = sm.OLS(ret, sm.add_constant(res_lag)).fit()
            param = hl_model.params.iloc[1]
            hl = -np.log(2) / param if param < 0 else 999
            
            return {
                "p_value": float(p_val),
                "beta": float(beta),
                "z_score": float(z_score),
                "history_z_score": [round(float(z), 2) for z in history_z_score],
                "half_life": float(hl),
                "preco_y": float(df_par.iloc[-1, 0]),
                "preco_x": float(df_par.iloc[-1, 1])
            }
        except:
            return None

    def scan_opportunities(self, df_precos, capital_total=20000.0):
        """Varre pares e calcula a 'Boleta' de execução com base no capital."""
        pares = list(combinations(df_precos.columns, 2))
        resultados = []

        for ativo_y, ativo_x in pares:
            janelas_aprovadas = 0
            dados_finais = None
            
            # Validação Multi-Janela (Robustez) 
            for j in self.janelas:
                res = self.calcular_metricas(df_precos[ativo_y].tail(j), df_precos[ativo_x].tail(j))
                if res and res['p_value'] < (1 - self.min_confianca):
                    janelas_aprovadas += 1
                    dados_finais = res # Mantém os dados da última janela testada
            
            # Gatilho de entrada: Estacionaridade + Z-Score Extremo 
            if janelas_aprovadas >= 2 and dados_finais and abs(dados_finais['z_score']) >= 1.9:
                # Definição de Pontas (Long vs Short) baseado no Z-Score 
                z = dados_finais['z_score']
                if z < 0: # Resíduo abaixo da média -> Compra Y, Vende X
                    long, short = ativo_y, ativo_x
                    p_long, p_short = dados_finais['preco_y'], dados_finais['preco_x']
                    ratio = dados_finais['beta']
                else: # Resíduo acima da média -> Vende Y, Compra X
                    long, short = ativo_x, ativo_y
                    p_long, p_short = dados_finais['preco_x'], dados_finais['preco_y']
                    ratio = 1 / dados_finais['beta']

                # Cálculo da Alocação (Financeiro)
                financeiro_ponta = capital_total / 2 # Exposição dividida
                qtd_long = round(financeiro_ponta / p_long, -2) # Arredonda p/ lote de 100
                if qtd_long == 0: qtd_long = 100
                
                financeiro_real_long = qtd_long * p_long
                qtd_short = round((financeiro_real_long * ratio) / p_short, -2)
                if qtd_short == 0: qtd_short = 100
                
                financeiro_real_short = qtd_short * p_short

                resultados.append({
                    "par": f"{ativo_y.replace('.SA','')} x {ativo_x.replace('.SA','')}",
                    "z_score": round(z, 2),
                    "history_z_score": dados_finais['history_z_score'],
                    "half_life": round(dados_finais['half_life'], 1),
                    "robustez": f"{janelas_aprovadas}/3",
                    "boleta": {
                        "long": {"ticker": long, "qtd": int(qtd_long), "financeiro": round(financeiro_real_long, 2)},
                        "short": {"ticker": short, "qtd": int(qtd_short), "financeiro": round(financeiro_real_short, 2)},
                        "financeiro_total": round(financeiro_real_long + financeiro_real_short, 2),
                        "composicao_pct": {
                            long: round((financeiro_real_long / (financeiro_real_long + financeiro_real_short)) * 100, 1),
                            short: round((financeiro_real_short / (financeiro_real_long + financeiro_real_short)) * 100, 1)
                        }
                    }
                })

        return sorted(resultados, key=lambda x: abs(x['z_score']), reverse=True)