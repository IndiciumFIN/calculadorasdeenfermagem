# Crosswalk CME W5 — sem fusão de identidades

| Objeto | Origem | Tipo real | Estado |
| --- | --- | --- | --- |
| `cko.library.cme` | GitHub `cme.library.json` | Biblioteca de conhecimento existente; `object_refs=[]` | template_evaluation / not_reviewed / not_verified |
| `LIB-046` | Supabase `cko_governance.b6_knowledge_library_profile_v1_candidate` | Perfil de governança “Materiais de CME” | `BLOCK_UNTIL_SOURCE_VALIDATION_AND_PROFILE_GATE`; `HOLD_NOT_AUTHORIZED` |
| `cko.library.cme#module:cme-flow` e demais IDs | GitHub `cme.content.json` | Módulos **de página/UI** | não são unidades curriculares nem critérios clínicos |
| `CKO-W4-CME-MODULO-REVIEW` | W4.1, PR #66 `calculadorasdeenfermagem` | Primeiro módulo educativo separado, rascunho | preservado como versão anterior |
| `CKO-W5-CME-FUNDAMENTOS-PROCESSAMENTO` | W5 | **Novo conteúdo didático complementar** ao W4.1, não biblioteca nova | DRAFT / HOLD |
| `CKO-W4-CENTRO-CIRURGICO-REVIEW` | W4.1, PR #66 | Conteúdo distinto de Centro Cirúrgico/SRPA | related-only |
| `CARDIOLOGIA-UC-xx` | GitHub `dev-chatgpt-workspace` PR #66 | Especialidade com 10 UCs, 51 módulos detalhados e 295 tópicos | não relacionado como módulo de CME |

## Decisão de modelagem
A ligação biblioteca↔perfil é `CANDIDATE_GOVERNANCE_PROFILE_CROSSWALK` (não `EQUIVALENT_TO`). É necessário validar `exact binding`, origem e direitos; `LIB-046` lista explicitamente holds de materialização e origem. Não criar registros paralelos em `ce_platform.library_entities` ou `courses`.

## Drive contextual
O título histórico `Biblioteca de Materiais Cirúrgicos - Instrumentais e CME` (`biblioteca-cirurgica.html`) evidencia sobreposição editorial antiga. Não é autorização para unificar CME e Centro Cirúrgico. Nenhuma ementa institucional específica de CME foi recuperada; horas e certificação permanecem **nulas**.

## Rastreabilidade
- GitHub `cme.library.json` blob `ed09a836d6e66663f4db0c25580e05738103b5f5`.
- GitHub `cme.content.json` blob `4a0df56ca16f92d81fdf5ba9d9646e7a5310dd15`.
- GitHub `cme.provenance.json` blob `225bfed18028f17141a391c62783cdfe0ebbb918`.
- Supabase `LIB-046`: `evidence_status=RUN022_PROFILE_CONTROLLED_CANONICAL_EVIDENCE_NOT_UNIVERSAL`, `rights_status=HOLD_RIGHTS_CHAIN_NOT_FULLY_ASSURED`, publicação bloqueada.
- Drive histórico https://drive.google.com/file/d/13HQPOXR1ozh_QtaFZDqO9iaP5FINKer9/view.

**Pendências:** fonte institucional CME, conciliação exata LIB-046↔ biblioteca, fontes normativas com bytes e versão, direitos, revisão especialista e decisão de publicação. Não executar migração.
