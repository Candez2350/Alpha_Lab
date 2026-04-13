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
import { ListFilter, Sparkles, TrendingUp } from 'lucide-react'
import { api } from '@/services/api'

export default function AlphaDashboard() {
  const [nMf, setNMf] = useState<number>(6);
  const [nBancos, setNBancos] = useState<number>(2);
  const [nEletricas, setNEletricas] = useState<number>(2);
  
  const [mfData, setMfData] = useState<any[]>([]);
  const [momData, setMomData] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const fetchAlpha = async () => {
    setLoading(true);
    setMfData([]);
    setMomData([]);
    try {
      const response = await api.get(`/selection/magic-momentum`, {
        params: { n_mf: nMf, n_bancos: nBancos, n_eletricas: nEletricas }
      });
      if(response.data) {
        setMfData(response.data.magic_formula || []);
        setMomData(response.data.momentum || []);
      }
    } catch (error) {
      console.error("Erro ao buscar alpha:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700 ease-out pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Seleção Alpha</h1>
        <p className="text-slate-500 text-lg">Stock Picking quantitativo combinando Magic Formula e Momentum setorial.</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold text-slate-700">Tamanho M. Formula</label>
            <input 
              type="number"
              value={nMf}
              onChange={(e) => setNMf(Number(e.target.value))}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl shadow-sm focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all text-slate-900 font-semibold text-lg"
              min={1}
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold text-slate-700">Qtd. Bancos (Momentum)</label>
            <input 
              type="number"
              value={nBancos}
              onChange={(e) => setNBancos(Number(e.target.value))}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl shadow-sm focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all text-slate-900 font-semibold text-lg"
              min={0}
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold text-slate-700">Qtd. Elétricas (Momentum)</label>
            <input 
              type="number"
              value={nEletricas}
              onChange={(e) => setNEletricas(Number(e.target.value))}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl shadow-sm focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all text-slate-900 font-semibold text-lg"
              min={0}
            />
          </div>
          <button 
            onClick={fetchAlpha} 
            disabled={loading}
            className="w-full h-[52px] bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl shadow-md hover:shadow-lg hover:-translate-y-0.5 transition-all font-bold flex items-center justify-center gap-3 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <ListFilter size={20} />
            )}
            Gerar Rankings
          </button>
        </div>
      </div>

      {(mfData.length > 0 || momData.length > 0) && (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-8 mt-4">
          
          {/* Table Magic Formula */}
          {mfData.length > 0 && (
            <Card className="bg-white border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col p-0">
              <div className="px-6 py-5 border-b border-slate-100 flex items-center gap-3 bg-slate-50">
                <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
                  <Sparkles size={20} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900">Magic Formula</h3>
                  <p className="text-xs font-medium text-slate-500">Excluindo Financeiras e Utilities</p>
                </div>
              </div>
              <div className="overflow-x-auto">
                <Table className="min-w-full">
                  <TableHead className="bg-white">
                    <TableRow className="border-b border-slate-100">
                      <TableHeaderCell className="text-slate-400 font-bold py-3 px-6 w-16">#</TableHeaderCell>
                      <TableHeaderCell className="text-slate-600 font-bold py-3 px-6">Ticker</TableHeaderCell>
                      <TableHeaderCell className="text-slate-600 font-bold text-right py-3 px-6">ROIC</TableHeaderCell>
                      <TableHeaderCell className="text-slate-600 font-bold text-right py-3 px-6">Score</TableHeaderCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {mfData.map((item, idx) => (
                      <TableRow key={idx} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                        <TableCell className="font-bold text-slate-400 py-4 px-6">{idx + 1}</TableCell>
                        <TableCell className="py-4 px-6">
                          <span className="font-extrabold text-slate-900 bg-slate-100 px-2 py-1 rounded-md border border-slate-200">{item.ticker}</span>
                        </TableCell>
                        <TableCell className="text-right text-emerald-600 font-bold py-4 px-6">
                          {(item.roic * 100).toFixed(2)}%
                        </TableCell>
                        <TableCell className="text-right text-slate-500 font-bold py-4 px-6">
                          {item.magic_score}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </Card>
          )}

          {/* Table Momentum */}
          {momData.length > 0 && (
            <Card className="bg-white border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col p-0">
              <div className="px-6 py-5 border-b border-slate-100 flex items-center gap-3 bg-slate-50">
                <div className="p-2 bg-orange-100 text-orange-600 rounded-lg">
                  <TrendingUp size={20} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-slate-900">Momentum Setorial</h3>
                  <p className="text-xs font-medium text-slate-500">Tendência Combinada (12M + 3M)</p>
                </div>
              </div>
              <div className="overflow-x-auto">
                <Table className="min-w-full">
                  <TableHead className="bg-white">
                    <TableRow className="border-b border-slate-100">
                      <TableHeaderCell className="text-slate-400 font-bold py-3 px-6 w-16">Setor</TableHeaderCell>
                      <TableHeaderCell className="text-slate-600 font-bold py-3 px-6">Ticker</TableHeaderCell>
                      <TableHeaderCell className="text-slate-600 font-bold text-right py-3 px-6">Score (Momentum)</TableHeaderCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {momData.map((item, idx) => (
                      <TableRow key={idx} className="border-b border-slate-50 hover:bg-slate-50/50 transition-colors">
                        <TableCell className="py-4 px-6">
                          <span className={`text-xs font-bold px-2 py-1 rounded-md border ${
                            item.setor === 'BANCO' ? 'bg-blue-50 text-blue-700 border-blue-200' : 'bg-yellow-50 text-yellow-700 border-yellow-200'
                          }`}>
                            {item.setor}
                          </span>
                        </TableCell>
                        <TableCell className="py-4 px-6">
                          <span className="font-extrabold text-slate-900 bg-slate-100 px-2 py-1 rounded-md border border-slate-200">{item.ticker}</span>
                        </TableCell>
                        <TableCell className="text-right text-emerald-600 font-bold py-4 px-6">
                          {item.score ? item.score.toFixed(2) : "0.00"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </Card>
          )}

        </div>
      )}
    </div>
  )
}