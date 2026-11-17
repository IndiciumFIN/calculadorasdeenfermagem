# CKO P0/P1 — critérios numéricos de formação em lesões cutâneas (candidato)

**Data:** 2026-11-17. **Fonte primária:** https://www.cofen.gov.br/resolucao-cofen-no-787-de-21-de-agosto-de-2025/ — Resolução Cofen 787/2025, art. 9º. **Identidade normativa:** `COFEN-787-2025:ART-9`. **Status:** `EVIDENCE_INDEXED_CANDIDATE` (sem aprovação curricular/clínica).

## Extração mínima, sem duplicação

O art. 9º recomenda, ao enfermeiro que trata lesões cutâneas complexas e/ou atua em ambientes especializados, pós-graduação lato sensu na área com mínimo de **360 horas acrescidas de 20% dessa carga horária para práticas supervisionadas**. A conta literal de referência é `360 × 0,20 = 72` horas adicionais; `360 + 72 = 432` horas totais, caso a oferta siga exatamente o mínimo de base. **É recomendação contextual**, não exigência geral de habilitação nem prova de cumprimento de uma instituição. Não confundir com as **100 horas práticas supervisionadas** previstas na cadeia normativa específica de Enfermagem Estética (Resolução 715/2023): são atos, contextos e escopos distintos.

## Casos candidatos para teste determinístico

| Caso | Entrada de metadados | Esperado |
|---|---|---|
| T01 | `base_hours=360; supervised_hours=72; total_hours=432; specialty=lesoes_complexas` | `MEETS_NUMERIC_REFERENCE_CANDIDATE`, **não** `QUALIFICATION_APPROVED` |
| T02 | `base_hours=360; supervised_hours=0; total_hours=360` | `BELOW_RECOMMENDED_SUPERVISED_REFERENCE`, **não** inferir ilegalidade |
| T03 | `base_hours=360; supervised_hours=100; total_hours=460` | `NUMERICALLY_ABOVE_REFERENCE`, **não** validar natureza/realização das práticas |
| T04 | `total_hours=432; supervised_hours=72; no_PPC_or_edition` | `HOLD_SOURCE_FOR_EDITION`, indexação dos fatos permitida |
| T05 | `specialty=enfermagem_estetica; 100h_practice` | Não aplicar automaticamente regra `COFEN-787-2025:ART-9`; avaliar norma específica |
| T06 | `source=COFEN-787-2025:ART-9; program_id=unknown` | Sem vínculo `PROGRAM_SATISFIES_REQUIREMENT` nem duplicação de programa |

## Controle de evidência e direitos

- Os metadados numéricos e o identificador do artigo podem ser indexados com URL oficial. **Não** copiar integralmente anexos, material didático ou PPCs sem análise de direitos.
- `HOLD_SOURCE` limita apenas a comprovação de curso, edição, prática e vínculo específico; não bloqueia o catálogo de evidências nem o teste candidato.
- `HOLD_HUMAN` limita somente aprovação de competência profissional, interpretação jurídica definitiva ou promoção clínica.
- Os seis casos acima são **especificações documentais**, não testes executados. Não há alteração de código, schema, conteúdo clínico, main ou Supabase.

## Dependências do EPIC #74

Plano e manifesto: `management/PLAN_MESTRE_CONCLUSAO_v1.0.0.md`, `management/EXECUTION_MANIFEST_v1.0.0.json`. Crosswalk anterior: `management/COFEN_736_787_44_ARTICLE_CROSSWALK_20261117_CANDIDATE.md`. Esta nota **refina o mesmo ID normativo**; não cria novo átomo de fonte ou especialidade. Para qualquer PPC candidato, registrar `institution_id`, `program_id`, `edition`, `source_url`, `supervised_hours_documented`, `rights_status` antes de propor cobertura.
