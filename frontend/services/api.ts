import axios from 'axios';
import { IPortfolio, IAlphaSelection, IPairTrade } from '@/types/quant';

export const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
  timeout: 120000,
});

export const QuantService = {
  getMonthlyPortfolio: async (capital: number, n_br: number, n_bdr: number): Promise<IPortfolio> => {
    const response = await api.get(`/selection/monthly-portfolio`, {
      params: { capital, n_br, n_bdr }
    });
    
    // Mapeamento da resposta do backend para a interface do frontend
    return {
      remainingCash: response.data.resumo.caixa_restante,
      allocations: response.data.ativos.map((ativo: any) => ({
        ticker: ativo.ticker,
        price: ativo.preco,
        shares: ativo.qtd,
        totalVolume: ativo.financeiro,
        weight: ativo.participacao_pct / 100
      }))
    };
  },
  getStatArbScan: async (capital: number): Promise<IPairTrade[]> => {
    const response = await api.get(`/strategy/long-short/scan`, { params: { capital } });
    
    // Mapeamento da resposta do backend para a interface do frontend
    return response.data.data.map((item: any) => ({
      pair: item.par,
      zScore: item.z_score,
      historyZScore: item.history_z_score,
      halfLife: item.half_life,
      robustness: item.robustez,
      residualSeries: 0, // placeholder if not returned
      boleta: item.boleta
    }));
  }
};