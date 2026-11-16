# W7 — reconciliação P1 USP Apolo × 114 programas (16/11/2026)

**EPIC:** #74 · **PR:** #70 · **Estado:** `CANDIDATE_READ_ONLY` / `HOLD_SOURCE`. Sem alteração de cadastro canônico.

## Evidências reproduzíveis

1. Registro versionado: [CURRICULUM_PROGRAM_COVERAGE_114_v0.2.8.jsonl](https://github.com/IndiciumFIN/calculadorasdeenfermagem/blob/review/cko-w7-public-evidence-20261114/governance/cko/reconciliation/2026-11-14/w7/curriculum/CURRICULUM_PROGRAM_COVERAGE_114_v0.2.8.jsonl), blob SHA Git `ad68e422c7e4ac00c093db336d8fbd4d44919cca`, lido nesta execução. Foram parseadas **114/114 linhas JSONL**.
2. Relatório de descoberta USP Apolo já versionado no [commit 86956e21375baad2e0738445884326cdbe749d5b](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/86956e21375baad2e0738445884326cdbe749d5b), com quatro IDs de atividades Apolo: 92849, 125923, 122199, 135580. Esses IDs foram **herdados do relatório anterior**, não revalidados diretamente nas páginas Apolo nesta execução.
3. CI do commit anterior: [CKO Curriculum and Market Read-only Audit #43914219642](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43914219642) **success**; [Canonical repository invariants #43914219536](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43914219536) **failure**, com etapas `Reject unresolved parser or import dependencies` e `Verify canonical source and policy references`. Não confundir sucesso do auditor curricular com aprovação global.

## Resultado da comparação exata do inventário

- O registro de 114 programas contém **7 programas com Centro Cirúrgico, CME ou Perioperatória no título**: `PG-EIN-CC-CME`, `PG-SIRIO-CC-CME`, `PG-SANTA-CC`, `PG-PUCPR-PERIOP`, `PG-MOINHOS-CC`, `PG-PUCPR-CC-RPA-CME-LON`, `PG-PUCPR-GESTAO-PERIOP-CME`.
- Os únicos **2 registros** cujo `institution_id` contém `HCFMUSP` são `PG-IPQ-PSYCH` e `PG-INCOR-NURSING`; **nenhum** dos 114 registros é programa USP de Centro Cirúrgico identificado por título ou `institution_id`. Isso não prova inexistência de oferta USP fora do inventário.
- Nenhum dos quatro IDs Apolo consta como `program_id` nos 114 registros. **ID de atividade Apolo não é automaticamente ID de programa**, e quatro atividades não demonstram quatro cursos ou quatro novas edições de um curso.
- **Decisão:** não criar `PG-USP-CC` ou `PART_OF` por semelhança de título; manter quatro atividades como candidatos de descoberta, sem alteração dos 114 programas nem dos 65 IDs COFEN.

## Fila de evidência para desbloqueio

| Item | Evidência exigida | Estado |
|---|---|---|
| USP-A-92849 | Página oficial Apolo, curso/programa pai, turma/edição, campus, tipo e horas | HOLD_SOURCE |
| USP-A-125923 | Página oficial Apolo, curso/programa pai, turma/edição, campus, tipo e horas | HOLD_SOURCE |
| USP-A-122199 | Página oficial Apolo, curso/programa pai, turma/edição, campus, tipo e horas | HOLD_SOURCE |
| USP-A-135580 | Página oficial Apolo, curso/programa pai, turma/edição, campus, tipo e horas | HOLD_SOURCE |
| USP direitos | Titular, condições por operação (consultar, extrair, guardar, adaptar, publicar) | HOLD_RIGHTS |
| USP competência | Equivalência entre atividades, ementas e competência de enfermagem | HOLD_HUMAN |

**Método:** comparação exata de `program_id`, `institution_id` e títulos em JSONL. Não houve coleta de texto integral protegido, deduplicação destrutiva ou inferência de aprovação. Este documento não é homologação clínica, jurídica, pedagógica nem resultado de CI para seu próprio commit.
