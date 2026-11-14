# Auditoria CKO / NCOS — normativos externos, políticas internas e branches

**Corte:** 14/11/2026. **Escopo:** repositório privado `IndiciumFIN/calculadorasdeenfermagem`; leitura de 55 branches existentes antes deste relatório e 41 PRs abertas. Esta branch de auditoria eleva o inventário para 56 branches. **Decisão:** `HOLD_MERGE / HOLD_CLINICAL / HOLD_NORMATIVE_VERSION / HOLD_RIGHTS`.

## 1. Método e limitações

1. Enumerar SHA de todas as branches e PRs abertas e preservar snapshot no mesmo commit da auditoria: `BRANCH_PR_INVENTORY.json`.
2. Comparar as famílias e as branches com potencial de afetar Kernel, fontes, conteúdo, segurança e governança (comparação Git `main...branch`); **não** atribuir status de auditoria profunda a cada um dos milhares de blobs das branches históricas.
3. Ler os normativos internos atuais, os contratos candidatos nas branches históricas e os PMO M08/M09, inclusive 46 claims e seus dispositivos declarados.
4. Consultar fontes primárias externas: Cofen, Anvisa, HL7 e NLM, e fontes públicas oficiais LGPD. Separar **atos legais brasileiros**, **padrões técnicos internacionais**, **documentação interna** e **propostas candidatas**.
5. Classificar evidência como `CONFIRMADO`, `CONFLITO`, `RISCO`, `PENDENTE`; **não afirmar vigência normativa definitiva**, direitos editoriais ou homologação clínica sem verificação própria de publicação, alterações e revisão humana independente.
6. Nenhuma merge, branch deletion, Supabase write, Drive write, publicação ou autorização clínica nesta auditoria.

**Fontes externas checadas:**
- Cofen Resolução 736/2024: https://www.cofen.gov.br/resolucao-cofen-no-736-de-17-de-janeiro-de-2024/
- Cofen Resolução 754/2024 (prontuário eletrônico e plataformas digitais; revogação da 429/2012): https://www.cofen.gov.br/resolucao-cofen-no-754-de-16-de-maio-de-2024/\n- Anvisa RDC 36/2013 em AnvisaLegis: https://anvisalegis.datalegis.net/action/ActionDatalegis.php?acao=abrirTextoAto&cod_menu=1696&cod_modulo=134&numeroAto=00000036&orgao=RDC%2FDC%2FANVISA%2FMS&pesquisa=true&seqAto=000&tipo=RDC&valorAno=2013
- Anvisa, orientação de prazos: https://www.gov.br/anvisa/pt-br/acessoainformacao/perguntasfrequentes/servicos-de-saude/notificacao-de-incidentes-e-eventos-adversos-relacionados-a-assistencia-a-saude
- HL7 FHIR R4 v4.0.1 Vital Signs: https://hl7.org/fhir/R4/observation-vitalsigns.html ; https://hl7.org/fhir/R4/vitalsigns.html
- MedlinePlus XML: https://medlineplus.gov/xmldescription.html
- NLM direitos MedlinePlus: https://medlineplus.gov/about/using/usingcontent/
- NLM MeSH XML, versões e direitos: https://www.nlm.nih.gov/mesh/xml_data_elements.html ; https://www.nlm.nih.gov/databases/download/mesh.html ; https://www.nlm.nih.gov/databases/download/terms_and_conditions.html
- Ministério da Saúde, LGPD de dados de saúde: https://www.gov.br/saude/pt-br/acesso-a-informacao/lgpd

