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


## Rodada 2026-11-19 16:50 BRT — delta versionado

**Base de leitura:** checkpoint commit `c43e1ff1a57baeb0dac8e19cbbbc0a09270dcd90`, arquivo checkpoint blob `e4aab4ff577a610a31642d26de1dcb444b7a4b45`; Kernel `packages/cli/kernel/core.py` blob `1d4e729e80aff7ce3f9d46323f512d9f9349898f` (sem delta). Branch audit em comparação com main: ahead 142, behind 0, 150 arquivos no compare (antes do commit de testes). Sem merge.

**Alteração efetiva:** criado `tests/test_kernel_gate_fail_closed_20261119.py`, commit `0ce429752bbce1748354d70d8b076b823b251e1a`. Casos parametrizados de ausência de método, método não callable, retorno False, 1, None, True, exceção, política desconhecida, política sem validadores e validador não registrado. Não há mocks de aprovação clínica, SQL ou publicação. Os testes foram **adicionados, não executados** nesta rodada; seu resultado ainda depende de CI/pytest.

**CI observado para HEAD anterior `c43e1ff1`:** Pipeline Determinístico PASS [44592983813](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44592983813), Proveniência PASS [44592983764](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44592983764), CI - Validação PASS [44592983745](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44592983745), Canonical repository invariants FAIL [44592983793](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44592983793). Nesse último, 2/2 jobs falharam: referências canônicas e bloqueadores de parser/import; compilação e testes negativos PASS, smoke CLI/Kernel SKIPPED. **3/4 workflows PASS (75%), CI global FAIL**. Não atribuir PASS ao commit de testes sem execução.

**Supabase físico único:** SELECT de `pg_constraint` no projeto `pgsybzggewhinaniybiy` retornou `ce_platform` CHECK 3/FK 135/PK 96/UNIQUE 18 (252); `cko_governance` CHECK 61/FK 81/PK 88/UNIQUE 34 (264); `public` CHECK 53/FK 71/PK 48/UNIQUE 25 (197). Total 713 constraints **apenas nesses 3 schemas**. Inventário histórico de 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices e 100 policies é snapshot `NON_ATOMIC_ACROSS_QUERIES`, não homologação nem prova de equivalência. Crosswalk histórico 8/1996 (0,40%), sem novo objeto validado ou fingerprint reprocessado.

| WO | Objeto / fingerprint | Delta | Estado / risco | Teste | Responsável / próxima ação | Aceite |
|---|---|---|---|---|---|---|
| KERNEL-REGRESSION | `tests/test_kernel_gate_fail_closed_20261119.py`; commit `0ce42975`; Kernel blob `1d4e729e` | Testes determinísticos novos, sem alterar o gate | PASS_WRITE / HOLD_TEST; médio | 0/10 cenários executados nesta rodada; NOT_RUN | Engenharia: executar pytest no HEAD exato e revisar qualquer FAIL | Casos negativos exit 2, positivo exit 0; nenhum efeito colateral em rejeição |
| CI-73 | `c43e1ff1`, run `44592983793` | Novo diagnóstico de jobs; bloqueios persistem | FAIL; alto | 3/4 workflows PASS no HEAD anterior | Engenharia: examinar logs de invariantes, corrigir por menor delta | 4/4 PASS no HEAD final |
| PARSERS | `integration/cko-parsers-catalog-20261114` | Nenhum delta aplicado | HOLD_VERIFY; alto | 0/16 | Integração: comparar contratos e licenças, portar por arquivo | 16/16 homologados |
| TOOLS | `feat/ce-tools-governed-backend-20261115` | Nenhum delta aplicado | HOLD_VERIFY; alto | 0/24 | Engenharia clínica: smoke e vetos | 24/24 homologadas |
| METAMODEL | `feat/cko-catalog-metamodel-automated-20261114` | Nenhum delta | HOLD_VERIFY; alto | denominador não aferido | CKO: dicionário e PK/FK SELECT | Crosswalk individual versionado |
| CORPUS | `feat/cko-m08-m09-corpus-atomic-20261114` | Nenhum delta | HOLD_VERIFY; alto | denominador não aferido | Conteúdo: licença e proveniência | Átomos com fontes rastreáveis |
| PG-CROSSWALK | `constraints.jsonl` fingerprint histórico `83642780302397204b39796e1bd3604a77c68f53` | Sem delta individual; não reprocessado | HOLD_SEMANTIC; alto | 8/1996 histórico | Dados: conciliar definições por PK/FK | Equivalência por objeto e versão |
| WORKSPACE | `IndiciumFIN/dev-chatgpt-workspace` PR #71 | Não revalidado | HOLD_VERIFY; médio | NOT_RUN | Integração: revisar PR | Sem contratos concorrentes |

**Coberturas verificadas:** Kernel gate 0/1 homologado; imports 0/3; parsers 0/16; ferramentas 0/24; crosswalk 8/1996 histórico (0,40%); novo teste 0/10 executados. Denominadores de metamodelo, corpus, LGPD, clínica e jurídico não aferidos. **Estimativa global de conclusão: NÃO AFERÍVEL**. PR #73 NO-GO. Nenhum DDL/DML, migration, seed, merge, deploy, exclusão de branch ou publicação. Sem fontes normativas externas novas.

