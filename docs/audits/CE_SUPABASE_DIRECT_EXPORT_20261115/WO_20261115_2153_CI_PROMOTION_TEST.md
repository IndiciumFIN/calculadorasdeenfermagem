# WO-20261115-2153 — CI do predicado de promoção

Escopo: Calculadoras-Smart `pgsybzggewhinaniybiy`, somente SELECT; PR #73; branch `audit/ce-supabase-migration-first-20261115`.

## Alteração executada
- Workflow `.github/workflows/ce-migration-provenance.yml` atualizado no commit `d451d13c825a5b652e82f161ab8f33096cb96514`.
- Adicionado filtro de path `tests/test_cko_promotion_status_predicate.py` ao gatilho pull_request e passo de execução `python -m unittest discover -s tests -p "test_cko_promotion_status_predicate.py" -v`.
- Suíte já existente: blob `fab2add51f5137a9c1a5c84bf869f3fcc9f3eb84`, commit `a3c93a2cef37c469b4b8cd93805f33ec7c2e1648`.
- Nenhuma política de publicação foi alterada: testes apenas caracterizam o predicado atual.

## Evidência física
- SELECT `count(*),count(DISTINCT status)` em `cko_governance.controlled_artifacts`: 530 linhas e 30 estados em 2026-11-15.
- Manifest PR #73: 59 schemas, 678 relações, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies, 255 migrations. Snapshot não atômico; não presumir equivalência integral ao estado atual.

## Gates e registro incremental
| Objeto | Fingerprint/commit | Estado | Próxima ação |
|---|---|---|---|
| Workflow CE | `d451d13c825a5b652e82f161ab8f33096cb96514` | PASS_CODE / CI_PENDING | verificar execução Actions e logs |
| Teste predicado | blob `fab2add51f5137a9c1a5c84bf869f3fcc9f3eb84` | PASS_PREVIOUS_OFFLINE / CI_PENDING | verificar resultado exato do arquivo commitado |
| `cko_governance.controlled_artifacts.status` | 530 registros; 30 estados, SELECT 2026-11-15 | PASS_CATALOG | comparar delta em próxima rodada |
| 24 ferramentas | branch `feat/ce-tools-governed-backend-20261115` | HOLD_SEMANTIC | confrontar SQL candidato com catálogo |

Sem migration, seed, DDL/DML, merge ou publicação. HOLD_HUMAN para equivalência clínica, licenciamento, LGPD e release. CI ainda não observado como PASS; não confundir mudança de workflow com teste executado.
