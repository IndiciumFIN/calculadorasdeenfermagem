'use client';
import { useCallback, useEffect, useState } from 'react';
import type { ToolDraft } from '@/lib/ce-tools/types';

type FormValue = {capability_key:string;slug:string;title:string;summary:string;category:string;kind:string;risk_level:string;projection:string;payload:string;source_version:string;source_id:string};
const blank:FormValue={capability_key:'',slug:'',title:'',summary:'',category:'educacao',kind:'reference',risk_level:'medium',projection:'public',payload:JSON.stringify({summary:'',disclaimer:'Material educativo. Não substitui julgamento clínico ou protocolos institucionais.',sections:[],fields:[],referenceUrls:[],safeOffline:false,containsPatientData:false},null,2),source_version:'1.4.0',source_id:''};
export function AdminToolsManager({role}:{role:string}){
 const [items,setItems]=useState<ToolDraft[]>([]);const [loading,setLoading]=useState(true);
 const [search,setSearch]=useState('');const [editKey,setEditKey]=useState<string|null>(null);
 const [form,setForm]=useState<FormValue>(blank);const [message,setMessage]=useState('');const [busy,setBusy]=useState(false);
 const canWrite=role==='admin'||role==='editor';
 const reload=useCallback(async()=>{try{const r=await fetch('/api/admin/ferramentas',{cache:'no-store'});if(!r.ok)throw new Error('Falha de autorização');const j=await r.json();setItems(j.items||[]);}catch{setMessage('Não foi possível consultar o Registry. Confirme a migração e as permissões.');}finally{setLoading(false);}},[]);
 useEffect(()=>{void reload();},[reload]);
 function choose(x:ToolDraft){setEditKey(x.capability_key);setForm({capability_key:x.capability_key,slug:x.slug,title:x.title,summary:x.summary,category:x.category,kind:x.kind,risk_level:x.risk_level,projection:x.projection,payload:JSON.stringify(x.payload,null,2),source_version:String(x.provenance.source_version||''),source_id:String(x.provenance.source_id||'')});setMessage('');}
 function reset(){setEditKey(null);setForm(blank);setMessage('');}
 async function save(){setBusy(true);setMessage('');try{
   const body={capability_key:form.capability_key,slug:form.slug,title:form.title,summary:form.summary,category:form.category,kind:form.kind,risk_level:form.risk_level,projection:form.projection,payload:JSON.parse(form.payload),provenance:{source_version:form.source_version,source_id:form.source_id}};
   const url=editKey?'/api/admin/ferramentas/'+encodeURIComponent(editKey):'/api/admin/ferramentas';const r=await fetch(url,{method:editKey?'PATCH':'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});const json=await r.json();if(!r.ok)throw new Error(json.error||'Falha ao salvar');setMessage(editKey?'Rascunho atualizado.':'Candidato registrado; não publicado.');await reload();
  }catch(e){setMessage(e instanceof Error?e.message:'Erro inesperado');}finally{setBusy(false);}}
 async function submit(x:ToolDraft){if(!confirm(`Enviar ${x.title} para revisão? Não será publicado.`))return;setBusy(true);setMessage('');try{const r=await fetch('/api/admin/ferramentas/'+encodeURIComponent(x.capability_key)+'/enviar-revisao',{method:'POST',headers:{'content-type':'application/json'},body:'{}'});const data=await r.json();if(!r.ok)throw new Error(data.error);setMessage('Enviado à revisão. Publicação exige Kernel e evidências.');await reload();}catch(e){setMessage(e instanceof Error?e.message:'Falha');}finally{setBusy(false);}}
 const visible=items.filter(x=>(x.title+' '+x.category+' '+x.capability_key).toLocaleLowerCase('pt-BR').includes(search.toLocaleLowerCase('pt-BR')));
 const input=(field:keyof FormValue,label:string,opts?:string[])=> <label className="ce-tool-label" key={field}>{label}{opts?<select value={form[field]} onChange={e=>setForm(f=>({...f,[field]:e.target.value}))}>{opts.map(o=><option key={o} value={o}>{o}</option>)}</select>:<input value={form[field]} maxLength={field==='summary'?900:160} disabled={!!editKey && field==='capability_key'} onChange={e=>setForm(f=>({...f,[field]:e.target.value}))}/>}</label>;
 return <div className="ce-admin-layout"><section aria-label="Lista de ferramentas"><div className="ce-admin-bar"><label>Filtrar catálogo<input aria-label="Filtrar catálogo" value={search} onChange={e=>setSearch(e.target.value)}/></label><button type="button" onClick={reset}>Novo candidato</button></div><p>{loading?'Carregando...':`${visible.length} registros encontrados`}</p><div className="ce-admin-list">{visible.map(x=><article key={x.id} className="ce-tools-card"><h2>{x.title}</h2><p>{x.summary}</p><small>{x.capability_key} · {x.lifecycle} · {x.projection} · risco {x.risk_level}</small><div className="ce-tool-actions"><button type="button" onClick={()=>choose(x)}>Ver {canWrite&&x.lifecycle!=='in_review'?' / editar':''}</button>{canWrite&&x.lifecycle!=='in_review'&&x.lifecycle!=='rejected'&&<button type="button" disabled={busy} onClick={()=>submit(x)}>Enviar à revisão</button>}</div></article>)}</div></section>
 <section className="ce-admin-editor" aria-label="Editor de rascunho"><h2>{editKey?'Rascunho: '+editKey:'Novo candidato'}</h2><p>As alterações somente entram no Registry. Sem deploy, publicação ou mudança de direitos.</p><fieldset disabled={!canWrite||busy}>
 {input('capability_key','Chave técnica (o Kernel atribui o ID definitivo)')}{input('slug','Slug público')}{input('title','Título')}
 <label className="ce-tool-label">Resumo<textarea rows={3} maxLength={900} value={form.summary} onChange={e=>setForm(f=>({...f,summary:e.target.value}))}/></label>
 {input('category','Área',['protecao','carreiras','educacao','gestao','saude-ocupacional','pesquisa','comunicacao','comunidade','clinica-educativa'])}
 {input('kind','Tipo de interface',['reference','checklist','planner','guided-form'])}
 {input('risk_level','Nível de risco',['low','medium','high','critical'])}
 {input('projection','Destino',['public','subscriber','institutional'])}
 {input('source_version','Versão da pesquisa de origem')}{input('source_id','ID da pesquisa de origem')}
 <label className="ce-tool-label">Payload JSON controlado<textarea rows={15} value={form.payload} onChange={e=>setForm(f=>({...f,payload:e.target.value}))} spellCheck={false}/></label>
 <button type="button" onClick={()=>void save()}>Salvar {editKey?'rascunho':'candidato'}</button></fieldset>
 <p role="status" aria-live="polite">{message}</p></section></div>;
}
