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


---

# Rodada incremental — 2026-11-19 09:53 BRT (checkpoint técnico)

## Estado físico e hashes verificados
- PR #73 branch `audit/ce-supabase-migration-first-20261115`; HEAD de entrada `0ebc24b8f3b18d4726d4536059f67a63505adddf` (confirmado via compare).
- Comparação direta **PR73 → integration/cko-parsers-catalog-20261114**: diverged; integração 163 commits ahead e 128 behind; merge-base `e0f62491b104f4a97c6025a6393cabc2e7ada30e`. **Não fazer cherry-pick geral**.
- Export `MANIFEST.json` blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14` (sem delta); `constraints.jsonl` blob histórico `83642780302397204b39796e1bd3604a77c68f53`. 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies. NON_ATOMIC_ACROSS_QUERIES/HOLD_HUMAN.
- Supabase exclusivo `pgsybzggewhinaniybiy`: SELECT em `pg_constraint` para 15 definições PK/FK de `ce_platform` (alert_rules, applications, assessments, attempts, calendar_events, canonical_objects); **15/15 PASS_READ, 0 novas equivalências com export**. Não confundir leitura com reconciliação.
- GitHub fonte: branches, compare e arquivos consultados em 2026-11-19; Supabase catálogo físico consultado em 2026-11-19.

## Mudanças funcionais efetivamente commitadas (sem merge)
1. `packages/cli/main.py`: blob `79fe358e7698c0eddf70357fac696daac0abc1e6` → `bec5bfa0db972988495dd847c4a4df4c7887a2ee`; commit `6992e3eb45ae8802aff091554e74298ac56e5ac5`. Imports absolutos corrigidos para `packages.cli.kernel.*` e `packages.cli.validators.*`; validação sem átomos e decisão PENDING_REVIEW passam a exit 2 (fail-closed).
2. `packages/cli/kernel/cli.py`: blob `a1c15dba3e9a1d36c39f5fe7af14b52b22b0c328` → `66c9efb6e6e47c228d1a261f82af6b47e53c84c3`; commit `2d14b19effade8604e4d9be37be06974dc6f9374`. Mesma correção de namespace e HOLD bloqueante.
3. Portabilidade **seletiva** de semântica da branch de integração, sem importar parsers nem remover `contracts/fonts`. Revisão textual dos seis fragmentos esperados por arquivo: PASS_SOURCE_MATCH. **Execução Python, testes de smoke, negativos e CI: NOT_RUN / NOT_OBSERVED**, não alegar correção integral dos cinco imports nem aprovação.

## Work orders incrementais / critério de aceite
| WO | Arquivo/objeto, fingerprint e delta | Estado | Risco | Teste e aceite | Responsável / ação seguinte |
|---|---|---|---|---|---|
| CE-01 | PR73 HEAD de entrada `0ebc24b8`; dois commits de código acima | IN_PROGRESS | alto | CI 4/4 PASS, invariantes sem afrouxar guard | Engenharia: verificar CI no HEAD final |
| CE-02 | `packages/cli/main.py`, blob `bec5bfa0`; 6 mudanças direcionadas | PASS_SOURCE_MATCH / HOLD_TEST | alto | `python -m packages.cli.main --help`, gate negativo e validação PENDING_REVIEW exit 2 | Engenharia: rodar testes |
| CE-03 | `packages/cli/kernel/cli.py`, blob `66c9efb6`; 6 mudanças direcionadas | PASS_SOURCE_MATCH / HOLD_TEST | alto | import do módulo, gate sem política, PENDING_REVIEW exit 2 | Engenharia: rodar testes |
| CE-04 | Branch parsers, merge-base `e0f62491`, 163 ahead/128 behind | PASS_COMPARE / HOLD_INTEGRATION | alto | 16 parsers com proveniência e testes, sem stubs | Engenharia: comparar arquivo a arquivo |
| CE-05 | `contracts/fonts/*` remoções candidatas | HOLD_HUMAN | alto | inventário de consumidores e regressão antes de exclusão | Arquitetura: não remover |
| CE-06 | Export manifest `8099e3ff`, constraints `83642780` | PASS_READ / HOLD_SEMANTIC | alto | snapshot e crosswalk 1996/1996, sem duplicar fingerprint | Dados: próximo lote ainda não validado |
| CE-07 | 15 PK/FK `ce_platform` lidas | PASS_READ / HOLD_CROSSWALK | médio | equivalência individual com export | Dados: confrontar por identidade |
| CE-08 | 24 ferramentas, metamodelo, M08/M09 e workspace PR71 | NOT_RUN | alto | gates clínicos, licença, segurança e CI | Equipes responsáveis: seguir independentemente |

## Progresso com denominadores
- Código: **2/2 arquivos-alvo alterados**, com 0/2 testes de execução confirmados; não representa 2 imports homologados.
- Parsers: **0/16** homologados; imports: **0/5** homologados.
- Ferramentas: **0/24** revalidadas nesta rodada.
- Constraints: **8/1996 = 0,40%** crosswalk histórico; **0 novas**; 15 definições físicas lidas, não homologadas.
- CI novo HEAD: **NOT_RUN / não observado**; último CI histórico 3/4 PASS, global FAIL (não atribuir ao HEAD atual).
- Estimativa global de conclusão: **NÃO AFERÍVEL**, denominadores técnicos, clínicos, jurídicos e de segurança ainda incompletos.

## Decisão e rollback
PR73 permanece **DRAFT / NO-GO** até CI e gates. Rollback do código: reverter isoladamente os commits `6992e3e` e `2d14b19` em branch de revisão após conferir o HEAD; alterações são textuais e não alteram dados. Não houve DDL/DML, migrations, seeds, deploy, merge, exclusão de branch, publicação clínica ou manipulação de registros pessoais. Próxima execução: CI e testes de importação/fail-closed; prosseguir em parsers e crosswalk independentes.
