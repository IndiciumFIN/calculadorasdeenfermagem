# WO — 2026-11-16 02:53 BRT — confronto incremental da branch de parsers

## Escopo e evidência
- Repositório: IndiciumFIN/calculadorasdeenfermagem; destino: audit/ce-supabase-migration-first-20261115 (PR #73).
- HEAD da PR #73 verificado por compare: ef191b8cbaae03b27ce69b168625f42dfe1698ff (identical, ahead=0, behind=0 antes deste checkpoint).
- Branch candidata: integration/cko-parsers-catalog-20261114; compare contra main e0f62491b104f4a97c6025a6393cabc2e7ada30e: 159 commits ahead, 0 behind; comparação contra PR #73: diverged (159 behind, 36 ahead). Não realizar merge cego.
- Arquivo examinado na branch: governance/migrations/2026-11-14/legacy-fonts-reconciliation.json, schema CE-LEGACY-SOURCE-RECONCILIATION-1.0.0.
- Inventário-base da PR #73: docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json, project pgsybzggewhinaniybiy; 59 schemas, 678 relations, 255 migration versions, 7246 columns, 1996 constraints, 1268 indexes, 100 RLS policies; snapshot NON_ATOMIC_ACROSS_QUERIES e HOLD_HUMAN.
- Teste existente na PR: tests/test_repository_integrity_fail_closed.py, blob 5f940f0b32774f3c6d0269a50fd91f5e58583b28; 3 casos, execução de CI nesta rodada NOT_RUN.

## Achado e ação
A branch de parsers já contém uma reconciliação explícita de 20 JSONs legados em contracts/fonts/ com contracts/fontes/, incluindo pares de Git blob SHA1, e declara igualdade semântica após omitir o campo source_contract canônico. Esse é um candidato a reaproveitamento do trabalho anterior, **não** comprovação independente da igualdade ou autorização de apagar arquivos. O compare mostra remoções do diretório legado e modificações dos contratos/políticas; exige revisão de dependências e do CI antes de cherry-pick seletivo.

## Registro incremental
| Unidade | Fingerprint | Último commit/base | Estado | Delta confirmado | Próxima ação |
|---|---|---|---|---|---|
| PR #73 HEAD | ef191b8cbaae03b27ce69b168625f42dfe1698ff | ef191b8 | PASS leitura | 0 | verificar CI novo |
| integration/cko-parsers-catalog-20261114 | compare main...branch: ahead 159, behind 0 | base e0f6249 | CANDIDATE | 159 commits | diff semântico por parser e contrato |
| governance/migrations/2026-11-14/legacy-fonts-reconciliation.json | 20 pares SHA1 declarados no próprio arquivo | branch integration/cko-parsers-catalog-20261114 | HOLD_VERIFY | 20/20 pares documentados, 0/20 revalidados nesta rodada | conferir blobs, imports, links normativos, licenças |
| contracts/fonts/ -> contracts/fontes/ | 20 JSONs conforme manifesto da branch | base e0f6249 | HOLD | 0 correções transferidas | testes de integridade, remoção somente após equivalência |
| tests/test_repository_integrity_fail_closed.py | blob 5f940f0b32774f3c6d0269a50fd91f5e58583b28 | PR #73 | NOT_RUN | 0 | executar pytest e CI |
| 16 MISSING_PARSER / 5 PACKAGE_IMPORT_NAMESPACE | run 43783129926 | PR #73 | HOLD | 0/21 resolvidos | comparar implementações reais sem stubs |

## Gates
Nenhuma migration, DDL/DML, seed, merge, exclusão, mudança de RLS ou publicação. Nenhuma consulta nova ao Supabase nesta rodada; números do manifesto são baseline, não verificação física fresca. Falhas do CI herdadas: 1 FAIL estrutural e 21 HOLD. Homologação clínica 0/24. Rollback do checkpoint documental: revert do commit deste arquivo; não há rollback de banco. Próxima rodada deve validar blobs e executar os testes antes de qualquer cherry-pick.
