'use client'
import { useState } from 'react'
import { 
  Card,
  Table, 
  TableHead, 
  TableRow, 
  TableHeaderCell, 
  TableBody, 
  TableCell
} from '@tremor/react'
import { Radar, Target, MoveUpRight, MoveDownRight, Flame, ChevronUp, ChevronDown, AlertCircle, Search, ActivitySquare } from 'lucide-react'
import { api } from '@/services/api'

// Hardcoded IBRX_100 list from constants to populate the select efficiently
const IBRX_100 = [
    "ABEV3", "ALOS3", "ALPA4", "ASAI3", "AZUL4", "B3SA3", "BBAS3", "BBDC3", "BBDC4",
    "BBSE3", "BEEF3", "BPAC11", "BPAN4", "BRAP4", "BRAV3", "BRFS3", "BRKM5", "CAML3",
    "CASH3", "CCRO3", "CMIG4", "CMIN3", "COGN3", "CPFE3", "CPLE6", "CRFB3", "CSAN3",
    "CSNA3", "CVCB3", "CYRE3", "DXCO3", "ECOR3", "EGIE3", "ELET3", "ELET6", "EMBR3",
    "ENEV3", "ENGI11", "EQTL3", "EZTC3", "FLRY3", "GGBR4", "GOAU4", "GOLL4", "HAPV3",
    "HYPE3", "IGTI11", "IRBR3", "ITSA4", "ITUB4", "JBSS3", "JHSF3", "KLBN11", "LREN3",
    "LWSA3", "MGLU3", "MOVI3", "MRFG3", "MRVE3", "MULT3", "NTCO3", "PCAR3", "PETR3",
    "PETR4", "PETZ3", "PLPL3", "POMO4", "PRIO3", "PSSA3", "RADL3", "RAIL3", "RAIZ4",
    "RANI3", "RDOR3", "RECV3", "RENT3", "ROMI3", "SANB11", "SBSP3", "SLCE3", "SMTO3",
    "STBP3", "SUZB3", "TAEE11", "TIMS3", "TOTS3", "TRPL4", "UGPA3", "USIM5", "VALE3",
    "VBBR3", "VIVA3", "VIVT3", "WEGE3", "YDUQ3", "VAMO3", "BOVA11", "SMAL11"
].sort();

