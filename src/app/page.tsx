import Link from 'next/link';

/** Minimal integration with current Next.js root without replacing the official site. */
export default function Home() {
  return (
    <main style={{ padding: '2rem', fontFamily: 'var(--ce-font, Inter, system-ui, sans-serif)' }}>
      <h1>Calculadoras de Enfermagem</h1>
      <p>Estrutura base inicializada. Próximos passos: conectar Supabase e migrar calculadoras.</p>
      <ul>
        <li>Normativos atômicos</li>
        <li>Calculadoras paramétricas</li>
        <li>Builder de camadas</li>
        <li><Link href="/ferramentas">Ferramentas públicas governadas</Link></li>
        <li><Link href="/admin/ferramentas">Painel de ferramentas (acesso restrito)</Link></li>
      </ul>
    </main>
  )
}
