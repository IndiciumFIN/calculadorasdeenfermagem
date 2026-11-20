# CE / CKO / NCOS — programa de trabalho — 2026-11-19 14:54 BRT

## Escopo, checkpoint, controle de delta
Projeto físico exclusivo Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. Checkpoint precedente `b4880ebadf5aaacf783768186a7de7e472fa083b`; branch `audit/ce-supabase-migration-first-20261115`; PR #73 DRAFT/NO-GO. Main verificada `e0f62491b104f4a97c6025a6393cabc2e7ada30e`, branch 138 commits à frente e 0 atrás na comparação anterior à escrita. Manifesto `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json` relido, observação 2026-11-15, `NON_ATOMIC_ACROSS_QUERIES`, `HOLD_HUMAN`, 22 arquivos. Não tratar contagem como homologação.

## Delta de código efetivo
- WO-KERNEL-GATE: `packages/cli/kernel/core.py`, blob anterior `7097a142c62bdf9c15f0fde4dadb5a97dd3a6f16`, novo `629c506ed89fa615490ed4049d25c57fb9a4ddf0`, commit `d13505aa90171dc5fe608b9db88372a4b4b15323`. Fingerprint Git blob alterado. Alteração: validador sem `run_tests` não pode mais ser aprovado pelo gate, retorna exit 2. Risco médio (comportamento de admissão); status PASS_WRITE/HOLD_TEST. Responsável Engenharia; aceite: teste positivo com validador implementado, negativo sem `run_tests`, CI e smoke, sem bypass. Testes novos NOT_RUN.
- WO-CLI-NS: `packages/cli/kernel/__init__.py` blob `f39feaf9ac6445595d3ba35dbe27b86120ebaeb0`; `packages/cli/kernel/core.py` blob atualizado acima; `packages/cli/validators/registry.py` blob `65242eb3b9be2ac24eeef2f3318e8c1b8dda101e`. 3/3 arquivos editados anteriormente, 0/3 homologados. Status HOLD_TEST; responsável Engenharia; aceite import smoke e ausência de import circular.
- WO-CI-73: workflows do checkpoint `b4880eba`: Pipeline Determinístico PASS run 44572058662; CI-Validação PASS run 44572058841; Proveniência Supabase PASS run 44572058553; Canonical repository invariants FAIL run 44572058906. 3/4 PASS, global FAIL. CI após novo commit NOT_RUN/NOT_OBSERVED; responsável Engenharia; aceite 4/4 green e gates adicionais.
- WO-PARSER-16: branch `integration/cko-parsers-catalog-20261114`, 0/16 homologados; fingerprint individual ainda não consolidado, HOLD_VERIFY. Responsável Integração; aceite parser real, testes, licença/proveniência e contrato.
- WO-TOOLS-24: branch `feat/ce-tools-governed-backend-20261115`, 0/24 revalidadas, HOLD_VERIFY; responsável Engenharia clínica; aceite contratos, testes e veto segurança.
- WO-METAMODEL: branch `feat/cko-catalog-metamodel-automated-20261114`, denominador não aferido, HOLD_VERIFY; responsável CKO; aceite crosswalk semântico/dicionário/terminologias.
- WO-CORPUS: branch `feat/cko-m08-m09-corpus-atomic-20261114`, denominador não aferido, HOLD_VERIFY; responsável Conteúdo; aceite licenças, proveniência, normativos oficiais datados; não reprocessar fingerprint sem delta.
- WO-PG-CROSSWALK: `constraints.jsonl` fingerprint manifesto `83642780302397204b39796e1bd3604a77c68f53`, 8/1996 (0,40%) reconciliações históricas, 0 novas; status HOLD_SEMANTIC. Responsável Dados; aceite confronto individual PK/FK, definição, dicionário, metamodelo, normativos e átomos. Consulta SELECT desta rodada confirmou 713 constraints nos schemas ce_platform 252, cko_governance 264 e public 197, sem alteração física.
- WO-WORKSPACE-71: `IndiciumFIN/dev-chatgpt-workspace` main `dacfaa6bc29fd213ffc4d63998b4dd669d10854b`; PR #71 não revalidada individualmente, HOLD_VERIFY. Responsável Integração; aceite revisão independente antes de integração.

## Inventário do manifesto (não homologação)
59 schemas; 678 relações; 255 migrations; 7246 colunas; 1996 constraints; 1268 índices; 100 RLS policies. Snapshot não atômico; sem DDL/DML.

## Percentuais e bloqueios
CI histórico 3/4 (75%, FAIL global); imports homologados 0/3 (0%); parsers 0/16 (0%); ferramentas 0/24 (0%); constraints reconciliadas historicamente 8/1996 (0,40%). Gate de kernel: 1 alteração implementada / 1 proposta (100% edição), 0/1 homologada. Metamodelo, corpus, LGPD e jurídico sem denominadores confiáveis. **Estimativa global: NÃO AFERÍVEL**. Nenhum candidato promovido. Bloqueios: invariantes CI, parsers, testes CLI/Kernel, licenças e proveniência.

## Segurança e próximas ações
Não houve DDL/DML, migrations, seeds, merges, deploy, exclusões de branch ou publicação. Preservar fail-closed, LGPD, direitos autorais, proveniência e revisão clínica/jurídica. Próxima rodada: verificar CI do novo HEAD, testar `Kernel.gate` em casos positivo/negativo, resolver imports/parsers por delta, crosswalk individual SELECT-only. Fontes desta rodada: GitHub conectado e catálogo PostgreSQL do projeto indicado em 2026-11-19; nenhum normativo externo novo utilizado.
