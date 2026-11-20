# W7 v0.3.9 — revisão das 33 entradas de evidências e reutilização

**Escopo auditado:** 15 unidades de conteúdo autoral (5 da v0.3.7 e 10 da v0.3.8), contendo 33 entradas originalmente classificadas como afirmações com fontes. Estas 33 entradas **não são 33 normas nem 33 fatos clínicos validados**.

## Classificação rastreável

| Evidência | Contagem | Tratamento |
|---|---:|---|
| Fato normativo com localização oficial | 21 | Candidato fundamentado, sem liberação clínica |
| Evidência curricular de edição histórica | 2 | Válido apenas para aquela edição |
| Calendário de disciplina confirmado | 2 | Título/datas, não comprova ementa |
| Inferência explicativa fundamentada no contexto | 4 | Revisar redação e não atribuir literalmente à norma |
| Método editorial/didático, não comando normativo | 2 | Reclassificar como orientação pedagógica |
| Metadado autorreferencial, não evidência | 1 | Excluir de contagem de afirmações substantivas |
| Referência institucional indexada, URL principal retornou 404 | 1 | HOLD para revalidação da página ou programa assinado |
| **Total** | **33** | **Nenhuma aprovação automática** |

## Fontes oficiais verificadas

- Portaria GM/MS 5.674/2024 (Art. 423 §3º, Lista B, Cap. I) — causalidade e LDRT.
- NR-1, capítulo 1.5 na redação vigente desde 26/05/2026; página histórica do MTE distingue versões.
- NR-9 atualizada pela Portaria MTE 105/2026 (9.1.1, 9.3.1, 9.4.3).
- NR-17, 17.3.1 e avaliação ergonômica preliminar.
- NR-32, 32.1 e 32.2, incluindo risco biológico e seu PGR setorial.
- NR-7, página oficial, finalidade do PCMSO.
- Orientação de PGR do MTE, seção “O que é o PGR?”, complementada por perguntas e respostas de 2026, que são orientativas e não substituem a norma.
- Ementário histórico PUC Minas (oferta 3, turma 1 assíncrona) e calendário Einstein 2026-4BM foram visualmente verificados; página PUCPR recuperada em índice mas falhou na reabertura direta (HTTP 404).

**Controles de integridade:** 33/33 com ID, versão, rótulo, fonte, localizador e status individual; 16/16 validações locais de estrutura. Hash dos bytes originais de terceiros segue nulo, sem alegação de preservação forense.

## Reutilização

A matriz `educational/REUSE_PUBLICATION_MATRIX_15_v0.3.9.json` determina os destinos editoriais possíveis de cada átomo: artigo, aula, flashcard, quiz, caso fictício e checklist. `PART_OF` continua independente, não foi homologado. Materiais de atenção clínica ou protocolos requerem fontes e homologação adicionais.

## Próximas etapas para publicação

1. Revisar e reescrever 4 inferências, distinguindo-as da redação literal das normas.
2. Retirar 3 itens de método/metadado do indicador de afirmações normativas (sem apagar histórico).
3. Revalidar a página da PUCPR ou obter a versão institucional de curso, sem presumir a edição.
4. Submeter conteúdo à revisão editorial e clínica especializada, conforme necessidade, com registro de direitos e controle de versão.
5. Executar CI efetivo; `NO_GO` até evidências de aprovação.

**Nenhum merge, deploy, mudança no Supabase, cópia de texto integral de terceiro, nem publicação clínica nesta rodada.**
