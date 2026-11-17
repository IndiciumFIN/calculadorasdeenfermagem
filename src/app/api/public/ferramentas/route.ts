import { NextResponse } from 'next/server';
import { publicToolList } from '@/lib/ce-tools/db';
export const dynamic = 'force-dynamic';
export async function GET() {
  const tools = await publicToolList();
  return NextResponse.json({ items: tools, total: tools.length }, { headers: { 'Cache-Control': 'public, max-age=60' } });
}
