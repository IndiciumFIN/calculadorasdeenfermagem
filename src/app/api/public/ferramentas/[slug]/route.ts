import { NextResponse } from 'next/server';
import { publicToolBySlug } from '@/lib/ce-tools/db';
export const dynamic = 'force-dynamic';
export async function GET(_req: Request, { params }: { params: Promise<{slug:string}> }) {
  const { slug } = await params;
  const tool = await publicToolBySlug(slug);
  if (!tool) return NextResponse.json({ error: 'Ferramenta não publicada' }, { status: 404, headers: { 'Cache-Control': 'no-store' } });
  return NextResponse.json({ tool }, { headers: { 'Cache-Control': 'public, max-age=60' } });
}
