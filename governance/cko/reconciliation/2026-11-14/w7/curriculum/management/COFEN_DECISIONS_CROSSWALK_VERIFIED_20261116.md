# Crosswalk candidato — cinco decisões Cofen e catálogo W7 (16/11/2026)

Escopo: EPIC #74, PR #70, P0 baseline / P1 specialties. Fonte canônica consultada: https://www.cofen.gov.br/resolucao-cofen-no-581-2018/ . Catálogo confrontado: `curriculum/specialties/COFEN_581_SPECIALTIES_65_AND_SUBAREAS_v0.5.0.jsonl` (65 registros, leitura da branch de revisão em 16/11/2026).

| Decisão | Identidade existente | Resultado de reconciliação | Fonte |
|---|---|---|---|
| 65/2021 | COFEN-581-I-49 | Enfermagem Nuclear já presente; não criar novo ID | https://www.cofen.gov.br/decisao-cofen-no-65-2021/ |
| 120/2021 | COFEN-581-III-07 | Bases Epistemológicas e Filosóficas da Enfermagem já presente | https://www.cofen.gov.br/decisao-cofen-no-120-2021/ |
| 263/2023 | COFEN-581-I-50 | Podiatria Clínica já presente; não fundir com subárea COFEN-581-I-11-03 (Podiatria) | https://www.cofen.gov.br/decisao-cofen-n-263-de-15-de-dezembro-de-2023/ |
| 264/2023 | COFEN-581-I-51 | Especialização em Reabilitação já presente | https://www.cofen.gov.br/resolucao-cofen-no-581-2018/ |
| 21/2024 | COFEN-581-III-08 | História da Enfermagem já presente | https://www.cofen.gov.br/decisao-cofen-n-21-de-02-de-fevereiro-de-2024/ |

## Resultado e limites

- 5/5 correspondências de **identidade nominal** verificadas entre a lista oficial consolidada e o JSONL W7; 0 novos IDs propostos; 0 exclusões; denominador permanece 65 entradas principais / 80 subáreas na baseline.
- **Não** significa 5/5 decisões juridicamente revisadas integralmente: texto integral, publicação, vigência e possíveis efeitos específicos seguem em revisão jurídica `HOLD_HUMAN`. Especialmente a Decisão 264/2023 foi conferida nesta rodada pelo anexo consolidado, não por leitura integral de sua página individual.
- A subárea Podiatria e a especialidade Podiatria Clínica são duas identidades do catálogo, não duplicatas exatas. Relação semântica `RELATED_TO` somente candidata; não criar `EQUIVALENT_TO` ou `PART_OF` automaticamente.
- A Resolução 610/2019 altera o item 38 (Saúde Ocupacional) e a 625/2020 altera procedimento de registro: https://www.cofen.gov.br/resolucao-cofen-no-610-2019/ e https://www.cofen.gov.br/resolucao-cofen-no-625-2020/ . Não confundir alteração procedimental com novo item curricular.
- Evidência de CI: https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43897687450 — job `CKO 65-specialty evidence and backlog checks` concluído com success; testes determinísticos e upload de auditoria concluídos. Este run precede o presente commit, não valida automaticamente este documento.

## Próxima ação

Continuar recuperação de PPC/ementas **por instituição, curso, campus, edição/coorte e URL primária**, com triagem de direitos por operação. Não promover crosswalk, publicar conteúdo clínico, modificar Supabase nem efetuar merge. Status: `CANDIDATE_VERIFIED_IDENTITY`; `HOLD_HUMAN` para equivalências semânticas/jurídicas; `HOLD_SOURCE` para fontes primárias curriculares ainda não capturadas.
