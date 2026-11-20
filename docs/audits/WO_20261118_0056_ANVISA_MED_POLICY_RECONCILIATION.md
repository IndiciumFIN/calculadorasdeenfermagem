# CE / CKO / NCOS — checkpoint 2026-11-18 00:56 BRT

## Escopo, autoridade e bloqueios
Supabase Calculadoras-Smart `pgsybzggewhinaniybiy` é única verdade física. Banco somente SELECT. Candidato NO-GO. Nenhuma DDL/DML, migration, seed, deploy, merge ou exclusão de branch. Gates clínico, jurídico, LGPD, licenciamento, segurança e proveniência permanecem fail-closed.

## Checkpoint anterior e fingerprints
Anterior: `WO_20261117_2353_ANVISA_VALIDATOR_CONTRACT_FIX.md` blob `b17483a52031cdb84b5e11a531c74a9859648cea`; ANVISA dev `54372d627c73a7b9ccdb8ce9b39281fd15d22e55` sem delta e sem reprocessamento. CI do commit anterior `4c167d1b77ed449f56090da0abc22fa88c53d5b5`: 3/4 workflows PASS, canonical invariants FAIL, run 44226617670; jobs 134541222100 e 134541222551 FAIL. Logs de 2026-11-18 02:54 UTC confirmam SOURCE_VALIDATOR_SCHEMA persistente, MISSING_PARSER 16, PACKAGE_IMPORT_NAMESPACE 5 e legado. Falha não é homologação.

## Correção funcional desta rodada
`contracts/fontes/anvisa_med.json` blob `c6342f4f340924e468124b53b0be4eadf00e8a27` continha `validators: "schema_validator"`. Política `contracts/policies/KERNEL-POLICY-006.json` blob `89e7577b8edd7b4ae71a9bfead7dcf784e6409d2` exige exatamente `["schema_validator","ncm_validator"]`. Branch de integração parsers continha contrato correspondente blob `7248b9dd818ea6ebd7869f2f8fc93b18fe988d2d`. Atualização pontual na branch audit produziu blob `7248b9dd818ea6ebd7869f2f8fc93b18fe988d2d`, commit `8c05dd22698f1fcecc9114b4a72f7e107f4d312c`. Identificadores preservados, sem criar parser, promover conteúdo ou alterar política.

`contracts/fontes/catmat.json` blob `cb1af111303c56a109bb89d97c9bf1c99099ef99` também contém string; branch parsers blob `fd9b62b9e9ca7e9335e1eb71b23b842a93573a28` contém `["schema_validator","catmat_validator"]`. **HOLD_VERIFY** até confrontar diretamente KERNEL-POLICY-013; não corrigido nesta rodada.

## Banco e inventário
SELECT em `pg_constraint` para `cko_governance.artifact_normative_bindings`: 4 constraints retornadas, incluindo FK `artifact_normative_bindings_artifact_id_fkey` com `ON DELETE CASCADE`. PASS_READ / HOLD_PROVENANCE. Inventário informado e não recontado: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS policies. Histórico de comparação JSONL: 5/1996 (0,25%), não expandido nesta rodada.

## Work orders e critérios de aceite
| WO / objeto / branch | SHA ou fingerprint / delta | Status | Risco | Teste / aceite | Responsável / próxima ação |
|---|---|---|---|---|---|
| CE-ANVISA-MED / contracts/fontes/anvisa_med.json / audit | c6342f4f → 7248b9dd; string → array de 2 validadores, igual política 006 | PASS_CODE / HOLD_CI | alto | CI invariants PASS, smoke e teste de política | Engenharia: revalidar novo HEAD |
| CE-ANVISA-DEV / contracts/fontes/anvisa_dev.json / audit | 54372d62 sem delta | PASS_CODE / HOLD_CI | médio | CI invariants PASS | Engenharia |
| CE-CATMAT / contracts/fontes/catmat.json / audit | cb1af111 vs branch parsers fd9b62b9; não alterado | HOLD_VERIFY | alto | confirmar política 013, testar | Engenharia |
| CE-SOURCE-OTHERS / contracts/fontes / audit | 15 ocorrências históricas SOURCE_VALIDATOR_SCHEMA, não equivalem a 15 objetos distintos; 2 arquivos corrigidos em rodadas diferentes | FAIL_CI / HOLD_VERIFY | alto | reconciliar individualmente políticas e fontes; novo CI | Engenharia |
| CE-LEGACY / contracts/fonts | fingerprint pendente | FAIL_CI | alto | verificar referências, não excluir sem análise | Engenharia |
| CE-PARSERS / integration/cko-parsers-catalog-20261114 | main ahead 163 behind 0, comparação atual | HOLD_VERIFY | alto | 16/16 parsers e licença/proveniência | Engenharia |
| CE-IMPORTS / packages/cli | 5 pendências do log atual | HOLD_VERIFY | alto | 5/5 smoke | Engenharia |
| CE-TOOLS / feat/ce-tools-governed-backend-20261115 | SHA não revalidado | HOLD_HUMAN | crítico | 24/24 testes + gates clínicos | Engenharia/Clínica |
| CE-METAMODEL / feat/cko-catalog-metamodel-automated-20261114 | SHA não revalidado | HOLD_VERIFY | alto | PK/FK/dicionário reconciliados | CKO |
| CE-CORPUS / feat/cko-m08-m09-corpus-atomic-20261114 | SHA não revalidado | HOLD_VERIFY | alto | átomos, direitos, proveniência | Conteúdo |
| CE-DB / artifact_normative_bindings | SELECT 4/4 PASS_READ; FK CASCADE | HOLD_PROVENANCE | crítico | retenção comprovada | BD/Jurídico |
| CE-PR73 / audit | HEAD não revalidado nesta rodada; CI anterior 3/4 PASS | FAIL_CI | alto | checks obrigatórios PASS | Engenharia |
| CE-PR71 / dev-chatgpt-workspace | HEAD não revalidado | HOLD_CI | alto | PMO/auth/Vercel PASS | Workspace |

## Percentuais e testes
- Correção ANVISA MED: 1/1 arquivo-alvo = 100% do patch pontual, **não** homologação.
- Arquivos com correção tipada identificada: 2 (ANVISA DEV e MED); denominador total de fontes defeituosas não consolidado, portanto percentual não aferível.
- CI anterior: 3/4 workflows PASS, 1 FAIL. CI após commit 8c05dd: NOT_RUN/NOT_VERIFIED.
- Testes unitários/adversariais locais: NOT_RUN. Consulta SQL: 1/1 PASS_READ (4 constraints).
- Parsers: 0/16 corrigidos nesta rodada; imports 0/5. Ferramentas homologadas 0/24 histórico, não revalidado.
- Constraints export histórico 5/1996 = 0,25%; nesta rodada nenhuma comparação adicional.
- Estimativa global: **NÃO AFERÍVEL**; ausência de denominadores completos de aceite.

## Próximos passos
Verificar novo HEAD/CI da PR #73; confrontar política 013 com CATMAT e demais contratos; testar validador e casos adversariais; inspecionar diretório legado e parsers/imports sem contornar gates; retomar metamodelo, corpus, ferramentas e PR #71. Não reprocessar fingerprint sem delta.
