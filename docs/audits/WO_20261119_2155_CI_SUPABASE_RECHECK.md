# CE / CKO / NCOS — checkpoint 2026-11-19 21:55 BRT

## Escopo e decisão
Repositório IndiciumFIN/calculadorasdeenfermagem; branch `audit/ce-supabase-migration-first-20261115`; PR [#73](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/73). Checkpoint de entrada [5ba1deb7d62683cea44a52d96b558057f3290136](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/5ba1deb7d62683cea44a52d96b558057f3290136). Fonte física exclusiva: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. NO-GO / fail-closed; nenhuma migration, DDL/DML, seed, merge, deploy ou promoção de conteúdo.

## Evidência nova: CI do checkpoint anterior
GitHub Actions consultado para SHA exato `5ba1deb7d62683cea44a52d96b558057f3290136`:
- [Pipeline Determinístico #44641665245](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44641665245): PASS.
- [CE Migration-first Supabase provenance #44641665191](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44641665191): PASS.
- [CI - Validação #44641665284](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44641665284): PASS.
- [Canonical repository invariants #44641665122](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44641665122): FAIL.
- Job `Full admission blockers (fail closed)`: FAIL no step `Reject unresolved parser or import dependencies`.
- Job `Canonical contracts and CLI smoke`: instalação, compilação e testes negativos PASS; FAIL em `Verify canonical source and policy references`; `CLI import smoke` e `Kernel policy registry smoke` SKIPPED.
Não afirmar que o CI completo passou. A suite Kernel 11/11 PASS pertence à evidência de execução anterior; não há execução nova da suíte nesta rodada.

## Evidência nova: catálogo PostgreSQL (somente SELECT)
Consulta `pg_constraint` com `pg_namespace`, filtrada por três schemas, em 2026-11-19:
| Schema | CHECK | FK | PK | UNIQUE | Total |
|---|---:|---:|---:|---:|---:|
| ce_platform | 3 | 135 | 96 | 18 | 252 |
| cko_governance | 61 | 81 | 88 | 34 | 264 |
| public | 53 | 71 | 48 | 25 | 197 |
| Total | 117 | 287 | 232 | 77 | 713 |

O snapshot histórico informado `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/` (59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 policies) continua `NON_ATOMIC_ACROSS_QUERIES`; não confundir as 713 constraints de três schemas com 1996 de snapshot geral. Sem nova equivalência semântica individual; fingerprint histórico `83642780302397204b39796e1bd3604a77c68f53` não reprocessado.

## Work orders / registro de objetos
| WO | Objeto/fingerprint | Delta | Status/risco | Teste | Responsável e próxima ação | Critério de aceite |
|---|---|---|---|---|---|---|
| CI-INV | SHA `5ba1deb7`, run `44641665122` | Nova observação de dois jobs FAIL | FAIL/alto | admission FAIL; canonical refs FAIL; smoke SKIPPED | Engenharia: obter logs detalhados, corrigir menor delta | 2/2 jobs PASS e smoke executado |
| KERNEL | `packages/cli/kernel/core.py`, fingerprint histórico `f0adfa60`; suite `tests/test_kernel_gate_fail_closed_20261119.py` | Nenhum delta nesta rodada | HOLD_INTEGRATION/médio | 11/11 PASS histórico; smoke SKIPPED | Engenharia: executar smoke integrado | Gate positivo/negativo e integração PASS |
| PARSERS | `integration/cko-parsers-catalog-20261114` | Nenhum arquivo portado; fingerprints individuais ainda não aferidos | HOLD_VERIFY/alto | 0/16 homologados | Integração: inventariar contratos, fontes e licenças antes de portar | 16/16 homologados |
| TOOLS | `feat/ce-tools-governed-backend-20261115` | Sem delta | HOLD_VERIFY/alto | 0/24 revalidadas | Engenharia clínica: vetos, contratos e testes | 24/24 homologadas |
| METAMODEL | `feat/cko-catalog-metamodel-automated-20261114` | Sem delta | HOLD_VERIFY/alto | denominador desconhecido | CKO: mapear PK/FK/dicionário com SELECT | crosswalk individual com provas |
| CORPUS | `feat/cko-m08-m09-corpus-atomic-20261114` | Sem delta | HOLD_VERIFY/alto | denominador desconhecido | Conteúdo: licenças, normativos, proveniência | átomos licenciados e rastreáveis |
| PG-CROSSWALK | `constraints.jsonl` fingerprint `83642780302397204b39796e1bd3604a77c68f53` | Consulta agregada nova, zero objetos semânticos novos | HOLD_SEMANTIC/alto | 8/1996 histórico | Dados: comparar PK/FK por objeto sem reprocessar fingerprints iguais | equivalência por objeto/versão |
| WORKSPACE | `IndiciumFIN/dev-chatgpt-workspace` PR #71 | Não inspecionada nesta rodada | HOLD_VERIFY/médio | NOT_RUN | Integração: avaliar compatibilidade | nenhum contrato concorrente |
| PROGRAM | `docs/audits/WO_20261119_2155_CI_SUPABASE_RECHECK.md` | Novo checkpoint de evidência e work orders | PASS_WRITE após commit; baixo | CI deste novo commit NOT_OBSERVED | Engenharia: verificar workflow do novo HEAD | arquivo versionado, link e SHA confirmados |

## Cobertura / decisão
- Workflows no SHA de entrada: 3/4 PASS (75%), **CI global FAIL**.
- Kernel regressão específica: 11/11 PASS histórico; homologação integrada 0/1.
- Imports 0/3; parsers 0/16; ferramentas 0/24.
- Constraints semanticamente reconciliadas: 8/1996 = 0,40% **histórico**, sem avanço nesta rodada.
- Metamodelo, corpus, LGPD, clínica e jurídico: denominadores não aferidos.
- **Estimativa global: NÃO AFERÍVEL.** Inventário não é homologação.
- CI do novo commit: NOT_OBSERVED. Nenhuma fonte normativa externa nova consultada nesta rodada.

## Próxima execução
Verificar novo HEAD/CI, obter logs dos steps FAIL, corrigir os bloqueios canônicos por menor delta seguro e executar smoke; continuar em paralelo inventário de parsers e ferramentas, crosswalk PK/FK SELECT-only e auditoria de direitos/proveniência. Preservar NO-GO e não criar tabelas concorrentes.
