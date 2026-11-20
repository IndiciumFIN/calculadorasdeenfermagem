# CE / CKO / NCOS — checkpoint 2026-11-17 22:50 BRT

## Escopo e autoridade
Banco físico exclusivo: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; SQL apenas SELECT. Branch `audit/ce-supabase-migration-first-20261115`. Sem Neon, SOT, WU-TRIB, DDL/DML, migration, seed, deploy ou merge. Candidato não publicado.

## Checkpoint anterior e fingerprints
Anterior: `docs/audits/WO_20261117_2154_CANONICAL_TEST_FIXTURE_CI.md` (conteúdo lido). Fixture `tests/test_repository_integrity.py` blob `77546609224f5f71e0617fb532276ecd194637fe`; sem delta comprovado. Verificador blob histórico `f6d72d91455c530d5bc3f9fbed283b389851b151`, não revalidado nesta rodada. Não reprocessados fingerprints já verificados sem delta.

## Evidências novas de CI (2026-11-17/18 UTC)
- Commit de correção da fixture `65fa629b6789561bb49e32e1f6bb8b4caaf1b152`: 4 workflows; 3 SUCCESS, 1 FAILURE (Canonical invariants run 44211712924). A correção da fixture NÃO liberou gate global.
- Commit de checkpoint `6f5cd54813394e290379ac7f8ff705bf91f3faab`: 4 workflows; 3 SUCCESS, 1 FAILURE (Canonical invariants run 44211754821).
- Jobs do run 44211754821: `134491589063` FAIL em 'Verify canonical source and policy references', mas 'Run deterministic negative tests' PASS; `134491589344` FAIL em 'Reject unresolved parser or import dependencies'. Logs obtidos. Não afirmar 11/11 nem 5/5 sem resultado granular.
- Logs do strict gate persistem com `SOURCE_VALIDATOR_SCHEMA` nos contratos de fontes, 16 `MISSING_PARSER` e 5 `PACKAGE_IMPORT_NAMESPACE`. Corrigir contrato por contrato, sem preencher identificadores arbitrários nem enfraquecer fail-closed.

## Supabase SELECT desta rodada
Consulta em `pg_constraint`, `pg_class`, `pg_namespace` retornou 5/5 definições selecionadas, inclusive PK composta `architecture_layer_bindings(profile_id, architecture_layer_id, implementation_layer_id)` e FK `artifact_normative_bindings_artifact_id_fkey` com ON DELETE CASCADE. Sem delta observado em relação às definições anteriormente documentadas; sem nova comparação export JSONL. Retenção normativa permanece HOLD_HUMAN.

## Programa de trabalho (por objeto/branch)
| WO / objeto | Fingerprint / delta | Status | Risco | Teste e critério de aceite | Responsável / ação |
|---|---|---|---|---|---|
| CE-FIXTURE / audit branch | blob 77546609; sem delta | PASS_READ / HOLD_CI | alto | CI invariants verde; executar 11/11 granular | Engenharia / diagnosticar contratos reais |
| CE-VALIDATOR / audit branch | histórico f6d72d91; não revalidado | HOLD_TEST | alto | cinco adversariais PASS | Engenharia / executar testes |
| CE-SOURCE-CONTRACTS / contracts/fontes | SOURCE_VALIDATOR_SCHEMA em logs atuais; SHA por arquivo pendente | FAIL_CI | alto | todos contratos com validators válidos e correspondência com políticas | Governança / comparar JSON por fonte |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | 16 faltantes no run; SHA individual pendente | HOLD_VERIFY | alto | 16/16 parsers testados, licença e origem | Parsers / confrontar branch |
| CE-IMPORTS / packages/cli | 5 pendentes no run; SHA individual pendente | HOLD_VERIFY | alto | 5/5 smoke de import | Engenharia / corrigir imports |
| CE-DB / cko_governance | cinco definições SELECT sem delta; export histórico 5/1996 | HOLD_PROVENANCE | crítico | retenção demonstrada; comparações individualizadas | BD / investigar CASCADE |
| CE-TOOLS / feat/ce-tools-governed-backend-20261115 | SHA não revalidado | HOLD_HUMAN | crítico | 24/24 gates clínicos | Clínica / testes |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | SHA não revalidado | HOLD_VERIFY | alto | PK/FK/dicionário/metamodelo | CKO / reconciliar |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | SHA não revalidado | HOLD_VERIFY | alto | direitos/proveniência/átomos | Conteúdo / reconciliar |
| CE-PR73 / audit branch | checks de commit 6f5cd54: 3/4 PASS, 1 FAIL | FAIL_CI | alto | HEAD atual e checks obrigatórios PASS | Engenharia / nova consulta HEAD |
| CE-PR71 / workspace | não consultada nesta rodada | HOLD_VERIFY | alto | checks PMO/Vercel PASS | Workspace / investigar |

## Métricas sem confundir inventário com homologação
- Workflows observados no commit 6f5cd54: 3/4 SUCCESS (75%), gate geral FAIL.
- Jobs bloqueantes do workflow: 0/2 PASS (0%), observados.
- Constraints conciliadas contra export: 5/1996 (0,25%) **histórico**, não ampliadas nesta rodada.
- SELECT de constraints nesta rodada: 5/5 linhas esperadas, PASS_READ, não homologação.
- Ferramentas clínicas homologadas: 0/24 **histórico não revalidado**.
- Parsers resolvidos nesta rodada: 0/16; imports resolvidos: 0/5.
- Testes locais e cinco adversariais: NOT_RUN nesta rodada.
- Inventário informado (não recontado): 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS.
- Estimativa global de conclusão: NÃO AFERÍVEL; denominadores de aceite incompletos.

## Próxima ação independente
Confrontar `SOURCE_VALIDATOR_SCHEMA` dos contratos com políticas por SHA; executar cinco testes adversariais, corrigir fonte comprovada e repetir CI; reconciliar 16 parsers e cinco imports com branch de integração; verificar HEADs de PR #73/#71; continuar reconciliação semântica em SELECT. Gates clínicos, legais, LGPD, licenciamento e segurança continuam fail-closed.
