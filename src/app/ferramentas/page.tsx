import Link from 'next/link';
import { publicToolList } from '@/lib/ce-tools/db';
export const dynamic='force-dynamic';
export const metadata={title:'Ferramentas públicas | Calculadoras de Enfermagem'};
export default async function PublicToolsPage(){
  const tools=await publicToolList();
  return <main className="ce-tools-page"><div className="ce-tools-header"><Link href="/">Calculadoras de Enfermagem</Link><h1>Ferramentas públicas</h1><p>Recursos que passaram pela publicação governada. Conteúdos candidatos não são exibidos.</p></div>
    {tools.length?<section className="ce-tools-grid" aria-label="Catálogo público">{tools.map(t=><article key={t.release_id} className="ce-tools-card"><span>{t.category}</span><h2><Link href={'/ferramentas/'+t.slug}>{t.title}</Link></h2><p>{t.summary}</p><small>Versão {t.version}</small></article>)}</section>:<section role="status" className="ce-tools-empty"><h2>Catálogo em preparação</h2><p>Não há ferramentas homologadas e publicadas neste backend. As calculadoras existentes do site não são alteradas por esta implantação.</p></section>}
  </main>;
}
