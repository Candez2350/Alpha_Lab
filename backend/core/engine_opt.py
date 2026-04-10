import numpy as np
import pandas as pd
from scipy.stats import norm
import core.yf_setup as yf

class BreakoutEngine:
    def __init__(self):
        self.lookback_momentum = 60 # ~3 meses para medir a "estancada" prévia
        self.consolidation_days = 20 # Janela para medir a "bandeira" ou "tightness"

    def analyze_qullamaggie(self, df):
        """
        Executa o rastreio dos 3 setups principais de Qullamaggie adaptados para B3.
        """
        close = df['Close'].squeeze()
        high = df['High'].squeeze()
        volume = df['Volume'].squeeze()
        open_p = df['Open'].squeeze()
        
        # 1. Indicadores Base
        sma10 = close.rolling(10).mean()
        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()
        
        # --- SETUP 1: BREAKOUT (TENDÊNCIA + CONSOLIDAÇÃO) ---
        # Momentum Prévio: Subiu pelo menos 12% nos últimos 60 dias
        momentum_60d = (close.iloc[-1] / close.iloc[-60]) - 1
        trend_ok = (momentum_60d > 0.12) and (close.iloc[-1] > sma20.iloc[-1] > sma50.iloc[-1])
        
        # Consolidação: Está "apertado" perto da máxima de 20 dias (distância < 8%)
        max_20d = high.rolling(20).max().shift(1)
        dist_to_high = (max_20d.iloc[-1] - close.iloc[-1]) / close.iloc[-1]
        tight_ok = -0.05 < dist_to_high < 0.08
        
        # Gatilho: Rompendo máxima de 10 dias com Volume > Média 20d
        max_10d = high.rolling(10).max().shift(1)
        is_breakout = (close.iloc[-1] > max_10d.iloc[-1]) and (volume.iloc[-1] > volume.rolling(20).mean().iloc[-1] * 1.3)

        # --- SETUP 2: EPISODIC PIVOT (EP) ---
        # Gap de Alta > 1.5% com Volume > 2x a Média
        prev_high = high.shift(1).iloc[-1]
        gap_pct = (open_p.iloc[-1] - prev_high) / prev_high
        vol_avg = volume.rolling(20).mean().shift(1).iloc[-1]
        is_ep = (gap_pct > 0.015) and (volume.iloc[-1] > 2 * vol_avg) and (close.iloc[-1] > open_p.iloc[-1])

        # --- SETUP 3: PARABOLIC SHORT (EXAUSTÃO) ---
        # RSI esticado + Distância da média de 10 dias > 15%
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        dist_sma10 = (close.iloc[-1] / sma10.iloc[-1]) - 1
        is_parabolic = (rsi.iloc[-1] > 75) and (dist_sma10 > 0.15)

        return {
            "breakout": {"active": bool(trend_ok and (tight_ok or is_breakout)), "status": "🔥 BREAKOUT" if is_breakout else "💤 SETUP FORMANDO"},
            "episodic_pivot": {"active": bool(is_ep), "gap_pct": round(float(gap_pct) * 100, 2) if not pd.isna(gap_pct) else 0},
            "parabolic_short": {"active": bool(is_parabolic), "rsi": round(float(rsi.iloc[-1]), 1) if not pd.isna(rsi.iloc[-1]) else 0},
            "momentum_60d": round(float(momentum_60d) * 100, 2) if not pd.isna(momentum_60d) else 0
        }


