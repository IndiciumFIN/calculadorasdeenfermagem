# CE / CKO / NCOS — programa incremental — 2026-11-16 08:02 BRT

## Fonte de verdade e limites
- Supabase: `pgsybzggewhinaniybiy` (Calculadoras-Smart), somente SELECT; nenhum DDL/DML.
- Repositório: `IndiciumFIN/calculadorasdeenfermagem`; integração seletiva, sem merge.
- Base main observada no compare: `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.
- Branch `integration/cko-parsers-catalog-20261114`: 161 commits à frente da main, 0 atrás **antes do novo commit**.
- PR #73: integração/publicação HOLD_VERIFY; estado atual da PR não reconsultado nesta rodada.

## Fingerprint ledger / ações
| Objeto | Fingerprint observado | Estado | Delta / evidência | Próxima ação |
|---|---|---|---|---|
| `contracts/fontes/anvisa_dev.json` | git blob `54372d627c73a7b9ccdb8ce9b39281fd15d22e55` | HOLD_VERIFY | validators é array; source_contract canônico; divergência de hash do manifesto legado | reconciliar manifesto por conteúdo semântico |
| `contracts/fontes/anvisa_dou.json` | git blob `7ad43853784754937320425833cebfd94c24f868` | HOLD_VERIFY | validators é array; source_contract canônico | conferir manifest e política |
| `packages/cli/parsers/anvisa_dev.py` | não aferido | HOLD_VERIFY | caminho declarado no contrato | executar teste no CI |
| `packages/cli/adapters/dou.py` | não aferido | HOLD_VERIFY | caminho declarado no contrato | executar teste no CI |
| `tests/test_cko_anvisa_contract_paths_fail_closed_20261116.py` | commit `c85bef97c734f6373ffdbe6d30197c00dc929558` | IMPLEMENTED / NOT_RUN | teste offline de canonical path, validators, kernel policy, parser path e arquivo | CI executar `python -m unittest discover -s tests -p 'test_cko_anvisa_contract_paths_fail_closed_20261116.py'` |
| Supabase `pg_class` por relkind | SELECT 2026-11-16 | PASS contagem, HOLD semântica | r=611, p=1, v=49, S=17 = 678; índices i=1266, I=2 = 1268; composite c=5 excluídos | comparar 7246 colunas, 1996 constraints e 100 policies por objeto |
| 24 ferramentas clínicas | não aferido individualmente | HOLD_HUMAN | 0/24 homologadas | mapear código + SQL candidato + RLS |

## Evidência de banco — SELECT somente
`SELECT c.relkind, count(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname NOT IN ('pg_catalog','information_schema') AND n.nspname NOT LIKE 'pg_toast%' AND n.nspname NOT LIKE 'pg_temp%' GROUP BY c.relkind ORDER BY c.relkind`.

Retorno: `I=2, S=17, c=5, i=1266, p=1, r=611, v=49`. A soma das relações de escopo é 678; índices 1268. Não equivale a validação semântica nem comprova RLS.

## Testes, gates e métricas
- Teste novo: **commitado**, **NOT_RUN** (nenhum runner executado nesta rodada).
- Pares ANVISA com fingerprint lido: 2/20; pares com equivalência semântica homologada: 0/20.
- Parsers faltantes no gate histórico: 16; corrigidos e revalidados nesta rodada: 0/16.
- Ferramentas clínicas homologadas: 0/24.
- Relações inventariadas quantitativamente: 678/678; relações semanticamente homologadas nesta rodada: 0/678.
- Percentual global: **não aferível** até matriz de aceite por camada; não usar estimativa gerencial 65% como conclusão auditada.
- HOLD_HUMAN: publicação clínica, segurança/LGPD, licenciamento, proveniência, migrations e merge.

## Plano de execução seguinte
1. Rodar teste ANVISA no CI e corrigir qualquer falha sem afrouxar validação.
2. Conferir os outros 18 pares e recuperar manifesto histórico; não normalizar SHA divergente automaticamente.
3. Reconciliar 16 parsers e 5 imports por diff semântico; transportar apenas correções testadas.
4. Verificar PK/FK/RLS das 24 ferramentas contra catálogo físico Supabase com SELECT.
5. Atualizar este ledger com SHA por arquivo e objeto de banco, WOs e PASS/FAIL/HOLD.

Nenhum deploy, seed, migration, DDL/DML, merge ou exclusão de branch foi executado.
