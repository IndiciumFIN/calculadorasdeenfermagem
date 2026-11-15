import type { ToolKind, ToolProjection, ToolRisk } from './types';

const pattern = /^[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*$/;
const slugPattern = /^[a-z0-9]+(?:-[a-z0-9]+)*$/;
const categories = ['protecao', 'carreiras', 'educacao', 'gestao', 'saude-ocupacional', 'pesquisa', 'comunicacao', 'comunidade', 'clinica-educativa'];
const kinds: ToolKind[] = ['checklist', 'reference', 'planner', 'guided-form'];
const risks: ToolRisk[] = ['low', 'medium', 'high', 'critical'];
const projections: ToolProjection[] = ['public', 'subscriber', 'institutional'];

export type DraftInput = { capability_key: string; slug: string; title: string; summary: string; category: string; kind: ToolKind; risk_level: ToolRisk; projection: ToolProjection; payload: Record<string, unknown>; provenance: Record<string, unknown> };

export function parseDraftInput(value: unknown): DraftInput {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new Error('Objeto JSON obrigatório');
  const v = value as Record<string, unknown>;
  const text = (name: string, max: number): string => {
    if (typeof v[name] !== 'string' || !v[name] || (v[name] as string).length > max) throw new Error(`Campo inválido: ${name}`);
    return (v[name] as string).trim();
  };
  const capability_key = text('capability_key', 100);
  const slug = text('slug', 100);
  const title = text('title', 160);
  const summary = text('summary', 900);
  const category = text('category', 80);
  const kind = text('kind', 50) as ToolKind;
  const risk_level = text('risk_level', 50) as ToolRisk;
  const projection = text('projection', 50) as ToolProjection;
  if (!pattern.test(capability_key) || !slugPattern.test(slug)) throw new Error('Chave ou slug fora do contrato');
  if (!categories.includes(category) || !kinds.includes(kind) || !risks.includes(risk_level) || !projections.includes(projection)) throw new Error('Classificação fora do contrato');
  if (!v.payload || typeof v.payload !== 'object' || Array.isArray(v.payload)) throw new Error('Payload obrigatório');
  const payload = v.payload as Record<string, unknown>;
  if (payload.containsPatientData !== false) throw new Error('Dados de paciente são proibidos neste módulo');
  if (!Array.isArray(payload.sections) || payload.sections.length > 30 || !Array.isArray(payload.fields) || payload.fields.length > 30) throw new Error('Estrutura de formulário inválida');
  const list = payload.fields as Record<string,unknown>[];
  const keys = new Set<string>();
  const types = ['text','textarea','checkbox','select','date'];
  for (const f of list) {
    if (!f || typeof f !== 'object' || typeof f.key !== 'string' || !pattern.test(f.key) ||
        typeof f.label !== 'string' || !f.label.trim() || f.label.length > 160 ||
        !types.includes(String(f.type)) || keys.has(f.key)) throw new Error('Campo de formulário inválido/duplicado');
    keys.add(f.key);
    if (f.type === 'select' && (!Array.isArray(f.options) || f.options.length > 30 || f.options.some(o => !o || typeof o.value !== 'string' || typeof o.label !== 'string'))) throw new Error('Opções inválidas');
  }
  for (const section of payload.sections as Record<string,unknown>[]) {
    if (!section || typeof section.heading !== 'string' || typeof section.body !== 'string' || section.heading.length > 180 || section.body.length > 5000) throw new Error('Seção inválida');
  }
  if (!Array.isArray(payload.referenceUrls) || payload.referenceUrls.length > 30 || payload.referenceUrls.some(u => { try { return typeof u !== 'string' || new URL(u).protocol !== 'https:'; } catch { return true; } })) throw new Error('Fontes devem usar HTTPS');
  if (typeof payload.disclaimer !== 'string' || !payload.disclaimer.trim()) throw new Error('Aviso educativo obrigatório');
  if (typeof payload.safeOffline !== 'boolean') throw new Error('Política offline obrigatória');
  if (JSON.stringify(payload).length > 32_000) throw new Error('Payload acima do limite');
  if (!v.provenance || typeof v.provenance !== 'object' || Array.isArray(v.provenance)) throw new Error('Proveniência obrigatória');
  const provenance = v.provenance as Record<string, unknown>;
  if (typeof provenance.source_version !== 'string' || typeof provenance.source_id !== 'string') throw new Error('Versão e ID de origem obrigatórios');
  return { capability_key, slug, title, summary, category, kind, risk_level, projection, payload, provenance };
}