**Próxima ação:** executar a nova suíte no HEAD do commit de testes; verificar o CI disparado; corrigir qualquer falha real sem enfraquecer invariantes; depois portar parsers seletivamente e ampliar o crosswalk com SELECT por objeto.


## Rodada 2026-11-19 17:51 BRT — teste obrigatório no CI

**Checkpoint de entrada:** PR #73 DRAFT/open, HEAD `3d34f09cbfbe5de19c541a2e6abb8555d4cbe231`; Kernel blob `1d4e729e80aff7ce3f9d46323f512d9f9349898f`; suíte blob `92eacbf90b3fa82284aaa44617c6ae0092fd777a`. A suíte foi inspecionada, não reescrita nem presumida como aprovada.

**Delta persistido:** `.github/workflows/ci.yml` blob `7ecc09d952463223d9b433da5bf02d58b71ba7fe` -> `a26b6bca58561426ad8d2e5f0a4c66e5b002c115`, commit [1f6080036709788014c214248bb5bb4d0573119d](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/1f6080036709788014c214248bb5bb4d0573119d). Acrescenta instalação de pytest e etapa **obrigatória**, sem `continue-on-error`, `python -m pytest -q tests/test_kernel_gate_fail_closed_20261119.py`. Mantida configuração anterior de typecheck/CLI, cujas tolerâncias são débito técnico separado; não atribuir a elas aprovação real. Sem alteração em código clínico.

**CI do HEAD anterior 3d34f09:** [Pipeline Determinístico PASS](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44602597409), [CI - Validação PASS](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44602597560), [Proveniência PASS](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44602597834), [Canonical repository invariants FAIL](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44602597296). Nos invariantes: 2/2 jobs FAIL; compilação e testes negativos PASS, referências canônicas FAIL, admissão parser/import FAIL, smoke CLI e Kernel SKIPPED. O PASS anterior de CI-Validação **não executava** os dez cenários novos. Resultado do CI após commit de workflow: NOT_OBSERVED nesta rodada.

**Supabase:** SELECT-only no projeto `pgsybzggewhinaniybiy`, `pg_constraint` por `contype`, confirmou novamente ce_platform 252, cko_governance 264, public 197, total 713 **apenas três schemas**. Snapshot histórico de 1996 constraints permanece `NON_ATOMIC_ACROSS_QUERIES`, sem reconciliação semântica nova; fingerprint `83642780302397204b39796e1bd3604a77c68f53` sem delta, não reprocessado. Não foram usados outros bancos.

| WO | Objeto / fingerprint | Delta / status / risco | Teste | Responsável e próxima ação | Critério de aceite |
|---|---|---|---|---|---|
| CI-KERNEL-TEST | `.github/workflows/ci.yml` `7ecc09d9` -> `a26b6bca`; suíte `92eacbf9` | Novo step pytest obrigatório; PASS_WRITE / HOLD_TEST, médio | 10/10 cenários definidos; execução nova NOT_OBSERVED | Engenharia: ler logs CI novo e corrigir falhas de dependência/testes | 10/10 PASS no HEAD e falha de teste reprova CI |
| CI-CANONICAL | run 44602597296 | Sem delta nos invariantes; FAIL, alto | 2/2 jobs FAIL | Engenharia: reparar refs e parsers por menor delta, não relaxar gate | 2/2 jobs PASS |
| PARSERS | branch `integration/cko-parsers-catalog-20261114` | Sem delta; HOLD_VERIFY, alto | 0/16 homologados | Integração: contratos, licença e teste por parser | 16/16 PASS |
| TOOLS | branch `feat/ce-tools-governed-backend-20261115` | Sem delta; HOLD_VERIFY, alto | 0/24 homologadas | Engenharia clínica: contratos e veto | 24/24 PASS |
| METAMODEL | branch `feat/cko-catalog-metamodel-automated-20261114` | Sem delta; HOLD_VERIFY, alto | denominador não aferido | CKO: dicionário/PK/FK | crosswalk por objeto |
| CORPUS | branch `feat/cko-m08-m09-corpus-atomic-20261114` | Sem delta; HOLD_VERIFY, alto | denominador não aferido | Conteúdo: direitos/proveniência | átomos rastreáveis |
| PG-CROSSWALK | `constraints.jsonl` fingerprint `8364278030` | Sem delta; HOLD_SEMANTIC, alto | histórico 8/1996 = 0,40% | Dados: SELECT por PK/FK | equivalência individual |
| WORKSPACE | PR #71 `dev-chatgpt-workspace` | Sem delta; HOLD_VERIFY, médio | NOT_RUN | Integração: revisar isoladamente | sem contratos concorrentes |

**Percentuais por camada:** CI HEAD anterior 3/4 PASS = 75%, global FAIL; regressões definidas 10/10, executadas no novo HEAD **não observadas** (não inferir 0 falhas nem PASS); gate homologado 0/1; imports 0/3; parsers 0/16; ferramentas 0/24; constraints historicamente reconciliadas 8/1996 = 0,40%. Metamodelo, corpus, LGPD, clínica e jurídico sem denominador validado. **Estimativa global de conclusão: NÃO AFERÍVEL**. PR #73 DRAFT/NO-GO. Nenhum DDL/DML, migration, seed, merge, deploy, exclusão de branch ou publicação. Sem novas fontes normativas externas nesta rodada.
