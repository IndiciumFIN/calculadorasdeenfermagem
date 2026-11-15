# W7 v0.4.4 — Índice mestre atualizado da produção educacional

**Escopo:** conteúdo autoral preparado para revisão; nenhum material publicado no site ou incorporado à `main`. A revisão é centrada em ensino, questões e reutilização, não nos parsers.

## Produção desta rodada

| Objeto | Novos | Acumulado W7 |
|---|---:|---:|
| Microaulas | 11 | **38** |
| Artigos completos | 2 | **7** |
| Flashcards | 11 | **38** |
| Questões estruturadas | 20 | **59** |
| Casos fictícios | 3 | **10** |
| Checklists | 3 | **8** |
| Entradas de afirmação + fonte | 22 | **79** |

**Atenção:** apenas **33** das entradas anteriores passaram pelo processo de classificação individual da v0.3.9. As demais são **candidatas**; 79 não significa 79 afirmações clinicamente homologadas.

## Novos materiais e links relativos

- [Onze microaulas: urgência, comunicação e segurança](README_URGENCIA_SEGURANCA_v0.4.3.md)
- [Corpus estruturado das 11 microaulas](CANDIDATE_MICROLESSONS_UE_11_v0.4.3.jsonl)
- [Artigo: fluxo, rede de urgência e contingência](articles/ARTIGO_REDE_FLUXOS_CONTINGENCIA_URGENCIA_v0.4.4.md)
- [Artigo: segurança, incidentes, Notivisa e debriefing](articles/ARTIGO_SEGURANCA_INCIDENTES_NOTIVISA_URGENCIA_v0.4.4.md)
- [Casos, questões e checklists](README_UE_CASES_CHECKLISTS_v0.4.4.md)
- [Objetos de aprendizagem estruturados](REUSE_UE_CASES_CHECKLISTS_QUIZ_v0.4.4.json)

## Delimitação de fontes e direitos

Os títulos e IDs do corpus `microtopic_registry.csv` foram usados como referência de identidade, mas os registros originais de urgência constam como `MIXED_BY_SOURCE_AND_ATOM`. Não foram reproduzidos capítulos, ementas protegidas, arquivos de terceiros, dados clínicos identificáveis ou protocolos proprietários. As fontes governamentais e AHRQ foram utilizadas para elaboração independente, com URL e localizador.

A RDC Anvisa 36/2013 e o PNSP são marcos legais brasileiros; técnicas TeamSTEPPS da AHRQ são referências educacionais internacionais e não equivalem a obrigações normativas brasileiras. O Notivisa (eventos adversos assistenciais) foi diferenciado do Sinan (agravos de notificação compulsória).

## Controle de qualidade e próximos gates

- PASS — `no_overlap`
- PASS — `new_11_real_id`
- PASS — `source_rights_mixed_preserved`
- PASS — `new_22_evidence_links`
- PASS — `all_evidence_sources_known`
- PASS — `two_full_articles`
- PASS — `all_no_go`
- PASS — `synthetic_cases`
- PASS — `three_checklists`
- PASS — `nine_new_quiz`
- PASS — `combined_units`
- PASS — `combined_articles`
- PASS — `combined_flashcards`
- PASS — `combined_quizzes`
- PASS — `combined_cases`
- PASS — `combined_checklists`
- PASS — `claims_not_all_audited`
- PASS — `no_main_merge`
- PASS — `no_supabase_write`
- PASS — `no_clinical_protocol_created`

20/20 verificações **locais de estrutura e consistência de arquivos efetivamente recuperados do GitHub**, que não substituem teste de integração/CI, validação normativa frase a frase, avaliação clínica e aprovação editorial. Nenhuma publicação, merge, deploy ou escrita no Supabase foi realizada nesta etapa.

**Estado:** `HOLD_EDITORIAL`, `HOLD_CLINICAL_REVIEW`, `HOLD_RIGHTS_FOR_EXTERNAL_CONTENT` e `NO_GO_PUBLICATION`.
