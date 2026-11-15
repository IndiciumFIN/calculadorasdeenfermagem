# W7 v0.4.5 — contrato pedagógico de reutilização de conteúdo (candidato)

**Estado:** `DRAFT_EDUCATIONAL_ARCHITECTURE`; não homologa curso, prontuário, conduta nem texto protegido.

## Identidade curricular

Uma disciplina institucional e um microtópico autoral não são a mesma entidade. A disciplina registra fonte e versão da instituição; um microtópico reúne conceitos e competências candidatos. Vínculos `PART_OF` só devem ser materializados após prova de que aquela edição realmente contém o tema. Títulos parecidos não são suficientes.

## Requisitos mínimos de cada átomo antes da publicação

| Campo | Requisito |
|---|---|
| Identidade | `microtopic_id`, `curriculum_context`, `competency_id` |
| Sequenciamento | `learning_level` (B/I/A), `prerequisite_ids`, `learning_objective` |
| Fonte | `source_id`, edição, jurisdição, publicador, vigência |
| Evidência | `snapshot_id`, `fragment_id`, localizador e hash quando aplicável |
| Licença | tipo, finalidade, reuso comercial, adaptação/tradução, TDM, decisão revisada |
| Claims | afirmações mínimas com classificação de fato/inferência/hipótese |
| Reuso | relações explícitas com artigo, aula, quiz, flashcard, caso, OSCE, checklist |
| Revisão | revisão técnico-científica, editorial, jurídica, aprovação clínica se necessária |
| Distribuição | canais, idiomas, acessibilidade, status de publicação, data de revisão |

## Aprendizagem

**Básico** introduz fundamentos e vocabulário, **intermediário** aplica conceitos com contexto e fluxos, **avançado** exige integração entre áreas, simulação e análise crítica. Essa é uma **rubrica proposta**. A grade existente ainda não registra os níveis e pré-requisitos com aprovação.

## Reutilização de um mesmo fundamento

A fonte governamental sobre segurança do paciente pode fundamentar um claim autoral sobre comunicação. Esse claim pode ser usado em aula, flashcard, questão ou caso fictício. O uso de um mesmo claim em cinco formatos não cria cinco evidências independentes. Cada derivado aponta ao claim e à fonte, de modo que alteração de norma gere fila de revisão para todos os produtos dependentes.

## Gates

Regras de publicação: `SOURCE_EVIDENCE_APPROVED && SOURCE_LICENSE_USABLE_FOR_ACTION && CLAIM_REVIEW_APPROVED && CURRICULUM_CONTEXT_APPROVED && EDITORIAL_APPROVED && CLINICAL_APPROVED_WHEN_APPLICABLE && SECURITY_CI_PASS`.

O status `DEFAULT_ACTIVE` de uma fonte no registro de direitos não é uma licença automática para qualquer modo de uso. Um campo de direitos ausente não pode ser presumido como `ALLOWED`. Quando a exigência é de aprovação humana, o sistema deve manter o item em `HOLD`.

## Primeira rodada de priorização de conteúdo

- **Onda B1:** fundamentos do Processo de Enfermagem (COFEN 736/2024), segurança, anatomia/fisiologia de base e pesquisa de evidências, atravessando Urgência, CME, Centro Cirúrgico e SRPA.
- **Onda I1:** organização de processos de trabalho, vigilância, prevenção de incidentes, avaliação do paciente e assistência perioperatória, vinculando fontes específicas por área.
- **Onda A1:** simulações, cenários integrativos, OSCE, questões clínicas de maior complexidade e análise de incidentes, com validação especializada antes de instrução prescritiva.

Os campos de nível só serão promovidos após revisão da grade e alinhamento à fonte primária. Não utilizar `W7-38` como representação de 100% do planejamento geral.

**Nenhuma mudança clínica, jurídica ou de publicação efetuada por este contrato.**
