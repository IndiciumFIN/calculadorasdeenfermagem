# W7 v0.4.5 — auditoria da grade curricular, fontes, direitos e cobertura

**Data:** 15/11/2026 · **Estado:** AUDITORIA CONCLUÍDA PARA AS BASES IDENTIFICADAS; GRADE COMPLETA E PUBLICAÇÃO `NO_GO`.

## Respostas executivas

1. **Existe grade curricular de referência?** Sim, como cadastro de **114 programas**, **985 itens curriculares** (83 programas com itens e 31 sem), **182 conceitos curriculares** e **1.514 vínculos candidatos**. Ela não está integralmente homologada. Entre os 31 programas sem itens, 28 estão dentro do escopo e três foram classificados fora do objetivo.
2. **As fontes estão todas mapeadas?** Não. Inventário público de 14/11 reconcilia 118 fontes no Drive com 157 no Supabase: **114 sem correspondência direta**, **3 aliases de URI candidatos** e **1 correspondência ambígua**, sem igualdade exata de ID/URI. NÃO significa que 114 fontes sejam inválidas.
3. **Licenciamento completo?** Não. O arquivo original `sources.jsonl` (118 linhas, SHA-256 confirmado) registra 84 direitos revisados e 34 pendentes. Mesmo entre as revisadas, 22 estão em quarentena, 19 apenas como referência, 22 exigem habilitação explícita, 21 aparecem como `DEFAULT_ACTIVE`. Isso não significa permissão de reprodução integral em todos os casos. No cadastro vivo `cko_evidence.sources` (157 registros), o campo `attributes` não possui chaves `license`, `rights` ou `copyright`.
4. **Conteúdo extraído/atomizado?** Parcialmente, e com objetos de naturezas distintas. Snapshot Drive: 124 documentos, **28.001 átomos de evidência**, 28.790 blocos e 9.102 vínculos evidência–tópico candidatos; isso não significa 28.001 claims clínicos homologados. O catálogo de 1.055 microtópicos contém **885 candidatos à atomização com fonte individual** e **170 associados ao corpus de evidências com direitos governados**. Nem mesmo os 170 demonstram aprovação clínica e jurídica por átomo.
5. **Produção básica a avançada em 100%?** Não. Na W7 existem **38 microaulas candidatas / 1.055 microtópicos identificados = 3,60% de cobertura de rascunhos**, não de conteúdo concluído. São **27** rascunhos entre 885 tópicos de Saúde do Trabalhador e **11** entre 170 de Urgência. **27 de 39 áreas temáticas** ainda não receberam microaula na W7. O registro de origem tem **141 módulos**, mas não há coluna de `difficulty`, `Bloom`, `prerequisite` ou equivalência que comprove uma progressão de básico a avançado. W5/CME, W6/Centro Cirúrgico e SRPA estão fora do denominador de 1.055, portanto a cobertura integral de TODA a plataforma não pode ser expressa por esse único percentual.

## Contraste das bases — não somar universos diferentes

| Base | Registro | Natureza |
|---|---:|---|
| Drive, arquivo `sources.jsonl` de 09/10 | 118 | Catálogo de fontes com direitos classificados |
| Supabase `cko_evidence.sources`, leitura de 15/11 | 157 | Metadados e acreditação de fontes; escopo não idêntico ao Drive |
| Supabase `cko_evidence.snapshots` | 84 | Capturas de fonte no banco |
| Supabase `cko_evidence.fragments` | 103 | Fragmentos extraídos no banco |
| Supabase `cko_evidence.claims` | 41 | Afirmações no banco, em vários estados |
| Supabase `cko_evidence.assertions` | 46 | Asserções estruturadas no banco |
| Supabase `cko_evidence.evidence_bundles` | 22 | Dossiês de evidência |
| Supabase `cko_evidence.source_accreditations` | 20 | Revisões de acreditação; **20 pendentes** |
| Supabase `ce_platform.courses`, `questions`, `content_documents` | 0 / 0 / 0 | Ainda não recebeu conteúdo editorial nessas tabelas |
| W7 GitHub | 38 microaulas, 7 artigos, 59 questões, 38 flashcards, 10 casos, 8 checklists | **Rascunhos educacionais**, não material implantado no banco/site |

O inventário histórico de 28.001 evidências no Drive e as 103 linhas de fragmentos no Supabase são **bases diferentes** e não equivalem entre si.

## Proveniência e direitos

- Fontes e atos normativos oficiais: verificar jurisdição, edição, vigência e localizador; utilizar como base para texto original e separar texto do ato de conteúdos editoriais protegidos.
- Materiais de editoras, manuais de associações e livros: referência bibliográfica e identificação temática sem importar o texto protegido, a menos que haja licença aplicável.
- Obras `CC BY`: observar atribuição, alterações, outros direitos sobre imagens e ativos de terceiros.
- `CC BY-NC`, `BY-ND`, `BY-NC-ND`: não presumir que adaptação, comercialização, tradução ou TDM por IA sejam liberados. Verificar obra, edição, licença e uso desejado; se necessário, solicitar autorização.
- Fontes `RIGHTS_AUDIT_REQUIRED`, `LICENSE_QUARANTINED` ou `HUMAN_REFERENCE_ONLY`: sem ingestão de texto integral para reutilização ou publicação automática.
- **Catálogo da Saúde do Trabalhador:** 34 fontes do Drive seguem com direitos em auditoria (`RIGHTS_AUDIT_REQUIRED`).

