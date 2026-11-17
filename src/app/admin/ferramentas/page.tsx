import Link from 'next/link';
import { requireAdmin } from '@/lib/ce-tools/db';
import { AdminToolsManager } from '@/components/ce-tools/AdminToolsManager';
export const dynamic='force-dynamic';
export default async function AdminToolsPage(){
  const admin=await requireAdmin();
  if(!admin)return <main className="ce-tools-page"><h1>Acesso administrativo</h1><p>Autenticação e papel de editor ou administrador necessários.</p><Link href="/admin/acesso">Entrar com conta autorizada</Link></main>;
  return <main className="ce-tools-page"><header className="ce-tools-header"><h1>Registro de ferramentas</h1><p>Cadastro e submissão para revisão. Publicação bloqueada sem validação externa do Kernel.</p></header><AdminToolsManager role={admin.role}/></main>;
}
