'use client'
import { useState, useEffect } from 'react'
import { 
  Card, 
  DonutChart, 
  Table, 
  TableHead, 
  TableRow, 
  TableHeaderCell, 
  TableBody, 
  TableCell 
} from '@tremor/react'
import { Wallet, Settings2 } from 'lucide-react'
import { QuantService } from '@/services/api'
import { IPortfolio } from '@/types/quant'

export default function AlocacaoDashboard() {
  const [capital, setCapital] = useState<number>(50000);
  const [qtdBr, setQtdBr] = useState<number>(10);
  const [qtdBdr, setQtdBdr] = useState<number>(5);
  
  const [portfolio, setPortfolio] = useState<IPortfolio | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    const fetchPortfolio = async () => {
      setLoading(true);
      try {
        const data = await QuantService.getMonthlyPortfolio(capital, qtdBr, qtdBdr);
        setPortfolio(data);
      } catch (error) {
        console.error("Erro ao buscar alocação da API:", error);
      } finally {
        setLoading(false);
      }
    };
    
    const timeoutId = setTimeout(() => {
      if(capital > 0 && qtdBr > 0 && qtdBdr > 0) {
        fetchPortfolio();
      }
    }, 800);
    
    return () => clearTimeout(timeoutId);
  }, [capital, qtdBr, qtdBdr]);

  const valueFormatter = (number: number) => `R$ ${Intl.NumberFormat('pt-BR').format(number)}`;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out pb-10">
      <div className="flex flex-col gap-2">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Alocação Tática Mensal</h1>
        <p className="text-slate-500 text-lg">Otimização de portfólio de caixa zerado para Ações Nacionais e BDRs.</p>
      </div>

      {/* Painel de Inputs Customizado */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-4 opacity-5 pointer-events-none">
          <Settings2 size={120} />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative z-10">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold text-slate-700">Capital Disponível (R$)</label>
            <input 
              type="number"
              value={capital}
              onChange={(e) => setCapital(Number(e.target.value))}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl shadow-sm focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all text-slate-900 font-semibold text-lg"
              min={0}
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold text-slate-700">Quantidade Ações Nacionais</label>
            <input 
              type="number"
              value={qtdBr}
              onChange={(e) => setQtdBr(Number(e.target.value))}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl shadow-sm focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all text-slate-900 font-semibold text-lg"
              min={1}
            />
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold text-slate-700">Quantidade BDRs</label>
            <input 
              type="number"
              value={qtdBdr}
              onChange={(e) => setQtdBdr(Number(e.target.value))}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl shadow-sm focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 outline-none transition-all text-slate-900 font-semibold text-lg"
              min={1}
            />
          </div>
        </div>
      </div>

      {loading && (
         <div className="flex items-center justify-center gap-3 text-emerald-700 font-semibold bg-emerald-50 p-6 rounded-2xl border border-emerald-100 shadow-inner">
           <div className="w-6 h-6 border-4 border-emerald-600 border-t-transparent rounded-full animate-spin"></div>
           Calculando matriz de otimização em tempo real...
         </div>
      )}

      {portfolio && !loading && (
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mt-4">
          <div className="xl:col-span-1 flex flex-col gap-8">
            <Card className="bg-white border-slate-200 rounded-2xl shadow-sm">
              <h3 className="text-lg font-bold text-slate-900 mb-6">Macro-Alocação</h3>
              <DonutChart
                data={portfolio.allocations}
                category="totalVolume"
                index="ticker"
                valueFormatter={valueFormatter}
                colors={['emerald', 'teal', 'cyan', 'blue', 'indigo', 'violet', 'fuchsia']}
                className="h-64"
                showAnimation={true}
              />
            </Card>
            
            <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 flex flex-col gap-3 shadow-sm relative overflow-hidden group hover:border-emerald-300 transition-colors">
              <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform duration-500">
                 <Wallet size={100} className="text-emerald-600" />
              </div>
              <div className="flex items-center gap-3 text-emerald-800 font-bold text-lg relative z-10">
                <Wallet className="text-emerald-600" />
                Caixa Restante
              </div>
              <p className="text-emerald-900 leading-relaxed relative z-10">
                Após a execução otimizada dos lotes padrão da B3, restará <strong className="text-emerald-700 text-xl block mt-2">{valueFormatter(portfolio.remainingCash)}</strong>
              </p>
            </div>
          </div>

          <Card className="xl:col-span-2 bg-white border-slate-200 rounded-2xl shadow-sm overflow-hidden flex flex-col">
            <h3 className="text-lg font-bold text-slate-900 mb-6 px-2">Execução Tática de Lotes</h3>
            <div className="overflow-x-auto -mx-4 sm:mx-0">
              <Table className="min-w-full">
                <TableHead className="bg-slate-50 border-b border-slate-200">
                  <TableRow>
                    <TableHeaderCell className="text-slate-500 font-semibold py-4 px-4">Ticker</TableHeaderCell>
                    <TableHeaderCell className="text-slate-500 font-semibold text-right py-4 px-4">Preço</TableHeaderCell>
                    <TableHeaderCell className="text-slate-500 font-semibold text-right py-4 px-4">Cotas</TableHeaderCell>
                    <TableHeaderCell className="text-slate-500 font-semibold text-right py-4 px-4">Financeiro</TableHeaderCell>
                    <TableHeaderCell className="text-slate-500 font-semibold text-right py-4 px-4">Peso</TableHeaderCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {portfolio.allocations.map((item) => (
                    <TableRow key={item.ticker} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                      <TableCell className="font-extrabold text-slate-900 py-5 px-4">
                        <span className="bg-slate-100 px-2 py-1 rounded-md border border-slate-200">{item.ticker}</span>
                      </TableCell>
                      <TableCell className="text-right text-slate-600 py-5 px-4 font-medium">{valueFormatter(item.price)}</TableCell>
                      <TableCell className="text-right text-slate-700 font-bold py-5 px-4">{item.shares}</TableCell>
                      <TableCell className="text-right font-extrabold text-emerald-600 py-5 px-4">{valueFormatter(item.totalVolume)}</TableCell>
                      <TableCell className="text-right text-slate-500 py-5 px-4 font-medium">{(item.weight * 100).toFixed(2)}%</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </Card>
        </div>
      )}
    </div>
  )
}