class OptionsEngine:
    def __init__(self, risk_free=0.1175):
        self.r = risk_free # Selic/Taxa Livre de Risco padrão 

    @staticmethod
    def black_scholes(S, K, T, r, sigma, option_type='call'):
        """Calcula Preço Justo e Gregas (Delta, Gamma, Theta, Vega)."""
        if T <= 0: 
            return {"price": max(0, S-K) if option_type == 'call' else max(0, K-S), "delta": 0}
        
        d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)
        
        pdf_d1 = norm.pdf(d1)
        cdf_d1 = norm.cdf(d1)
        cdf_d2 = norm.cdf(d2)

        if option_type == 'call':
            price = S * cdf_d1 - K * np.exp(-r * T) * cdf_d2
            delta = cdf_d1
        else: 
            price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
            delta = cdf_d1 - 1 
            
        # Gregas Adicionais para o Front-end 
        gamma = pdf_d1 / (S * sigma * np.sqrt(T))
        vega = (S * np.sqrt(T) * pdf_d1) / 100 # Vega por 1% de IV
        theta = (-(S * sigma * pdf_d1) / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * cdf_d2) / 365

        return {
            "price": round(float(price), 2),
            "delta": round(float(delta), 2),
            "gamma": round(float(gamma), 4),
            "vega": round(float(vega), 4),
            "theta": round(float(theta), 4)
        }

    def analyze_volatility_and_squeeze(self, df):
        """Detecta compressão (Squeeze) e status da Volatilidade."""
        if isinstance(df.columns, pd.MultiIndex):
            df = df.droplevel(1, axis=1)

        close = df['Close'].squeeze()
        high = df['High'].squeeze()
        low = df['Low'].squeeze()

        sma = close.rolling(window=20).mean()
        
        # 1. Volatilidade Histórica Comparada (HV20 vs HV50) 
        log_ret = np.log(close / close.shift(1))
        hv20 = log_ret.rolling(window=20).std() * np.sqrt(252) * 100
        hv50 = log_ret.rolling(window=50).std() * np.sqrt(252) * 100
        
        # 2. Lógica de Squeeze (Bollinger vs Keltner) 
        std = close.rolling(window=20).std()
        bb_upper, bb_lower = sma + (2 * std), sma - (2 * std)
        
        tr = pd.concat([high - low, 
                        abs(high - close.shift(1)), 
                        abs(low - close.shift(1))], axis=1).max(axis=1)
        atr = tr.rolling(window=20).mean()
        kc_upper, kc_lower = sma + (1.5 * atr), sma - (1.5 * atr)
        
        is_squeezed = bool((bb_upper.iloc[-1] < kc_upper.iloc[-1]) and (bb_lower.iloc[-1] > kc_lower.iloc[-1]))
        
        # 3. Status da Volatilidade para Estratégia 
        vol_status = "⚖️ MÉDIA"
        if hv20.iloc[-1] < hv50.iloc[-1] * 0.9: vol_status = "📉 BAIXA (Barata)"
        elif hv20.iloc[-1] > hv50.iloc[-1] * 1.2: vol_status = "📈 ALTA (Cara)"

        # 4. Breakout Engine (Qullamaggie)
        qullamaggie_data = BreakoutEngine().analyze_qullamaggie(df)

        return {
            "hv20": round(float(hv20.iloc[-1]), 2),
            "hv50": round(float(hv50.iloc[-1]), 2),
            "vol_status": vol_status,
            "squeeze_on": is_squeezed,
            "direction": "BULLISH" if close.iloc[-1] > sma.iloc[-1] else "BEARISH",
            "qullamaggie": qullamaggie_data
        }

    def scan_market(self, tickers):
        """Varre o mercado buscando ativos com Squeeze ou Qullamaggie ativos via Banco de Dados."""
        try:
            from core.db import engine, DailyPrice
            from sqlalchemy import select
            tickers_sa = [f"{t}.SA" for t in tickers]
            if not tickers_sa: return []
            
            query = select(
                DailyPrice.date, DailyPrice.ticker, DailyPrice.close, 
                DailyPrice.high, DailyPrice.low, DailyPrice.open, DailyPrice.volume
            ).where(DailyPrice.ticker.in_(tickers_sa)).order_by(DailyPrice.date.asc())
            
            df_all = pd.read_sql(query, engine)
            if df_all.empty: return []

            results = []
            for t_sa in tickers_sa:
                df_ativo = df_all[df_all['ticker'] == t_sa].copy()
                if df_ativo.empty: continue
                
                df_ativo.set_index('date', inplace=True)
                df_ativo.index = pd.to_datetime(df_ativo.index)
                
                # Mapping column names to Capitalized to match existing logic:
                df_ativo.rename(columns={'close': 'Close', 'high': 'High', 'low': 'Low', 'open': 'Open', 'volume': 'Volume'}, inplace=True)
                
                if len(df_ativo) < 60: continue
                
                analysis = self.analyze_volatility_and_squeeze(df_ativo)
                
                # Só adiciona se tiver algo interessante
                has_squeeze = analysis['squeeze_on']
                has_qullamaggie = analysis['qullamaggie']['breakout']['active'] or analysis['qullamaggie']['episodic_pivot']['active'] or analysis['qullamaggie']['parabolic_short']['active']
                
                if has_squeeze or has_qullamaggie:
                    ticker_clean = t_sa.replace('.SA', '')
                    results.append({
                        "ticker": ticker_clean,
                        "squeeze": analysis['squeeze_on'],
                        "qullamaggie_status": analysis['qullamaggie']['breakout']['status'],
                        "is_ep": analysis['qullamaggie']['episodic_pivot']['active'],
                        "is_parabolic": analysis['qullamaggie']['parabolic_short']['active'],
                        "direction": analysis['direction'],
                        "momentum_60d": analysis['qullamaggie']['momentum_60d']
                    })
            
            # Ordenar por momentum (maior primeiro)
            results = sorted(results, key=lambda x: x['momentum_60d'], reverse=True)
            return results
        except Exception as e:
            return []
