# CE / CKO / NCOS — checkpoint 2026-11-18 19:50 BRT

## Escopo, baseline e controle
- Projeto físico exclusivo: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. Consulta apenas SELECT.
- PR #73: branch `audit/ce-supabase-migration-first-20261115`; baseline anterior documentado `8954084f3f6e00039ac82a9bab76b26775a82c34`; dois commits funcionais desta rodada `16a53355841c1a033e4083fe3821bbba2c800e78` e `1a32fce43732a6aa28f446f24b87592042bbfcba`.
- Export `docs/audits/CE_SUPABASE_DIRECT_EXPORT_20261115/`: inventário informado 59 schemas, 678 relações, 255 migrations, 7246 colunas, 1996 constraints, 1268 índices, 100 RLS; 22/22 hashes PASS histórico, não recalculados sem delta confirmado.
- CI no commit `8954084f3f6e00039ac82a9bab76b26775a82c34`: 3/4 PASS, invariants FAIL, run https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44406304694 . CI nos commits desta rodada NOT_RUN/NOT_VERIFIED.
- SELECT `pg_constraint` / `pg_namespace`: `cko_governance` CHECK 61, FK 81, PK 88, UNIQUE 34; total 264, PASS_AGGREGATE. Não representa reconciliação individual.
- Políticas e contratos consultados diretamente no GitHub, sem busca externa nesta rodada.

## Registro de objetos / work orders
| WO / objeto | Fingerprint SHA de entrada / política | Delta / SHA de saída | Teste e status | Risco | Responsável e ação seguinte | Aceite |
|---|---|---|---|---|---|---|
| CE-FHIR / `contracts/fontes/fhir_vitais.json` | blob `40fe156c001ff55a2e138ac385f1f2aa189f8e03`; policy `KERNEL-POLICY-008` blob `cef0e5b8a4ef404bf4fdb427c7e6c4147afd4d81` | string `schema_validator` → array `[schema_validator,loinc_validator]`; blob `caabd194d51beb1cff23ca272f64229b2833ca57`; commit `16a53355841c1a033e4083fe3821bbba2c800e78` | PASS_STATIC policy comparison; CI NOT_RUN | médio | engenharia CE: verificar CI e dependências | invariants + smoke PASS no mesmo HEAD |
| CE-CDC / `contracts/fontes/vacinas_cdc.json` | blob `5e5216ddd4914665ed3358f1171b038bff92212b`; policy `KERNEL-POLICY-007` blob `9e8309d94b3e5908a8764214a5cd718df43d5e84` | string `cvx_validator` → array `[cvx_validator,schema_validator]`; blob `2f8bffa651db5c82a23780bc2878da7119a5a050`; commit `1a32fce43732a6aa28f446f24b87592042bbfcba` | PASS_STATIC policy comparison; CI NOT_RUN | médio | engenharia CE: verificar CI | invariants + smoke PASS no mesmo HEAD |
| CE-CI / PR #73 | baseline `8954084f3f6e00039ac82a9bab76b26775a82c34` | 2 commits acima | 3/4 PASS histórico; global FAIL | alto | engenharia: analisar logs parsers/imports e executar CI | 4/4 PASS no mesmo HEAD |
| CE-SUPABASE / `cko_governance` | 264 agregado anterior | 264 atual, delta agregado 0 | PASS_AGGREGATE, HOLD_SEMANTIC | alto | DBA: diff PK/FK/colunas por objeto, sem DDL | catálogo físico e export reconciliados |
| CE-TOOLS / `feat/ce-tools-governed-backend-20261115` | SHA não aferido nesta rodada | nenhum | 0/24 revalidadas nesta rodada, HOLD_VERIFY | clínico alto | engenharia clínica: teste por ferramenta | 24/24 homologadas com proveniência |
| CKO-META / `feat/cko-catalog-metamodel-automated-20261114` | SHA não aferido | nenhum | NOT_RUN | alto | arquitetura: comparar metamodelo, PK/FK, dicionário | equivalência semântica |
| CKO-CORPUS / `feat/cko-m08-m09-corpus-atomic-20261114` | SHA não aferido | nenhum | NOT_RUN | direitos alto | editorial: licenças e átomos | proveniência primária válida |
| CKO-PARSERS / `integration/cko-parsers-catalog-20261114` | SHA não aferido | nenhum | 0/16 parsers e 0/5 imports corrigidos nesta rodada; FAIL histórico | alto | engenharia: diff e smoke antes de copiar | dependências sem duplicação |
| CE-WORKSPACE / PR #71 | HEAD não aferido nesta rodada | nenhum | NOT_RUN | médio | engenharia: CI e contrato de integração | build PASS e sem migration |

## Métricas e gates
- Contratos selecionados corrigidos: **2/2 PASS_STATIC**, não homologados em CI.
- Integridade export: **22/22 PASS_HASH histórico**, sem reprocessamento.
- Workflows HEAD anterior: **3/4 PASS**, global FAIL.
- Constraints individualmente reconciliadas nesta rodada: **0/1996**, HOLD_SEMANTIC.
- Ferramentas revalidadas nesta rodada: **0/24**, HOLD_VERIFY.
- Parsers/imports corrigidos nesta rodada: **0/16** e **0/5**, histórico.
- **Estimativa global de conclusão: NÃO AFERÍVEL**; denominador consolidado de homologação inexistente.
- Sem DDL/DML, migrations, seeds, merges, deploy, exclusão ou publicação de candidatos. Preservados fail-closed, LGPD, segurança, direitos autorais, proveniência e gates clínicos/jurídicos.
- Próximo: CI do HEAD atualizado, diagnosticar os jobs canônicos, diff da branch parsers, reconciliação individual PK/FK, testes das 24 ferramentas. Não repetir fingerprints sem delta.
