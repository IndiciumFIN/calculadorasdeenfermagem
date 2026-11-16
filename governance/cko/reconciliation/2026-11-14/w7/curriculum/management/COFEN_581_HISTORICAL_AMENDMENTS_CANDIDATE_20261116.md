# WO P0/P1 — Matriz histórica das alterações da Resolução Cofen 581/2018

**Consulta:** 16/11/2026 · **Estado:** CANDIDATE_NOT_APPLIED · **EPIC:** #74 · **PR:** #70.

## Evidência primária e descoberta

O próprio [Cofen, página consolidada da Resolução 581/2018](https://www.cofen.gov.br/resolucao-cofen-no-581-2018/), lista alterações pelas Resoluções **610/2019** e **625/2020**, além das Decisões **065/2021, 120/2021, 263/2023, 264/2023 e 21/2024**. É uma constatação documental concreta: a referência vigente não é apenas o texto de 2018 isolado. O [Parecer Cofen 16/2026](https://www.cofen.gov.br/parecer-n-16-2026-camaras-tecnicas-de-emfermagem/) continua citando a Resolução 581/2018 atualizada pela 625/2020. **Nenhuma proposta de consulta pública foi promovida a ato vigente.**

## Registro de impactos candidatos

| Instrumento | Referência/assunto mostrado pelo Cofen | Tratamento |
|---|---|---|
| COFEN-581-2018 | Anexo das especialidades e áreas I/II/III | BASE |
| COFEN-610-2019 | Alteração indicada no cabeçalho oficial, impacto granular a conferir | LISTED_AS_AMENDMENT |
| COFEN-625-2020 | Alteração da Resolução 581, alcance artigo a artigo a conferir | LISTED_AS_AMENDMENT |
| COFEN-DEC-065-2021 | Enfermagem Nuclear | RECOGNITION_CANDIDATE |
| COFEN-DEC-120-2021 | Bases Epistemológicas e Filosóficas da Enfermagem (Área III) | RECOGNITION_CANDIDATE |
| COFEN-DEC-263-2023 | Podiatria Clínica (Área I) | RECOGNITION_CANDIDATE |
| COFEN-DEC-264-2023 | Especialização em Reabilitação (Área I) | RECOGNITION_CANDIDATE |
| COFEN-DEC-021-2024 | História da Enfermagem (Área III) | RECOGNITION_CANDIDATE |

## Decisão de reconciliação

O inventário local de **65 especialidades principais e 80 subáreas** permanece **congelado**. Não é possível concluir se esses oito instrumentos já estão todos refletidos nas 65 entradas sem comparar os textos integrais de cada ato, seus anexos e a versão exata do catálogo. **Não adicionar oito linhas ao inventário**: algumas são alterações processuais, outras podem ser inserções ou ajustes de nomes, e uma especialidade já pode constar do baseline.

O índice JSON anexo documenta cada instrumento com a fonte oficial e a limitação `direct_act_text_verified=false`. Links e metadados não concedem licença para republicação de materiais terceiros; não houve cópia integral.

## Próxima microtarefa objetiva

1. Recuperar individualmente o texto oficial dos sete atos posteriores, inclusive vigência e revogações.
2. Confrontar os nomes e IDs de Enfermagem Nuclear, Bases Epistemológicas e Filosóficas, Podiatria Clínica, Reabilitação e História da Enfermagem com o catálogo de 65/80, marcando `PRESENT`, `MISSING`, `RENAMED`, `AMBIGUOUS`.
3. Conservar os achados de currículo/skills independentemente desse gate; equivalências de formação e `PART_OF` dependem de revisão humana.
4. Não alterar Supabase, branch main, conteúdo clínico ou normas aplicadas automaticamente.

**HOLD_SOURCE_FULL_ACT**, **HOLD_HUMAN_TAXONOMY_DELTA**, **HOLD_RIGHTS**. A cobertura normativa desta microtarefa é **8/8 instrumentos indexados no cabeçalho oficial**, **0/7 atos posteriores com análise integral verificada nesta rodada**, e **0/65 linhas do catálogo alteradas**. Isto não representa 100% de conformidade normativa.