**Rastreabilidade:** referência no Drive `sources.jsonl` (ID `1C7T4ZDhFLHdTifp-3XqHLSwfvAwBWh2S`, SHA-256 `39352bc418844e563f85908cdac03f1cf1e12d01eac2ce513b9e97744187649e`), conciliada com `audit/SOURCE_REGISTRY_URI_SUMMARY_v0.2.1.json`. O SHA do registro de microtópicos acessível nesta rodada (`e325d280...`) **difere** do SHA registrado na W7 v0.3.2 (`58550a17...`): **HOLD de equivalência dos bytes**, ainda que a contagem e os 38 IDs de conteúdo coincidam.

## Diagnóstico de cobertura por área

Conforme matriz JSON adjacente: **39 áreas** (32 de Saúde do Trabalhador, 7 de Urgência/Emergência), **141 módulos**, **1.055 microtópicos**, com apenas 12 áreas recebendo algum rascunho W7.

Prioridades com maior lacuna incluem: Urgência clínica (D2: 0/51), Urgência traumática (D3: 0/34), Epidemiologia/OH04 (1/27), Bioestatística/OH05 (0/30), Processo de Enfermagem em Saúde do Trabalhador (OH19: 0/26), Imunização Ocupacional (OH20: 0/15), Pesquisa e Evidências (OH32: 0/26). A ordem de produção deve considerar riscos clínicos, pré-requisitos e fontes, não apenas tamanho da lacuna.

## Fluxo correto para reutilização

`GRADE_CANÔNICA_CANDIDATA → COMPETÊNCIA/PRÉ-REQUISITOS → SOURCE_ID + EDIÇÃO + LICENÇA → SNAPSHOT/FONTE AUTORIZADA → FRAGMENTO COM LOCALIZADOR → CLAIM ATÔMICO COM CLASSIFICAÇÃO → LINK SEMÂNTICO REVISADO → MICROAULA → ARTIGO/AULA/FLASHCARD/QUIZ/CASO/OSCE/CHECKLIST → QA CLÍNICO/EDITORIAL/JURÍDICO → PUBLICAÇÃO`.

Relações semânticas e licenças precisam ser avaliadas independentemente. Fontes não liberadas podem ser referências para sínteses autorais baseadas em fatos legalmente utilizáveis; **não** são autorização de copiar suas formulações proprietárias.

## Progressão básico → intermediário → avançado (proposta, não aprovada)

- **Básico:** conceitos, linguagem, anatomia e fisiologia pertinente, legislação aplicável, segurança e reconhecimento de riscos.
- **Intermediário:** interpretação de evidências, aplicação contextual, Processo de Enfermagem, comunicação, integração de serviços e planejamento do cuidado com protocolos pertinentes.
- **Avançado:** casos complexos simulados, integração interespecialidades, tomada de decisão supervisionada, pesquisa crítica, melhoria da qualidade e OSCE.

Cada microtópico exige atribuição revisada de `learning_level`, `learning_objective`, `competency_id`, `prerequisite_ids`, `source_claim_ids`, `rights_status`, `validation_status` e `content_object_ids`. Não preencher campos de competência com inferência não comprovada.

## Critérios para afirmar 100% em cada camada

- **Grade 100%:** todos os programas/disciplinas/módulos previstos identificados, com versão e escopo fixos, incluindo CME, CC, SRPA e especialidades, 28 lacunas curriculares em escopo resolvidas ou excluídas por decisão comprovada.
- **Fontes 100%:** cada entrada curricular com fontes necessárias mapeadas, edição/vigência/autoridade conferidas, licenciamento documentado por objeto e uso.
- **Atomização 100%:** cada afirmação editorial requerida com `source_id`, fragmento/localizador, hash da captura quando exigido, sem duplicidades e com revisão de semântica.
- **Aprendizagem 100%:** competências, pré-requisitos e níveis B/I/A definidos em toda a grade.
- **Conteúdo 100%:** cada objetivo com os formatos educacionais planejados, revisão especializada, avaliações e acessibilidade aprovadas.
- **Publicação 100%:** CI, segurança, direitos e gates clínicos concluídos; releases rastreáveis.

**A plataforma ainda não atende a esses seis critérios.** Não usar um único “% concluído” para substituir as aprovações de cada camada.

## Risco técnico adicional: banco de evidências

A inspeção retornou **alerta crítico de RLS desabilitado em sete tabelas `cko_evidence`**. É necessário revisar exposição no Data API, privilégios e políticas antes de reutilização ou divulgação de conteúdo potencialmente protegido. Nenhuma política foi alterada nesta auditoria.

## Próxima sequência editorial

1. Congelar uma versão da grade transversal e identificar disciplinas não contempladas no registro de 1.055 microtópicos; conciliar W5/CME, W6/Centro Cirúrgico/SRPA, W7 e os módulos de especialidades.
2. Conciliar IDs entre fontes Drive/Supabase e a divergência de hash do registro; manter todos os direitos herdados das fontes.
3. Atribuir nível e pré-requisitos com revisão pedagógica e estruturar uma matriz completa de objetivos de aprendizagem.
4. Produzir, por ondas, microaulas com claims rastreáveis, começando por base e segurança e avançando para casos e simulações clínicas somente após evidências.
5. Só contar `PUBLISHED_APPROVED` quando houver parecer clínico/editorial, direitos e teste; `DRAFT_AUTHORIAL` é progresso de produção, não de cobertura aprovada.

**Sem merge na main, sem deploy, sem migração Supabase e sem alteração retroativa nos átomos originais.**
