export interface IAlphaSelection {
  ticker: string;
  roic: number;
  yield: number;
  momentum: number;
  finalRank: number;
}

export interface IAllocation {
  ticker: string;
  price: number;
  shares: number;
  totalVolume: number;
  weight: number;
}

export interface IPortfolio {
  remainingCash: number;
  allocations: IAllocation[];
}

export interface IPairTrade {
  pair: string;
  zScore: number;
  historyZScore?: number[];
  halfLife: number;
  robustness: string;
  residualSeries: number;
  boleta?: {
    long: { ticker: string; qtd: number; financeiro: number };
    short: { ticker: string; qtd: number; financeiro: number };
    financeiro_total: number;
    composicao_pct: Record<string, number>;
  };
}