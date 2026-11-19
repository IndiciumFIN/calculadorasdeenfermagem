# CE / CKO / NCOS — checkpoint 2026-11-19 15:55 BRT

## Escopo e cadeia de evidências
Projeto físico único: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; consultas exclusivamente SELECT. PR #73 aberta/DRAFT, branch `audit/ce-supabase-migration-first-20261115`, base main (GitHub conectado 2026-11-19). Checkpoint anterior `0aa0cd97a3cf1c947a01a0820417309f9c592134`. Código commit `da67fc2c7eda93c406e65cd29bdc58934300d0a9`. Nenhum merge, DDL/DML, migration, seed, deploy ou publicação.

## Registro de delta / work orders
| WO | Objeto e fingerprint | Delta | Estado / risco | Teste | Responsável e próximo passo | Aceite |
|---|---|---|---|---|---|---|
| KERNEL-GATE | `packages/cli/kernel/core.py` blob `629c506ed89fa615490ed4049d25c57fb9a4ddf0` -> `1d4e729e80aff7ce3f9d46323f512d9f9349898f` | `run_tests` deve ser callable, retornar literalmente True e não lançar exceção; remove anúncio de sucesso prematuro e dependência de `test_suite()` para exibição | PASS_WRITE / HOLD_TEST; risco médio | NOT_RUN local; CI novo NOT_OBSERVED | Engenharia: adicionar testes unitários para ausência, exception, False, True e smoke | Gate retorna 2 em falhas, 0 somente com testes válidos, sem regressões |
| CI-73 | HEAD anterior `0aa0cd97` | GitHub Actions runs 44582305513 FAIL invariants; 44582305530 PASS pipeline; 44582305368 PASS provenance; 44582305430 PASS validation | FAIL global; risco alto | 3/4 PASS histórico | Engenharia: inspecionar logs, corrigir 16 parsers e legado com evidência | 4/4 PASS no novo HEAD e demais gates |
| CLI-NS | `packages/cli/kernel/__init__.py` blob `f39feaf9ac6445595d3ba35dbe27b86120ebaeb0`; `packages/cli/validators/registry.py` blob `65242eb3b9be2ac24eeef2f3318e8c1b8dda101e` | Nenhum delta nesta rodada | HOLD_TEST / médio | 0/3 homologados (inclui core) | Engenharia: smoke/imports | imports reais sem circularidade |
| PARSERS | `integration/cko-parsers-catalog-20261114`; fingerprints individuais pendentes | Nenhum delta validado | HOLD_VERIFY / alto | 0/16 | Integração: portar por arquivo com licenças/testes | 16/16 com contratos e proveniência |
| TOOLS | `feat/ce-tools-governed-backend-20261115` | Nenhum delta validado | HOLD_VERIFY / alto | 0/24 | Engenharia clínica: contratos e testes | 24/24 homologadas com veto |
| METAMODEL | `feat/cko-catalog-metamodel-automated-20261114` | Sem delta | HOLD_VERIFY / alto | denominador não aferido | CKO: dicionário/PK/FK/terminologias | crosswalk versionado |
| CORPUS | `feat/cko-m08-m09-corpus-atomic-20261114` | Sem delta | HOLD_VERIFY / alto | denominador não aferido | Conteúdo: licenças/proveniência | átomos rastreáveis, candidatos não publicados |
| PG-CROSSWALK | `constraints.jsonl` fingerprint histórico `83642780302397204b39796e1bd3604a77c68f53` | Sem delta individual; não reprocessado | HOLD_SEMANTIC / alto | 8/1996 histórico (0,40%) | Dados: confronto PK/FK individual SELECT-only | equivalência semântica por objeto |
| WORKSPACE | `IndiciumFIN/dev-chatgpt-workspace` PR #71 | Não revalidada | HOLD_VERIFY / médio | NOT_RUN | Integração: inspecionar branch | revisão independente |

## Inventário físico (não homologação)
Manifesto histórico informado: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies; `NON_ATOMIC_ACROSS_QUERIES` / HOLD_HUMAN. Consulta SELECT de 2026-11-19: ce_platform 252 (CHECK 3, FK 135, PK 96, UNIQUE 18), cko_governance 264 (CHECK 61, FK 81, PK 88, UNIQUE 34), public 197 (CHECK 53, FK 71, PK 48, UNIQUE 25); total selecionado 713. Não inferir equivalência entre snapshot e catálogo atual.

## Cobertura e decisão
CI anterior 3/4 PASS (75%; global FAIL). Gate: 1/1 arquivo modificado, 0/1 homologado. Imports 0/3, parsers 0/16, ferramentas 0/24, constraints históricas 8/1996 (0,40%). Metamodelo/corpus/segurança clínica/jurídico sem denominador aferido. **Estimativa global: NÃO AFERÍVEL**. PR #73 continua NO-GO. Testes locais NOT_RUN; CI do novo HEAD NOT_OBSERVED. Sem fontes normativas externas novas nesta rodada.

## Próxima ação
Testar comportamento do Kernel com doubles e smoke, verificar CI do commit de código, depois resolver falhas canônicas e parsers por menor delta seguro. Preservar fail-closed, LGPD, segurança, direitos autorais e proveniência; nenhum candidato promovido.
