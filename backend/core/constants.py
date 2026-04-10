import fundamentus
import time

_cache_ibrx = None
_cache_time = 0

def get_ibrx_100():
    """
    Retorna dinamicamente os 100 ativos mais líquidos da B3 usando o Fundamentus.
    Isso substitui a lista estática do IBRX-100 e evita erros com ativos deslistados
    que quebravam o download do yfinance.
    """
    global _cache_ibrx, _cache_time
    
    # Cache de 24 horas (86400 segundos) para não sobrecarregar o Fundamentus
    if _cache_ibrx is not None and time.time() - _cache_time < 86400:
        return _cache_ibrx
        
    try:
        df = fundamentus.get_resultado()
        # O index do dataframe é o 'papel' (ticker)
        # Filtra fundos imobiliários e BDRs simples se necessário, mas as mais líquidas 
        # do Fundamentus geralmente são as do IBRX.
        
        # Pega as 100 mais líquidas (evita as com baixa liquidez ou deslistadas)
        top_100 = df.sort_values('liq2m', ascending=False).head(100).index.tolist()
        
        # Filtra apenas tickers que parecem ações comuns (terminam em 3, 4, 5, 6, 11)
        valid_tickers = [t for t in top_100 if any(t.endswith(str(n)) for n in [3, 4, 5, 6, 11])]
        
        # Se por algum motivo a lista estiver vazia, levanta erro para ir pro fallback
        if len(valid_tickers) < 50:
            raise ValueError("Poucos ativos retornados do Fundamentus")
            
        _cache_ibrx = valid_tickers
        _cache_time = time.time()
        return _cache_ibrx
    except Exception as e:
        print(f"Erro ao buscar universo dinâmico: {e}. Usando fallback estático.")
        # FALLBACK: Lista Estática de Segurança
        return [
            "ABEV3", "ALOS3", "ALPA4", "ASAI3", "B3SA3", "BBAS3", "BBDC3", "BBDC4",
            "BBSE3", "BEEF3", "BPAC11", "BRAP4", "BRAV3", "BRKM5", "CAML3",
            "CASH3", "CMIG4", "CMIN3", "COGN3", "CPFE3", "CSAN3",
            "CSNA3", "CVCB3", "CYRE3", "DXCO3", "ECOR3", "EGIE3",
            "ENEV3", "ENGI11", "EQTL3", "EZTC3", "FLRY3", "GGBR4", "GOAU4", "HAPV3",
            "HYPE3", "IGTI11", "IRBR3", "ITSA4", "ITUB4", "KLBN11", "LREN3",
            "LWSA3", "MGLU3", "MOVI3", "MRVE3", "MULT3", "PCAR3", "PETR3",
            "PETR4", "PLPL3", "POMO4", "PRIO3", "PSSA3", "RADL3", "RAIL3", "RAIZ4",
            "RANI3", "RDOR3", "RECV3", "RENT3", "ROMI3", "SANB11", "SBSP3", "SLCE3", "SMTO3",
            "SUZB3", "TAEE11", "TIMS3", "TOTS3", "UGPA3", "USIM5", "VALE3",
            "VBBR3", "VIVA3", "VIVT3", "WEGE3", "YDUQ3", "VAMO3", "BOVA11", "SMAL11"
        ]

# Para manter compatibilidade onde for importado diretamente, exportamos como property
# Mas o ideal é chamar get_ibrx_100()
IBRX_100 = get_ibrx_100()

# LISTA VIP (LIQUIDEZ ALTA EM OPÇÕES)
VIP_TICKERS = [
    "VALE3.SA", "PETR4.SA", "ITUB4.SA", "BBDC4.SA", "BBAS3.SA", "PETR3.SA", 
    "BOVA11.SA", "ELET3.SA", "LREN3.SA", "PRIO3.SA", "WEGE3.SA", "GGBR4.SA", 
    "JBSS3.SA", "ITSA4.SA", "B3SA3.SA", "HAPV3.SA", "SUZB3.SA", "CSNA3.SA",
    "CMIG4.SA", "USIM5.SA", "RAIL3.SA"
]

BDR_TICKERS = [
    'S1TX34.SA', 'W1DC34.SA', 'MUTC34.SA', 'J2BL34.SA', 'T1EL34.SA', 'HPQB34.SA', 'DELL34.SA',
    'AVGO34.SA', 'QCOM34.SA', 'A1MD34.SA', 'ITLC34.SA', 'TSMC34.SA', 'SMCI34.SA', 'NVDC34.SA',
    'M2PM34.SA', 'S1BS34.SA', 'G1FI34.SA', 'AURA33.SA', 'N1EM34.SA', 'VALE34.SA', 'RIO34.SA', 'FCXO34.SA',
    'MSFT34.SA', 'AAPL34.SA', 'AMZO34.SA', 'GOGL34.SA', 'M1TA34.SA', 'P2LT34.SA', 'SSFO34.SA', 'ADBE34.SA', 'ORCL34.SA',
    'W2YF34.SA', 'MELI34.SA', 'NIKE34.SA', 'MCDC34.SA', 'COCA34.SA', 'PEPB34.SA', 'LILY34.SA', 'N1VO34.SA', 'TSLA34.SA'
]
