-- CANDIDATE ONLY. DO NOT APPLY WITHOUT KERNEL-VALIDATED WO.
-- Version 0.1.0. Supabase/PostgreSQL 15+, pgcrypto.
-- Separation: draft -> review -> external Kernel grant -> immutable publication.
create extension if not exists pgcrypto;

create table if not exists public.ce_staff_memberships (
  user_id uuid primary key references auth.users(id) on delete restrict,
  role text not null check(role in ('admin','editor','auditor')),
  status text not null default 'active' check(status in ('active','suspended')),
  created_at timestamptz not null default now()
);
create table if not exists public.ce_tool_drafts (
  id uuid primary key default gen_random_uuid(),
  capability_key text not null unique check(capability_key ~ '^[a-z][a-z0-9._-]{0,99}$'),
  slug text not null unique check(slug ~ '^[a-z0-9]+(-[a-z0-9]+)*$'),
  title text not null check(length(title) between 1 and 160),
  summary text not null check(length(summary) between 1 and 900),
  category text not null,
  kind text not null check(kind in ('checklist','reference','planner','guided-form')),
  risk_level text not null check(risk_level in ('low','medium','high','critical')),
  projection text not null check(projection in ('public','subscriber','institutional')),
  lifecycle text not null default 'candidate' check(lifecycle in ('candidate','draft','in_review','rejected')),
  payload jsonb not null default '{}'::jsonb,
  provenance jsonb not null check(provenance ? 'source_version' and provenance ? 'source_id'),
  authored_by uuid references auth.users(id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint ce_draft_no_patient_info check(payload->>'containsPatientData'='false')
);
create table if not exists public.ce_kernel_grants (
  grant_id uuid primary key default gen_random_uuid(),
  kernel_wo_id text not null unique,
  source_draft_id uuid not null references public.ce_tool_drafts(id) on delete restrict,
  source_payload_sha256 text not null check(source_payload_sha256 ~ '^[a-f0-9]{64}$'),
  status text not null check(status in ('validated','revoked')),
  validation_evidence_uri text not null,
  validation_evidence_sha256 text not null check(validation_evidence_sha256 ~ '^[a-f0-9]{64}$'),
  evidence_signed_by text not null,
  validated_at timestamptz not null,
  created_at timestamptz not null default now()
);
create table if not exists public.ce_tool_releases (
  release_id uuid primary key default gen_random_uuid(),
  source_draft_id uuid not null references public.ce_tool_drafts(id) on delete restrict,
  kernel_grant_id uuid not null unique references public.ce_kernel_grants(grant_id) on delete restrict,
  kernel_wo_id text not null,
  capability_key text not null,
  slug text not null,
  title text not null,
  summary text not null,
  category text not null,
  kind text not null check(kind in ('checklist','reference','planner','guided-form')),
  risk_level text not null check(risk_level in ('low','medium','high','critical')),
  projection text not null check(projection in ('public','subscriber','institutional')),
  payload jsonb not null,
  version text not null check(version ~ '^[0-9]+\.[0-9]+\.[0-9]+$'),
  status text not null check(status='published'),
  snapshot_sha256 text not null check(snapshot_sha256 ~ '^[a-f0-9]{64}$'),
  published_at timestamptz not null default now(),
  unique(capability_key,version)
);
create table if not exists public.ce_tool_revocations (
  release_id uuid primary key references public.ce_tool_releases(release_id) on delete restrict,
  kernel_wo_id text not null,
  reason text not null check(length(reason) between 10 and 1000),
  evidence_sha256 text not null check(evidence_sha256 ~ '^[a-f0-9]{64}$'),
  revoked_at timestamptz not null default now()
);
create table if not exists public.ce_tool_audit (
  id bigint generated always as identity primary key,
  entity_kind text not null,
  entity_id uuid not null,
  event_name text not null,
  actor_id uuid,
  before_row jsonb,
  after_row jsonb,
  occurred_at timestamptz not null default now()
);

create or replace function public.ce_draft_guard() returns trigger language plpgsql security invoker as $$
begin
  if TG_OP='DELETE' then raise exception 'CE_DELETE_FORBIDDEN'; end if;
  if TG_OP='INSERT' then
    if NEW.lifecycle<>'candidate' then raise exception 'CE_CANDIDATE_REQUIRED'; end if;
  else
    if OLD.lifecycle not in ('candidate','draft') then raise exception 'CE_DRAFT_LOCKED'; end if;
    if NEW.id is distinct from OLD.id or NEW.capability_key is distinct from OLD.capability_key then
      raise exception 'CE_IDENTITY_IMMUTABLE'; end if;
    if NEW.lifecycle not in ('candidate','draft','in_review') then raise exception 'CE_INVALID_TRANSITION'; end if;
  end if;
  if jsonb_typeof(NEW.payload->'sections') <> 'array' or jsonb_typeof(NEW.payload->'fields') <> 'array' then
    raise exception 'CE_PAYLOAD_CONTRACT'; end if;
  if octet_length(NEW.payload::text)>32000 then raise exception 'CE_PAYLOAD_TOO_LARGE'; end if;
  NEW.updated_at:=now();
  return NEW;
end$$;
create or replace function public.ce_draft_audit() returns trigger language plpgsql security definer set search_path=public,pg_temp as $$
begin
  insert into public.ce_tool_audit(entity_kind,entity_id,event_name,actor_id,before_row,after_row)
  values ('tool_draft',NEW.id,TG_OP,auth.uid(),case when TG_OP='UPDATE' then to_jsonb(OLD) else null end,to_jsonb(NEW));
  return NEW;
end$$;
create or replace function public.ce_release_guard() returns trigger language plpgsql security invoker as $$
declare g public.ce_kernel_grants%rowtype; d public.ce_tool_drafts%rowtype;
begin
  if TG_OP in ('UPDATE','DELETE') then raise exception 'CE_RELEASE_IMMUTABLE'; end if;
  select * into g from public.ce_kernel_grants where grant_id=NEW.kernel_grant_id and status='validated';
  if not found then raise exception 'CE_NO_KERNEL_GRANT'; end if;
  select * into d from public.ce_tool_drafts where id=NEW.source_draft_id;
  if not found or d.lifecycle<>'in_review' then raise exception 'CE_SOURCE_NOT_REVIEWED'; end if;
  if NEW.kernel_wo_id<>g.kernel_wo_id or g.source_draft_id<>d.id then raise exception 'CE_GRANT_MISMATCH'; end if;
  if NEW.capability_key<>d.capability_key or NEW.slug<>d.slug or NEW.title<>d.title or NEW.summary<>d.summary
     or NEW.category<>d.category or NEW.kind<>d.kind or NEW.projection<>d.projection or NEW.risk_level<>d.risk_level
     or NEW.payload<>d.payload then raise exception 'CE_SNAPSHOT_MISMATCH'; end if;
  if NEW.snapshot_sha256<>encode(digest(convert_to(NEW.payload::text,'UTF8'),'sha256'),'hex')
    or NEW.snapshot_sha256<>g.source_payload_sha256 then raise exception 'CE_SHA_MISMATCH'; end if;
  return NEW;
end$$;
create or replace function public.ce_revocation_guard() returns trigger language plpgsql security invoker as $$
begin
  if TG_OP <> 'INSERT' then raise exception 'CE_REVOCATION_IMMUTABLE'; end if;
  if not exists(select 1 from public.ce_tool_releases where release_id=NEW.release_id) then
    raise exception 'CE_NO_RELEASE_TO_REVOKE'; end if;
  return NEW;
end$$;
create or replace function public.ce_release_audit() returns trigger language plpgsql security definer set search_path=public,pg_temp as $$
begin
  insert into public.ce_tool_audit(entity_kind,entity_id,event_name,actor_id,after_row)
  values('tool_release',NEW.release_id,'PUBLISHED',auth.uid(),to_jsonb(NEW));
  return NEW;
end$$;

-- CREATE OR REPLACE TRIGGER supported in PostgreSQL 14+.
create or replace trigger ce_guard_drafts before insert or update or delete on public.ce_tool_drafts
for each row execute function public.ce_draft_guard();
create or replace trigger ce_audit_drafts after insert or update on public.ce_tool_drafts
for each row execute function public.ce_draft_audit();
create or replace trigger ce_guard_releases before insert or update or delete on public.ce_tool_releases
for each row execute function public.ce_release_guard();
create or replace trigger ce_audit_releases after insert on public.ce_tool_releases
for each row execute function public.ce_release_audit();
create or replace trigger ce_guard_revocations before insert or update or delete on public.ce_tool_revocations
for each row execute function public.ce_revocation_guard();

alter table public.ce_staff_memberships enable row level security;
alter table public.ce_tool_drafts enable row level security;
alter table public.ce_kernel_grants enable row level security;
alter table public.ce_tool_releases enable row level security;
alter table public.ce_tool_audit enable row level security;
alter table public.ce_tool_revocations enable row level security;
-- Memberships are provisioned by a trusted external process only.
create policy ce_staff_self_select on public.ce_staff_memberships for select to authenticated
using(user_id=auth.uid());
create policy ce_drafts_staff_select on public.ce_tool_drafts for select to authenticated
using(exists(select 1 from public.ce_staff_memberships s where s.user_id=auth.uid() and s.status='active' and s.role in ('admin','editor','auditor')));
create policy ce_drafts_staff_insert on public.ce_tool_drafts for insert to authenticated
with check(authored_by=auth.uid() and lifecycle='candidate' and exists(select 1 from public.ce_staff_memberships s where s.user_id=auth.uid() and s.status='active' and s.role in ('admin','editor')));
create policy ce_drafts_staff_update on public.ce_tool_drafts for update to authenticated
using(lifecycle in ('candidate','draft') and exists(select 1 from public.ce_staff_memberships s where s.user_id=auth.uid() and s.status='active' and s.role in ('admin','editor')))
with check(lifecycle in ('candidate','draft','in_review') and exists(select 1 from public.ce_staff_memberships s where s.user_id=auth.uid() and s.status='active' and s.role in ('admin','editor')));
-- No INSERT/UPDATE/DELETE policies for kernel grants, published releases, or audit.
create policy ce_public_releases_select on public.ce_tool_releases for select to anon,authenticated
using(status='published' and projection='public');
-- Expose only release IDs of revocations to guarantee fail-closed public filtering.
create policy ce_public_revocations_select on public.ce_tool_revocations for select to anon,authenticated using(true);

create or replace view public.ce_tool_publications with (security_invoker=true) as
select distinct on (slug) release_id,capability_key,slug,title,summary,category,kind,risk_level,projection,
  payload,version,published_at,snapshot_sha256,kernel_wo_id
from public.ce_tool_releases r where r.status='published' and r.projection='public'
  and not exists(select 1 from public.ce_tool_revocations z where z.release_id=r.release_id)
order by slug,published_at desc,version desc;

-- Explicit role grants; avoid broad schema USAGE assumptions.
grant select on public.ce_tool_publications to anon,authenticated;
grant select on public.ce_tool_releases to anon,authenticated;
grant select(release_id) on public.ce_tool_revocations to anon,authenticated;
revoke insert,update,delete on public.ce_tool_revocations from anon,authenticated;
grant select on public.ce_staff_memberships to authenticated;
grant select,insert,update on public.ce_tool_drafts to authenticated;
revoke all on public.ce_kernel_grants from anon,authenticated;
revoke all on public.ce_tool_audit from anon,authenticated;
revoke delete on public.ce_tool_drafts from anon,authenticated;
revoke insert,update,delete on public.ce_tool_releases from anon,authenticated;
-- PUBLISHING REQUIRES a separate trusted service process that verifies
-- Kernel grant signature, WO, independent tests and evidence BEFORE inserting
-- ce_kernel_grants and ce_tool_releases. No endpoint in this patch publishes.
