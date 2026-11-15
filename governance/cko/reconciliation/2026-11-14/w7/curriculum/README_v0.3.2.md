# W7 v0.3.2 — crosswalk curricular de microtópicos (somente metadados)

**HOLD_SEMANTIC_REVIEW / HOLD_RIGHTS_PER_SOURCE / NO_GO**

Recebidos e inspecionados previamente os 15 anexos. Após revisão estática e verificação de duplicação, a fonte de microtópicos foi limitada ao corpus v1.7.7 e suas cópias comprovadamente idênticas; nenhuma ferramenta, script de aquisição ou conteúdo clínico foi executado ou importado.

**Confronto:** 1.055 microtópicos (885 Enfermagem do Trabalho e 170 Urgência/Emergência) contra 985 itens curriculares, 182 rótulos de tópicos e 42 títulos candidatos W7. Resultado: 27 pares para avaliação, representando 18 microtópicos, sendo 1 coincidência textual normalizada, 10 aproximações lexicais fortes e 16 moderadas. **1.037 microtópicos não tiveram correspondência textual conservadora; isso não significa conteúdo inexistente ou excluído.**

Critérios locais: normalização Unicode e de pontuação, remoção conservadora de palavras funcionais e muito genéricas, índice invertido, similaridade lexical ponderada por frequência, mínimo de dois termos informativos compartilhados para pares não exatos, limite de cinco sugestões por microtópico. Nenhum indicador lexical autoriza transformação em relação normativa, clínica, semântica ou curricular canônica.

## Integração segura
- ID-only public review register em `LEXICAL_REVIEW_PAIRS_IDS_ONLY_v0.3.2.jsonl`. Os rótulos completos, status de 1.055 microtópicos, cobertura por domínio e 20 testes locais estão no pacote de revisão mantido fora do repositório público.
- `MICRO-WORK-00199` e `CURITEM-00145` coincidem como *título*, mas não foram aprovados como equivalentes.
- Os pares lexicalmente próximos podem ser falsos positivos (ex. "doenças relacionadas ao calor" não equivale a "doenças relacionadas ao trabalho"). Revisão humana é obrigatória.
- Direitos por item e fonte, edição, escopo de programa e validação clínica/editorial são gates independentes.
- O registro de 985 itens, 182 tópicos, 1.514 vínculos históricos, mais 42 títulos candidatos, permanece intacto. Nada foi publicado.
- Este commit é uma documentação de reconciliação, **não uma importação canônica de 1.055 tópicos**. `main` e Supabase não devem ser alterados.

A revisão local está vinculada por SHA-256 no sumário e pode ser reaplicada sem alterar fonte e nem usar APIs de escrita.
