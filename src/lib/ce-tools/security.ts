import { NextRequest, NextResponse } from 'next/server';

/** Reject cross-origin state changes even if a cookie is present. */
export function verifyWriteRequest(req: NextRequest): NextResponse | null {
  const origin = req.headers.get('origin');
  const host = req.headers.get('host');
  if (!origin || !host) return NextResponse.json({ error: 'Origem não verificada' }, { status: 403 });
  try {
    const o = new URL(origin);
    if (!['https:', 'http:'].includes(o.protocol) || o.host !== host || o.username || o.password) throw new Error('origin');
    // Production writes must originate over HTTPS; never trust a matching Host alone.
    if (process.env.NODE_ENV === 'production' && o.protocol !== 'https:') throw new Error('insecure-origin');
  } catch {
    return NextResponse.json({ error: 'Origem incompatível' }, { status: 403 });
  }
  if (!(req.headers.get('content-type') || '').startsWith('application/json')) return NextResponse.json({ error: 'JSON obrigatório' }, { status: 415 });
  const rawLength = req.headers.get('content-length');
  // A missing length is allowed for chunked requests, but malformed values fail closed.
  if (rawLength !== null && !/^(0|[1-9][0-9]*)$/.test(rawLength))
    return NextResponse.json({ error: 'Content-Length inválido' }, { status: 400 });
  const contentLength = rawLength === null ? 0 : Number(rawLength);
  if (!Number.isSafeInteger(contentLength) || contentLength > 40_000)
    return NextResponse.json({ error: 'Payload grande demais' }, { status: 413 });
  return null;
}
export const noStore = { 'Cache-Control': 'no-store, max-age=0' };
