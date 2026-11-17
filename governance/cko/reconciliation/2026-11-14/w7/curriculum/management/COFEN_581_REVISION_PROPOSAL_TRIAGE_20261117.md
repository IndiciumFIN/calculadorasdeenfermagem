# P0 — triagem da proposta de revisão Cofen 581/2018 (17/11/2026)

**EPIC:** #74; **PR:** #70; **WO:** WO-CKO-CURR-20261115-01 (baseline) e -04 (especialidades). **Status:** `CANDIDATE_EVIDENCE`, `HOLD_SOURCE_VERSION`; sem promoção automática.

## Nova evidência oficial, distinta do anexo normativo

1. **Norma-base com alterações explicitamente indicadas:** [Resolução Cofen 581/2018](https://www.cofen.gov.br/resolucao-cofen-no-581-2018/). A página oficial lista alterações pelas Resoluções 610/2019 e 625/2020 e pelas Decisões 065/2021, 120/2021, 263/2023, 264/2023 e 21/2024. É a referência do catálogo versionado; qualquer contagem deve ser reproduzida sobre a edição consolidada e seus atos, não inferida de notícia.
2. **Notícia oficial datada de 25/09/2026:** [GT conclui proposta de revisão sobre registro das especialidades](https://cofen.gov.br/gt-conclui-proposta-de-revisao-sobre-registro-das-especialidades-de-profissionais-da-enfermagem/). Relata entrega de **relatório/proposta** de revisão da 581/2018, com reorganização proposta em duas dimensões, carga horária mínima e requisitos de prática clínico-assistencial. **Não comprova publicação ou vigência de nova resolução.**
3. **Antecedente oficial de 05/08/2025:** [GT propõe atualização da lista](https://www.cofen.gov.br/grupo-de-trabalho-do-cofen-propoe-atualizacao-da-lista-de-especialidades-da-enfermagem/). Evidencia processo de revisão, não alteração normativa por si só.

## Decisão de reconciliação

| Entidade | Identidade | Classe | Relação permitida | Bloqueio |
|---|---|---|---|---|
| Resolução 581/2018 e alterações listadas | `COFEN:RES:581:2018` + atos modificadores individuais | Norma | `NORMATIVE_BASELINE` candidato | Confirmar consolidação e hashes por edição |
| Relatório do GT apresentado em 25/09/2026 | `COFEN:GT:REVISAO-581:2026-09-25` | Proposta, notícia institucional | `PROPOSES_CHANGE_TO` 581/2018 | `HOLD_ENACTMENT` |
| Catálogo interno de 65 especialidades e 80 subáreas | `COFEN_581_SPECIALTIES_65_AND_SUBAREAS_v0.5.0.jsonl` | Snapshot derivado | `DERIVED_FROM` somente com correspondência auditada | `HOLD_SOURCE_VERSION` |

**Regra fail-closed:** não substituir o universo 65/80, não adicionar/remover especialidade, não alterar direitos de título, nem assumir nova carga horária ou requisitos como vigentes com base na notícia de setembro. O texto integral da proposta e eventual resolução aprovada/publicada devem ser localizados e confrontados por artigo, anexo, data de publicação e vigência; decisão jurídica humana necessária para promoção.

## Critérios de saída e impacto

- P0: obter texto oficial publicado do ato final, caso exista, com identificador, data, anexo, revogações e vigência; comparar delta da lista de especialidades com 65/80. Até lá, `HOLD_SOURCE_VERSION` e `HOLD_HUMAN`.
- P1: manter a proposta como objeto de acompanhamento normativo separado, não como curso, ementa, vaga, claim clínico ou especialidade nova. Direitos de reutilização textual permanecem `HOLD_RIGHTS`.
- Métricas baseline **inalteradas**: 65/65 catalogadas (não homologadas); 14/65 com vagas na amostra; 38/1055 microaulas candidatas do subconjunto Trabalho/Urgência; 0/22 bloqueios canônicos comprovadamente resolvidos.
- Evidência obtida por consulta às páginas oficiais em 17/11/2026. Não houve teste de software, merge, acesso ao banco ou publicação clínica neste microtrabalho.
