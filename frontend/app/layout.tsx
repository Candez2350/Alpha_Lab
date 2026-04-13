import './globals.css'
import { Providers } from './providers'
import { Activity, PieChart, ArrowLeftRight, Sigma } from 'lucide-react'
import Link from 'next/link'

export const metadata = {
  title: 'Alpha Lab',
  description: 'Terminal de Inteligência Quantitativa',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <body className="bg-slate-50 text-slate-900 flex flex-col md:flex-row h-screen overflow-hidden antialiased">
        <Providers>
          {/* Sidebar Fixa / Bottom Nav Mobile */}
          <aside className="w-full md:w-20 lg:w-64 bg-white border-t md:border-t-0 md:border-r border-slate-200 shadow-sm flex flex-row md:flex-col items-center md:items-start py-3 md:py-8 px-2 md:px-4 flex-shrink-0 z-10 relative order-last md:order-first justify-around md:justify-start">
            <div className="hidden md:flex mb-12 lg:px-4 w-full justify-center lg:justify-start">
              <Link href="/">
                <span className="font-extrabold text-3xl hidden lg:block tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-emerald-800 to-emerald-500 drop-shadow-sm hover:opacity-80 transition-opacity cursor-pointer">
                  Alpha Lab
                </span>
                <span className="font-extrabold text-2xl lg:hidden text-transparent bg-clip-text bg-gradient-to-br from-emerald-600 to-emerald-400">AL</span>
              </Link>
            </div>
            
            <nav className="flex flex-row md:flex-col gap-1 md:gap-2 w-full justify-around md:justify-start">
              <Link href="/" className="flex flex-col md:flex-row items-center gap-1 md:gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-2 md:p-3 transition-all lg:px-4 group font-medium text-[10px] md:text-base">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                <span className="hidden lg:block">Início</span>
              </Link>
              <Link href="/alocacao" className="flex flex-col md:flex-row items-center gap-1 md:gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-2 md:p-3 transition-all lg:px-4 group font-medium text-[10px] md:text-base">
                <PieChart size={22} className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600" />
                <span className="hidden lg:block">Alocação Tática</span>
              </Link>
              <Link href="/arbitragem" className="flex flex-col md:flex-row items-center gap-1 md:gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-2 md:p-3 transition-all lg:px-4 group font-medium text-[10px] md:text-base">
                <ArrowLeftRight size={22} className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600" />
                <span className="hidden lg:block">Long & Short</span>
              </Link>
              <Link href="/opcoes" className="flex flex-col md:flex-row items-center gap-1 md:gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-2 md:p-3 transition-all lg:px-4 group font-medium text-[10px] md:text-base">
                <Activity size={22} className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600" />
                <span className="hidden lg:block">Radar Volatilidade</span>
              </Link>
              <Link href="/alpha" className="flex flex-col md:flex-row items-center gap-1 md:gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-2 md:p-3 transition-all lg:px-4 group font-medium text-[10px] md:text-base">
                <Sigma size={22} className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600" />
                <span className="hidden lg:block">Seleção Alpha</span>
              </Link>
            </nav>
          </aside>

          {/* Área Central do Dashboard */}
          <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-12 bg-slate-50">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </Providers>
      </body>
    </html>
  )
}
