-- Correções de governança (GOV-004 no banco + RLS por estágio de publicação).
-- ATENÇÃO: arquivo proposto nesta mudança e AINDA NÃO APLICADO ao projeto
-- Supabase. A aplicação exige aprovação humana e execução via CLI/SQL Editor.
-- Rastreabilidade: docs/GAP_REMEDIATION.md.

-- 1) Vigência nunca é default (GOV-004): estado inicial é 'Não verificado'.
alter table public.normatives alter column status set default 'Não verificado';
alter table public.atoms alter column status set default 'Não verificado';

-- 2) Leitura pública restrita a conteúdo com estado publicável.
--    Conteúdo em quarentena ('Não verificado', 'bruto' etc.) não é exposto.
drop policy if exists "Public read normatives" on public.normatives;
drop policy if exists "Public read atoms" on public.atoms;
drop policy if exists "Public read registry" on public.registry;

create policy "Public read published normatives" on public.normatives
  for select using (status in ('Vigente', 'Alterado', 'Revogado'));

create policy "Public read published atoms" on public.atoms
  for select using (status in ('Vigente', 'Alterado', 'Revogado'));

-- 3) Registry não é público: leitura apenas para papéis autenticados
--    (auditoria/operação). O anon não enxerga a quarentena nem o lineage.
create policy "Authenticated read registry" on public.registry
  for select to authenticated using (true);
