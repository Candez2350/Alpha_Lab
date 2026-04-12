import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Fazemos um ping na raiz da API (onde está o Status) para manter o Render acordado
    const response = await fetch(`${backendUrl}/`, {
      method: 'GET',
      headers: {
        'Cache-Control': 'no-cache' // Força não usar cache
      }
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return NextResponse.json({ success: true, timestamp: new Date().toISOString(), data });
  } catch (error: any) {
    console.error("Erro no ping do Render:", error);
    return NextResponse.json({ success: false, error: error.message }, { status: 500 });
  }
}
