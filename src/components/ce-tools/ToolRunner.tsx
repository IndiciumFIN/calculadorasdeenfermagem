'use client';
import { useState } from 'react';
import type { ToolRelease, ToolField } from '@/lib/ce-tools/types';

/** Public educational runner: no clinical/patient data or server-side submissions. */
export function ToolRunner({ tool }: { tool: ToolRelease }) {
  const [data, setData] = useState<Record<string,string|boolean>>({});
  const [finished, setFinished] = useState(false);
  const fields=tool.payload?.fields ?? [];
  const completed=fields.filter(f=>f.type==='checkbox'?data[f.key]===true:String(data[f.key]||'').trim().length>0).length;
  const progress=fields.length?Math.round((completed/fields.length)*100):100;
  const fill=(key:string,val:string|boolean)=>{setData(s=>({...s,[key]:val}));setFinished(false);};
  const fieldControl=(f:ToolField)=>{
    const value=data[f.key]??'';
    const common={id:f.key,name:f.key};
    switch(f.type){
      case 'checkbox':return <label className="ce-tool-check"><input {...common} type="checkbox" checked={value===true} onChange={e=>fill(f.key,e.target.checked)}/>{f.label}</label>;
      case 'textarea':return <label className="ce-tool-label" htmlFor={f.key}>{f.label}<textarea {...common} value={String(value)} onChange={e=>fill(f.key,e.target.value)} rows={3} maxLength={1200} placeholder="Sem dados pessoais ou de pacientes"/></label>;
      case 'select':return <label className="ce-tool-label" htmlFor={f.key}>{f.label}<select {...common} value={String(value)} onChange={e=>fill(f.key,e.target.value)}><option value="">Selecione</option>{f.options?.map(x=><option key={x.value} value={x.value}>{x.label}</option>)}</select></label>;
      default:return <label className="ce-tool-label" htmlFor={f.key}>{f.label}<input {...common} type={f.type==='date'?'date':'text'} value={String(value)} onChange={e=>fill(f.key,e.target.value)} maxLength={220}/></label>;
    }
  };
  return <section className="ce-tool-runner" aria-label="Ferramenta educativa">
    <p className="ce-tool-warning" role="note">{tool.payload.disclaimer || 'Ferramenta educativa. Não substitui avaliação profissional ou normas institucionais.'}</p>
    {tool.payload.sections.map((s,i)=><section key={i}><h2>{s.heading}</h2><p>{s.body}</p></section>)}
    {fields.length>0&&<>
      <div className="ce-tool-progress"><span>Progresso: {completed}/{fields.length}</span><progress max={100} value={progress} aria-label="Progresso do preenchimento">{progress}%</progress></div>
      <form onSubmit={e=>{e.preventDefault();const pending=fields.filter(f=>f.required && (f.type==='checkbox'?data[f.key]!==true:!String(data[f.key]||'').trim()));if(!pending.length)setFinished(true);}}>
        {fields.map(f=><div key={f.key} className="ce-tool-field">{fieldControl(f)}</div>)}
        <button type="submit">Concluir atividade local</button> <button type="button" onClick={()=>{setData({});setFinished(false);}}>Recomeçar</button>
      </form>
      <p role="status" aria-live="polite">{finished?'Atividade concluída neste dispositivo. Nenhum dado foi enviado ou salvo.':''}</p>
    </>}
    {tool.payload.referenceUrls?.length>0&&<aside><h2>Referências</h2><ul>{tool.payload.referenceUrls.filter(u=>/^https:\/\//.test(u)).map(u=><li key={u}><a target="_blank" rel="noopener noreferrer" href={u}>{new URL(u).hostname}</a></li>)}</ul></aside>}
    <small>Versão {tool.version} · WO: {tool.kernel_wo_id} · Publicada em {new Date(tool.published_at).toLocaleDateString('pt-BR')}</small>
  </section>;
}
