---
content_id: CKO-W4-CME-MODULO-REVIEW
version: 0.1.1-correction
locale: pt-BR
classification: INDEPENDENT_EDUCATIONAL_MODULE_CANDIDATE
status: DRAFT_EDITORIAL / HOLD_SOURCE / HOLD_HUMAN / HOLD_RIGHTS / NO_GO
parent_core_ref: CKO-CORE-PROCESSO-ENFERMAGEM
library_ref: cko.library.cme
library_profile_candidate_ref: LIB-046
source_retired_object_ref: CKO-W4-CENTRO-CIRURGICO-CME
context: CME — Centro de Material e Esterilização
---

# CME — módulo educacional independente

> Correção W4.1: **CME é um módulo separado do Centro Cirúrgico/SRPA.** Sua biblioteca `cko.library.cme` permanece objeto distinto; não confundir módulo didático, biblioteca, módulo de interface e unidade curricular. Sem aprovação normativa/clínica, este texto não é POP.

## Evidências do cânone
No GitHub `dev-chatgpt-workspace`, `contracts/cko-bibliotecas/entities/libraries/cme.library.json` registra `cko.library.cme`, `review_status: not_reviewed`, `evidence_verification_status: not_verified` e `object_refs: []`. O arquivo `cme.content.json` organiza a página com módulos **de interface**, incluindo `cme-flow`, `processing-methods` e `quality-indicators`. Eles não são unidades curriculares aprovadas. No Supabase `Calculadoras-Smart`, o perfil `LIB-046 — Materiais de CME` está bloqueado para promoção, e sua correspondência com a biblioteca GitHub permanece candidata.

## Conteúdo de aprendizagem
O módulo aborda, como assuntos a aprofundar, a cadeia documental de produtos para saúde: recepção, identificação, limpeza, preparo/embalagem, processamento quando permitido, monitorização, armazenamento, disponibilização e rastreabilidade. A RDC Anvisa 15/2012 é referência a ser avaliada artigo por artigo; a lista de assuntos **não valida** método, equipamento, produto, ciclo, tempo, monitorização ou reprocessabilidade.

A documentação técnica do processamento e a documentação do cuidado de um paciente são registros distintos. Uma relação de identificadores pode apoiar rastreabilidade sem misturar escopos, proprietários e dados pessoais.

## Caso educacional fictício
Dois cadastros didáticos contêm: (A) identificação técnica de um lote disponibilizado pelo CME e (B) uma referência de material em registro assistencial. O aluno deve propor apenas um relacionamento de dados, preservando as duas finalidades. Nenhuma indicação ou liberação de produto pode ser inferida apenas dessa relação.

**Discussão:** a presença de um identificador não comprova que o produto seja reprocessável; é necessário avaliar instruções e exigências específicas, com responsáveis e fontes verificados.

## Questões comentadas
1. **O lote registrado pelo CME prova reprocessabilidade?** Não. A decisão depende do tipo de produto, informações técnicas e regras aplicáveis. Vínculo candidato: `CKO-CLAIM-M08-PS-09`.
2. **É correto misturar dados pessoais de prontuário com registro técnico do processamento?** Não. Os objetos possuem finalidades, permissões e responsabilidade próprias.
3. **O registro `cko.library.cme` é o mesmo objeto que este módulo?** Não. Ele é a biblioteca existente; este é um complemento didático independente candidato vinculado, sem homologação.

## Checklist de revisão
- [ ] Obter a ementa institucional do módulo antes de atribuir carga, unidade ou competências
- [ ] Conferir RDC 15/2012, normas e instruções por produto
- [ ] Validar IDs, relações, direitos e governança do perfil `LIB-046`
- [ ] Proibir publicação de instruções operacionais não aprovadas

**Gate:** `HOLD_SOURCE / HOLD_RIGHTS / HOLD_HUMAN / NO_GO`.
