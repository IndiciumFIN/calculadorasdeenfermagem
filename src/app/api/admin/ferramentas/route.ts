import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/ce-tools/db';
import { verifyWriteRequest, readBoundedJson, WriteBodyTooLargeError, noStore } from '@/lib/ce-tools/security';
import { parseDraftInput } from '@/lib/ce-tools/validation';
export const dynamic = 'force-dynamic';
export async function GET() {
  const ctx = await requireAdmin();
  if (!ctx) return NextResponse.json({error:'Acesso não autorizado'}, {status:403,headers:noStore});
  const {data,error} = await ctx.db.from('ce_tool_drafts').select('*').order('updated_at',{ascending:false}).limit(200);
  if (error) return NextResponse.json({error:'Falha ao consultar catálogo'}, {status:503,headers:noStore});
  return NextResponse.json({items:data||[]},{headers:noStore});
}
export async function POST(req:NextRequest) {
  const reject = verifyWriteRequest(req); if(reject) return reject;
  const ctx = await requireAdmin();
  if (!ctx || !['admin','editor'].includes(ctx.role)) return NextResponse.json({error:'Acesso não autorizado'},{status:403,headers:noStore});
  let input;
  try { input = parseDraftInput(await readBoundedJson(req)); }
  catch(e){ if(e instanceof WriteBodyTooLargeError) return NextResponse.json({error:e.message},{status:413,headers:noStore}); return NextResponse.json({error: e instanceof Error ? e.message : 'JSON inválido'},{status:400,headers:noStore}); }
  const {data,error} = await ctx.db.from('ce_tool_drafts')
    .insert({...input,lifecycle:'candidate',authored_by:ctx.user.id}).select('id,capability_key,lifecycle').single();
  if(error) return NextResponse.json({error:error.code==='23505'?'Chave/slug já existente':'Inserção não autorizada pelo contrato'}, {status:error.code==='23505'?409:422,headers:noStore});
  return NextResponse.json({item:data},{status:201,headers:noStore});
}
