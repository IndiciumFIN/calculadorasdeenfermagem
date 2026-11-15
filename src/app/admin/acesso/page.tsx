'use client';
import { useState } from 'react';
import Link from 'next/link';
import { createClient } from '@/lib/supabase/client';
export default function AdminLoginPage(){
 const [email,setEmail]=useState('');const [message,setMessage]=useState('');const [busy,setBusy]=useState(false);
 return <main className="ce-tools-page"><h1>Autenticação administrativa</h1><p>Somente contas provisionadas no registro de equipe podem editar o catálogo.</p>
 <form onSubmit={async e=>{e.preventDefault();setBusy(true);setMessage('');try{const c=createClient();const {error}=await c.auth.signInWithOtp({email,options:{emailRedirectTo:window.location.origin+'/auth/callback?next=/admin/ferramentas'}});setMessage(error?'Solicitação indisponível.':'Verifique seu e-mail. O acesso ainda exige perfil autorizado.');}catch{setMessage('Serviço de autenticação não configurado.');}finally{setBusy(false);}}}>
 <label className="ce-tool-label">E-mail institucional<input type="email" autoComplete="email" value={email} required onChange={e=>setEmail(e.target.value)} maxLength={254}/></label><button disabled={busy} type="submit">Solicitar acesso por e-mail</button></form><p role="status">{message}</p><Link href="/ferramentas">Voltar ao catálogo público</Link></main>;
}
