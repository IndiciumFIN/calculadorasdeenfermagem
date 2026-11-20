# CE / CKO / NCOS — checkpoint 2026-11-18 20:54 BRT

## Escopo e linha de base
- Fonte física única: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; somente SELECT.
- Branch de auditoria PR #73: `audit/ce-supabase-migration-first-20261115`.
- Checkpoint anterior: `docs/audits/WO_20261118_1950_FHIR_CDC_CI_CHECKPOINT.md` blob SHA `0c9b1839c13af46f5cc2466453973ad3b7741cb4`; commit de referência `4871afba39aa181030095f2fca9d86876d2860cd`. Este registro é aditivo, não reprocessa fingerprints anteriores.
- Export histórico `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/`: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies (inventário informado; não recontado nesta rodada). 22/22 hashes históricos PASS no checkpoint anterior, NÃO revalidados nesta rodada.
- Fontes consultadas: GitHub Actions, branches, PRs e catálogo PostgreSQL em 2026-11-18.

## Evidência nova — CI no HEAD anterior exato
- Commit `4871afba39aa181030095f2fca9d86876d2860cd`: workflow provenance PASS [run 44415511130](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44415511130), CI-Validação PASS [run 44415510994](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44415510994), Pipeline Determinístico PASS [run 44415511038](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44415511038), Canonical repository invariants FAIL [run 44415510969](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44415510969).
- Job `Full admission blockers (fail closed)`: checkout e Python PASS; `Reject unresolved parser or import dependencies` FAIL. Diagnóstico de classe; logs de erro detalhados não extraídos nesta rodada.
- Job `Canonical contracts and CLI smoke`: instalação, compilação e testes negativos PASS; `Verify canonical source and policy references` FAIL; CLI import smoke e kernel policy registry smoke SKIPPED.
- Não declarar que as duas correções FHIR/CDC resolveram invariants. CI global FAIL, PR #73 NO-GO.
- Quatro branches prioritárias localizadas: `feat/ce-tools-governed-backend-20261115`, `feat/cko-catalog-metamodel-automated-20261114`, `feat/cko-m08-m09-corpus-atomic-20261114`, `integration/cko-parsers-catalog-20261114`. HEADs e diffs individuais NOT_RUN nesta rodada.
- Workspace PR #71 localizada: [PR #71](https://github.com/IndiciumFIN/dev-chatgpt-workspace/pull/71), candidato DRAFT/NO-GO; não inferir homologação a partir do preflight histórico.

## Supabase — somente SELECT
`SELECT contype, count(*) AS n FROM pg_constraint WHERE connamespace='cko_governance'::regnamespace GROUP BY contype ORDER BY contype` retornou CHECK 61, FK 81, PK 88, UNIQUE 34, total 264. Agregado igual ao histórico, mas não há prova de equivalência semântica individual. Comparação 1996 vs 2109 permanece HOLD_SEMANTIC; não assumir que diferença de 113 implica criação ou exclusão de objetos.

## Work orders, fingerprints, deltas, riscos e aceite
| WO / objeto | Fingerprint / SHA de referência | Delta nesta rodada | Status / teste | Risco | Responsável / próxima ação | Critério de aceite |
|---|---|---|---|---|---|---|
| CE-CI / PR #73 | commit `4871afba39aa181030095f2fca9d86876d2860cd` | novo diagnóstico de steps no mesmo SHA | 3/4 PASS; global FAIL | alto | engenharia: extrair saída de step e corrigir apenas causas verificadas | 4/4 PASS no mesmo HEAD com smoke executado |
| CE-CONTRACTS / source-policy | CI run 44415510969 | step de referência FAIL após FHIR/CDC | FAIL | alto | engenharia: listar objetos divergentes e cruzar com políticas, testar | invariants PASS sem enfraquecer validador |
| CE-PARSERS / integração | branch `integration/cko-parsers-catalog-20261114`; SHA não aferido | branch localizada, sem delta de código | HOLD_VERIFY; 0/16 parsers e 0/5 imports corrigidos nesta rodada | alto | engenharia: diff de namespace e imports; testes de smoke | admissão PASS sem duplicações |
| CE-TOOLS / 24 ferramentas | branch `feat/ce-tools-governed-backend-20261115`; SHA não aferido | localizada | 0/24 revalidadas nesta rodada; HOLD_VERIFY | clínico alto | engenharia clínica: matriz por ferramenta | 24/24 com teste, proveniência e gate |
| CKO-META | branch `feat/cko-catalog-metamodel-automated-20261114`; SHA não aferido | localizada | NOT_RUN | alto | arquitetura: comparar dicionário, metamodelo, PK/FK | equivalência semântica |
| CKO-M08/M09 | branch `feat/cko-m08-m09-corpus-atomic-20261114`; SHA não aferido | localizada | NOT_RUN | direitos alto | editorial: evidência primária e licenças | átomos admissíveis e rastreáveis |
| CE-SUPABASE / `cko_governance` | agregado 264 histórico | 264, delta agregado 0 | PASS_AGGREGATE, HOLD_SEMANTIC | alto | DBA: SELECT por constraint, PK/FK e definições | reconciliação objeto a objeto |
| CE-WORKSPACE / PR #71 | PR #71; HEAD não aferido | PR localizada | HOLD / NOT_RUN | médio | engenharia: verificar build, auth e preview | gates CI/SSR/auth/RLS e preview aprovados |
| CE-EXPORT / manifesto | 22/22 hashes históricos | nenhum reprocessamento | PASS_HASH histórico, NOT_RUN atual | médio | auditoria: recalcular somente sob delta | fingerprints e integridade reproduzíveis |

## Métricas e controles
- CI no SHA de referência: 3/4 workflows PASS (75% de workflows; não é homologação); 2/2 jobs do workflow falho identificados.
- Branches prioritárias localizadas: 4/4; HEADs revalidados: 0/4.
- Constraints individualmente reconciliadas nesta rodada: 0/1996; agregado governança: 1/1 PASS_READ.
- Ferramentas revalidadas: 0/24; parsers corrigidos: 0/16; imports corrigidos: 0/5.
- Testes locais novos: NOT_RUN; CI após este commit: NOT_RUN.
- **Estimativa global de conclusão: NÃO AFERÍVEL**, falta denominador de homologação.
- **Correções funcionais nesta rodada: nenhuma.** Este commit adiciona evidência e programa persistente; não altera SQL nem contratos.
- Nenhum DDL/DML, migration, seed, deploy, merge, exclusão de branch ou publicação de candidato. Fail-closed, LGPD, segurança, direitos autorais, proveniência e gates clínicos/jurídicos preservados.
