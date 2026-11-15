import { NextRequest, NextResponse } from 'next/server';
import { createServerClient } from '@supabase/ssr';
export async function GET(request:NextRequest){
  const url=new URL(request.url);const code=url.searchParams.get('code');
  const next=url.searchParams.get('next');
  const destination=next?.startsWith('/')&&!next.startsWith('//')?next:'/admin/ferramentas';
  const response=NextResponse.redirect(new URL(code?destination:'/admin/acesso',request.url));
  if(!code)return response;
  const supaUrl=process.env.NEXT_PUBLIC_SUPABASE_URL,anon=process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if(!supaUrl||!anon)return NextResponse.redirect(new URL('/admin/acesso',request.url));
  const supabase=createServerClient(supaUrl,anon,{cookies:{getAll(){return request.cookies.getAll();},setAll(cookiesToSet){cookiesToSet.forEach(c=>{request.cookies.set(c.name,c.value);response.cookies.set(c.name,c.value,c.options);});}}});
  const {error}=await supabase.auth.exchangeCodeForSession(code);
  if(error)return NextResponse.redirect(new URL('/admin/acesso',request.url));
  return response;
}
