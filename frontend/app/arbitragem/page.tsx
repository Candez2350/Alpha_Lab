'use client'
import React, { useState } from 'react'
import { 
  Card, 
  Table, 
  TableHead, 
  TableRow, 
  TableHeaderCell, 
  TableBody, 
  TableCell
} from '@tremor/react'
import { Search, ActivitySquare, ChevronDown, ChevronUp } from 'lucide-react'
import { QuantService } from '@/services/api'
import { IPairTrade } from '@/types/quant'

export default function ArbitragemDashboard() {
  const [capital, setCapital] = useState<number>(20000);
  const [pairs, setPairs] = useState<IPairTrade[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const toggleRow = (idx: number) => {
    if (expandedRow === idx) setExpandedRow(null);
    else setExpandedRow(idx);
  };

  const fetchScan = async () => {
    setLoading(true);
    setPairs([]); // Clear previous to show loading state nicely
    try {
      const data = await QuantService.getStatArbScan(capital);
      setPairs(data);
    } catch (error) {
      console.error("Erro ao buscar scan:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700 ease-out pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Long & Short</h1>
        <p className="text-slate-500 text-lg">Arbitragem Estatística por Cointegração e Análise de Pares.</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex flex-col md:flex-row gap-4 items-end">
          <div className="flex flex-col gap-2 flex-1">
            <label className="text-sm font-bold text-slate-700">Capital de Exposição (R$)</label>
            <input 
              type="number"
              value={capital}
              onChange={(e) => setCapital(Number(e.target.value))}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl shadow-sm focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all text-slate-900 font-semibold text-lg"
              min={0}
            />
          </div>
          <button 
            onClick={fetchScan} 
            disabled={loading}
            className="w-full md:w-auto px-8 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl shadow-md hover:shadow-lg transition-all font-bold flex items-center justify-center gap-3 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <Search size={20} />
            )}
            {loading ? 'Calculando Cointegração...' : 'Escanear Mercado'}
          </button>
        </div>
      </div>

      {loading && (
        <div className="text-center py-12 animate-pulse">
           <ActivitySquare size={48} className="mx-auto text-emerald-200 mb-4" />
           <p className="text-slate-500 font-medium">Buscando o índice IBRX-100 e testando ~4950 combinações...</p>
           <p className="text-slate-400 text-sm mt-1">Este processo de Data Science pode levar até 60 segundos.</p>
        </div>
      )}

      {pairs.length > 0 && (
        <Card className="bg-white border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col mt-4">
          <div className="px-6 pt-6 pb-4 border-b border-slate-100 flex justify-between items-center">
            <h3 className="text-lg font-bold text-slate-900">Oportunidades Encontradas</h3>
            <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-1 rounded-full border border-emerald-200">
              {pairs.length} Pares Ativos
            </span>
          </div>
          <div className="overflow-x-auto">
            <Table className="min-w-full">
              <TableHead className="bg-slate-50">
                <TableRow>
                  <TableHeaderCell className="text-slate-500 font-semibold py-4 px-6">Par (Ativo 1 x Ativo 2)</TableHeaderCell>
                  <TableHeaderCell className="text-slate-500 font-semibold text-right py-4 px-6">Z-Score</TableHeaderCell>
                  <TableHeaderCell className="text-slate-500 font-semibold text-right py-4 px-6">Half-Life</TableHeaderCell>
                  <TableHeaderCell className="text-slate-500 font-semibold text-right py-4 px-6">Robustez</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {pairs.map((item, idx) => {
                  const zAbs = Math.abs(item.zScore);
                  const isHighlight = zAbs >= 1.9;
                  const isExpanded = expandedRow === idx;
                  const valueFormatter = (number: number) => `R$ ${Intl.NumberFormat('pt-BR').format(number)}`;

                  return (
                    <React.Fragment key={idx}>
                      <TableRow 
                        className={`border-b border-slate-100 hover:bg-slate-50 transition-colors cursor-pointer ${isExpanded ? 'bg-slate-50' : ''}`}
                        onClick={() => toggleRow(idx)}
                      >
                        <TableCell className="py-5 px-6">
                          <div className="flex items-center gap-2">
                            <button className="text-slate-400 hover:text-slate-600 transition-colors mr-2">
                              {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                            </button>
                            <span className="font-extrabold text-slate-900">{item.pair.split('x')[0].trim()}</span>
                            <span className="text-slate-400 text-sm font-medium">x</span>
                            <span className="font-extrabold text-slate-600">{item.pair.split('x')[1]?.trim()}</span>
                          </div>
                        </TableCell>
                        <TableCell className="text-right py-5 px-6">
                          <span className={`inline-flex items-center justify-center px-3 py-1 rounded-md font-bold text-sm border ${
                            isHighlight 
                              ? 'bg-emerald-50 text-emerald-700 border-emerald-200' 
                              : 'bg-slate-100 text-slate-700 border-slate-200'
                          }`}>
                            {item.zScore > 0 ? '+' : ''}{item.zScore.toFixed(2)}
                          </span>
                        </TableCell>
                        <TableCell className="text-right text-slate-600 py-5 px-6 font-medium">
                          {item.halfLife} <span className="text-slate-400 text-sm">dias</span>
                        </TableCell>
                        <TableCell className="text-right py-5 px-6">
                          <span className="text-slate-700 font-bold bg-slate-100 px-2 py-1 rounded-md border border-slate-200">
                            {item.robustness}
                          </span>
                        </TableCell>
                      </TableRow>
                      {isExpanded && item.boleta && (
                        <TableRow className="bg-slate-50/50">
                          <TableCell colSpan={4} className="p-0 border-b border-slate-100">
                            <div className="p-6 bg-slate-50 border-t border-slate-100 flex flex-col md:flex-row gap-6 animate-in slide-in-from-top-2 duration-300">
                              
                              <div className="flex-1 bg-white border border-slate-200 rounded-xl p-5 shadow-sm">
                                <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 border-b border-slate-100 pb-2">Boleta de Execução</h4>
                                <div className="grid grid-cols-2 gap-4">
                                  <div className="flex flex-col gap-1">
                                    <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded w-max">COMPRAR (Long)</span>
                                    <span className="font-extrabold text-slate-900 text-lg">{item.boleta.long.ticker}</span>
                                    <span className="text-slate-600 font-medium">{item.boleta.long.qtd} cotas</span>
                                    <span className="text-slate-500 text-sm">{valueFormatter(item.boleta.long.financeiro)} ({(item.boleta.composicao_pct[item.boleta.long.ticker] || 0).toFixed(1)}%)</span>
                                  </div>
                                  <div className="flex flex-col gap-1">
                                    <span className="text-xs font-bold text-red-600 bg-red-50 px-2 py-1 rounded w-max">VENDER (Short)</span>
                                    <span className="font-extrabold text-slate-900 text-lg">{item.boleta.short.ticker}</span>
                                    <span className="text-slate-600 font-medium">{item.boleta.short.qtd} cotas</span>
                                    <span className="text-slate-500 text-sm">{valueFormatter(item.boleta.short.financeiro)} ({(item.boleta.composicao_pct[item.boleta.short.ticker] || 0).toFixed(1)}%)</span>
                                  </div>
                                </div>
                                <div className="mt-4 pt-4 border-t border-slate-100 flex justify-between items-center">
                                  <span className="text-sm font-bold text-slate-500">Exposição Total:</span>
                                  <span className="font-extrabold text-slate-900">{valueFormatter(item.boleta.financeiro_total)}</span>
                                </div>
                              </div>

                              <div className="flex-1 bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col justify-center">
                                <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4 border-b border-slate-100 pb-2">Parâmetros do Trade</h4>
                                <div className="flex flex-col gap-3">
                                  <div className="flex justify-between items-center">
                                    <span className="text-sm font-semibold text-slate-600">Objetivo (Alvo):</span>
                                    <span className="text-sm font-bold text-slate-900 bg-slate-100 px-2 py-1 rounded">Retorno à Média (Z-Score = 0)</span>
                                  </div>
                                  <div className="flex justify-between items-center">
                                    <span className="text-sm font-semibold text-slate-600">Período Máximo (Stop no Tempo):</span>
                                    <span className="text-sm font-bold text-slate-900 bg-slate-100 px-2 py-1 rounded">~{Math.ceil(item.halfLife * 2)} dias (2x Half-Life)</span>
                                  </div>
                                  <div className="flex justify-between items-center">
                                    <span className="text-sm font-semibold text-slate-600">Risco (Stop Loss sugerido):</span>
                                    <span className="text-sm font-bold text-red-600 bg-red-50 px-2 py-1 rounded">Z-Score {item.zScore > 0 ? '> +' + (item.zScore + 1.0).toFixed(2) : '< ' + (item.zScore - 1.0).toFixed(2)}</span>
                                  </div>
                                </div>
                                {item.historyZScore && item.historyZScore.length > 0 && (
                                  <div className="mt-4 pt-4 border-t border-slate-100">
                                    <span className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3 block">Evolução do Z-Score (7d)</span>
                                    <div className="flex justify-between items-end h-16 gap-1 relative">
                                      {/* Linha zero */}
                                      <div className="absolute w-full h-[1px] bg-slate-200 bottom-1/2 translate-y-1/2"></div>
                                      {item.historyZScore.map((z, i) => {
                                        const zAbs = Math.abs(z);
                                        const h = Math.min(100, zAbs * 15); // max 100% height relative to half
                                        return (
                                          <div key={i} className="flex flex-col items-center flex-1 group relative h-full justify-center">
                                            {z > 0 ? (
                                              <div className="w-full bg-red-400 rounded-t-sm absolute bottom-1/2 transition-all hover:brightness-110" style={{ height: `${h}%`, opacity: 0.4 + (i * 0.1) }}></div>
                                            ) : (
                                              <div className="w-full bg-emerald-400 rounded-b-sm absolute top-1/2 transition-all hover:brightness-110" style={{ height: `${h}%`, opacity: 0.4 + (i * 0.1) }}></div>
                                            )}
                                            <div className={`absolute ${z > 0 ? '-top-6' : '-bottom-6'} bg-slate-800 text-white text-[10px] font-bold px-1.5 py-0.5 rounded opacity-0 group-hover:opacity-100 transition-opacity z-10 pointer-events-none`}>
                                              {z > 0 ? '+' : ''}{z.toFixed(2)}
                                            </div>
                                          </div>
                                        );
                                      })}
                                    </div>
                                    <div className="flex justify-between mt-2 text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                                      <span>D-7</span>
                                      <span>Hoje</span>
                                    </div>
                                  </div>
                                )}
                              </div>

                            </div>
                          </TableCell>
                        </TableRow>
                      )}
                    </React.Fragment>
                  );
                })}
              </TableBody>
            </Table>
          </div>
          <div className="bg-slate-50 p-6 border-t border-slate-100 text-sm text-slate-500">
            <h4 className="font-bold text-slate-700 mb-2">Como interpretar esta tabela:</h4>
            <ul className="list-disc pl-5 space-y-1.5">
              <li><strong className="text-slate-600">Par (Ativo 1 x Ativo 2):</strong> A direção da operação depende do sinal do Z-Score.</li>
              <li><strong className="text-emerald-700">Se o Z-Score for Negativo:</strong> Compre o Ativo 1 e Venda o Ativo 2 (Aposta na alta do resíduo).</li>
              <li><strong className="text-red-700">Se o Z-Score for Positivo:</strong> Venda o Ativo 1 e Compre o Ativo 2 (Aposta na queda do resíduo).</li>
              <li><strong className="text-slate-600">Z-Score:</strong> Distorção atual em relação à média (0). O alvo da operação é sempre o retorno do Z-Score para zero.</li>
              <li><strong className="text-slate-600">Half-Life:</strong> Expectativa estatística de tempo (em dias) para retorno à média.</li>
              <li><strong className="text-slate-600">Robustez:</strong> Quantas janelas de tempo diferentes validaram a cointegração.</li>
            </ul>
          </div>
        </Card>
      )}
    </div>
  )
}