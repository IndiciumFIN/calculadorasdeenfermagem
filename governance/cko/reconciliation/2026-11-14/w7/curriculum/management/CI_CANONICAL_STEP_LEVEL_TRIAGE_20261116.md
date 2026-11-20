# CKO — triagem dos bloqueios de admissão canônica por job/step

Data: 2026-11-16. EPIC #74 / PR #70. Escopo: diagnóstico somente leitura; não altera workflow, parser, política, Supabase ou gates.

## Execução consultada

Run: https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43932821589 — `Canonical repository invariants`, **FAIL**. Jobs e passos obtidos diretamente via GitHub Actions:

| Job | ID | Primeiro passo com FAIL | Passos anteriores relevantes |
|---|---:|---|---|
| Full admission blockers (fail closed) | 133529481976 | #4 `Reject unresolved parser or import dependencies` | Checkout e Python PASS |
| Canonical contracts and CLI smoke | 133529482910 | #7 `Verify canonical source and policy references` | Install packages, compile imports/code/tests e deterministic negative tests PASS |

Os passos `CLI import smoke` (#8) e `Kernel policy registry smoke` (#9) do segundo job constam como **skipped**, portanto não são PASS nem FAIL independentes. O resultado indica classe de bloqueio, não identifica por si só o nome dos arquivos; requer logs/artefatos detalhados antes de corrigir.

## CI de mesmo ciclo / limites

- CKO read-only audit PASS: https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43932821688
- Pipeline determinístico PASS: https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43932821814
- CI validação PASS: https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43932821634
- Estes resultados não superam o FAIL canônico nem validam o presente commit.

## Plano de resolução candidato, sem contornar gates

1. Obter logs dos jobs 133529481976 e 133529482910; listar dependências de parser/import ausentes e caminhos exatos de fonte/política.
2. Comparar cada referência com o registro canônico, manifestos e hashes da mesma revisão; classificar `MISSING_FILE`, `MISSING_IMPORT`, `PATH_DRIFT`, `POLICY_REFERENCE_MISMATCH` ou `UNDETERMINED`, sem inferência.
3. Corrigir somente em branch de revisão e com testes negativos; não transformar checks obrigatórios em opcionais.
4. Reexecutar e documentar **todos** os gates; merge segue NO-GO até aprovação humana e CI integral.

## Dependências P0/P1

`HOLD_CI_CANONICAL`: dois passos acima; `HOLD_SOURCE`: vínculos atividade USP Apolo → curso-mãe e edições não demonstrados; `HOLD_RIGHTS`: direitos de reprodução de ementas; `HOLD_HUMAN`: revisão jurídica, curricular e semântica. Nenhuma mudança nos denominadores baseline: 65 especialidades, 114 programas, 14/65 especialidades representadas por vagas e 38/1055 microaulas candidatas do subconjunto Trabalho/Urgência.
