# Crosswalk candidato: Resoluções Cofen 736/2024 e 787/2025 × Parecer 44/2026

**Data da consulta:** 2026-11-17. **EPIC:** #74; **PR:** #70; **WO:** P0 fonte/versão e P1 semântica curricular. **Status:** `EVIDENCE_INDEXED_CANDIDATE`, não publicação clínica. Consulta direta a fontes primárias oficiais; apenas metadados e paráfrases curtas, sem replicação integral.

## Fontes oficiais e granularidade

| Fonte / identidade | Localizador | Evidência delimitada | Uso candidato |
|---|---|---|---|
| Resolução Cofen 736/2024 | arts. 1º–4º | Processo de Enfermagem obrigatório onde há cuidado; cinco etapas inter-relacionadas: avaliação, diagnóstico, planejamento, implementação, evolução | `NORMATIVE_PROCESS_FRAMEWORK` |
| Resolução Cofen 736/2024 | arts. 6º–8º | Diagnóstico e prescrição de Enfermagem são atribuições privativas do enfermeiro; registros e participação da equipe seguem papéis diferenciados | `ROLE_BOUNDARY` |
| Resolução Cofen 736/2024 | art. 10 | Formação e educação permanente devem contemplar Processo de Enfermagem | `CURRICULUM_REQUIREMENT_CANDIDATE` |
| Resolução Cofen 787/2025 | arts. 1º–4º | Escopo: promoção, prevenção, tratamento e reabilitação em lesões cutâneas; exige avaliação integral e respeito à habilitação | `WOUND_CARE_SCOPE` |
| Resolução Cofen 787/2025 | art. 9º | Recomenda pós-graduação lato sensu para contextos de lesões complexas/especializados, com 360 h mais 20% de práticas supervisionadas | `TRAINING_RECOMMENDATION`, **não converter em exigência universal de registro de título** |
| Resolução Cofen 787/2025 | art. 12 | Revoga a Resolução Cofen 567/2018 | `SUPERSEDES` por fonte expressa |
| Parecer Cofen 44/2026 | conclusão, item 18 | Manifestação desfavorável à artrocentese e infiltração intra-articular por enfermeiros, inclusive com especializações em Estomaterapia e Estética | `SCOPE_NEGATIVE_OPINION`, não instrução clínica |

Fontes:
- https://www.cofen.gov.br/resolucao-cofen-no-736-de-17-de-janeiro-de-2024/
- https://www.cofen.gov.br/wp-content/uploads/2024/01/Resolucao-736-2024.pdf (publicação DOU)
- https://www.cofen.gov.br/resolucao-cofen-no-787-de-21-de-agosto-de-2025/
- https://www.cofen.gov.br/parecer-no-44-2026-camaras-tecnicas-de-enfermagem/
- https://www.cofen.gov.br/wp-content/uploads/2026/06/Parecer-no-44-2026-Camaras-Tecnicas-de-Enfermagem.pdf

## Decisões de reconciliação (sem duplicação)

1. `COFEN-736-2024:ART-10` gera requisito de **cobertura temática curricular** candidato transversal às 65 especialidades; **não** cria 65 novos objetos de fonte nem prova cobertura por curso. Proposta de vínculo `APPLIES_TO_EDUCATIONAL_SCOPE`, pendente de revisão semântica.
2. `COFEN-787-2025:ART-9` é recomendação para contexto definido, não critério universal de homologação curricular. A regra de 20% refere-se à carga horária de 360 h explicitada no artigo; não inferir prática supervisionada efetivamente cumprida por qualquer IES.
3. `COFEN-PARECER-44-2026:CONCLUSION-18` é manifestação específica negativa; não inferir proibição universal de todo procedimento injetável nem criar competência por analogia.
4. `COFEN-736-2024` e `COFEN-787-2025` têm escopos diferentes e podem coexistir como fontes de um mesmo objetivo educacional, sem `EQUIVALENT_TO` entre atos.
5. `COFEN-736-2024:ART-14` revoga a 358/2009; `COFEN-787-2025:ART-12` revoga a 567/2018. Guardar arestas de revogação **distintas** com artigo e fonte; nunca apagar a norma histórica.

## Critérios de teste candidatos, não executados

- T01: referência normativa exige `act_id`, `article_locator`, `official_url`, `source_date` e `evidence_status`.
- T02: `TRAINING_RECOMMENDATION` não pode ser automaticamente transformado em `MANDATORY_LICENSE_REQUIREMENT`.
- T03: `SCOPE_NEGATIVE_OPINION` não pode produzir `AUTHORIZED_PROCEDURE`.
- T04: `SUPERSEDES` exige artigo expresso e preservação do registro revogado.
- T05: deduplicação por `act_id + article_locator + edition`; jamais por palavra-chave ou título.
- T06: cobertura curricular só é aprovada com fonte do curso/edição e revisão competente, não por referência normativa transversal.

## Política de avanço não bloqueante

**AUTO_PERMITTED:** descoberta, leitura e indexação de metadados públicos, reconciliação por identificador, documentação e testes candidatos em branch de revisão. **GATED:** importação de texto integral protegido, atribuição de competência profissional, aprovação de PPC, direitos de adaptação/republicação, implantação e publicação clínica. Pendências `HOLD_SOURCE`, `HOLD_RIGHTS`, `HOLD_HUMAN` ficam associadas ao **objeto específico**, sem bloquear descoberta e indexação dos demais.

**Denominadores preservados:** 65 especialidades catalogadas, 14/65 com vagas na amostra, 38/1055 microaulas candidatas de Trabalho/Urgência, 0/22 correções canônicas comprovadas no baseline anterior. Este crosswalk contém **7 localizadores normativos** indexados; não representa 7 claims clínicos homologados. Não alterar main, Supabase, gates ou conteúdo publicado.
