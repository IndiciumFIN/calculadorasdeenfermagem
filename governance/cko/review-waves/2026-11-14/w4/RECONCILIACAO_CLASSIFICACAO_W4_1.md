# Recuperação de contexto e correção W4.1 — 14/11/2026

**HOLD_STRUCTURE / NO_GO.** Esta correção foi preparada a partir de leitura real do GitHub, Supabase e Google Drive; não é autorização de publicação ou de renumeração curricular.

## Falha histórica
A W4 original apresentava quatro complementos como “módulos” e unia Centro Cirúrgico/SRPA com CME no mesmo arquivo. Cardiologia, entretanto, é especialidade/trilha curricular. CME deve ser módulo didático separado, vinculado à sua biblioteca existente. A PR anterior e o ZIP W4 original permanecem evidências **históricas superseded**: o ZIP não foi alterado e continua contendo o documento misto original.

## GitHub — conteúdo recuperado
- `IndiciumFIN/dev-chatgpt-workspace`, [PR #66](https://github.com/IndiciumFIN/dev-chatgpt-workspace/pull/66), branch `cko/cardiologia-corpus-editorial-20261114`:
  - `datasets/01_unidades_curriculares.csv`: 10 UCs de 30h (total informado 300h).
  - `datasets/02_modulos.csv`: 51 módulos detalhados em 9 UCs.
  - `datasets/03_topicos.csv`: 295 tópicos, `EXTRAIDO_NAO_HOMOLOGADO`.
  - `editorial/17_UC08_DECISOES_PENDENTES.md`: oito eixos UC08 coincidem com UC07 e título UC08 coincide com UC09. `HOLD_HUMAN`.
- `main` do mesmo repositório, `contracts/cko-bibliotecas/entities/libraries/cme.library.json`: `cko.library.cme`, `object_refs: []`, `not_reviewed`, `not_verified`.
- `bindings/content/cme.content.json` e `bindings/composition/cme.composition.json`: `cme-flow`, `processing-methods` e outras estruturas são módulos de **página/UI**, não módulos curriculares.
- `bindings/provenance/cme.provenance.json`: origem `declared_unverified`, sem hash de fonte, exige revisão.

## Supabase `Calculadoras-Smart` (SELECT, sem mutações)
- `ce_platform.library_entities`: 56 linhas; `ce_platform.domains`: 45. Nas buscas textuais por Cardiologia/CME/Cirúrgico nas colunas examinadas, **não houve correspondência**; não extrapolar essa ausência para outros schemas.
- `cko_governance.b6_knowledge_library_profile_v1_candidate`: 79 perfis, com `LIB-046 — Materiais de CME`, `BLOCK_UNTIL_SOURCE_VALIDATION_AND_PROFILE_GATE` e `HOLD_NOT_AUTHORIZED`.
- `ce_platform.courses`: 0; `ce_platform.content_documents`: 0. Não há prova de promoção do currículo a essas duas tabelas.

## Google Drive — documentos abertos
- [PMO Corpus & Knowledge](https://docs.google.com/spreadsheets/d/1vi129pgXWMZPFddxlMd5YemMEohumxqk714yCoGCVOg/edit): Cardiologia 10 UCs/51 módulos; áreas citadas como frentes distintas: Cardiologia, U/E, Trabalho, Centro Cirúrgico, CME.
- [CKO-CONTENT-ENGINE](https://drive.google.com/file/d/1912hJ4dr4aYs_pn099lKRTncgjQMDSJe/view): distingue shell e módulos editoriais de página.
- [ARQUITETURA-MENU](https://drive.google.com/file/d/1ArkRisqBscGe7EfgVSDwKOehWv76wwcc/view): Centro Cirúrgico na navegação clínica, Saúde Ocupacional em ramo diferente. É documentação histórica de arquitetura.
- Busca por título exato CME no Drive não identificou uma ementa institucional específica; o PMO registra a frente. Não inferir nova UC ou carga horária de CME.

## Hierarquia aplicada
| Área ou objeto | Classificação | Identidade/ligação |
| --- | --- | --- |
| Cardiologia | ESPECIALIDADE / TRILHA CURRICULAR; W4 é projeção sobre tópico preexistente | `CARDIOLOGIA-UC-03-MOD-01-TOP-01` |
| Centro Cirúrgico e SRPA | COMPLEMENTO DIDÁTICO PRÓPRIO | `CKO-W4-CENTRO-CIRURGICO-REVIEW` |
| CME | MÓDULO EDUCACIONAL INDEPENDENTE CANDIDATO | `CKO-W4-CME-MODULO-REVIEW` → `cko.library.cme` → candidato `LIB-046` |
| Processo de Enfermagem | CORE transversal, **não** conteúdo duplicado | `CKO-CORE-PROCESSO-ENFERMAGEM` |

## Histórico e ação
- Objeto anterior `CKO-W4-CENTRO-CIRURGICO-CME`: superseded, dividido em dois documentos; o texto integral original é recuperável pelo commit histórico/ZIP W4.
- Cardiologia: mesmo `content_id`, agora tipado `CURRICULUM_SPECIALTY_PROJECTION`. **Não criar unidade ou módulo curricular**.
- Não houve alteração na `main`, no site, Supabase, nem promoção ou validação de claim.
- **Pendente**: fonte institucional específica para CME, crosswalk aprovado entre a biblioteca GitHub e `LIB-046`, fontes por dispositivo/fragmento, direitos e revisão profissional.
