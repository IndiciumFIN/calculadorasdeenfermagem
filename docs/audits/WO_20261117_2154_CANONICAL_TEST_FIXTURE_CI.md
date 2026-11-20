# CE / CKO / NCOS — checkpoint 2026-11-17 21:54 BRT

## Autoridade e continuidade
- Único banco físico: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; consulta executada exclusivamente SELECT; sem Neon/SOT/WU-TRIB.
- Checkpoint anterior: `docs/audits/WO_20261117_2057_VALIDATOR_PARITY_CODE_TESTS.md`, blob `6fe2c7d1bbb1d82db2d2c97fed11724eb889f0ae`.
- Verificador confirmado blob `f6d72d91455c530d5bc3f9fbed283b389851b151`; teste novo blob `fb063b37c6971eed2f5dda0e55946c26f7617775`.
- Branch de trabalho: `audit/ce-supabase-migration-first-20261115`. Sem merge, DDL/DML, migration, seed, deploy ou publicação de candidato.

## Alteração real
- Commit `65fa629b6789561bb49e32e1f6bb8b4caaf1b152`: corrigida fixture de `tests/test_repository_integrity.py` para declarar `validators: ["atomo_schema_validator"]` também na fonte, em paridade com política; blob anterior `660ced97c7cab5f6f5a127ac5a67106b530eec78`, novo `77546609224f5f71e0617fb532276ecd194637fe`. Nenhum gate foi relaxado.

## Evidências CI novas
- Commit anterior `ca9a7830256e39de8b32d0227e11bbc2eaab62a1`: quatro workflows encontrados, três SUCCESS (provenance, pipeline determinístico, validação) e um FAILURE (Canonical repository invariants), run `44203896440`.
- Job `134464770471`: 11 testes `test_repository_integrity.py`, 8 PASS e 3 FAIL (`test_valid_minimal_registry`, `test_missing_parser_is_strict_hold`, `test_invalid_import_is_strict_hold`), todos com `structural_pass=False`; fixture não declarava validadores na fonte. Correção candidata acima; resultado posterior ainda NÃO VERIFICADO.
- Job `134464770174`: strict gate FAIL, mantém 16 parsers ausentes, 5 imports e erros de esquema de validadores de fontes. Não desabilitar.
- Cinco novos testes adversariais de `test_ce_canonical_validator_parity.py` continuam sem resultado específico demonstrado. Não declarar PASS.
- Supabase SELECT retornou cinco constraints, incluindo FK `artifact_normative_bindings_artifact_id_fkey` com ON DELETE CASCADE; nenhuma comparação nova contra JSONL. HOLD_PROVENANCE.

## Registro de trabalho
| WO / objeto | Fingerprint e delta | Estado | Risco | Teste/aceite | Responsável / próximo passo |
|---|---|---|---|---|---|
| CE-TEST-FIXTURE | `660ced97` -> `77546609`, fonte validators adicionado | HOLD_CI | médio | repetir 11 testes; 11/11 PASS | Engenharia, CI após commit |
| CE-VALIDATOR | `f6d72d91`, sem delta | HOLD_TEST | alto | cinco testes adversariais PASS e CI | Engenharia |
| CE-PARSER | 16 dependências reportadas no run 44203896440 | HOLD_VERIFY | alto | 16/16 parsers implementados/testados e licenciados | Parsers |
| CE-IMPORT | cinco imports reportados no mesmo run | HOLD_VERIFY | alto | 5/5 import smoke | Engenharia |
| CE-SOURCE-VALIDATORS | SOURCE_VALIDATOR_SCHEMA nos contratos reais | FAIL_CI | alto | reconciliar contratos por fonte e política sem inventar IDs | Governança CKO |
| CE-DB-NORMATIVE | FK CASCADE, sem delta | HOLD_HUMAN | crítico | prova de retenção e rollback idempotente | Governança BD |
| CE-PR73 | HEAD pós commit ainda não confirmado; CI antigo FAIL | HOLD_CI | alto | HEAD e checks atuais verdes | Engenharia |
| CE-PR71 | não reconsultada | HOLD_VERIFY | alto | checks PMO e Vercel | Workspace |
| CE-TOOLS-24 | sem novo fingerprint | HOLD_HUMAN | crítico | 24/24 gates clínicos | Clínica |
| CE-METAMODEL | sem novo fingerprint | HOLD_VERIFY | alto | PK/FK/dicionário/ontologia | CKO |
| CE-M08M09 | sem novo fingerprint | HOLD_VERIFY | alto | átomos, direitos, proveniência | Conteúdo |

## Cobertura e percentuais
- CI histórico observado: 3/4 workflows SUCCESS (75%), mas gate global FAIL. Testes legados do job: 8/11 PASS (72,73%) **antes da correção**; após correção 0/11 executados/observados nesta rodada.
- Testes adversariais novos: 5 criados / 5 planejados; 0/5 executados comprovadamente nesta rodada.
- Constraints semanticamente conciliadas: histórico 5/1996 (0,25%), não reprocessadas.
- Ferramentas clínicas homologadas: histórico 0/24, não revalidado.
- Parsers validados: 0/16 nesta rodada; imports validados: 0/5 nesta rodada.
- Estimativa global: NÃO AFERÍVEL (denominador dos critérios de aceite não consolidado).

## Próxima execução
Consultar CI no HEAD novo e logs, executar cinco testes adversariais explicitamente, reconciliar `SOURCE_VALIDATOR_SCHEMA` dos contratos reais, depois parser/imports; paralelizar reconciliação semântica das constraints exportadas e branches de metamodelo/corpus. Não promover candidato. Fontes: GitHub Actions run 44203896440, commits citados, catálogo PostgreSQL SELECT de 17/11/2026. Nenhuma fonte normativa externa consultada.
