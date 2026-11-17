import { createClient } from '@supabase/supabase-js';
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';
import type { ToolRelease } from './types';

/** Public data: anon key only, RLS enforces immutable published releases. */
export function publicDb() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  return createClient(url, key, { auth: { persistSession: false, autoRefreshToken: false } });
}

/** Authenticated request: cookies + user verification on the Supabase server. */
export async function authenticatedDb() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL;
  const key = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY;
  if (!url || !key) return null;
  const jar = await cookies();
  return createServerClient(url, key, {
    cookies: {
      getAll() { return jar.getAll(); },
      setAll(changes) {
        try { changes.forEach(({ name, value, options }) => jar.set(name, value, options)); }
        catch { /* Server component: cookie refresh is handled in middleware if configured. */ }
      },
    },
  });
}
export async function requireAdmin() {
  const db = await authenticatedDb();
  if (!db) return null;
  const { data: { user }, error } = await db.auth.getUser();
  if (error || !user) return null;
  const result = await db.from('ce_staff_memberships')
    .select('role,status').eq('user_id', user.id).eq('status','active').in('role',['admin','editor']).maybeSingle();
  if (result.error || !result.data) return null;
  return { db, user, role: result.data.role as string };
}
export async function publicToolList(): Promise<ToolRelease[]> {
  const db = publicDb();
  if (!db) return [];
  const { data, error } = await db.from('ce_tool_publications')
    .select('release_id,capability_key,slug,title,summary,category,kind,risk_level,projection,payload,version,published_at,snapshot_sha256,kernel_wo_id')
    .eq('projection','public').order('title');
  if (error) { console.error('Public tools query failed', error.code); return []; }
  return (data || []) as ToolRelease[];
}
export async function publicToolBySlug(slug: string): Promise<ToolRelease | null> {
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) return null;
  const db = publicDb();
  if (!db) return null;
  const { data, error } = await db.from('ce_tool_publications')
    .select('release_id,capability_key,slug,title,summary,category,kind,risk_level,projection,payload,version,published_at,snapshot_sha256,kernel_wo_id')
    .eq('slug',slug).eq('projection','public').maybeSingle();
  return error ? null : (data as ToolRelease | null);
}
