-- Schema inicial - Calculadoras de Enfermagem
-- Executar no Supabase SQL Editor ou via CLI

create table if not exists public.normatives (
  id uuid primary key default gen_random_uuid(),
  id_canonico text unique not null,
  titulo text not null,
  tipo text not null,
  numero text,
  ano integer,
  orgao text,
  status text not null default 'Vigente',
  link_fonte text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create table if not exists public.atoms (
  id uuid primary key default gen_random_uuid(),
  id_atomo text unique not null,
  normative_id uuid references public.normatives(id),
  texto_regra text not null,
  dispositivo_legal text,
  status text not null default 'Vigente',
  versao_contrato text default '1.0.0',
  payload jsonb,
  created_at timestamptz default now()
);

create table if not exists public.calculators (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,
  nome text not null,
  descricao text,
  parametros jsonb not null default '{}',
  atom_ids text[] default '{}',
  created_at timestamptz default now()
);

-- RLS básico (ajustar depois)
alter table public.normatives enable row level security;
alter table public.atoms enable row level security;
alter table public.calculators enable row level security;

-- Políticas de exemplo (leitura pública para conteúdo publicado)
create policy "Public read normatives" on public.normatives for select using (true);
create policy "Public read atoms" on public.atoms for select using (true);
create policy "Public read calculators" on public.calculators for select using (true);
