import Link from 'next/link';
import { notFound } from 'next/navigation';
import { publicToolBySlug } from '@/lib/ce-tools/db';
import { ToolRunner } from '@/components/ce-tools/ToolRunner';
export const dynamic='force-dynamic';
export default async function PublicToolPage({params}:{params:Promise<{slug:string}>}){
  const {slug}=await params;
  const tool=await publicToolBySlug(slug); if(!tool)notFound();
  return <main className="ce-tools-page"><nav aria-label="Navegação"><Link href="/ferramentas">Todas as ferramentas</Link></nav><h1>{tool.title}</h1><p>{tool.summary}</p><ToolRunner tool={tool}/></main>;
}
