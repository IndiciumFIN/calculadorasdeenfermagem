# Conclusão da Atomização — Status

**Data**: 2026-10-15  
**Branch**: `cursor/fix-governance-gaps-ec54`

## Critérios de conclusão

| Critério | Status | Evidência |
|----------|--------|-----------|
| Porta do CLI antigo | Código na branch | `ingest`, `process`, `pipeline run`, `registry add` e `registry set-status` saem com código 2 antes de gravar. FIND-0001 permanece aberto. |
| IDs da heurística | Harness | `NORM-` + 12 hex em `atomizar_heuristica`. O comando não chama essa função. |
| Validador da heurística | Harness | `_validar_id_atomo`. O schema `AtomoBlindado` continua `NORM-` + ano + sequência. |
| Máscara com lookaround | Código | sequência longa de dígitos não entra na máscara de telefone |
| Hash de proveniência | Harness | proveniência incompleta sai com código 2 dentro de `atomizar_heuristica` |
| Status inicial | Harness | a heurística grava `Não verificado` |
| Schema fail-closed | Código | `AtomoBlindado` + invariantes, via `validate` |
| Gates agregadores | Código local | `gates/aggregate.sh` + workflow. Branch protection da `main` continua ação humana. |
| Mapeamento Drive | Documento | `docs/DRIVE_MAPPING.md` |
| Fases 1–11 | Documento | `docs/FASES_STATUS.md` não homologa produção |

## Pendências de ação humana

- **Fase 12**: branch protection na `main` (GOV-001)
- **Fase 13**: aplicação da migration Supabase

## Fluxo que grava

A escrita qualificada entra por `python -m packages.cli.kernel`, com procedimento já qualificado. T01, T02, T04 e T07 continuam não qualificadas. Uma Work Order válida de outro procedimento não autoriza o CLI antigo.

`validate` continua leitura fail-closed.

A heurística, o identificador em hash e a checagem de proveniência ficam fora do comando. Este documento não declara a atomização pronta para operação nem autoriza promoção canônica.
