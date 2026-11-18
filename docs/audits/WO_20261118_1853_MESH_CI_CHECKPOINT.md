# CE / CKO / NCOS — checkpoint 2026-11-18 18:53 BRT

## Base e escopo
- PR #73 aberta/draft; branch `audit/ce-supabase-migration-first-20261115`; HEAD de partida `7afb7750d61f5d3b51572ae1a58b6ee58afef95a`, árvore `b21b7d2ba44220558e0da7fb90803ab210427fb8`.
- PR #71 do workspace aberta/draft; sem alteração nesta rodada.
- Supabase exclusivo `pgsybzggewhinaniybiy`, SELECT somente. `cko_governance`: 61 CHECK, 81 FK, 88 PK, 34 UNIQUE, total 264 (PASS_AGGREGATE).
- Export histórico `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/` localizado no GitHub. Inventário informado: 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS; 22/22 hashes PASS histórico **não reprocessados**, sem confirmação de delta.
- CI no HEAD inicial: 3/4 PASS; `Canonical repository invariants` FAIL, execução https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44395711002. CI do novo HEAD NOT_RUN no momento do commit.

## Work orders / registro por objeto
| WO | Objeto/branch | SHA/fingerprint de entrada | Delta / SHA de saída | Estado / teste | Risco | Responsável / próxima ação | Critério de aceite |
|---|---|---|---|---|---|---|---|
| CE-CONTRACT-MESH | `contracts/fontes/mesh.json` / PR #73 | blob `21a227a3f9dfae60dc2d8ab4267e0bbfdee7e8da`; política `contracts/policies/KERNEL-POLICY-005.json` blob `ee919b4f1537d48de901c920bfc1b1c70e1881a4` | validators string `mesh_validator` -> array `[mesh_validator,schema_validator]`; blob `7628756b35907e267303dcf09c67d4a532dd47ec` | PASS_STATIC por comparação de JSON; CI NOT_RUN após correção | baixo estrutural, médio de admissão | engenharia CE: conferir novo CI | contrato/política idênticos e invariants PASS |
| CE-CI | PR #73 | HEAD `7afb7750d61f5d3b51572ae1a58b6ee58afef95a` | correção MeSH candidata | 3/4 workflows PASS no HEAD anterior; global FAIL; novo CI NOT_RUN | alto | engenharia: logs, contratos FHIR Vitais/Vacinas CDC, parsers/imports | 4/4 PASS no mesmo HEAD |
| CE-CATALOG | Supabase `cko_governance` | agregado histórico 264 | agregado atual 264, sem delta | SELECT PASS_AGGREGATE, reconciliação individual HOLD_SEMANTIC | médio | DBA: comparar PK/FK/definições com export | correspondência por objeto comprovada |
| CE-TOOLS | `feat/ce-tools-governed-backend-20261115` | SHA não aferido nesta rodada | sem alteração | 0/24 revalidadas nesta rodada; HOLD_VERIFY | clínico alto | engenharia clínica: testes e segurança | 24/24 homologadas com evidências |
| CKO-META | `feat/cko-catalog-metamodel-automated-20261114` | SHA não aferido | sem alteração | NOT_RUN | alto | arquitetura: dicionário/PK/FK | semântica e integridade verificadas |
| CKO-CORPUS | `feat/cko-m08-m09-corpus-atomic-20261114` | SHA não aferido | sem alteração | NOT_RUN | direitos alto | editorial: proveniência/licenças | fontes primárias e direitos validados |
| CKO-PARSERS | `integration/cko-parsers-catalog-20261114` | SHA não aferido | sem alteração | 0/16 parsers, 0/5 imports corrigidos nesta rodada; FAIL histórico sujeito a recontagem | alto | engenharia: diff de arquivos e smoke | dependências resolvidas sem duplicar |
| CE-WORKSPACE | PR #71 `IndiciumFIN/dev-chatgpt-workspace` | HEAD não aferido | sem alteração | draft, CI NOT_RUN | médio | engenharia: revisar build | build seguro, sem migrations |

## Métricas e decisões
- Contrato MeSH selecionado: **1/1 PASS_STATIC**; não equivale a homologação.
- Export: **22/22 PASS_HASH histórico**, não recalculado.
- Workflows no HEAD anterior: **3/4 PASS**, status global FAIL.
- Constraints individualmente reconciliadas: **0/1996 nesta rodada**; HOLD_SEMANTIC.
- Ferramentas: **0/24 revalidadas nesta rodada**; HOLD_VERIFY.
- Parsers/imports: **0/16** e **0/5** corrigidos nesta rodada; números históricos.
- **Estimativa global de conclusão: NÃO AFERÍVEL** — denominador de aceite consolidado ausente.
- Nenhuma DDL/DML, migration, seed, deploy, merge, exclusão de branch ou publicação. Fail-closed, LGPD, segurança, direitos, proveniência e gates clínicos/jurídicos mantidos.
- Próximo: verificar CI do novo HEAD; confrontar FHIR Vitais e Vacinas CDC com políticas; comparar parsers; reconciliação individual do catálogo.
