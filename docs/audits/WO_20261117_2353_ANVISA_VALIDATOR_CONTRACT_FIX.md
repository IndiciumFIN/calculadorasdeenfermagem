# CE / CKO / NCOS — checkpoint 2026-11-17 23:53 BRT

## Autoridade e limites
Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` exclusivamente SELECT. Nenhuma DDL/DML/migration/seed/merge/deploy. Candidato permanece NO-GO. Preservar fail-closed, LGPD, proveniência, licenciamento e gates clínicos/jurídicos.

## Checkpoint e delta real
Antecessor: `WO_20261117_2250_CANONICAL_CI_POST_FIXTURE.md` blob `e12dbbf856d403d20dbaeb431db01ff950b74dd9`.
Verificador `scripts/verify_repository_integrity.py` blob `f6d72d91455c530d5bc3f9fbed283b389851b151`, sem delta observado.
Logs GitHub Actions job 134491589063 (run 44211754821) identificaram 15 ocorrências SOURCE_VALIDATOR_SCHEMA (não inferir que todas são causas distintas), além de LEGACY_SOURCE_DIR. A inspeção direta confirmou `contracts/fontes/anvisa_dev.json` com `validators` string `schema_validator`; política `KERNEL-POLICY-009.json` blob `24d4d43ab5723c1c9dc9ef3d21924fa3c9d46c7b` exige array `["schema_validator"]`. Alteração estritamente tipada e semanticamente equivalente, sem mudar identidade do validador. Commit funcional `4d8a0a0793e5d970210673ba20e8818018cdf7b6`; fonte blob anterior `902ae7991a116db4563b99daec9722a7cb87679c`, novo `54372d627c73a7b9ccdb8ce9b39281fd15d22e55`.
Comparação `main...audit/ce-supabase-migration-first-20261115` antes da alteração: ahead 81 / behind 0. Branch parsers: ahead 163 / behind 0, 175 arquivos. PR #73 e workspace #71 localizadas, sem HEAD/checks atuais revalidados.

## Banco
SELECT `pg_constraint` / `pg_class` / `pg_namespace`: cinco constraints selecionadas, sem delta observado; `artifact_normative_bindings_artifact_id_fkey` permanece `ON DELETE CASCADE` (HOLD_PROVENANCE). Não houve nova comparação JSONL. Inventário informado, não recontado: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies.

## Work orders / objetos / aceite
| WO / branch / objeto | Fingerprint e delta | Estado | Risco | Teste / aceite | Responsável e próxima ação |
|---|---|---|---|---|---|
| CE-ANVISA-DEV / audit / contracts/fontes/anvisa_dev.json | 902ae799 → 54372d62; string → array, política 009 conferida | PASS_CODE / HOLD_CI | médio | teste unitário, invariants e strict CI PASS | Engenharia: reexecutar CI e verificar vínculo |
| CE-SOURCE-OTHERS / audit / contracts/fontes | 14 outras ocorrências SOURCE_VALIDATOR_SCHEMA no log; SHAs pendentes | FAIL_CI / HOLD_VERIFY | alto | reconciliar 14/14 fonte-política, sem inventar IDs | Engenharia: confrontar arquivos e políticas |
| CE-LEGACY / contracts/fonts | log LEGACY_SOURCE_DIR; SHA pendente | FAIL_CI | alto | rastrear referências antes de remoção | Engenharia |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | ahead 163 / behind 0; 16 faltantes históricos | HOLD_VERIFY | alto | 16/16 importáveis com licença e origem | Engenharia |
| CE-IMPORTS / packages/cli | cinco pendências históricas | HOLD_VERIFY | alto | 5/5 smoke imports | Engenharia |
| CE-TOOLS / feat/ce-tools-governed-backend-20261115 | SHA não revalidado | HOLD_HUMAN | crítico | 24/24 testes e gates clínicos | Engenharia/Clínica |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | SHA não revalidado | HOLD_VERIFY | alto | PK/FK/dicionário/metamodelo reconciliados | CKO |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | SHA não revalidado | HOLD_VERIFY | alto | átomos e direitos/proveniência | Conteúdo |
| CE-DB / cko_governance | SELECT 5/5; comparação export 5/1996 histórica | HOLD_PROVENANCE | crítico | evidenciar retenção e crosswalk | BD |
| CE-PR73 / audit | HEAD e CI novo NOT_RUN | HOLD_CI | alto | checks obrigatórios PASS | Engenharia |
| CE-PR71 / workspace | HEAD e CI novo NOT_RUN | HOLD_CI | alto | PMO, auth e Vercel PASS | Workspace |

## Percentuais e testes
- Correções tipadas confirmadas nesta rodada: 1/1 arquivo-alvo (100% da alteração planejada, não do escopo total).
- SOURCE_VALIDATOR_SCHEMA: 1/15 ocorrências históricas tratada em código (6,67% da lista do log, **não** prova de correção do CI); 14 pendentes de confronto.
- Constraints comparadas ao export: 5/1996 = 0,25% histórico; SELECT atual 5/5 PASS_READ.
- Parsers 0/16 e imports 0/5 corrigidos nesta rodada.
- Ferramentas clínicas homologadas: 0/24 histórico não revalidado.
- Testes locais: NOT_RUN; CI após commit funcional: NOT_RUN; SQL SELECT: PASS_READ; correção de arquivo: PASS_CODE.
- Estimativa global de conclusão: **NÃO AFERÍVEL** por ausência de denominadores de aceite de todas as camadas.

## Próxima execução
Confrontar outros contratos com suas políticas por blob SHA; corrigir somente divergências provadas, executar testes e consultar Actions do HEAD; não enfraquecer gate. Prosseguir em parsers, imports e dicionário/átomos independentemente de HOLD_HUMAN.
