# USP Apolo — triagem de escopo e proveniência de quatro atividades (candidato)

**Data:** 2026-11-16. **WO:** WO-CKO-CURR-20261115-04 (P1), condicionado a baseline P0 e direitos. **EPIC:** #74. **Modo:** leitura de metadados públicos, sem cópia de ementa integral.

## Identidade e elegibilidade

| Apolo activity ID | Período declarado | CH | Informação diferenciadora da página primária | Decisão candidata |
|---|---|---:|---|---|
| 92849 | 01/03/2020–28/02/2022 | 40 h | Centro Cirúrgico; descrição com relação à CME, cuidados perioperatórios e bibliografia de enfermagem | `POTENTIAL_NURSING_RELEVANCE_HOLD_PARENT_PROGRAM` |
| 125923 | 01/03/2025–28/02/2027 | 80 h | Centro Cirúrgico; conteúdo semelhante ao 92849, mas edição, carga horária e ID diferentes | `POTENTIAL_NURSING_RELEVANCE_HOLD_PARENT_PROGRAM` |
| 122199 | 01/03/2024–01/03/2027 | 242 h | Centro Cirúrgico; estágios no centro cirúrgico e centro obstétrico do Instituto Central; sem identificação de curso de Enfermagem na página | `HOLD_DISCIPLINE_AND_PARENT_PROGRAM` |
| 135580 | 01/03/2026–28/02/2031 | 710 h | Centro Cirúrgico; descrição pública apenas genérica | `HOLD_DISCIPLINE_AND_PARENT_PROGRAM` |

URLs oficiais por ID:
- https://uspdigital.usp.br/apolo/apoObterAtividade?cod_oferecimentoatv=92849
- https://uspdigital.usp.br/apolo/apoObterAtividade?cod_oferecimentoatv=125923
- https://uspdigital.usp.br/apolo/apoObterAtividade?cod_oferecimentoatv=122199
- https://uspdigital.usp.br/apolo/apoObterAtividade?cod_oferecimentoatv=135580

## Reconciliação e riscos

- Identidade primária `institution=USP; system=Apolo; activity_offering_id`; não deduplicar por título nem semelhança de descrição. Quatro atividades distintas, zero programas novos, zero vínculos aprovados.
- A presença de terminologia de Enfermagem ou bibliografia de Enfermagem **não comprova** curso-mãe, profissão de matrícula, tipo de formação ou equivalência a especialidade Cofen. As duas atividades mais longas tampouco devem ser automaticamente classificadas como Enfermagem.
- `program_id`, unidade, curso-mãe, modalidade, coorte e vínculo `PART_OF`: **HOLD_SOURCE** até página institucional com relação explícita. Evitar contaminação de currículo de Enfermagem por atividades de Medicina ou outras áreas.
- Direitos: indexação de fatos bibliográficos/administrativos e URL não concede licença para armazenar e republicar texto integral, imagens, avaliações ou bibliografia; `HOLD_RIGHTS` por operação.
- Revisão de pertinência curricular e mapeamento de competências: `HOLD_HUMAN`; nenhum claim clínico derivado destas páginas.
- Nenhuma exclusão ou mudança de 65 especialidades, 114 programas, 985 átomos e 1.514 links candidatos; indicadores permanecem baseline até reconciliação formal.

## Critério da próxima microtarefa

Buscar no próprio Apolo página de oferta do **curso** contendo o ID de atividade, curso, edição e unidade. Somente depois propor `activity_id -> course_offering_id -> program_id`, com revisão humana. Não promover registros nem modificar Supabase, main ou publicação.

## Evidência de CI anterior

Commit `61ec4a97f37ad5e5d9ce0854988c43c239d23a80`: auditoria curricular PASS https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43924560784 ; pipeline PASS https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43924560795 ; CI PASS https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43924560971 ; invariantes canônicos FAIL https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43924560776 . Estes runs **não validam este novo commit**.
