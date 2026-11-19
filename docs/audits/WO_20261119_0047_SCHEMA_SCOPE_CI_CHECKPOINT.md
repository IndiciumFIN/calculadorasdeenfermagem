# CE / CKO / NCOS — checkpoint 2026-11-19 00:47 BRT

## Fonte e limites
- Repositório IndiciumFIN/calculadorasdeenfermagem; PR #73 OPEN/DRAFT, HEAD confirmado `7d667157e972171d9b9b22c18e1091fc800ce666`, base main `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. PR workspace #71 OPEN/DRAFT, HEAD `1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d`. Sem merges.
- Checkpoint anterior lido por blob SHA `4a2d2514618635098fe3ae9973feada8a06b9650` em `docs/audits/WO_20261118_2352_BRANCH_CI_PG_SCOPE_CHECKPOINT.md`. Não reprocessar fingerprints sem delta.
- Export `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/`: 59 schemas / 678 relações / 255 migrations / 7246 colunas / 1996 constraints / 1268 índices / 100 RLS são inventário **informado**, não reconciliação validada. 22/22 hashes PASS histórico; NOT_RUN nesta rodada.
- Banco único pgsybzggewhinaniybiy; SELECT apenas. Sem fontes normativas externas novas nesta rodada.

## CI atual (HEAD exato)
GitHub Actions por SHA `7d667157e972171d9b9b22c18e1091fc800ce666`: Canonical repository invariants FAIL; CI - Validação PASS; Pipeline Determinístico PASS; CE Migration-first Supabase provenance (NO SQL) PASS. Resultado 3/4 workflows PASS; global FAIL. Jobs/smoke atuais não relidos: NOT_RUN. CI deste novo checkpoint: NOT_RUN.

## Branches: comparações main...branch reexecutadas
| Branch | Ahead | Behind | Arquivos alterados | Base SHA |
|---|---:|---:|---:|---|
| feat/ce-tools-governed-backend-20261115 | 15 | 0 | 33 | e0f62491b104f4a97c6025a6393cabc2e7ada30e |
| feat/cko-catalog-metamodel-automated-20261114 | 22 | 0 | 48 | e0f62491b104f4a97c6025a6393cabc2e7ada30e |
| feat/cko-m08-m09-corpus-atomic-20261114 | 8 | 0 | 8 | e0f62491b104f4a97c6025a6393cabc2e7ada30e |
| integration/cko-parsers-catalog-20261114 | 163 | 0 | 175 | e0f62491b104f4a97c6025a6393cabc2e7ada30e |

HEAD SHAs individuais ainda NOT_CAPTURED 0/4; comparações 4/4 PASS_READ. Contagem de commits não é progresso.

## PostgreSQL: nova evidência de escopo
Consulta `SELECT n.nspname, count(*) FROM pg_constraint c JOIN pg_namespace n ON n.oid=c.connamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%' GROUP BY n.nspname ORDER BY n.nspname`.
- Retornaram **43 schemas com constraints** (não é total de schemas físicos). Exemplos de escopo misturado: auth 110, storage 26, realtime 5, supabase_migrations 2, contabilidade_cfc 33, cko_governance 264, ce_platform 252, public 197.
- O agregado histórico 1997 inclui namespaces operacionais/de terceiros e alheios ao escopo clínico; portanto a diferença 1997 vs export 1996 **não deve ser interpretada como um objeto faltante**. Antes de crosswalk, definir conjunto de schemas e tipos de constraints por snapshot e classificar cada objeto. Não consultar conteúdo contábil; apenas nome de schema apareceu na enumeração de metadados.
- Sem comparação individual por nome/definição nesta rodada: 0/1996; FAIL-CLOSED.

## Work orders e critérios de aceite
| WO | Objeto / fingerprint | Delta nesta rodada | Status / teste | Risco | Responsável / ação seguinte | Aceite |
|---|---|---|---|---|---|---|
| CE-CI-73 | PR #73 HEAD 7d667157... | quatro workflows atuais verificados | FAIL 3/4; smoke NOT_RUN | alto | engenharia: inspecionar jobs e corrigir isoladamente | 4/4 PASS e smoke mesmo SHA |
| CE-PG-SCOPE | pg_constraint / filtro SELECT acima | 43 schemas com constraints e escopo misto confirmado | PASS_READ; crosswalk HOLD | alto | dados: definir whitelist de schemas, tipos, snapshot e chaves | 1996/1996 classificados, divergências justificadas |
| CE-EXPORT | 22 fingerprints históricos | sem delta demonstrado | PASS_HASH histórico; NOT_RUN agora | médio | auditoria: revalidar apenas delta | hash e snapshot coerentes |
| CE-TOOLS | feat/ce-tools-governed-backend-20261115 | 15 ahead, 33 arquivos | HOLD_VERIFY 0/24 | alto | engenharia/clínica: autenticação, RLS, testes | 24/24 com gates |
| CE-METAMODEL | feat/cko-catalog-metamodel-automated-20261114 | 22 ahead, 48 arquivos | HOLD_VERIFY | alto | arquitetura: PK/FK/dicionário e consumidores legacy | equivalência demonstrada |
| CE-CORPUS | feat/cko-m08-m09-corpus-atomic-20261114 | 8 ahead, 8 arquivos | HOLD_VERIFY | alto | curadoria: licença, fonte e dedup | átomos licenciados e rastreáveis |
| CE-PARSERS | integration/cko-parsers-catalog-20261114 | 163 ahead, 175 arquivos | FAIL histórico 0/16 resolvidos nesta rodada | alto | engenharia: mapear imports e arquivos | 16/16 PASS |
| CE-IMPORTS | 5 problemas históricos; fingerprint NOT_CAPTURED | nenhum | FAIL histórico 0/5 corrigidos | alto | engenharia: testes smoke isolados | 5/5 PASS |
| CE-LEGACY | contracts/fonts/DIRECTORY_OBSOLETO.json blob e9d6f77c80a9fcc0e45f3e444729bc5e548be870 | nenhum | HOLD_VERIFY | alto | engenharia: inventário consumidores antes de exclusão | ausência de regressões |
| CE-WORKSPACE-71 | PR #71 HEAD 1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d | SHA capturado, OPEN/DRAFT | HOLD_BUILD/RELEASE; CI atual NOT_RUN | alto | engenharia: CI, preview e auth/RLS | gates independentes e aprovação |

## Métricas / decisão
- CI 3/4 PASS (75% dos workflows, não do projeto); branches comparadas 4/4; HEADs individuais 0/4; ferramentas 0/24 revalidadas; parsers 0/16 corrigidos nesta rodada; imports 0/5 corrigidos; crosswalk 0/1996.
- Testes unitários/adversariais locais NOT_RUN; SQL de escrita NOT_RUN; CI do commit novo NOT_RUN.
- Estimativa global de conclusão: **NÃO AFERÍVEL** (sem denominador de aceite consolidado).
- Nenhuma correção funcional nesta rodada; atualização documental com nova evidência física de escopo. NO-GO PR #73 e PR #71; não executar DDL/DML, migrations, seeds, merges, deploy ou exclusão de branches. Preservar LGPD, direitos autorais, proveniência, gates clínicos/jurídicos e fail-closed.
