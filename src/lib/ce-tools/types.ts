/** Contrato canônico candidato. IDs definitivos pertencem ao Kernel. */
export type ToolKind = 'checklist' | 'reference' | 'planner' | 'guided-form';
export type ToolRisk = 'low' | 'medium' | 'high' | 'critical';
export type ToolLifecycle = 'candidate' | 'draft' | 'in_review' | 'rejected';
export type ToolProjection = 'public' | 'subscriber' | 'institutional';
export type ToolField = {
  key: string;
  label: string;
  type: 'text' | 'textarea' | 'checkbox' | 'select' | 'date';
  required?: boolean;
  options?: { value: string; label: string }[];
};
export type ToolPayload = {
  summary: string;
  disclaimer: string;
  sections: { heading: string; body: string }[];
  fields: ToolField[];
  referenceUrls: string[];
  safeOffline: boolean;
  containsPatientData: false;
};
export type ToolDraft = {
  id: string;
  capability_key: string;
  slug: string;
  title: string;
  summary: string;
  category: string;
  kind: ToolKind;
  risk_level: ToolRisk;
  projection: ToolProjection;
  lifecycle: ToolLifecycle;
  payload: ToolPayload;
  provenance: Record<string, unknown>;
  updated_at: string;
};
export type ToolRelease = {
  release_id: string;
  capability_key: string;
  slug: string;
  title: string;
  summary: string;
  category: string;
  kind: ToolKind;
  risk_level: ToolRisk;
  projection: ToolProjection;
  payload: ToolPayload;
  version: string;
  published_at: string;
  snapshot_sha256: string;
  kernel_wo_id: string;
};
