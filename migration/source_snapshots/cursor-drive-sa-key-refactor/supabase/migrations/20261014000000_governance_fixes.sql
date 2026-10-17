-- Correções de governança (GOV-004 no banco + RLS por estágio de publicação).
-- ATENÇÃO: arquivo proposto nesta mudança e AINDA NÃO APLICADO ao projeto
-- Supabase. A aplicação exige aprovação humana e execução via CLI/SQL Editor.
-- Rastreabilidade: docs/GAP_REMEDIATION.md.

-- 1) Vigência nunca é default (GOV-004): estado inicial é 'Não verificado'.
alter table public.normatives alter column status set default 'Não verificado';
alter table public.atoms alter column status set default 'Não verificado';

-- 2) Publicação é outra dimensão da condição normativa.
--    Vigente, Alterado e Revogado não autorizam leitura pública.
--    O default NAO_AUTORIZADA mantém o acervo fechado até uma autorização
--    explícita, separada do status.
alter table public.normatives
  add column if not exists autorizacao_publicacao text not null default 'NAO_AUTORIZADA';
alter table public.atoms
  add column if not exists autorizacao_publicacao text not null default 'NAO_AUTORIZADA';

drop policy if exists "Public read normatives" on public.normatives;
drop policy if exists "Public read atoms" on public.atoms;
drop policy if exists "Public read registry" on public.registry;
drop policy if exists "Public read published normatives" on public.normatives;
drop policy if exists "Public read published atoms" on public.atoms;

create policy "Public read published normatives" on public.normatives
  for select using (autorizacao_publicacao = 'AUTORIZADA');

create policy "Public read published atoms" on public.atoms
  for select using (autorizacao_publicacao = 'AUTORIZADA');

-- 3) Registry não é público: leitura apenas para papéis autenticados
--    (auditoria/operação). O anon não enxerga a quarentena nem o lineage.
create policy "Authenticated read registry" on public.registry
  for select to authenticated using (true);
