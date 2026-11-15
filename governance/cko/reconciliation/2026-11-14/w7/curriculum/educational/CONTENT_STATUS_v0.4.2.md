# W7 — painel consolidado de conteúdo (v0.4.2)

**Data:** 15/11/2026. **Foco:** produção educacional autoral reutilizável, sem promoção clínica ou institucional.

## O que foi efetivamente criado

| Objeto | Existia até v0.4.0 | Nova entrega | Total |
|---|---:|---:|---:|
| Microaulas candidatas | 15 | 12 | **27** |
| Artigos autorais completos | 2 | 3 | **5** |
| Flashcards | 15 | 12 | **27** |
| Questões estruturadas | 15 | 24 (12 microaulas + 12 casos) | **39** |
| Casos fictícios | 3 | 4 | **7** |
| Checklists educacionais | 2 | 3 | **5** |
| Entradas de afirmações/evidências | 33 revisadas na v0.3.9 | 24 novas candidatas | **57 entradas**, sem equivaler a 57 provas clínicas |

**Cobertura em relação ao registro de 1.055 microtópicos:** 27 temas com microaulas candidatas; **não** significa que o restante esteja validado ou que 27 tenham aprovação clínica.

## Novos eixos elaborados

- SUS, PNSTT, Renastt (denominação vigente desde 2024), Cerest e integração com a rede de atenção.
- VISAT, análise de processos, Sinan, notificação compulsória baseada na Portaria GM/MS 11.211/2026 e qualidade da informação.
- Ergonomia AEP/AET, fatores de risco psicossociais e capítulo 1.5 da NR-1 em vigor desde 26/05/2026.

## Artigos integrais

- [oldpgr](articles/ARTIGO_GRO_PGR_PCMSO_v0.4.0.md) — 6549 caracteres
- [oldbio](articles/ARTIGO_RISCO_BIOLOGICO_SERVICOS_SAUDE_v0.4.0.md) — 6229 caracteres
- [sus](articles/ARTIGO_SUS_PNSTT_RENASTT_CEREST_v0.4.2.md) — 8424 caracteres
- [visat](articles/ARTIGO_VISAT_SINAN_NOTIFICACAO_2026_v0.4.2.md) — 9393 caracteres
- [erg](articles/ARTIGO_AEP_AET_RISCOS_PSICOSSOCIAIS_v0.4.2.md) — 9770 caracteres

## Objetos reutilizáveis

As microaulas e cada artigo possuem temas e fontes rastreáveis. Os casos contam com perguntas, alternativas e gabaritos; os checklists são exercícios de aprendizagem e **não** atestados de conformidade. Todos permanecem sob `NO_GO_PUBLICATION`.

## Avaliação da integridade documental

- PASS baseline_15
- PASS batch_12
- PASS no_dup
- PASS all_5_articles_present
- PASS new_3_no_go
- PASS case_counts
- PASS checklist_counts
- PASS quiz_counts
- PASS flashcards
- PASS claim_numbers
- PASS all_new_no_go
- PASS all_old_no_go
- PASS topic_id_source_csv_manual_verified
- PASS no_main_merge
- PASS no_release_claim

Esta conferência valida contagens, referências e campos estruturais, não substitui leitura clínica, validação independente de fonte primária, revisão jurídica e editorial ou CI. Preservados: corpus original, 985 itens curriculares históricos, branches de origem e o status do PR #70 aberto com CI bloqueante.
