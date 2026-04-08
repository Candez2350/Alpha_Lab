import pandas as pd
import numpy as np

class SqueezeEngine:
    @staticmethod
    def detect_keltner_squeeze(df):
        """
        Detecta o 'Squeeze': Bandas de Bollinger dentro dos Canais de Keltner.
        Indica uma compressão de volatilidade prestes a explodir.
        """
        # Cálculo das Bandas de Bollinger (20, 2)
        sma = df['Close'].rolling(window=20).mean()
        std = df['Close'].rolling(window=20).std()
        bb_upper = sma + (2 * std)
        bb_lower = sma - (2 * std)
        
        # Cálculo do Canal de Keltner (20, 1.5 ATR)
        # (Lógica simplificada para a API)
        tr = df['High'] - df['Low']
        atr = tr.rolling(window=20).mean()
        kc_upper = sma + (1.5 * atr)
        kc_lower = sma - (1.5 * atr)
        
        is_squeezed = (bb_upper < kc_upper) and (bb_lower > kc_lower)
        return {
            "is_squeezed": is_squeezed,
            "direction": "UP" if df['Close'].iloc[-1] > sma.iloc[-1] else "DOWN"
        }