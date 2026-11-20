# W7 v0.3.1 — somente currículo atomizado: Cardiologia / Cirurgia Robótica

**Estado: CANDIDATE / HOLD_SOURCE_EDITION / HOLD_RIGHTS / HOLD_CLINICAL / NO_GO**

Recuperados **12 títulos de componentes curriculares** (6 + 6), ligados por ID aos programas PG-EIN-CARDIO e PG-EIN-ROBOT, ambos presentes nos 25 programas ainda sem nova grade na rodada v0.3.0. As duas fontes indicam 360h cada, conferidas pela soma dos componentes. Estágio foi tipificado como PRACTICUM, sem transformá-lo em disciplina clínica.

## Fontes
- Cardiologia: ebook institucional do Einstein em https://conteudo-ensino.s3.sa-east-1.amazonaws.com/documentos/pos-graduacao/e-book/pos-enfermagem-em-cardiologia-e-hemodinamica.pdf; seção DISCIPLINAS (texto web extraído, linhas 163-170). O material inclui 6 componentes, 360h. **A edição/compatibilidade com oferta 2026/2027 não foi homologada**. Captura visual de PDF falhou por cache; bytes e hash binário não obtidos.
- Cirurgia Robótica: página institucional https://cirurgiarobotica.ensinoeinstein.com/cirurgia-robotica/enfermagem-em-cirurgia-robotica/; seção PROGRAMA E METODOLOGIA recuperada por índice de busca, acesso direto deu HTTP 403. Seis blocos, somando 360h, permanecem pendentes de verificação de edição e da fonte primária acessível.
- Cronograma de Cirurgia Robótica 2026-5: https://conteudo-ensino.s3.sa-east-1.amazonaws.com/documentos/pos-graduacao/cronogramas/2026/cronograma-enfermagem-em-cirurgia-robotica-mensal-pta-2026-5.pdf. Ele informa datas e formatos, **não** comprova módulos. Guardado como evidência contextual negativa e não como grade.

**Sem inferir que a edição do ebook ou página atual coincide com a grade 2026/2027.** Não inventamos ementa, objetivos específicos, competências, avaliações, aulas ou links temáticos.

## Proveniência dos 191 objetivos parafraseados
A fonte original W7 v0.2.9 contém 191 registros PROGRAM_OBJECTIVE de 32 programas, associados a **20 CURSRCs**. O arquivo PARAPHRASE_SOURCE_REVIEW_QUEUE_v0.3.1.jsonl agrupa os IDs (sem republicar os objetivos) para recuperar texto primário, confirmar versões e verificar limites de paráfrase por fonte. Nenhuma paráfrase recebeu homologação de literalidade, direitos ou semântica.

## Integridade e escopo
Os 985 itens canônicos de origem e 30 títulos novos anteriores não foram editados. Apenas 2 dos 25 programas passam a ter uma nova **fonte candidata**; 23 seguem sem novas fontes detalhadas comprovadas nesta rodada. Não houve escrita no Supabase, merge, deploy ou alteração das branches de origem. Testes do artefato são estruturais e não comprovam CI GitHub nem autorização de direitos.

## Arquivos
- CURRICULAR_COMPONENT_CANDIDATES_12_v0.3.1.jsonl
- CURRICULAR_PRIMARY_SOURCE_EVIDENCE_2_v0.3.1.json
- CURRICULUM_COVERAGE_DELTA_2_v0.3.1.jsonl
- PARAPHRASE_SOURCE_REVIEW_QUEUE_20_v0.3.1.jsonl
- ROBOT_SURGERY_2026_CALENDAR_EXCLUSION_v0.3.1.json
- QA_CURRICULUM_REVIEW_v0.3.1.json
- SUMMARY_v0.3.1.json
- README_v0.3.1.md
