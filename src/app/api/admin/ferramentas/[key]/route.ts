import { NextRequest, NextResponse } from 'next/server';
import { requireAdmin } from '@/lib/ce-tools/db';
import { verifyWriteRequest, noStore } from '@/lib/ce-tools/security';
import { parseDraftInput } from '@/lib/ce-tools/validation';
export const dynamic = 'force-dynamic';
export async function PATCH(req:NextRequest,{params}:{params:Promise<{key:string}>}) {
  const reject=verifyWriteRequest(req);if(reject)return reject;
  const ctx=await requireAdmin();if(!ctx)return NextResponse.json({error:'Não autorizado'},{status:403,headers:noStore});
  const {key}=await params;
  if(!/^[a-z][a-z0-9_.-]{0,99}$/.test(key))return NextResponse.json({error:'Chave inválida'},{status:400,headers:noStore});
  let input;
  try{input=parseDraftInput(await req.json());}catch(e){return NextResponse.json({error:e instanceof Error?e.message:'Inválido'},{status:400,headers:noStore});}
  if(input.capability_key!==key)return NextResponse.json({error:'Identidade canônica imutável'},{status:409,headers:noStore});
  const {data,error}=await ctx.db.from('ce_tool_drafts').update({...input,lifecycle:'draft'})
    .eq('capability_key',key).in('lifecycle',['candidate','draft']).select('id,capability_key,lifecycle').maybeSingle();
  if(error||!data)return NextResponse.json({error:'Item não editável ou inexistente'},{status:409,headers:noStore});
  return NextResponse.json({item:data},{headers:noStore});
}
