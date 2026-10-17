-- Registry canônico
create table if not exists public.registry (
  id uuid primary key default gen_random_uuid(),
  id_canonico text unique not null,
  tipo text not null,
  hash_sha256 text,
  status text not null default 'bruto',
  origem text,
  drive_file_id text,
  versao_contrato text default '1.1.0',
  data_ingestao date default current_date,
  data_verificacao date,
  find_ids text[] default '{}',
  notas text,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

alter table public.registry enable row level security;

create policy "Public read registry" on public.registry for select using (true);

-- Índices úteis
create index if not exists idx_registry_status on public.registry(status);
create index if not exists idx_registry_tipo on public.registry(tipo);
create index if not exists idx_registry_hash on public.registry(hash_sha256);