export default function OpcoesDashboard() {
  const [ticker, setTicker] = useState<string>('BOVA11');
  const [loading, setLoading] = useState<boolean>(false);
  const [data, setData] = useState<any>(null);
  
  const [scanLoading, setScanLoading] = useState<boolean>(false);
  const [scanData, setScanData] = useState<any[]>([]);
  const [isScannerOpen, setIsScannerOpen] = useState<boolean>(true);

  const fetchRadar = async () => {
    if (!ticker) return;
    setLoading(true);
    setData(null);
    try {
      const response = await api.get(`/options/vol-radar`, { params: { ticker: ticker.toUpperCase() } });
      setData(response.data.analysis);
    } catch (error) {
      console.error("Erro ao buscar opções:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchScan = async () => {
    setScanLoading(true);
    setScanData([]);
    try {
      const response = await api.get(`/options/scan`);
      setScanData(response.data.data || []);
      setIsScannerOpen(true);
    } catch (error) {
      console.error("Erro ao realizar scan do mercado:", error);
    } finally {
      setScanLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700 ease-out pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Radar de Volatilidade & Qullamaggie</h1>
        <p className="text-slate-500 text-lg">Detecção de Squeeze, Análise Histórica e Setups Breakout no IBRX-100.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <div className="flex flex-col sm:flex-row gap-4 items-end">
            <div className="flex flex-col gap-2 flex-1">
              <label className="text-sm font-bold text-slate-700">Selecione o Ativo Base (IBRX-100)</label>
              <div className="relative">
                <select 
                  value={ticker}
                  onChange={(e) => setTicker(e.target.value)}
                  className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl shadow-sm focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all text-slate-900 font-semibold text-lg appearance-none cursor-pointer"
                >
                  {IBRX_100.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                <div className="absolute inset-y-0 right-4 flex items-center pointer-events-none text-slate-400">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
                </div>
              </div>
            </div>
            <button 
              onClick={fetchRadar} 
              disabled={loading}
              className="w-full sm:w-auto px-8 py-3 bg-slate-900 hover:bg-slate-800 text-white rounded-xl shadow-md hover:shadow-lg transition-all font-bold flex items-center justify-center gap-3 disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Radar size={20} />
              )}
              Analisar Ativo
            </button>
          </div>
        </div>

        <div className="lg:col-span-1 bg-gradient-to-br from-emerald-600 to-teal-700 rounded-2xl shadow-md p-6 flex flex-col justify-center relative overflow-hidden">
          <div className="absolute right-0 top-0 p-4 opacity-10">
             <Target size={120} className="text-white" />
          </div>
          <h3 className="text-white font-extrabold text-xl mb-2 relative z-10">Scanner Geral de Mercado</h3>
          <p className="text-emerald-100 text-sm mb-4 relative z-10 font-medium">Busque em todo o índice por Squeezes ou setups engatilhados.</p>
          <button 
            onClick={fetchScan} 
            disabled={scanLoading}
            className="w-full px-6 py-3 bg-white text-emerald-800 hover:bg-emerald-50 rounded-xl shadow-sm transition-all font-bold flex items-center justify-center gap-3 disabled:opacity-70 disabled:cursor-not-allowed relative z-10"
          >
            {scanLoading ? (
              <div className="w-5 h-5 border-2 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <Search size={20} />
            )}
            Escanear IBRX-100
          </button>
        </div>
      </div>

      {scanLoading && (
        <div className="text-center py-12 animate-pulse bg-white rounded-2xl border border-slate-200 shadow-sm mt-4">
           <ActivitySquare size={48} className="mx-auto text-emerald-200 mb-4" />
           <p className="text-slate-500 font-medium">Lendo as bases da B3 e executando cálculos de Volatilidade no IBRX-100...</p>
           <p className="text-slate-400 text-sm mt-1">Isso pode levar de 10 a 20 segundos.</p>
        </div>
      )}

      {scanData.length > 0 && !scanLoading && (
        <Card className="bg-white border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col mt-4">
          <div 
            className="px-6 pt-6 pb-4 border-b border-slate-100 flex justify-between items-center bg-slate-50 cursor-pointer hover:bg-slate-100 transition-colors"
            onClick={() => setIsScannerOpen(!isScannerOpen)}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-emerald-100 text-emerald-600 rounded-lg">
                <Target size={20} />
              </div>
              <div>
                <h3 className="text-lg font-bold text-slate-900">Oportunidades de Volatilidade</h3>
                <p className="text-xs font-medium text-slate-500">Ativos com setups engatilhados</p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="bg-emerald-100 text-emerald-800 text-xs font-bold px-3 py-1 rounded-full border border-emerald-200">
                {scanData.length} Ativos
              </span>
              <button className="text-slate-400 hover:text-slate-600 transition-colors">
                {isScannerOpen ? <ChevronUp size={24} /> : <ChevronDown size={24} />}
              </button>
            </div>
          </div>
          
          {isScannerOpen && (
            <div className="overflow-x-auto animate-in slide-in-from-top-2 duration-300">
              <Table className="min-w-full">
                <TableHead className="bg-white">
                  <TableRow className="border-b border-slate-100">
                    <TableHeaderCell className="text-slate-400 font-bold py-3 px-6">Ativo</TableHeaderCell>
                    <TableHeaderCell className="text-slate-600 font-bold py-3 px-6">Squeeze</TableHeaderCell>
                    <TableHeaderCell className="text-slate-600 font-bold py-3 px-6">Qullamaggie Status</TableHeaderCell>
                    <TableHeaderCell className="text-slate-600 font-bold text-right py-3 px-6">Momentum 60d</TableHeaderCell>
                    <TableHeaderCell className="text-slate-600 font-bold text-center py-3 px-6">Tendência</TableHeaderCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {scanData.map((item, idx) => (
                    <TableRow key={idx} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                      <TableCell className="py-4 px-6">
                        <div className="flex flex-col">
                          <span className="font-extrabold text-slate-900 text-base">{item.ticker}</span>
                          <div className="flex gap-1 mt-1">
                            {item.is_ep && <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-1.5 py-0.5 rounded">EP</span>}
                            {item.is_parabolic && <span className="bg-red-100 text-red-700 text-[10px] font-bold px-1.5 py-0.5 rounded">EXAUSTÃO</span>}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell className="py-4 px-6">
                        {item.squeeze ? (
                          <span className="bg-emerald-100 text-emerald-700 text-xs font-bold px-2 py-1 rounded-md border border-emerald-200 animate-pulse">
                            ATIVO
                          </span>
                        ) : (
                          <span className="text-slate-400 font-medium text-sm">Inativo</span>
                        )}
                      </TableCell>
                      <TableCell className="py-4 px-6">
                        <span className={`text-xs font-bold px-2 py-1 rounded-md border ${
                          item.qullamaggie_status.includes("BREAKOUT") 
                            ? 'bg-orange-50 text-orange-600 border-orange-200'
                            : 'bg-slate-100 text-slate-600 border-slate-200'
                        }`}>
                          {item.qullamaggie_status}
                        </span>
                      </TableCell>
                      <TableCell className="text-right py-4 px-6 font-bold">
                        <span className={item.momentum_60d > 12 ? 'text-emerald-600' : 'text-slate-600'}>
                          {item.momentum_60d}%
                        </span>
                      </TableCell>
                      <TableCell className="text-center py-4 px-6">
                        <span className={`text-xs font-bold px-2 py-1 rounded-md ${
                          item.direction === 'BULLISH' ? 'text-emerald-600 bg-emerald-50' : 'text-red-600 bg-red-50'
                        }`}>
                          {item.direction}
                        </span>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </Card>
      )}

      {data && !scanLoading && (
        <>
          {/* Volatilidade & Squeeze */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-4">
            <Card className={`relative overflow-hidden rounded-2xl shadow-sm p-8 text-center flex flex-col items-center justify-center border-2 transition-all ${
              data.squeeze_on ? 'bg-emerald-50 border-emerald-400' : 'bg-white border-slate-200'
            }`}>
              <span className={`text-sm font-bold uppercase tracking-wider mb-4 ${data.squeeze_on ? 'text-emerald-800' : 'text-slate-500'}`}>Status Squeeze</span>
              
              {data.squeeze_on ? (
                 <div className="bg-emerald-500 text-white font-extrabold text-2xl px-6 py-3 rounded-xl shadow-lg shadow-emerald-500/30 animate-pulse flex items-center gap-2">
                   <Target size={28} /> SQUEEZE ATIVO
                 </div>
              ) : (
                 <div className="bg-slate-100 text-slate-500 font-extrabold text-xl px-6 py-3 rounded-xl border border-slate-200">
                   SEM SQUEEZE
                 </div>
              )}
              
              <p className={`text-sm mt-6 font-medium ${data.squeeze_on ? 'text-emerald-700' : 'text-slate-400'}`}>
                {data.squeeze_on ? 'As Bandas de Bollinger entraram nos Canais de Keltner. Possível movimento explosivo iminente.' : 'Bandas de Bollinger fora dos Canais de Keltner.'}
              </p>
            </Card>
            
            <Card className="bg-white border-slate-200 rounded-2xl shadow-sm flex flex-col items-center justify-center p-8 text-center">
              <span className="text-slate-500 font-bold mb-4 uppercase tracking-wider text-sm">Volatilidade (20d)</span>
              <div className="flex items-end gap-1">
                <span className="text-5xl font-extrabold text-slate-900">
                  {data.hv20 !== undefined ? (data.hv20).toFixed(2) : '-'}
                </span>
                <span className="text-2xl font-bold text-slate-400 mb-1">%</span>
              </div>
              <div className="mt-6 flex items-center gap-2 text-sm font-bold px-3 py-1 bg-slate-100 rounded-lg text-slate-600 border border-slate-200">
                Curto Prazo
              </div>
            </Card>

            <Card className="bg-white border-slate-200 rounded-2xl shadow-sm flex flex-col items-center justify-center p-8 text-center relative overflow-hidden">
              <div className="absolute right-0 top-0 p-4 opacity-10">
                 {data.direction === 'BULLISH' ? <MoveUpRight size={80} className="text-emerald-500" /> : <MoveDownRight size={80} className="text-red-500" />}
              </div>
              <span className="text-slate-500 font-bold mb-4 uppercase tracking-wider text-sm relative z-10">Volatilidade (50d)</span>
              <div className="flex items-end gap-1 relative z-10">
                <span className="text-5xl font-extrabold text-slate-900">
                  {data.hv50 !== undefined ? (data.hv50).toFixed(2) : '-'}
                </span>
                <span className="text-2xl font-bold text-slate-400 mb-1">%</span>
              </div>
              <div className="mt-6 flex items-center gap-2 text-sm font-bold relative z-10">
                Tendência: 
                <span className={data.direction === 'BULLISH' ? 'text-emerald-600' : 'text-red-500'}>
                  {data.direction}
                </span>
              </div>
            </Card>
          </div>

          {/* Qullamaggie Breakout Engine */}
          {data.qullamaggie && (
            <div className="mt-12 pt-8 border-t border-slate-200">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 bg-orange-100 text-orange-600 rounded-lg">
                  <Flame size={24} />
                </div>
                <div>
                  <h2 className="text-xl font-extrabold text-slate-900">Qullamaggie Setups</h2>
                  <p className="text-sm font-medium text-slate-500">Rastreio de anomalias de Momentum e Breakouts</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                
                {/* Breakout */}
                <Card className={`rounded-2xl shadow-sm p-6 border-2 transition-all ${
                  data.qullamaggie.breakout.active ? 'bg-orange-50 border-orange-400' : 'bg-white border-slate-200'
                }`}>
                  <div className="flex justify-between items-start mb-4">
                    <span className="text-slate-500 font-bold uppercase tracking-wider text-sm">Breakout (Bandeira)</span>
                    {data.qullamaggie.breakout.active && <span className="flex h-3 w-3"><span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-orange-400 opacity-75"></span><span className="relative inline-flex rounded-full h-3 w-3 bg-orange-500"></span></span>}
                  </div>
                  <div className={`text-xl font-extrabold mb-2 ${data.qullamaggie.breakout.active ? 'text-orange-600' : 'text-slate-700'}`}>
                    {data.qullamaggie.breakout.status}
                  </div>
                  <div className="text-sm font-bold text-slate-500 mb-4 bg-white/60 p-2 rounded-lg inline-block border border-slate-100">
                    Momentum (60d): <span className={data.qullamaggie.momentum_60d > 12 ? 'text-emerald-600' : 'text-slate-600'}>{data.qullamaggie.momentum_60d}%</span>
                  </div>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed">
                    Mede uma tendência prévia de alta + consolidação lateral. Gatilho ativado quando há rompimento da máxima de 10/20 dias com volume alto.
                  </p>
                </Card>

                {/* Episodic Pivot */}
                <Card className={`rounded-2xl shadow-sm p-6 border-2 transition-all ${
                  data.qullamaggie.episodic_pivot.active ? 'bg-emerald-50 border-emerald-400' : 'bg-white border-slate-200'
                }`}>
                  <div className="flex justify-between items-start mb-4">
                    <span className="text-slate-500 font-bold uppercase tracking-wider text-sm">Episodic Pivot (EP)</span>
                    {data.qullamaggie.episodic_pivot.active && <ChevronUp className="text-emerald-500" />}
                  </div>
                  <div className={`text-xl font-extrabold mb-2 ${data.qullamaggie.episodic_pivot.active ? 'text-emerald-600' : 'text-slate-700'}`}>
                    {data.qullamaggie.episodic_pivot.active ? 'ATIVADO' : 'INATIVO'}
                  </div>
                  <div className="text-sm font-bold text-slate-500 mb-4 bg-white/60 p-2 rounded-lg inline-block border border-slate-100">
                    Gap de Abertura: <span className={data.qullamaggie.episodic_pivot.gap_pct > 1.5 ? 'text-emerald-600' : 'text-slate-600'}>{data.qullamaggie.episodic_pivot.gap_pct}%</span>
                  </div>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed">
                    Gap de alta explosivo (normalmente guiado por notícia) com volume massivo (2x+ a média) e fechamento positivo no dia.
                  </p>
                </Card>

                {/* Parabolic Short */}
                <Card className={`rounded-2xl shadow-sm p-6 border-2 transition-all ${
                  data.qullamaggie.parabolic_short.active ? 'bg-red-50 border-red-400' : 'bg-white border-slate-200'
                }`}>
                  <div className="flex justify-between items-start mb-4">
                    <span className="text-slate-500 font-bold uppercase tracking-wider text-sm">Parabolic Short</span>
                    {data.qullamaggie.parabolic_short.active && <AlertCircle className="text-red-500" />}
                  </div>
                  <div className={`text-xl font-extrabold mb-2 ${data.qullamaggie.parabolic_short.active ? 'text-red-600' : 'text-slate-700'}`}>
                    {data.qullamaggie.parabolic_short.active ? 'EXAUSTÃO' : 'NORMAL'}
                  </div>
                  <div className="text-sm font-bold text-slate-500 mb-4 bg-white/60 p-2 rounded-lg inline-block border border-slate-100">
                    RSI Atual: <span className={data.qullamaggie.parabolic_short.rsi > 75 ? 'text-red-600' : 'text-slate-600'}>{data.qullamaggie.parabolic_short.rsi}</span>
                  </div>
                  <p className="text-xs text-slate-500 font-medium leading-relaxed">
                    Movimento de alta parabólico e insustentável. Ocorre quando o RSI está esticado e o preço afasta severamente das médias curtas.
                  </p>
                </Card>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  )
}