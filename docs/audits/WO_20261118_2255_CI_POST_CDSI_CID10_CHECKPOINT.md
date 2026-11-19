# CE / CKO / NCOS — checkpoint 2026-11-18 22:55 BRT

## Escopo e baseline
- Repositório IndiciumFIN/calculadorasdeenfermagem, branch audit/ce-supabase-migration-first-20261115, PR #73 aberta/draft; workspace PR #71 aberta/draft. Sem merge.
- Checkpoint anterior: commit 223d9eebade74fc76201ad291436cf2c1e82abaa; docs/audits/WO_20261118_2152_CDSI_CID10_CI_CHECKPOINT.md (blob c7519869ff738663a60844826dce31fcb7264dae).
- Export histórico docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 policies RLS (inventário informado, não recontado nesta rodada). Fingerprints 22/22 PASS histórico; não reprocessados sem delta.
- Fonte física exclusiva: Supabase Calculadoras-Smart pgsybzggewhinaniybiy; SQL apenas SELECT.
- Evidência consultada em 2026-11-18 (BRT); nenhuma fonte normativa externa nova.

## CI após CDSI e CID10
- SHA exato 223d9eebade74fc76201ad291436cf2c1e82abaa: Proveniência PASS [44432637117](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44432637117); Pipeline Determinístico PASS [44432637295](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44432637295); CI-Validação PASS [44432637199](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44432637199); Canonical repository invariants FAIL [44432637062](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44432637062).
- Jobs FAIL: 135253571262 (Canonical contracts and CLI smoke) e 135253571697 (Full admission blockers). Logs inspecionados: 1 LEGACY_SOURCE_DIR, 16 MISSING_PARSER, 5 PACKAGE_IMPORT_NAMESPACE. Nenhum SOURCE_VALIDATOR_SCHEMA listado no filtro dos logs. CI global NO-GO.
- Não executar exclusão de contracts/fonts sem mapa de consumidores, nem criar parsers stubs.

## Supabase (somente SELECT)
- pg_constraint no schema cko_governance: CHECK 61, FK 81, PK 88, UNIQUE 34 = 264. Agregado 1/1 verificado, mas reconciliação semântica export ↔ catálogo 0/1996 nesta rodada.
- Divergência histórica export 1996 vs catálogo global 2109 = 113 de diferença aritmética, sem inferir ausência real antes do crosswalk.

## Branches e PRs
- Branches existentes 4/4 por busca: feat/ce-tools-governed-backend-20261115, feat/cko-catalog-metamodel-automated-20261114, feat/cko-m08-m09-corpus-atomic-20261114, integration/cko-parsers-catalog-20261114. HEAD SHA individual não revalidado 0/4; nenhum merge.
- PR #73 audit/ce-supabase-migration-first-20261115 → main, open/draft; PR #71 fix/ce-tanstack-vercel-build-no-migrations-20261114 → main, open/draft.

## Work orders / fingerprint / risco / aceite
| WO | Objeto/fingerprint | Delta | Status/teste | Risco | Responsável / próxima ação | Aceite |
|---|---|---|---|---|---|---|
| CE-CI-73 | HEAD 223d9eebade74fc76201ad291436cf2c1e82abaa | CI pós CDSI/CID10 confirmado | FAIL 3/4 workflows PASS; 2 jobs FAIL | alto | engenharia: isolar causas por arquivo | 4/4 PASS, smoke executado no mesmo SHA |
| CE-LEGACY-FONTS | contracts/fonts; fingerprint NOT_CAPTURED | LEGACY_SOURCE_DIR persiste | FAIL/HOLD_VERIFY | alto | engenharia: mapear consumidores e equivalências antes de remover | zero regressões e zero consumidores quebrados |
| CE-PARSERS | integration/cko-parsers-catalog-20261114; SHA NOT_CAPTURED | 16 MISSING_PARSER | FAIL, 0/16 corrigidos | alto | engenharia: diff contra branch, testes | 16/16 presentes e testados, sem stubs |
| CE-IMPORTS | 5 PACKAGE_IMPORT_NAMESPACE; fingerprint NOT_CAPTURED | 5 imports bloqueantes | FAIL, 0/5 corrigidos | alto | engenharia: mapear namespace e dependências | 5/5 imports e smoke PASS |
| CE-TOOLS | feat/ce-tools-governed-backend-20261115; SHA NOT_CAPTURED | branch localizada | HOLD_VERIFY, 0/24 revalidadas | alto | engenharia clínica: confrontar contratos e testes | 24/24 validadas com evidência e gates |
| CE-METAMODEL | feat/cko-catalog-metamodel-automated-20261114; SHA NOT_CAPTURED | branch localizada | HOLD_VERIFY | alto | arquitetura: crosswalk com catálogo físico | PK/FK/dicionário/ontologia equivalentes |
| CE-CORPUS | feat/cko-m08-m09-corpus-atomic-20261114; SHA NOT_CAPTURED | branch localizada | HOLD_VERIFY | alto | curadoria: proveniência/licença/duplicatas | átomos rastreáveis e licenciados |
| CE-WORKSPACE-71 | PR #71; SHA NOT_CAPTURED | draft aberto | HOLD_VERIFY | médio | engenharia: comparar escopo, CI e migrações | testes e segurança PASS, merge autorizado |
| CE-SUPABASE | pgsybzggewhinaniybiy / cko_governance | 264 constraints observadas | PASS_READ agregado 1/1; 0/1996 crosswalk | alto | dados: SELECT por schema/tabela/nome/definição | crosswalk completo com divergências justificadas |
| CE-EXPORT | 22 fingerprints históricos (SHAs no checkpoint anterior) | sem delta verificado | PASS_HASH histórico 22/22; NOT_RUN agora | médio | auditoria: repetir apenas com delta | 22/22 sem divergência no mesmo snapshot |

## Métricas e decisão
- CI: 3/4 workflows PASS = 75% de workflows, **não** de conclusão.
- Branches prioritárias localizadas 4/4; HEADs revalidados 0/4.
- Ferramentas 0/24 revalidadas; parsers 0/16 corrigidos; imports 0/5 corrigidos; crosswalk 0/1996 nesta rodada.
- Testes locais/unitários/adversariais NOT_RUN. CI no checkpoint documental novo NOT_RUN.
- Estimativa global de conclusão: NÃO AFERÍVEL; denominadores de homologação incompletos.
- Próximos passos: (1) inventário de contracts/fonts e consumidores; (2) comparar arquivos de parsers da branch com erros do CI; (3) imports e smoke; (4) crosswalk SELECT sem DDL/DML.
- Nenhuma correção funcional nesta rodada; somente diagnóstico, leitura e atualização do programa. Gates clínicos/jurídicos/LGPD/segurança/proveniência permanecem fail-closed. Sem DDL/DML, migrations, seeds, deploy, merge, exclusão ou publicação.
