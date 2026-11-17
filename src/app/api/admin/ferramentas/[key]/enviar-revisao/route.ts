import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/ce-tools/db';
import { verifyWriteRequest, noStore } from '@/lib/ce-tools/security';
export const dynamic='force-dynamic';
export async function POST(req:NextRequest,{params}:{params:Promise<{key:string}>}){
  const reject=verifyWriteRequest(req); if(reject)return reject;
  const ctx=await requireAdmin();if(!ctx || !['admin','editor'].includes(ctx.role))return NextResponse.json({error:'Não autorizado'},{status:403,headers:noStore});
  const {key}=await params;
  if(!/^[a-z][a-z0-9_.-]{0,99}$/.test(key))return NextResponse.json({error:'Chave inválida'},{status:400,headers:noStore});
  const {data,error}=await ctx.db.from('ce_tool_drafts').update({lifecycle:'in_review'})
    .eq('capability_key',key).in('lifecycle',['candidate','draft'])
    .select('capability_key,lifecycle').maybeSingle();
  if(error||!data)return NextResponse.json({error:'Transição bloqueada pelo Kernel/contrato'},{status:409,headers:noStore});
  return NextResponse.json({item:data,notice:'Enviado à revisão; não publicado'},{headers:noStore});
}
