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
      <body className="bg-slate-50 text-slate-900 flex h-screen overflow-hidden antialiased">
        <Providers>
          {/* Sidebar Fixa */}
          <aside className="w-20 lg:w-64 bg-white border-r border-slate-200 shadow-sm flex flex-col items-center lg:items-start py-8 px-4 flex-shrink-0 z-10 relative">
            <div className="mb-12 lg:px-4 w-full flex justify-center lg:justify-start">
              <Link href="/">
                <span className="font-extrabold text-3xl hidden lg:block tracking-tighter bg-clip-text text-transparent bg-gradient-to-r from-slate-900 via-emerald-800 to-emerald-500 drop-shadow-sm hover:opacity-80 transition-opacity cursor-pointer">
                  Alpha Lab
                </span>
                <span className="font-extrabold text-2xl lg:hidden text-transparent bg-clip-text bg-gradient-to-br from-emerald-600 to-emerald-400">AL</span>
              </Link>
            </div>
            
            <nav className="flex flex-col gap-2 w-full">
              <Link href="/" className="flex items-center gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-3 transition-all lg:px-4 group font-medium">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                <span className="hidden lg:block">Início</span>
              </Link>
              <Link href="/alocacao" className="flex items-center gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-3 transition-all lg:px-4 group font-medium">
                <PieChart size={22} className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600" />
                <span className="hidden lg:block">Alocação Tática</span>
              </Link>
              <Link href="/arbitragem" className="flex items-center gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-3 transition-all lg:px-4 group font-medium">
                <ArrowLeftRight size={22} className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600" />
                <span className="hidden lg:block">Long & Short</span>
              </Link>
              <Link href="/opcoes" className="flex items-center gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-3 transition-all lg:px-4 group font-medium">
                <Activity size={22} className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600" />
                <span className="hidden lg:block">Radar Volatilidade</span>
              </Link>
              <Link href="/alpha" className="flex items-center gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-3 transition-all lg:px-4 group font-medium">
                <Sigma size={22} className="group-hover:scale-110 transition-transform text-slate-400 group-hover:text-emerald-600" />
                <span className="hidden lg:block">Seleção Alpha</span>
              </Link>
            </nav>
          </aside>

          {/* Área Central do Dashboard */}
          <main className="flex-1 overflow-y-auto p-6 lg:p-12 bg-slate-50">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </Providers>
      </body>
    </html>
  )
}
