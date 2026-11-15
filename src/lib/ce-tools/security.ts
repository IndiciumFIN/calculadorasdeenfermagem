import { NextRequest, NextResponse } from 'next/server';

export const MAX_WRITE_BODY_BYTES = 40_000;

/** Reject cross-origin state changes even if a cookie is present. */
export function verifyWriteRequest(req: NextRequest): NextResponse | null {
  const origin = req.headers.get('origin');
  const host = req.headers.get('host');
  if (!origin || !host) return NextResponse.json({ error: 'Origem não verificada' }, { status: 403 });
  try {
    const o = new URL(origin);
    if (!['https:', 'http:'].includes(o.protocol) || o.host !== host || o.username || o.password) throw new Error('origin');
    if (process.env.NODE_ENV === 'production' && o.protocol !== 'https:') throw new Error('insecure-origin');
  } catch {
    return NextResponse.json({ error: 'Origem incompatível' }, { status: 403 });
  }
  if (!/^application\/json(?:\s*;\s*charset\s*=\s*"?utf-8"?\s*)?$/i.test(req.headers.get('content-type') || '')) return NextResponse.json({ error: 'JSON obrigatório (UTF-8)' }, { status: 415 });
  const rawLength = req.headers.get('content-length');
  if (rawLength !== null && !/^(0|[1-9][0-9]*)$/.test(rawLength))
    return NextResponse.json({ error: 'Content-Length inválido' }, { status: 400 });
  const contentLength = rawLength === null ? 0 : Number(rawLength);
  if (!Number.isSafeInteger(contentLength) || contentLength > MAX_WRITE_BODY_BYTES)
    return NextResponse.json({ error: 'Payload grande demais' }, { status: 413 });
  return null;
}

export class WriteBodyTooLargeError extends Error {
  constructor() { super('Payload grande demais'); this.name = 'WriteBodyTooLargeError'; }
}

/** Enforce the byte limit on the actual stream, even for chunked or dishonest Content-Length. */
export async function readBoundedJson(req: NextRequest): Promise<unknown> {
  if (!req.body) throw new SyntaxError('JSON obrigatório');
  const reader = req.body.getReader();
  const chunks: Uint8Array[] = [];
  let total = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      total += value.byteLength;
      if (total > MAX_WRITE_BODY_BYTES) {
        void reader.cancel().catch(() => undefined);
        throw new WriteBodyTooLargeError();
      }
      chunks.push(value);
    }
  } finally {
    reader.releaseLock();
  }
  const bytes = new Uint8Array(total);
  let offset = 0;
  for (const chunk of chunks) { bytes.set(chunk, offset); offset += chunk.byteLength; }
  return JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(bytes));
}

export const noStore = { 'Cache-Control': 'no-store, max-age=0' };
