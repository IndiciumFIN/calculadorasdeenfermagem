# CE / CKO / NCOS — checkpoint 2026-11-18 17:52 America/Sao_Paulo

## Escopo e evidências desta rodada
- Única verdade física: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; consulta exclusivamente SELECT.
- Checkpoint de partida informado: `de1ba57e0cbcaabed0f0960f1b1bdf5b37a4b5f7` (não revalidado como HEAD no início).
- PR #73: https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/73 — identificada na busca GitHub; estado draft e checks atuais NOT_RUN nesta rodada.
- Export histórico `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/`: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 policies RLS — números herdados, não recontados nesta rodada; 22/22 hashes PASS histórico, não recalculados sem delta.
- SELECT: `pg_constraint` no schema `cko_governance`: CHECK 61, FK 81, PK 88, UNIQUE 34, total 264. PASS_AGGREGATE; comparação individual com export HOLD_SEMANTIC.

## Work orders com delta verificado
| WO | Objeto | SHA anterior (blob) | SHA novo (blob) | Commit | Delta / fingerprint semântico | Status | Risco | Teste | Responsável / próxima ação | Aceite |
|---|---|---|---|---|---|---|---|---|---|
| CE-CONTRACT-ESAVI | `contracts/fontes/esavi.json` | `fcc302fd74726af484c1a155829da4dcd8c3454f` | `73b6f82c899c21be7b90de4385eef946abd5396e` | `616e68ae6c01b480362ad3b59cfea9c8f3b53ac7` | validators string -> array [schema_validator]; política `contracts/policies/KERNEL-POLICY-014.json` blob `830d7bb86fa2b5f0a6471e0af6dd26a8ca0d66a1` | PASS_STATIC / CI NOT_RUN | baixo para JSON, admissão não demonstrada | comparação exata de array PASS; CI NOT_RUN | engenharia CE: verificar workflow no HEAD | contrato corresponde à política, testes canônicos PASS |
| CE-CONTRACT-SINAN | `contracts/fontes/sinan.json` | `19704f794211c2cd6b627219b4f9c3261591ccde` | `37b15c6cdddb6b747f8171f54b44b47258c3738a` | `f91ac86f52c39e0286a0020fe4bec9cd5401c741` | validators string -> array [schema_validator]; política `contracts/policies/KERNEL-POLICY-011.json` blob `752c27d75393392cb7cf9fbd1b1c8268e4469703` | PASS_STATIC / CI NOT_RUN | médio: exige revisão humana na política | comparação exata de array PASS; CI NOT_RUN | engenharia + revisão clínica: preservar `requires_human_review=true` | contrato/política e revisão clínica demonstrados |
| CE-CATALOG | `cko_governance` / pg_constraint | histórico 264 | atual 264 | n/a | sem delta agregado | PASS_AGGREGATE; HOLD_SEMANTIC individual | médio | SELECT PASS | DBA: reconciliar por oid, nome, tabela e definição | 1996 objetos históricos identificados individualmente |
| CE-CI | PR #73 | HEAD pré-rodada não reconfirmado | `f91ac86f52c39e0286a0020fe4bec9cd5401c741` após correções | n/a | dois contratos corrigidos | HOLD_VERIFY | alto | CI NOT_RUN | engenharia: validar canonical invariants, parser/import smoke e logs | 4/4 workflows PASS no mesmo HEAD |
| CE-TOOLS | `feat/ce-tools-governed-backend-20261115` | não aferido | não aferido | n/a | sem verificação | HOLD_VERIFY | clínico alto | 0/24 revalidadas nesta rodada | engenharia clínica: comparar ferramentas, regras e segurança | 24/24 testes funcionais e clínicos documentados |
| CKO-META | `feat/cko-catalog-metamodel-automated-20261114` | não aferido | não aferido | n/a | sem verificação | HOLD_VERIFY | alto | NOT_RUN | arquitetura: reconciliar PK/FK e dicionário | semântica e integridade comprovadas |
| CKO-CORPUS | `feat/cko-m08-m09-corpus-atomic-20261114` | não aferido | não aferido | n/a | sem verificação | HOLD_VERIFY | direitos/proveniência alto | NOT_RUN | editorial: revisar átomos e licenças | fontes e direitos validados |
| CKO-PARSERS | `integration/cko-parsers-catalog-20261114` | não aferido | não aferido | n/a | 16 parsers/5 imports pendentes em CI histórico, não recontados | HOLD_VERIFY | alto | NOT_RUN | engenharia: comparar arquivos antes de copiar | dependências e smoke PASS |
| CE-WORKSPACE | `IndiciumFIN/dev-chatgpt-workspace` PR #71 | não aferido | não aferido | n/a | sem verificação | HOLD_VERIFY | médio | NOT_RUN | engenharia: verificar HEAD/checks e contratos | build seguro sem migrations |

## Métricas e gates
- Correções estáticas selecionadas nesta rodada: 2/2 PASS_STATIC; **não** representam homologação.
- Export histórico: 22/22 PASS_HASH histórico, não reprocessado.
- Constraints individuais: 0/1996 nesta rodada; HOLD_SEMANTIC.
- Ferramentas: 0/24 revalidadas nesta rodada; HOLD_VERIFY.
- Parsers/imports: 0/16 e 0/5 corrigidos nesta rodada; histórico sujeito a nova medição.
- CI pós-correções: NOT_RUN; status global de CI NÃO APROVADO.
- **Estimativa global de conclusão: NÃO AFERÍVEL** (denominadores de aceite não consolidados).
- Nenhum DDL/DML, migration, seed, merge, deploy, exclusão de branch ou publicação de candidato. Fail-closed, LGPD, segurança, gates clínicos/jurídicos, copyright e proveniência mantidos.
- Próxima rodada: CI no HEAD atual; contratos FHIR Vitais/MeSH/Vacinas CDC com políticas; branch de parsers; diff individual de constraints.
