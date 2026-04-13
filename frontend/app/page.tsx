'use client'
import Link from 'next/link'
import { Card } from '@tremor/react'
import { PieChart, ArrowLeftRight, Activity, Sigma, ArrowRight, TrendingUp, ShieldAlert, Sparkles } from 'lucide-react'

export default function Home() {
  return (
    <div className="space-y-12 animate-in fade-in slide-in-from-bottom-4 duration-700 ease-out pb-10">
      {/* Header Section */}
      <div className="flex flex-col gap-4 text-center lg:text-left">
        <h1 className="text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight">
          Bem-vindo ao <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-teal-500">Alpha Lab</span>
        </h1>
        <p className="text-slate-500 text-lg lg:text-xl max-w-3xl leading-relaxed">
          O seu Terminal de Inteligência Quantitativa. Tome decisões no mercado financeiro baseadas em dados reais, modelos matemáticos e setups com alta probabilidade estatística.
        </p>
      </div>

      {/* Highlights / Features Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Alocação Tática */}
        <Link href="/alocacao" className="group">
          <Card className="h-full bg-white border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-all p-8 flex flex-col gap-4 relative overflow-hidden">
            <div className="absolute -right-6 -bottom-6 opacity-5 group-hover:scale-110 transition-transform duration-500 pointer-events-none">
              <PieChart size={140} />
            </div>
            <div className="p-3 bg-blue-50 text-blue-600 rounded-xl w-fit">
              <PieChart size={28} />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Alocação Tática</h2>
            <p className="text-slate-500 font-medium leading-relaxed flex-1">
              Otimize sua carteira de forma inteligente. Utilize nosso modelo matemático de "Caixa Zerado" para distribuir capital balanceando ações nacionais e BDRs de forma eficiente.
            </p>
            <div className="flex items-center gap-2 text-blue-600 font-bold mt-2 group-hover:translate-x-2 transition-transform">
              Acessar Módulo <ArrowRight size={18} />
            </div>
          </Card>
        </Link>

        {/* Long & Short */}
        <Link href="/arbitragem" className="group">
          <Card className="h-full bg-white border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-all p-8 flex flex-col gap-4 relative overflow-hidden">
            <div className="absolute -right-6 -bottom-6 opacity-5 group-hover:scale-110 transition-transform duration-500 pointer-events-none">
              <ArrowLeftRight size={140} />
            </div>
            <div className="p-3 bg-purple-50 text-purple-600 rounded-xl w-fit">
              <ArrowLeftRight size={28} />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Long & Short</h2>
            <p className="text-slate-500 font-medium leading-relaxed flex-1">
              Encontre distorções no mercado. Scanner estatístico focado em identificar pares de ativos cointegrados (Arbitragem) para operações com neutralidade financeira.
            </p>
            <div className="flex items-center gap-2 text-purple-600 font-bold mt-2 group-hover:translate-x-2 transition-transform">
              Acessar Módulo <ArrowRight size={18} />
            </div>
          </Card>
        </Link>

        {/* Radar Volatilidade */}
        <Link href="/opcoes" className="group">
          <Card className="h-full bg-white border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-all p-8 flex flex-col gap-4 relative overflow-hidden">
            <div className="absolute -right-6 -bottom-6 opacity-5 group-hover:scale-110 transition-transform duration-500 pointer-events-none">
              <Activity size={140} />
            </div>
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-xl w-fit">
              <Activity size={28} />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Radar Volatilidade</h2>
            <p className="text-slate-500 font-medium leading-relaxed flex-1">
              Antecipe movimentos explosivos. Monitoramento avançado do IBRX-100 buscando compressões de volatilidade (Squeeze) e setups Qullamaggie engatilhados.
            </p>
            <div className="flex items-center gap-2 text-emerald-600 font-bold mt-2 group-hover:translate-x-2 transition-transform">
              Acessar Módulo <ArrowRight size={18} />
            </div>
          </Card>
        </Link>

        {/* Seleção Alpha */}
        <Link href="/alpha" className="group">
          <Card className="h-full bg-white border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-all p-8 flex flex-col gap-4 relative overflow-hidden">
            <div className="absolute -right-6 -bottom-6 opacity-5 group-hover:scale-110 transition-transform duration-500 pointer-events-none">
              <Sigma size={140} />
            </div>
            <div className="p-3 bg-orange-50 text-orange-600 rounded-xl w-fit">
              <Sigma size={28} />
            </div>
            <h2 className="text-2xl font-bold text-slate-900">Seleção Alpha</h2>
            <p className="text-slate-500 font-medium leading-relaxed flex-1">
              Stock picking de alta performance. Aplique os filtros consagrados da Magic Formula aliados ao Momentum Setorial para montar carteiras vencedoras a longo prazo.
            </p>
            <div className="flex items-center gap-2 text-orange-600 font-bold mt-2 group-hover:translate-x-2 transition-transform">
              Acessar Módulo <ArrowRight size={18} />
            </div>
          </Card>
        </Link>

      </div>

      {/* Info Footer */}
      <div className="bg-slate-900 rounded-2xl p-8 lg:p-10 flex flex-col md:flex-row items-center justify-between gap-8 shadow-lg mt-8 relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] pointer-events-none"></div>
        <div className="flex flex-col gap-3 relative z-10 text-center md:text-left">
          <div className="flex items-center justify-center md:justify-start gap-2 text-emerald-400 font-bold text-sm tracking-widest uppercase">
            <Sparkles size={16} /> Processamento em Batch
          </div>
          <h3 className="text-2xl font-bold text-white">Análise diária e automatizada</h3>
          <p className="text-slate-400 font-medium max-w-xl">
            Nossos modelos rodam em background diretamente nos servidores, lendo milhares de dados da B3 para garantir que suas análises sejam entregues em milissegundos, com risco zero de bloqueio de API.
          </p>
        </div>
        <div className="flex gap-4 relative z-10">
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex flex-col items-center justify-center min-w-[120px]">
            <TrendingUp size={24} className="text-emerald-500 mb-2" />
            <span className="text-slate-300 font-medium text-sm">Foco em</span>
            <span className="text-white font-bold">Alta Renda</span>
          </div>
          <div className="bg-slate-800 border border-slate-700 rounded-xl p-4 flex flex-col items-center justify-center min-w-[120px]">
            <ShieldAlert size={24} className="text-blue-500 mb-2" />
            <span className="text-slate-300 font-medium text-sm">Modelos</span>
            <span className="text-white font-bold">Quantitativos</span>
          </div>
        </div>
      </div>
    </div>
  )
}
