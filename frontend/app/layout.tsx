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
              <span className="font-extrabold text-2xl hidden lg:block text-slate-900 tracking-tight">
                Alpha <span className="text-emerald-600">Lab</span>
              </span>
              <span className="font-extrabold text-2xl lg:hidden text-emerald-600">AL</span>
            </div>
            
            <nav className="flex flex-col gap-2 w-full">
              <Link href="/" className="flex items-center gap-4 text-slate-600 hover:text-emerald-700 hover:bg-emerald-50 rounded-lg p-3 transition-all lg:px-4 group font-medium">
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
