# CKO W7 — diagnóstico de dependências do CI após triagem USP (16/11/2026)

**Escopo:** issue #74, PR #70, branch `review/cko-w7-public-evidence-20261114`. **Commit verificado:** `66d1576c4bed899b1ea977df8e1f8c64440cf454`. **Classificação:** relatório técnico candidato, leitura de GitHub Actions, não libera gates.

## Quatro workflows associados ao commit exato

| Workflow | Run | Resultado |
|---|---|---|
| CKO Curriculum and Market Read-only Audit | https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43932821688 | PASS |
| Pipeline Determinístico | https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43932821814 | PASS |
| CI - Validação | https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43932821634 | PASS |
| Canonical repository invariants | https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43932821589 | FAIL |

Esses quatro resultados são do **commit 66d1576**, não deste relatório. Auditoria CKO PASS verifica regras automatizadas de cobertura e artefatos, **não** aprova vínculo entre atividades USP e programa, licenças ou publicação clínica.

## Falha canônica — diagnóstico de passos verificados no run anterior

No run https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43924560776 , anterior ao commit 66d1576, o job `Full admission blockers (fail closed)` falhou no passo **Reject unresolved parser or import dependencies**. O job `Canonical contracts and CLI smoke` compilou imports/testes e passou testes negativos determinísticos, mas falhou em **Verify canonical source and policy references**. Passos de CLI smoke e Kernel policy smoke ficaram **skipped**. A execução mais recente `43932821589` também concluiu FAIL, mas o diagnóstico detalhado dos passos desta execução não foi consultado aqui; não presumir identidade exata das causas sem ler logs.

**Decisão:** `HOLD_CI_CANONICAL`, sem merge, release, promoção de fontes ou alteração em Supabase. Falhas de dependências de parsers/imports e referências de fontes/políticas devem ser corrigidas no fluxo próprio de integração e submetidas a CI novo, não por desabilitação de checks.

## Relação com WOs do plano mestre

- P0/01 `CANONICAL_BASELINE`: HOLD_SOURCE_VERSION (hash do corpus de 1.055 microtópicos e identidades pendentes); PASS de auditoria não equivale a baseline assinado.
- P0/02 `SOURCE_RIGHTS`: HOLD_RIGHTS (direitos por obra, edição e operação).
- P0/03 `SECURITY_PRIVACY`: HOLD_SECURITY (RLS/grants sem auditoria de aprovação).
- P1/04 `SPECIALTY_CURRICULA`: 4/4 atividades USP com IDs distintos, **0/4 vínculos curso-mãe aprovados**; HOLD_SOURCE e HOLD_HUMAN, conforme `USP_APOLO_ACTIVITY_SCOPE_TRIAGE_20261116.md`.
- P3/10 `INTEGRATION_RELEASE`: bloqueado por invariantes FAIL e gates P0/P2.

## Próxima ação executável sem violar gates

Continuar descoberta documental de páginas oficiais de **oferta do curso-mãe** no Apolo, com ID de curso, unidade e edição que referencie explicitamente cada atividade (92849, 125923, 122199, 135580). Registrar `NOT_FOUND/HOLD_SOURCE` quando a página não permitir a ligação; não inferir especialidade pelo título. Manter 65 especialidades, 114 programas e os 985 itens como denominadores do snapshot até reconciliação de identidade.
