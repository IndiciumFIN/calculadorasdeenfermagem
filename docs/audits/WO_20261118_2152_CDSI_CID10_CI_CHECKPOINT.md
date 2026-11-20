# CE / CKO / NCOS — checkpoint 2026-11-18 21:52 BRT

## Linha de base e escopo
- Repositório: IndiciumFIN/calculadorasdeenfermagem; branch audit/ce-supabase-migration-first-20261115; PR #73 DRAFT / NO-GO.
- Checkpoint anterior: f00e594e5a7fd55bc05ee130344ee655ca3be357; arquivo docs/audits/WO_20261118_2054_CI_CURRENT_HEAD_CHECKPOINT.md, blob 783239827676058f3b568114a80b3c3e6ffbae02.
- Supabase único pgsybzggewhinaniybiy; somente SELECT.
- Export histórico informado em docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies. 22/22 fingerprints históricos PASS, não reprocessados por ausência de delta verificado.
- GitHub Actions e PostgreSQL consultados em 2026-11-18. Nenhum normativo externo novo utilizado.

## CI verificado no SHA exato anterior
- HEAD f00e594e5a7fd55bc05ee130344ee655ca3be357: provenance PASS [44424777007](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44424777007), CI-Validação PASS [44424777061](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44424777061), Pipeline Determinístico PASS [44424777124](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44424777124), Canonical invariants FAIL [44424776990](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44424776990).
- Logs dos jobs 135226659069 e 135226659474: 3 erros de fonte (LEGACY_SOURCE_DIR em contracts/fonts, SOURCE_VALIDATOR_SCHEMA em cdsi.json e cid10.json), 16 MISSING_PARSER e 5 PACKAGE_IMPORT_NAMESPACE. O diretório legacy não foi removido, pois precisa de inventário e verificação de consumidores.
- Dois contratos corrigidos com políticas canônicas consultadas: CDSI KERNEL-POLICY-018 (blob 86a0de62f046de3ad75b901399f96abe521d0493), CID10 KERNEL-POLICY-003 (blob c0c5a672cc7afb998972b31dcd9ccd929448b56e). Sem relaxar fail-closed.

## Mudanças reais
- [CDSI commit 1dfbd4e](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/1dfbd4e280c95b3ec099ca317b2c937cd06b9e20): contracts/fontes/cdsi.json validators string -> ["schema_validator"]; blob 76e339ad20ef95ef9ee90d6264c971ad4292ea8f -> 6259b361765e5f9a0fbc97fbfc92dcf61e96d058.
- [CID10 commit 32bc4d1](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/32bc4d1da782712c5bdcc1ac97ec26b231d4e063): contracts/fontes/cid10.json validators string -> ["cid10_validator","schema_validator"]; blob 2965c7f77fc857fdb2e46f48b4238e94f85f9049 -> a38ab1a1924be155591d2e79e9d4d70b9cd5949a.
- Ambos reabertos no GitHub e comparados às políticas: PASS_STATIC 2/2. Testes unitários locais NOT_RUN; CI nos novos commits NOT_VERIFIED.

## Supabase / reconciliação
- SELECT pg_constraint por tipo em cko_governance: CHECK 61, FK 81, PK 88, UNIQUE 34 = 264; delta agregado 0 versus checkpoint.
- SELECT de 12 definições individuais pg_get_constraintdef, ordenadas por tabela e nome: 12/12 lidas (não equivalem a 12 reconciliações semânticas com export). Incluem PK de account_palm_master_register_v1, FK agent_appointments e FK agent_execution_fronts. Confronto contra SQL candidato/export ainda 0/1996 nesta rodada.
- Divergência histórica 1996 export vs 2109 catálogo global = HOLD_SEMANTIC; não inferir 113 objetos ausentes sem crosswalk por OID/nome/definição.

