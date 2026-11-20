# CE / CKO / NCOS — programa de trabalho — 2026-11-19 13:57 BRT

## Escopo e regras
Projeto físico exclusivo: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. Sem DDL/DML, migrations, seeds, merge, deploy ou publicação. Candidatos permanecem NO-GO. Gates clínicos, jurídicos, LGPD, segurança, direitos autorais e proveniência fail-closed.

## Checkpoint anterior e delta
Checkpoint anterior informado: commit `84ee9e588c68cab14c31242e7eba0010a2ca6138`; diagnóstico de três arquivos com imports não canônicos. Neste ciclo, leitura dos blobs atuais e correção direta de 5 linhas de import em 3 arquivos. Não houve tentativa de integração ampla de branch.

| Objeto | Blob anterior | Blob novo | Commit | Delta | Status | Risco/teste | Responsável/próxima ação |
|---|---|---|---|---|---|---|---|
| packages/cli/kernel/__init__.py | 0982c3d4c76905b1942ad8bca143b8ec65408f9a | f39feaf9ac6445595d3ba35dbe27b86120ebaeb0 | bbd77540ccfddfd6f8b8cbeeaf9559a480f45d75 | 2 imports canônicos | PASS_WRITE / HOLD_TEST | Médio; import smoke NOT_RUN | Engenharia: executar python -m e import tests |
| packages/cli/kernel/core.py | 7649f6e1f0160184e1014308cc05c90a5eb659e9 | 7097a142c62bdf9c15f0fde4dadb5a97dd3a6f16 | 297a7e3e70a8050fec06589cb92cb7434d544122 | 2 imports canônicos | PASS_WRITE / HOLD_TEST | Alto; imports de símbolos validadores requerem verificação; NOT_RUN | Engenharia: inspecionar API validators, smoke negativo |
| packages/cli/validators/registry.py | e03e88a0ebe1179448883b7567d59e47193e3bd0 | 65242eb3b9be2ac24eeef2f3318e8c1b8dda101e | 8e5c13e64ac8ef2a52d347a93353451c367a421b | 1 import TYPE_CHECKING canônico | PASS_WRITE / HOLD_TEST | Baixo; NOT_RUN | Engenharia: static imports/CI |
| CE_SUPABASE_DIRECT_EXPORT_20261115/MANIFEST.json | 8099e3ff225224eb00e8eb5accd6d8365ddfcf14 | mesmo blob lido | sem delta | Manifesto histórico 22 arquivos | PASS_READ / HOLD_HUMAN | Snapshot NON_ATOMIC_ACROSS_QUERIES | Governança: manter status candidato |

## Consulta física SELECT — 2026-11-19
`pg_constraint` por `ce_platform`, `cko_governance`, `public`: respectivamente 252 (3 CHECK,135 FK,96 PK,18 UNIQUE), 264 (61,81,88,34) e 197 (53,71,48,25); total 713. Consulta agregada NÃO é crosswalk objeto a objeto e NÃO modifica o banco.

## Work orders e critérios de aceite
- **WO-CLI-NS**: 3/3 arquivos com imports alterados (100% cobertura de edição, **0/3 homologados**). Exigir import smoke, execução negativa com exit 2, ausência de import circular e CI green; status HOLD_TEST.
- **WO-PARSER-16**: 0/16 parsers homologados. Inspecionar branch `integration/cko-parsers-catalog-20261114`, portar apenas código com proveniência e testes; HOLD_HUMAN se dependência/licença faltar.
- **WO-TOOLS-24**: 0/24 ferramentas revalidadas; confrontar `feat/ce-tools-governed-backend-20261115` com contratos, segurança e CI; NOT_RUN.
- **WO-CKO-META**: `feat/cko-catalog-metamodel-automated-20261114`; denominador de objetos semânticos não aferido; HOLD_VERIFY.
- **WO-CKO-CORPUS**: `feat/cko-m08-m09-corpus-atomic-20261114`; fingerprints sem delta não reprocessar; direitos e proveniência HOLD_VERIFY.
- **WO-PG-CROSSWALK**: histórico reportado 8/1996 constraints (0,40%) reconciliadas, não repetidas nesta rodada. PK/FK, dicionário, metamodelo, normativos e átomos pendentes; HOLD_SEMANTIC.
- **WO-WORKSPACE-71**: PR #71 complementar; estado atual não revalidado nesta rodada; HOLD_VERIFY.
- **WO-CI-73**: último CI histórico informado 3/4 workflows PASS; CI do novo HEAD NOT_RUN. Revalidar após commits; NO-GO.

## Percentuais e testes
Edição de arquivos alvo 3/3 (100%, **não equivale a correção homologada**). Homologação imports 0/3; parsers 0/16; ferramentas 0/24; crosswalk histórico 8/1996 (0,40%); CI novo HEAD NOT_RUN; testes locais NOT_RUN. Estimativa global de conclusão: **não aferível** (denominadores clínicos, jurídicos e técnicos não consolidados).

## Próxima execução
Verificar CI da PR #73, testes import/smoke; resolver imports de símbolos validadores caso a API não os exponha; prosseguir parsers e crosswalk por delta de fingerprint. Não promover candidatos sem gates.
