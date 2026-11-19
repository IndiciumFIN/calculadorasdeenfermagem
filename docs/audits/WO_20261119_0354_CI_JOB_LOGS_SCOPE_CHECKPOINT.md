# CE / CKO / NCOS — checkpoint 2026-11-19 03:54 BRT

## Proveniência e escopo
Branch real da PR #73: `audit/ce-supabase-migration-first-20261115`; comparação `main...audit/ce-supabase-migration-first-20261115` **ahead 122 / behind 0**, base SHA `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. Último checkpoint lido: `WO_20261119_0248_PR73_BRANCH_ALIGNMENT_CHECKPOINT.md` blob `761ef71e097bfcf1a7e5749db017e49913e12d10`; commit antecedente informado `b0630376ef89b96ff014f52a4a9a2cd3edf9c53d`. Comparação 121→122 corresponde ao checkpoint anterior, não a homologação. PR #71 do workspace permanece em HOLD_VERIFY (sem nova consulta nesta rodada).

## CI no commit b0630376
GitHub Actions 2026-11-19: `CE Migration-first Supabase provenance (NO SQL)` PASS [44467750600](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44467750600); `Pipeline Determinístico` PASS [44467750562](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44467750562); `CI - Validação` PASS [44467750570](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44467750570); `Canonical repository invariants` FAIL [44467750661](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44467750661). Resultado 3/4 workflows listados PASS; NO-GO global. Dois jobs FAIL: `Full admission blockers` job 135369522829 (passo reject unresolved parser/import dependencies); `Canonical contracts and CLI smoke` job 135369523055 (passo verify canonical source and policy references). Compile e testes negativos PASS; CLI smoke e kernel policy smoke SKIPPED. Logs obtidos nesta rodada: 1 `LEGACY_SOURCE_DIR` em `contracts/fonts`, 16 `MISSING_PARSER` e 5 `PACKAGE_IMPORT_NAMESPACE`; nenhuma nova ocorrência SOURCE_VALIDATOR_SCHEMA na filtragem. Não remover diretório legado sem inventário de consumidores; não fabricar parsers vazios; não desabilitar validadores.

## Export e banco
Manifesto `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` lido nesta rodada: observação 2026-11-15, `NON_ATOMIC_ACROSS_QUERIES`, `HOLD_HUMAN`, 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies, 22 arquivos. Fingerprint de manifesto histórico `8099e3ff225224eb00e8eb5accd6d8365ddfcf14` (não recalculado). Supabase **somente** `pgsybzggewhinaniybiy`, SELECT no catálogo `pg_constraint`/`pg_namespace`: `ce_platform` CHECK 3 FK 135 PK 96 UNIQUE 18 = 252; `cko_governance` CHECK 61 FK 81 PK 88 UNIQUE 34 = 264; `public` CHECK 53 FK 71 PK 48 UNIQUE 25 = 197. Total selecionado 713, apenas diagnóstico de escopo, não crosswalk de 1996. Nenhuma DDL/DML.

## Programa persistente / work orders
| WO/objeto | Fingerprint/SHA e delta | Estado/teste | Risco | Responsável e ação seguinte | Aceite |
|---|---|---|---|---|---|
| PR73 / branch | `b0630376` antecedente; ahead 121→122 | PASS_READ; CI no antecedente FAIL | alto | Engenharia: validar CI no HEAD desta atualização | 4/4 PASS + smoke |
| CI contracts/fonts | run 44467750661, LEGACY_SOURCE_DIR | FAIL | alto | Engenharia: inventário consumidores e migração segura | zero consumidores legados, testes PASS |
| CI parsers | 16 MISSING_PARSER, run 44467750661 | FAIL, 0/16 corrigidos | alto | Engenharia: comparar `integration/cko-parsers-catalog-20261114` por arquivo/SHA | 16/16 implementados e smoke PASS |
| CI imports | 5 PACKAGE_IMPORT_NAMESPACE | FAIL, 0/5 corrigidos | alto | Engenharia: corrigir namespace após inspecionar imports | 5/5 PASS |
| Export | MANIFEST histórico blob 8099e3ff; sem delta confirmado | PASS_READ; HOLD_HUMAN | alto | Auditoria: alinhar escopo/snapshot | 22/22 hash revalidado + snapshot |
| Constraints | SELECT 3 schemas: 713; sem crosswalk | PASS_READ, 0/1996 reconciliadas | alto | Dados: comparar objeto/schema/tipo/definição | 1996/1996 reconciliadas ou justificadas |
| Tools 24 | `feat/ce-tools-governed-backend-20261115`; HEAD não capturado | HOLD_VERIFY, 0/24 | alto | Engenharia/clínica: RLS e testes | 24/24 gates |
| Metamodelo | `feat/cko-catalog-metamodel-automated-20261114`; HEAD não capturado | HOLD_VERIFY | alto | Arquitetura: crosswalk PK/FK/dicionário | equivalência demonstrada |
| Corpus M08/M09 | `feat/cko-m08-m09-corpus-atomic-20261114`; HEAD não capturado | HOLD_VERIFY | alto | Curadoria: proveniência, licença e dedup | átomos auditáveis |
| Workspace PR71 | `fix/ce-tanstack-vercel-build-no-migrations-20261114`; não consultado nesta rodada | HOLD_VERIFY | alto | Engenharia: CI independente | CI + gates PASS |

## Percentuais e decisão
CI do antecedente: 3/4 = 75% dos workflows observados (não conclusão). Parser 0/16 corrigidos; imports 0/5; ferramentas 0/24 revalidadas; constraints 0/1996 reconciliadas; hashes 22/22 apenas histórico, NOT_RUN atual. Demais camadas: denominador de homologação indisponível. **Estimativa global: NÃO AFERÍVEL.** Nenhum código funcional alterado nesta rodada. Testes locais NOT_RUN; CI do commit deste checkpoint NOT_RUN. Não houve merges, DDL/DML, migrations, seeds, deploy, exclusões ou publicação de candidatos. Gates clínicos, jurídicos, LGPD, segurança, direitos autorais e proveniência permanecem fail-closed. Nenhuma fonte oficial externa nova consultada.