## Work orders / objetos / risco / aceite
| WO | Fingerprint/SHA | Delta | Status e teste | Risco | Responsável e próxima ação | Critério de aceite |
|---|---|---|---|---|---|---|
| CE-CONTRACT-CDSI | 76e339ad -> 6259b361 | validators array, política 018 | PASS_STATIC; CI NOT_VERIFIED | médio | engenharia: verificar novo CI | política e contrato iguais, CI PASS |
| CE-CONTRACT-CID10 | 2965c7f -> a38ab1a | validators array, política 003 | PASS_STATIC; CI NOT_VERIFIED | médio | engenharia: verificar novo CI | política e contrato iguais, CI PASS |
| CE-CI-73 | f00e594e5a7fd55bc05ee130344ee655ca3be357 | logs específicos obtidos | 3/4 PASS, global FAIL (SHA anterior) | alto | engenharia: checar CI após correções | 4/4 PASS no mesmo HEAD, smoke executado |
| CE-LEGACY-FONTS | contracts/fonts | erro confirmado, sem exclusão | FAIL / HOLD_VERIFY | alto | engenharia: inventariar consumidores e duplicatas | migrar sem quebra, teste de import |
| CE-PARSERS | integration/cko-parsers-catalog-20261114 | 16 MISSING_PARSER no CI | HOLD_VERIFY 0/16 | alto | engenharia: diff e smoke, sem stubs | 16/16 admitidos e testados |
| CE-IMPORTS | packages/cli/validators/registry.py e outros 4 | 5 PACKAGE_IMPORT_NAMESPACE | HOLD_VERIFY 0/5 | alto | engenharia: testar python -m packages.cli.main | imports resolvidos, CI PASS |
| CE-TOOLS | feat/ce-tools-governed-backend-20261115 | sem delta validado | 0/24 revalidadas nesta rodada | clínico alto | engenharia clínica: teste por ferramenta | 24/24 gates, proveniência |
| CKO-META | feat/cko-catalog-metamodel-automated-20261114 | sem delta validado | NOT_RUN | alto | arquitetura: dicionário/PK/FK | equivalência física/semântica |
| CKO-M08/M09 | feat/cko-m08-m09-corpus-atomic-20261114 | sem delta validado | NOT_RUN | direitos alto | editorial: licença/fonte/átomos | evidência primária e rights |
| CE-SUPABASE | pg_constraint cko_governance | 264, delta agregado 0; 12 definições lidas | PASS_READ; HOLD_SEMANTIC | alto | DBA: crosswalk individual com export | 1996/1996 comparados, exceções resolvidas |
| CE-EXPORT | manifesto 22/22 histórico | sem delta verificado | PASS_HASH histórico; NOT_RUN atual | médio | auditoria: recalcular apenas sob delta | integridade reproduzível |
| CE-WORKSPACE | [PR #71](https://github.com/IndiciumFIN/dev-chatgpt-workspace/pull/71) | localizada, sem revalidação do HEAD | HOLD / NOT_RUN | médio | engenharia: CI, preview, auth/RLS | gates completos, preview externo aprovado |

## Métricas e decisão
- Correções selecionadas: 2/2 PASS_STATIC (100% da amostra de 2, não cobertura total).
- CI anterior: 3/4 workflows PASS (75% dos workflows, global FAIL); novo HEAD CI NOT_VERIFIED.
- 2/2 jobs falhos diagnosticados; 3 erros de fonte conhecidos antes destas duas correções, 1 erro legacy ainda sem solução.
- Constraints agregadas 1/1 leitura PASS; 12/12 definições da amostra lidas; 0/1996 reconciliadas semanticamente.
- Ferramentas 0/24 revalidadas; parsers 0/16 corrigidos; imports 0/5 corrigidos; branches prioritárias 4/4 localizadas historicamente, 0/4 HEADs revalidados nesta rodada.
- **Estimativa global de conclusão: NÃO AFERÍVEL**, sem denominador de homologação.
- PR #73 e workspace PR #71 NO-GO. Nenhum DDL/DML, migrations, seeds, merge, deploy, exclusão de branches ou publicação. Fail-closed, LGPD, segurança, direitos autorais e gates clínicos/jurídicos preservados.
