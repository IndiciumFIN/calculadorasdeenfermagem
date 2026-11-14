# CKO — Wave 01 de parsers e políticas (checkpoint 14/11/2026)

**Estado de release:** `HOLD_HUMAN` / `HOLD_RIGHTS` / `NO_PUBLICATION`.
Repositório: `IndiciumFIN/calculadorasdeenfermagem` (privado).
O objetivo é preservar fonte oficial → contrato → política → parser → metadados/evidências candidatos → revisão → liberação; não gerar conteúdo clínico a partir de testes estruturais.

## PRs e fluxo de integração

| PR | Origem | Artefato técnico | Evidência de CI | Estado |
|---|---|---|---|---|
| [#39](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/39) | M08/M09 | ZIPs, SHA, 104 registros PMO, 46 claims, 43 evidências | [CKO PASS #43582520574](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43582520574) | DRAFT; 0 claims clínicos aprovados |
| [#40](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/40) | `main` | namespace CLI, 20 contratos duplicados conciliados e removidos da branch, validadores e Kernel fail-closed | estrutural/CLI PASS; strict FAIL | DRAFT; 16 parsers ausentes na própria branch |
| [#46](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/46) | #40 | FHIR R4 Observation vital-signs/LOINC/UCUM | [PASS #43584578311](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43584578311) | DRAFT; dados sintéticos apenas |
| [#47](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/47) | #40 | MedlinePlus XML metadados/vínculos, XXE bloqueado | [PASS #43584582732](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43584582732) | DRAFT; direitos/editorial HOLD |
| [#48](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/48) | #40 | MeSH DescriptorRecordSet XML/árvore/referências | [PASS #43584587984](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43584587984) | DRAFT; direitos/terminologia HOLD |

Os parsers são independentes, cada um com contrato, testes sintéticos negativos/positivos e política alterada em seu ramo. **Ainda não há uma branch com os três módulos integrados**. Se integrados sem novos bloqueios, a quantidade de caminhos de parser não implementados cairia de 16 para 13. Não registrar 13 como resultado de um gate já executado.

## Gates obrigatórios

1. **Normativo antes do editorial.** FHIR R4 v4.0.1 (HL7), XML MedlinePlus e MeSH XML (NLM) são referências de formato, não aprovação de claims clínicos.
2. **Rastreabilidade:** SOURCE → DOCUMENT → EVIDENCE_ATOM → CLAIM → KNOWLEDGE_ATOM → CONTENT_MASTER → RESOURCE. As saídas de parser ainda são candidatos, sem vínculos de claim promovidos.
3. **Segurança de fontes:** parser com entrada inválida deve levantar HOLD (inclusive duplicatas, referências órfãs, XXE, unidades/códigos inconsistentes). Dados reais de pacientes não autorizados.
4. **Direitos e LGPD:** NLM/LOINC/HL7/terceiros e dados assistenciais exigem parecer por operação. Não publicar texto integral de terceiros ou dados de paciente.
5. **Kernel:** campos `requires_human_review`, `wo_required`, `sha256_required`, `publication_allowed`, `rights_by_operation_approved` e `review_policy` devem integrar a decisão de liberação, não apenas ser exibidos no JSON. O Kernel da PR #40 agora bloqueia promoção sem estas evidências, inclusive lote vazio, validador ausente/stub e exceções.
6. **CI:** nunca relaxar o teste global de invariantes para obter verde. CI específico de parser valida apenas o módulo; `strict` global continua bloqueado por dependências restantes.

## Backlog e autoridades

- [WO #41](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/41): terminologias e classificações — MeSH implementado tecnicamente; CID-10, CID-11, CVX aguardam.
- [WO #42](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/42): vigilância/ANVISA — quatro parsers aguardam.
- [WO #43](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/43): imunização e insumos assistenciais — quatro parsers aguardam.
- [WO #44](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/44): FHIR e MedlinePlus implementados tecnicamente; ATLAS e TACO aguardam.
- [WO #45](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/45): nove validadores em HOLD, com self-tests insuficientes.

## Restrições de promoção

`main` inalterada. PRs #39/#40/#46/#47/#48 em DRAFT. Nenhum dado foi promovido clinicamente, nenhuma fonte externa integral foi publicada, nenhum esquema Supabase foi alterado. A homologação humana, a vigência normativa e a autorização por direitos permanecem necessárias.
