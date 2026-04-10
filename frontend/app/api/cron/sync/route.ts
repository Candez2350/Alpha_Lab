import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  // A Vercel (opcionalmente) envia um token no header Authorization
  // Você pode configurar a variável de ambiente CRON_SECRET no painel da Vercel
  // para garantir que ninguém mais acione essa rota acidentalmente
  const authHeader = request.headers.get('authorization');
  if (process.env.CRON_SECRET && authHeader !== `Bearer ${process.env.CRON_SECRET}`) {
    return NextResponse.json({ error: 'Não autorizado pela Vercel' }, { status: 401 });
  }

  try {
    // URL do seu Backend em Python no Render/Railway
    // Configure isso no painel da Vercel: BACKEND_URL="https://seu-app.onrender.com"
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    
    // A chave de segurança para liberar a extração no Python
    // Configure isso no painel da Vercel: SYNC_SECRET_KEY="sb_secret_acdz..."
    const secretKey = process.env.SYNC_SECRET_KEY;

    if (!secretKey) {
      return NextResponse.json(
        { error: 'A variável de ambiente SYNC_SECRET_KEY não foi configurada na Vercel.' }, 
        { status: 500 }
      );
    }

    console.log("⏰ Vercel Cron: Disparando o Pipeline ETL no Backend Python...");

    const response = await fetch(`${backendUrl}/api/system/sync`, {
      method: 'POST',
      headers: {
        'Authorization': secretKey,
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();

    if (!response.ok) {
      console.error("❌ Falha no Backend Python:", data);
      return NextResponse.json({ error: 'O backend Python retornou um erro.', details: data }, { status: response.status });
    }

    console.log("✅ Sincronização ETL finalizada com sucesso!");
    return NextResponse.json({ success: true, message: "Pipeline ETL concluído", backend_response: data });
    
  } catch (error: any) {
    console.error("❌ Erro de Conexão Vercel -> Render:", error.message);
    return NextResponse.json({ error: 'Erro de comunicação com o Backend', details: error.message }, { status: 500 });
  }
}