**Referências internas pinadas:**
- `main` `e0f62491b104f4a97c6025a6393cabc2e7ada30e`: `docs/GOVERNANCE.md`, `docs/GATES.md`, `docs/DETERMINISTIC_RULES.md`, `docs/SOURCES_HIERARCHY.md`, `docs/AGENTS.md`, `.github/workflows/{ci,pipeline,canonical-invariants}.yml`.
- Corpus M08/M09 `d395f6e69e935570d5355ba930745bf8cd91f537`: `governance/cko/canonical-atomic/2026-11-14/PMO_REGISTER_SNAPSHOT_M08_M09.json`.
- Correções estruturais `14fdc8a30369001bf0e0a0d37c80ab7e43b6eb2e` (PR #40).
- Metamodelo `d0197788d2453066d738c48441a2ad7a0ad32f73` (PR #49).
- Recuperação PMO `pmo/recovery-controlled-20261019`; agentes candidatos `feat/ce-local-agent-assurance-20261019`; G0 `fix/ce05-kernel-ci-security-20261017`; pilotos `migration/pilot-policies-20261017`; consolidação histórica `integration/canonical-main-20261017`.

## 2. Inventário e destinos de comparação

- **Inicialmente 55 branches**: 36 `cursor/*`, 6 `feat/*`, 4 `migration/*`, 2 `fix/*`, 2 `staging/*`, 1 `pmo/*`, 1 `integration/*`, 1 `audit/*`, `main` e uma branch individual `IndiciumFIN-patch-1`. A presente branch de auditoria foi criada depois desse corte.
- **41 PRs abertas**, 31 não-draft, 10 draft; **33 PRs abertas em `cursor/*`**. As PRs de Cursor têm muitas propostas semelhantes de WO/Drive, mas não são idênticas por SHA/implementação; nenhuma exclusão ou merge foi autorizada.
- `integration/canonical-main-20261017`: 8 commits à frente / 6 atrás de `main` em sua comparação, com retirada antiga de `contracts/fonts` que se sobrepõe ao saneamento da PR #40; NÃO importar a branch inteira.
- `fix/ce05-kernel-ci-security-20261017`: 12 commits à frente, política `CE-GOV-WO-ADMISSION-001` proposta, WO G0 `DRAFT_NOT_ADMITTED`. Autoridade formal não comprovada.
- `pmo/recovery-controlled-20261019`: 201 commits à frente e 107 arquivos de diferença, evidências históricas e limitações de custódia; requer verificação independente de snapshot atual.
- `feat/ce-local-agent-assurance-20261019`: 229 commits à frente e 139 arquivos de diferença; registros de agentes explicitamente `NOT_DEPLOYED`/`LOCAL_CANDIDATE_NOT_KERNEL_ADMITTED`.
- `migration/full-directory-20261017` e `migration/candidate-f08-20261017`: até 300 arquivos no primeiro lote da resposta de comparação, incluindo snapshots antigos e material legado; nunca transferir automaticamente (custódia, direitos, possível informação sensível, conflitos).
- `migration/pilot-policies-20261017`: nove políticas JSON `CANDIDATE_NOT_HOMOLOGATED`; `regulatorio` e `grc` proíbem autopromoção e confundimento de WO com autorização.
- `staging/wo-kernel-normativos-cli-20261016`: material normativo candidato; `universal_normative_naming.json` declara `NOT_SUBMITTED` e campos `CFC/CPC` não pertinentes ao domínio clínico CE.
- `cursor/atomiza-o-arquivos-kernel-ebc1` e `cursor/arquivos-kernel-pol-ticas-8061`: duas implementações distintas de WO/Drive; a primeira usa detecção de textos/nomes de validadores, a segunda inclui sondagem de metadados Drive; nenhuma é recibo de admissão formal. Seleção requer comparação de contratos, testes negativos, privilégio mínimo, sem leitura remota não autorizada.
- PR #39 (conteúdo clínico), #40 (Kernel/CLI), #46 FHIR, #47 MedlinePlus, #48 MeSH, #49 (metamodelo) são **DRAFT/HOLD**, ainda empilhadas, não somadas automaticamente à `main`.

## 3. Matriz de conformidade por tipo normativo

| Controle | Referencial | Observação verificável | Parecer |
|---|---|---|---|
| Processo de Enfermagem | Res. COFEN 736/2024 arts. 1–14 | 5 etapas recorrentes; diagnóstico/prescrição privativos do enfermeiro; demais registros segundo responsabilidade | Claims M08/M09 têm base textual; revisão individual/efeito editorial HOLD |
| Normativos substituídos | Res. COFEN 736/2024 art. 14 | 358/2009 expressamente revogada | Qualquer branch com PE antigo como norma vigente exige atualização |
| Prontuário digital e rastreabilidade | Res. COFEN 754/2024 arts. 3–9 | Regras de plataforma, sigilo, acesso e registros; **revogação da COFEN 429/2012** | Acrescentar norma conexa e dependências de segurança aos claims PE art. 8º; revisar referências históricas |
| Segurança do paciente | RDC 36/2013 arts. 2, 4, 7–10 | Exceções de abrangência; NSP; PSP; notificações até 15º dia útil e 72 h para óbito | M08 isolado é editorialmente incompleto; M09 adicionou claims, sem homologação de versão |
| Interoperabilidade | HL7 FHIR R4 4.0.1 | Vital Signs exige status, código LOINC, categoria, paciente, tempo, UCUM ou ausência; painel de PA tem componentes e existe painel 85353-1 | PR #46 implementa subconjunto estrito, não certificado FHIR integral |
| Informações educativas | MedlinePlus NLM | Resumos próprios de *health topics* são domínio público nos EUA, com atribuição; ADAM, monografias ASHP, imagens e outros itens podem ser licenciados | PR #47 **não deve afirmar que todos os full-summary são protegidos**; classificar por tipo/obra e uso |
| Terminologias | NLM MeSH | Descriptor, Concept, Term, Qualifier e SCR são tipos distintos; versões/DTD de ano de produção, termos de atribuição e atualização | PR #48 cobre Descriptor apenas; falta validação de release/DTD e direitos |
| Proteção de dados | LGPD 13.709/2018 | Dados de saúde são dados pessoais sensíveis; data/hora e medidas podem permitir reidentificação | FHIR real continua `HOLD_LGPD`; hash do registro não anonimiza |
| Governança interna | MGN; GATES; DETERMINISTIC_RULES | Fonte legal oficial prioritária; átomo nasce não verificado; evidência, WO, revisão e gate | Parte dos controles existe só em Markdown ou candidate JSON; comprovação executável incompleta |

**Ressalva de vigência:** os dispositivos acima são demonstráveis nas fontes consultadas; a auditoria não verificou cadeia jurídica completa de alterações e revogações até a data em todos os diários oficiais. Não converter `CURRENT_VERSION_REVIEW_PENDING` em `VIGENTE` automaticamente.

## 4. FINDs com severidade e evidências

### P0 — Bloqueios de segurança e integridade

**FIND-CKO-X01 — CI permissivo na main.** `.github/workflows/ci.yml` contém `npx tsc --noEmit || echo "Type check skipped..."` e `python packages/cli/main.py --help || echo "CLI skeleton"`; o workflow pode concluir verde mascarando falha. `pipeline.yml` executa compilação, help e registro mínimo, não G1–G6 completos. **Remediação:** pipeline estrito sem `|| echo`, testes adversariais e branch rules antes de merge.

**FIND-CKO-X02 — Gate G6 documental, não comprovadamente implementado.** `docs/GATES.md` declara G1–G6 e referência a `.github/workflows/gate.yml`; a `main` contém quatro workflows, **não** `gate.yml`. Exemplo G6 usa `random.sample` e apenas imprime `OK`, sem comparar o texto com o normativo. Commit `Reviewed-by:` não basta como identidade de aprovador independente. **Remediação:** aprovador humano confiável, 46 revisões claim-by-claim, auditoria vinculada ao SHA do texto e status não publicável.

**FIND-CKO-X03 — Critério técnico de parser é fraco.** `scripts/verify_repository_integrity.py` faz `is_file` no caminho de parser. Passar a existir arquivo não garante função, parsing nem direitos; PRs #46–#48 têm bons testes sintéticos, mas dependem de revisão externa. **Remediação:** smoke por contrato + schema de saída + negativos reais, direitos e política; não alterar contagem de pendências para obter PASS falso.

**FIND-CKO-X04 — Admissão Kernel vs. candidato.** Branch `fix/ce05-kernel-ci-security-20261017` contém `CE-GOV-WO-ADMISSION-001.candidate.json` `PROPOSED_NOT_HOMOLOGATED` e `WO-G0-CORRECTIVE-20261017.json` `DRAFT_NOT_ADMITTED`; `pmo/recovery-controlled` confirma falta de recibo de admissão. **Remediação:** separar `FIND → policy → validator → TASK → WO → Kernel receipt → isolated execution → independent audit → promotion` sem aceitar simples presença de arquivo.

**FIND-CKO-X18 — Lockfile npm incoerente, mascarado anteriormente.** Ao retirar os `|| echo` em `PR #52`, o [Actions #43587616906](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43587616906) revelou falha reproduzida em `npm ci`: `postcss@8.4.31` ausente no `package-lock.json` frente às dependências atuais. O job Python passou; a verificação TypeScript sequer iniciou. **Remediação:** regenerar lockfile com revisão independente de versões/integridade, exigir `npm ci` e TypeScript PASS, sem substituir por fallback. WO #53.

**FIND-CKO-X05 — Status de proteção de branch insuficientemente comprovado.** Endpoint GitHub de proteção da `main` respondeu 403 por permissão, enquanto a API de rulesets retornou 403 informando restrição do recurso ao plano/repo privado. **Remediação:** verificar permissões/branch rules pela interface/admin, validar revisão obrigatória e status checks; **não afirmar que existe proteção real**.

### P1 — Divergências clínicas, normativas, de dados e contratos

**FIND-CKO-X06 — M08 vs M09 e completude.** `CONFLICT-CKO-M09-COMPLETENESS-20261114` continua aberto: M08 art. 10 não explicita 15º dia útil/72h, PE art. 8º não discrimina plenamente deveres. Os 12 claims M09 suplementam os 34 iniciais; não retroativamente revisam automaticamente os 3 mestres ou quizzes. **Remediação:** matriz dispositivo → claim → mestre → questões → flashcards, revisão humana/artigo.

**FIND-CKO-X07 — Mapeamento fonte legal → contrato genérico não comprovado.** O PMO contém `SRC-COFEN-736-2024` e `SRC-ANVISA-RDC36-2013`, mas o registro estrutural contém `cofen_dou` / `anvisa_dou`. Nenhum crosswalk oficial verificado. **Remediação:** WO #50 com URL/identidade DOU, hash, versão, retificação, finalidade e auditor independente.

**FIND-CKO-X08 — 16 parsers + 9 validadores em HOLD na infraestrutura; divergência de declarações.** `PR #40` fecha os erros estruturais de namespace/duplicatas, mas strict CI mantém 16 parsers faltantes; 5/14 validadores passaram em self-test, 9 não. `PR #49`: 0 ERROR/39 PENDING, dos quais 16 MISSING_PARSER, 16 POLICY_REVIEW_INCOMPLETE e 7 SOURCE_VALIDATOR_DRIFT; com PMO: 41 PENDING. **Remediação:** resolver diferenças por fonte/política, implementar validadores verdadeiros e integrar PRs de parsers com testes cumulativos.

**FIND-CKO-X09 — FHIR é subconjunto, não validador completo.** `PR #46` lê um subconjunto de `Observation` FHIR R4 sem autenticação, validação formal contra StructureDefinition, nem suporte abrangente a `effectivePeriod`, painéis `85353-1` e extensões; dado pessoal real explicitamente não autorizado. **Remediação:** declarar suporte parcial, teste com instâncias normativas oficiais, controle LGPD e revisão clínica; não alegar conformidade total.

**FIND-CKO-X10 — MedlinePlus: classificação de direitos precisa correção.** Norma NLM diz que *health topic summaries* são de domínio público nos EUA e podem ser reutilizados com atribuição; material de terceiros tem regras distintas. O parser prudencialmente extrai só metadados, mas documentação não deve classificar todos os `full-summary` como texto protegido. **Remediação:** matriz `object_type × rights × operation × jurisdiction`, atribuição NLM, excluir ADAM/ASHP sem licença; manter HOLD para publicação até compliance.

**FIND-CKO-X11 — MeSH release/DTD e cobertura.** NLM disponibiliza produção com versões/DTD anuais (incluindo 2027) e atualizações SCR; `PR #48` não cobre Qualifier/SCR, recebe `production_year` declarado sem conferir release oficial. **Remediação:** verificar DTD e checksum oficial por ano, termos de uso, mudanças/retiros, e terminologia `mesh_validator` real.

**FIND-CKO-X12 — Identidade canônica contraditória.** `docs/DETERMINISTIC_RULES.md` diz que SHA-256 do texto é identidade imutável do átomo, mas R4 deriva ID `NORM-{ano}-{sha256(legacy_id)}`. Uma alteração de texto não altera necessariamente o `legacy_id`; isso conflita com a regra de novo átomo sob mudança de conteúdo. **Remediação:** modelo versionado distinguindo `source_id`, `document_version`, `atom_concept_id`, `atom_revision_id`, `content_sha256`, `evidence_span_sha256` e transições explicitadas; nunca reescrever histórico.

**FIND-CKO-X13 — Controles internos não promovidos confundidos com canon.** `migration/pilot-policies` declara explicitamente `CANDIDATE_NOT_HOMOLOGATED`; `feat/ce-local-agent-assurance` registra agentes `NOT_DEPLOYED`. Não contabilizar as regras/validadores declarados como executores operacionais. **Remediação:** reconciliar objetos por ID, contrato, testes e recibo de Kernel; não colar o pacote inteiro.

**FIND-CKO-X14 — Concorrência de implementações WO/Drive.** 36 branches `cursor/*`, 33 PRs abertas; exemplos usam técnicas diferentes para identidade de política, referência de pasta e recibo humano. Mesclar sequencialmente poderia restaurar import antigo, parser stub ou fluxo sem WO validada. **Remediação:** clusterização por hashes, diffs e contratos de entrada/saída, priorização de implementação com testes negativos, arquivamento somente após validação humana.

**FIND-CKO-X15 — Escopo CE e vocabulários de outras disciplinas.** Naming policy candidata de `staging/wo-kernel-normativos-cli-20261016` inclui emissores CFC/CPC; são metadados genéricos de outra área e não devem introduzir conteúdo de contabilidade no corpus CE. **Remediação:** whitelist por namespace clínico/enfermagem, com exceções tecnicamente justificadas e aprovadas.

### P2 — Manutenção e completude de custódia

**FIND-CKO-X17 — Norma conexa de prontuário eletrônico ausente do mapa M08/M09.** A Resolução COFEN 754/2024 trata das plataformas digitais e registros de enfermagem e revoga a 429/2012, ainda citada no preâmbulo histórico da 736/2024. Isso não invalida automaticamente os artigos da 736/2024, mas a operação atual de registro eletrónico depende de verificar a regra 754 e direitos de acesso/sigilo. **Remediação:** incorporar novo `NORM_SOURCE` explicitamente como candidato, revisar repercussões no claim PE art. 8º e no produto digital; sem fabricar texto normativo ou substituição tácita.

**FIND-CKO-X16 — Histórico de 2026-10 é muito maior que o snapshot atual.** `migration/full-directory` e `cursor/fix-governance-gaps` incluem milhares de arquivos históricos/candidatos. `feat/ce-local-agent-assurance` 139 diferenças; `pmo/recovery-controlled` 107. Um `git merge` indiscriminado não confere bytes, direitos, segredos, duplicatas ou divergências. **Remediação:** inventário por blob, matriz de conflito e quarentena com origem e decisão.

## 5. Plano de integração sem violar as fontes

**Gate 0 — Congelamento e custódia:** pin SHA/branch, comparar lineage e referências, criar relatório de risco de vazamento; nenhuma deleção.

**Gate 1 — Política/admissão:** resolver FIND-X01..X05; implementar CI efetivamente falhante, G6 real, segregação de função, WO com recibo assinado/verificável; artefato `PASS_LOCAL` não autoriza.

**Gate 2 — Normativo:** resolver X06/X07, validar COFEN e RDC artigo por artigo, fonte DOU e alterações; 46 claims exigem decisão independente rastreável. Se não houver fonte verificável: `HOLD_SOURCE`.

**Gate 3 — Técnica/terminologias:** integrador técnico une apenas arquivos aprovados de #46/#47/#48 sobre #40, roda testes cumulativos e verifica regressão. Corrige 7 divergências de validators e 16 policies; implementa WOs #41–#45 sem stubs.

**Gate 4 — Metamodelo:** rodar #49 sobre snapshot de contrato e PMO com crosswalk explicitamente verificado; nenhuma aresta inventada. Acoplar ao dicionário físico/Supabase somente por migração planejada e homologada.

**Gate 5 — Segurança/compliance:** direitos por operação, privacidade/LGPD, SAST, secrets, dependências, branch rules, acessibilidade e trilha independente; sem liberar PHI ou conteúdo editorial protegido.

**Gate 6 — Promoção:** somente mediante autorização institucional/clinicamente qualificada, logs e assinaturas por SHA, sem eliminar histórico candidato e sem bypass de `HOLD_HUMAN`.

### Prioridade operacional imediata\n\n**Acoplamentos formais:** [WO #53](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/53) (G6/CI/reprodutibilidade), [WO #54](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/54) (COFEN 754/2024).\n

1. Corrigir workflow `ci.yml` permissivo e documentar que G6 ainda não é executável.
2. Congelar as decisões sobre as 33 PRs `cursor/*`, sem unificar automaticamente.
3. Retificar documentação de direitos MedlinePlus, sem modificar parser nem liberar conteúdo.
4. Definir modelo único de identificação/versionamento de átomo e plano de proveniência.
5. Corrigir variáveis de política `REQUIRES_HUMAN_REVIEW`/`WO` e referências declaradas com revisão de domínio, não aplicação global cega.

**Disposição:** este relatório é **evidência para auditoria e desenho da correção**, não recibo de Kernel nem aprovação por norma/cliente. Não altera `main`, conteúdo clínico, Supabase, Drive nem website.
