# CE / CKO / NCOS — checkpoint 2026-11-19 08:55 BRT

## Proveniência e controle
PR #73: audit/ce-supabase-migration-first-20261115; HEAD de entrada `38edfcf2420f3caff5ed28db1a493625eca1acfd`. Checkpoint anterior `WO_20261119_0750_CI_LOGS_MANIFEST_CHECKPOINT.md`, blob `0b2cae542b595bb5eb942e35dc6fa4b5b65c5598`. Export `CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json`, blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`. Banco exclusivo `pgsybzggewhinaniybiy`. Somente SELECT; nenhuma migration ou publicação.

## Delta desta rodada
- GitHub Actions no HEAD de entrada: 3/4 workflows PASS (Pipeline Determinístico, CE Migration-first provenance, CI - Validação); Canonical repository invariants FAIL. Não inferir correção a partir de checks antigos.
- Comparação `main...integration/cko-parsers-catalog-20261114`: 163 commits à frente; mudanças verificadas em `packages/cli/parsers/__init__.py`, `anvisa_dev.py`, `anvisa_med.py`, `packages/cli/main.py`, `packages/cli/kernel/cli.py` e `wo_preflight.py`. A branch também remove `contracts/fonts/*`; exclusão **não autorizada** sem mapa de consumidores e testes. Trata-se de **candidatos a reaproveitamento**, não de correções integradas. O diff de main não prova compatibilidade com a PR #73: comparar especificamente os dois HEADs antes de cherry-pick.
- SELECT em `pg_catalog.pg_constraint` + `pg_namespace`: `ce_platform` 252 (3 CHECK, 135 FK, 96 PK, 18 UNIQUE); `cko_governance` 264 (61,81,88,34); `public` 197 (53,71,48,25). Total 713. Contagem sem delta; não repetir comparação individual sem fingerprint alterado.
- Export histórico NON_ATOMIC_ACROSS_QUERIES/HOLD_HUMAN: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 policies. 8/1996 constraints com crosswalk semântico histórico; 0 novos nesta rodada.

## Programa persistente — work orders
| WO | Objeto / SHA ou fingerprint | Delta | Status | Risco | Teste / aceite | Responsável e próxima ação |
|---|---|---|---|---|---|---|
| CE-01 | PR73 HEAD 38edfcf; workflow Canonical | FAIL permanece | FAIL | alto | guard e smoke PASS sem reduzir gates | Engenharia: extrair patches mínimos, executar CI |
| CE-02 | integration/cko-parsers-catalog-20261114; paths packages/cli/parsers/* | implementação candidata localizada | HOLD_HUMAN | alto | imports, parsers reais, testes negativos e proveniência | Engenharia: comparar HEADs e portar seletivamente |
| CE-03 | contracts/fonts/* vs contracts/fontes/* | remoções na branch de integração | HOLD_HUMAN | alto | mapa completo de consumidores e regressão | Engenharia: não excluir sem prova |
| CE-04 | packages/cli/main.py e kernel/cli.py | diferenças candidatas | HOLD_HUMAN | médio | python -m packages.cli.main + smoke | Engenharia: corrigir namespace sem stub |
| CE-05 | manifest blob 8099e3ff | sem delta identificado | PASS_READ | médio | verificar hashes somente se delta | Auditoria: manter fingerprint |
| CE-06 | pg_constraint schemas ce_platform/cko_governance/public | 713 sem delta | PASS_READ | médio | SELECT e harmonização de escopo | Dados: crosswalk por identidade |
| CE-07 | constraints.jsonl, 8/1996 histórico | 0 novas | HOLD_HUMAN | alto | definição PK/FK/CHECK, deferrability, snapshot | Dados: lote novo sem duplicar fingerprints |
| CE-08 | feat/ce-tools-governed-backend-20261115, 24 ferramentas | não inspecionado nesta rodada | NOT_RUN | alto | 24/24 testes e gates clínicos | Clínico/engenharia: validar |
| CE-09 | feat/cko-catalog-metamodel-automated-20261114 | não inspecionado nesta rodada | NOT_RUN | alto | metamodelo/dicionário, sem tabelas concorrentes | Arquitetura: comparar |
| CE-10 | feat/cko-m08-m09-corpus-atomic-20261114 | não inspecionado nesta rodada | NOT_RUN | alto | proveniência/licença/atomização | Editorial: comparar |
| CE-11 | workspace PR #71 | não inspecionado nesta rodada | NOT_RUN | médio | CI, auth, preview, homologação independente | Front-end: verificar |

## Cobertura verificável
- Workflows HEAD entrada: 3/4 PASS, global FAIL.
- Parsers corrigidos nesta rodada: 0/16; imports: 0/5; ferramentas revalidadas: 0/24.
- Constraints semanticamente reconciliadas: 8/1996 histórico = 0,40%; nesta rodada 0 novas.
- Branch de parsers: 1/1 comparação com main, **não** homologação.
- Testes locais: NOT_RUN. CI do novo commit: NOT_RUN.
- Estimativa global de conclusão: **não aferível**, sem denominador completo de aceites técnicos, clínicos e jurídicos.

## Decisão
NO-GO / fail-closed. Não houve código funcional alterado, DDL/DML, seeds, migrations, merge, deploy, exclusões ou publicação. Próximo ciclo: confronto PR73 vs branch de parsers e correção mínima testável, sem reprocessar fingerprints estáveis. Fontes: GitHub PR73/compare/Actions consultados em 2026-11-19; Supabase PostgreSQL SELECT em 2026-11-19.
