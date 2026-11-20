# CE / CKO / NCOS — checkpoint 2026-11-18 23:52 BRT

## Baseline e limites
- Base confirmada: commit 5de2d3fd43565eb022999d211385ffb3cbb3abf6; checkpoint anterior blob 71fcad6a027bcb74cdeb7202cea897112064267c. Branch de trabalho audit/ce-supabase-migration-first-20261115, PR #73. Nenhum merge.
- Export docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/: inventário **informado** 59 schemas / 678 relações / 255 migrations / 7246 colunas / 1996 constraints / 1268 índices / 100 RLS; fingerprints 22/22 PASS **histórico**, não reprocessados. Sem validação de equivalência nesta rodada.
- Supabase exclusivo pgsybzggewhinaniybiy, SELECT apenas. Nenhuma fonte normativa externa nova. Data de leitura 2026-11-18 BRT.

## CI do checkpoint anterior (SHA exato 5de2d3fd43565eb022999d211385ffb3cbb3abf6)
- PASS provenance [44440648131](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44440648131), pipeline [44440648123](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44440648123), validação [44440648221](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44440648221).
- FAIL canonical [44440648105](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44440648105); jobs 135280341919 (admission) e 135280342311 (contracts). Compilação e testes negativos PASS; CLI/policy smoke SKIPPED. Logs completos não relidos nesta rodada; classes de erros 1 legacy dir, 16 parsers, 5 imports são evidência do checkpoint anterior e não foram recontadas aqui.

## Evidência nova de branches (comparação main...branch)
- feat/ce-tools-governed-backend-20261115: ahead 15, behind 0. Manifest docs/ecossistema/governed-tools/MANIFEST_v0.1.0.json blob a conferir; status interno CANDIDATE_NOT_DEPLOYED. Contém candidato SQL e seed: NÃO EXECUTAR.
- feat/cko-catalog-metamodel-automated-20261114: ahead 22, behind 0; diff inclui remoção dos arquivos contracts/fonts/*.json, potencial solução para LEGACY_SOURCE_DIR, mas dependências/consumidores ainda NÃO validados. Não aplicar exclusão automaticamente.
- feat/cko-m08-m09-corpus-atomic-20261114: ahead 8, behind 0; inclui arquivos ZIP e validadores, conteúdo e licenças não homologados.
- integration/cko-parsers-catalog-20261114: ahead 163, behind 0; diff inclui alterações de contratos/fontes e workflows, candidato de reaproveitamento para parsers/imports; não realizar merge indiscriminado.
- Comparações confirmam base e0f62491b104f4a97c6025a6393cabc2e7ada30e para as quatro branches; HEADs individuais não retornados pelo endpoint de comparação, portanto 0/4 HEAD SHA capturados.
- contracts/fonts/DIRECTORY_OBSOLETO.json blob e9d6f77c80a9fcc0e45f3e444729bc5e548be870 declara renomeação para contracts/fontes/ em 2026-10-17; é indício documental, não prova ausência de consumidores.

## Catálogo físico SELECT
- SELECT pg_constraint WHERE connamespace='cko_governance'::regnamespace: CHECK 61 / FK 81 / PK 88 / UNIQUE 34 = 264 (PASS_READ).
- SELECT pg_constraint para namespaces não-sistema: 1997 constraints, sendo 681 FK e 610 PK. **A diferença aritmética com export informado 1996 é 1 sob este filtro**, NÃO equivale a crosswalk 1996/1996. O histórico 2109 usava escopo não confirmado; não comparar sem harmonizar filtros, snapshots e objetos.
- Nenhuma consulta de escrita, migration, seed ou DDL.

## Work orders versionadas
| WO | Objeto / fingerprint ou SHA | Delta | Estado / teste | Risco | Responsável e próxima ação | Aceite |
|---|---|---|---|---|---|---|
| CE-CI-73 | commit 5de2d3fd43565eb022999d211385ffb3cbb3abf6 | CI do SHA verificado | FAIL: 3/4 workflows; smoke skipped | alto | engenharia: ler logs e mapear erros atuais | 4/4 PASS + smoke no mesmo SHA |
| CE-LEGACY | contracts/fonts/DIRECTORY_OBSOLETO.json blob e9d6f77c80a9fcc0e45f3e444729bc5e548be870 | renomeação documental confirmada; remoção proposta em branch metamodelo | HOLD_VERIFY | alto | engenharia: buscar consumidores e testar diff isolado | sem consumidores/regressões, CI PASS |
| CE-PARSERS | integration/cko-parsers-catalog-20261114; fingerprint de arquivos NOT_CAPTURED | diff 163 commits ahead | FAIL histórico 0/16 corrigidos nesta rodada | alto | engenharia: inventariar implementações reais, comparar com erros | 16/16 dependências resolvidas e testadas |
| CE-IMPORTS | 5 PACKAGE_IMPORT_NAMESPACE histórico; fingerprint NOT_CAPTURED | nenhuma correção | FAIL histórico 0/5 | alto | engenharia: localizar módulos e smoke | 5/5 PASS |
| CE-TOOLS | feat/ce-tools-governed-backend-20261115; manifest CANDIDATE_NOT_DEPLOYED | 15 commits ahead | HOLD_VERIFY 0/24 ferramentas revalidadas | alto | clínica/engenharia: testes, auth, RLS, não executar SQL | 24/24 evidenciadas com gates |
| CE-METAMODEL | feat/cko-catalog-metamodel-automated-20261114 | 22 ahead; remoção legacy | HOLD_VERIFY | alto | arquitetura: equivalência PK/FK/dicionário | crosswalk e testes |
| CE-CORPUS | feat/cko-m08-m09-corpus-atomic-20261114 | 8 ahead | HOLD_VERIFY | alto | curadoria: verificar licença, proveniência, átomos e dedup | átomos com fonte/licença |
| CE-WORKSPACE-71 | PR #71; SHA NOT_CAPTURED | não revisada nesta rodada | NOT_RUN | médio | engenharia: conferir CI, diff e migrations | revisão e autorização |
| CE-SUPABASE | pgsybzggewhinaniybiy; query namespaces não-sistema | 1997 constraints sob filtro explícito | PASS_READ agregado; 0/1996 crosswalk | alto | dados: crosswalk por nome, schema, PK/FK, definição e snapshot | equivalência justificada por objeto |
| CE-EXPORT | 22 fingerprints históricos | nenhum delta demonstrado | PASS_HASH histórico 22/22; NOT_RUN agora | médio | auditoria: revalidar apenas com delta | hashes coerentes no mesmo snapshot |

## Métricas e decisão
- CI 3/4 PASS (75% **de workflows**, não progresso de projeto); 2 jobs FAIL; smoke SKIPPED.
- Branches comparadas 4/4, HEAD SHA capturados 0/4; 24 ferramentas revalidadas 0/24; parsers corrigidos 0/16; imports corrigidos 0/5; crosswalk semântico 0/1996 nesta rodada.
- Testes locais/adversariais NOT_RUN; CI deste novo commit NOT_RUN. Estimativa global: **NÃO AFERÍVEL**, denominador de aceite não consolidado.
- Nenhuma correção funcional nesta rodada. Próximas ações: inventário de consumidores legacy; reaproveitamento seletivo da branch de parsers; corrigir imports e rodar smoke; reconciliar constraints com filtros iguais e fingerprints.
- Gates clínico, jurídico, segurança, LGPD, copyright e proveniência: FAIL-CLOSED. Candidatos não publicados. Sem DDL/DML, migrations, seeds, merge, deploy, exclusão de branches.
