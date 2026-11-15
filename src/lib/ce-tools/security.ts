import { NextRequest, NextResponse } from 'next/server';

/** Reject cross-origin state changes even if a cookie is present. */
export function verifyWriteRequest(req: NextRequest): NextResponse | null {
  const origin = req.headers.get('origin');
  const host = req.headers.get('host');
  if (!origin || !host) return NextResponse.json({ error: 'Origem não verificada' }, { status: 403 });
  try {
    const o = new URL(origin);
    if (!['https:', 'http:'].includes(o.protocol) || o.host !== host) throw new Error('origin');
  } catch {
    return NextResponse.json({ error: 'Origem incompatível' }, { status: 403 });
  }
  if (!(req.headers.get('content-type') || '').startsWith('application/json')) return NextResponse.json({ error: 'JSON obrigatório' }, { status: 415 });
  const contentLength = Number(req.headers.get('content-length') || 0);
  if (contentLength > 40_000) return NextResponse.json({ error: 'Payload grande demais' }, { status: 413 });
  return null;
}
export const noStore = { 'Cache-Control': 'no-store, max-age=0' };
