# Diário de decisões — CKO Currículo e Mercado (início 15/11/2026)

| ID | Data | Decisão | Evidência | Efeito | Status |
|---|---|---|---|---|---|
| DEC-001 | 2026-11-15 | Usar 65 entradas COFEN como universo de descoberta de especialidades | `specialties/COFEN_581_SPECIALTIES_65_AND_SUBAREAS_v0.5.0.jsonl` | Não confundir especialidade com oferta de curso | ADMITTED_SCOPE_ONLY |
| DEC-002 | 2026-11-15 | Manter graduação, lato sensu e residência como modalidades distintas | `specialties/INSTITUTIONAL_CURRICULA_DELTA_5_v0.5.2.json` | Evitar inflar cursos/horas | ADMITTED_METHOD |
| DEC-003 | 2026-11-15 | Amostra de 34 vagas serve apenas para identificar sinais curriculares candidatos | `market/JOB_DESCRIPTIONS_34_v0.5.7.jsonl` | Não extrapolar frequência para mercado nacional | ADMITTED_METHOD |
| DEC-004 | 2026-11-15 | Vínculos 1.514 e interseções por título não equivalem a `PART_OF` aprovado | `CURRICULAR_TOPIC_CANDIDATE_LINKS_1514_v0.2.8.jsonl` | Bloquear promoção semântica automática | HOLD_SEMANTICS |
| DEC-005 | 2026-11-15 | Materiais W7 são originais candidatos, não licenciados para publicar terceiros nem clinicamente homologados | `educational/MASTER_CONTENT_INDEX_v0.4.4.json` | Separar produção e publicação | NO_GO_PUBLICATION |
| DEC-006 | 2026-11-15 | Auditor GitHub Actions é somente leitura; schedule só após workflow estar na branch padrão | Manifesto v1.0.0 e issue #74 | Automação não contorna CI/main/humano | APPROVED_AUTOMATION_SCOPE |
| DEC-007 | 2026-11-15 | Priorizar P0 direitos, integridade corpus e segurança RLS | `audit/CURRICULUM_COVERAGE_AND_RIGHTS_AUDIT_v0.4.5.json` | Não declarar corpus concluído | PENDING_REMEDIATION |
| DEC-008 | 2026-11-15 | Preservar anomalias da UFCSPA (XENF01001, ENF04004) sem correção inferida | `specialties/QA_UFCSPA_COMPONENTS_v0.5.6.json` | Identidade curricular e horas auditáveis | HOLD_SOURCE_CONFLICT |

## Modelo para novas decisões

`decision_id | scope_id | decision_type | evidence_uri | evidence_sha | normative_version | impact | reviewer_role | reviewer_identity | reviewer_date | result | rollback_plan`.

Para decisão normativa/clínica/licença, registrar aprovação real ou `HOLD_HUMAN`; não usar valores gerados por agentes como assinatura.
