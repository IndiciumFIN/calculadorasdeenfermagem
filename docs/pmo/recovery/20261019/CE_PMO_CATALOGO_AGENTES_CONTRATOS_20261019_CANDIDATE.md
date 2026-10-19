# CE — Catálogo canônico candidato de agentes e handoff operacional

**Corte:** 2026-10-19 (America/Sao_Paulo) · **Estado:** `DOCUMENTARY_CANDIDATE_NOT_DEPLOYED` · **Branch:** `pmo/recovery-controlled-20261019` · **Escopo:** somente preservação e coordenação documental do PMO. Este catálogo **não cria processos persistentes, código executável, credenciais, políticas aprovadas ou admissão do Kernel**.

## 1. Fonte, precedência e identidade

- Projeto-mãe: Calculadoras de Enfermagem, GitHub `IndiciumFIN/calculadorasdeenfermagem`. GitHub é autoridade documental final **somente para artefatos publicados e verificados**, Supabase Calculadoras-Smart é auxiliar READ_ONLY e Drive não deve ser reaberto.
- Referências já existentes: `CE_PMO_REGISTRO_MESTRE_20261019_v0.1.0_CANDIDATE.json`; `CE_PMO_FILA_EXECUCAO_P1_P5_20261019_CANDIDATE.json`; `CE_PMO_PLANO_INTEGRADO_P1_P5_AGENTES_20261019_CANDIDATE.md`; `CE_PMO_PLANO_P3_AGENTES_20261019_CANDIDATE.md`; `CE_PMO_CONTRATO_AGENTE_ANTI_RETRABALHO_20261019_CANDIDATE.md`; `CE_PMO_INVARIANTE_FILA_POS_FECHAMENTO_20261019_CANDIDATE.md` (todos neste diretório).
- Regra de versão: contratos anteriores mantidos; este documento constitui índice de responsabilidades, **não sobrescreve** implementações, estados ou evidências anteriores. Divergências geram relação de versão ou FIND, jamais escolha silenciosa.
- O executor humano/assistente em uma conversa e o agente de software implantado são entidades distintas. Papéis aqui enumerados **não são processos vivos**. Um runtime só é `DEPLOYED` com código, testes e readback de implantação comprovados.
- O plano de fechamento vigente conserva 12 tarefas na ordem `P1-CD-01, P1-D-01, P2-00, P2-01, P3-A, P3-B, P4-A, P4-D, P4-F, P5-01, P5-02, POST-001`. Descobertas posteriores vão à cauda, antes da homologação.

## 2. Orquestração e segregação de funções

| ID | Tipo | Responsabilidade exclusiva | Saída verificável | Permissão | Estado comprovável |
|---|---|---|---|---|---|
| PMO-CONTROLLER | ORCHESTRATOR | Atualizar registro mestre com precondição blob SHA, histórico append-only e status | diff versionado e recibo externo | Escritor único do registro mestre | CONTRATO DOCUMENTADO; serviço persistente NÃO VERIFICADO |
| PMO-PUBLISHER | SPECIALIST | Publicar documentos não sensíveis na branch PMO autorizada, serialmente | commit, blob SHA, readback exato | Escritor único dos demais documentos PMO | CONTRATO DOCUMENTADO; serviço persistente NÃO VERIFICADO |
| PMO-RECONCILER | VALIDATION | Recalcular denominadores, identidade, hashes e `REQUIRED×PRESENT×VALIDATED×PASS` | parecer independente sobre inventário | READ_ONLY | CONTRATO DOCUMENTADO |
| PMO-GUARDIAN | GUARDIAN | Validar política, escopo, secretos, conflitos, WO e riscos; negar por padrão | `DENY / HOLD / PASS_PREFLIGHT_ONLY` e testes negativos | READ_ONLY / veto; sem bypass | GUARDA LOCAL CANDIDATO; enforcement remoto NÃO COMPROVADO |
| AG-NR-01 | GUARDIAN/VALIDATION | Detectar retrabalho por intenção semântica e ledger, sem depender de task ID | `BLOCK/HOLD/ALLOW_PREFLIGHT_ONLY` + evidência | READ_ONLY | IMPLEMENTAÇÃO LOCAL CANDIDATA, não implantada |

**Segregação mandatória:** reconciliação e auditoria não certificam suas próprias saídas; Publisher não emite aceite; Controller não fabrica admissão. Nenhum papel equivale a aprovação do titular ou de profissional clínico/jurídico.

## 3. Agentes especializados por onda

| ID estável | Wave / tipo | Entrada congelada | Produto e critério de saída | Estado inicial |
|---|---|---|---|---|
| P1-HASH-INDEXER | P1 / SPECIALIST | ZIP/local/Git e cutoff | manifesto por objeto com SHA256, SHA Git se aplicável, caminho privado e classificação de custódia | SPEC_ONLY |
| P1-ZIP-INTEGRITY | P1 / VALIDATION | containers ZIP | CRC e integridade em microlotes, preservando nested ZIP | EVIDÊNCIA HISTÓRICA DELIMITADA; não rerodar sem FIND |
| P1-GIT-BLOB-MAPPER | P1 / SPECIALIST | 15 árvores pinadas e 1.295 payloads distintos | `ZIP-member ↔ blob/path/version` com classes e HOLD por membro | P1-CD-01 PENDENTE |
| P1-SNAPSHOT-CUSTODIAN | P1 / GUARDIAN | cutoffs 768/771/823 | trilha de deltas sem reconstruir nomes/hashes ausentes | P1-D-01/POST-001 HOLD ou fila |
| P2-GIT-CENSUS | P2 / SPECIALIST | refs Git e PRs | HEAD/base/tree SHAs por cutoff; distinguir 14 históricos de 15 atuais | P2-00 PARCIAL |
| P2-DELETE-GUARD | P2 / GUARDIAN | 22 exclusões propostas e PRs 2/3/4/6 | matriz de quarentena por path, antigo/novo SHA, decisão não destrutiva | P2-01 PENDENTE |
| P2-PR-ANALYST | P2 / SPECIALIST | branches, commits e patches | ancestralidade, sobreposições, divergências e implicações de retenção | SPEC_ONLY |
| P3-CONTRACT-REGISTRAR | P3 / SPECIALIST | 38 tarefas CE04, 164 WO JSON PR2, 102 WO históricas | crosswalk por família+schema+versão+SHA, sem equiparação implícita | P3-A PARCIAL |
| P3-SCHEMA-AUDITOR | P3 / VALIDATION | famílias WO/policy/task, validadores | testes positivos/negativos da família correta; classificação de stubs | P3-B PENDENTE |
| P3-EXECUTOR-BUILDER | P3 / SPECIALIST | WO admitida ou fixture sintética | código candidato isolado e testes, nunca promover stub a runtime | HOLD WO/KERNEL |
| P3-INDEPENDENT-AUDITOR | P3 / AUDITOR | resultados P3 e evidências externas | contraprova e parecer segregado | NOT_ASSIGNED_RUNTIME |
| P4-SOURCE-REGISTRAR | P4 / SPECIALIST | 61 objetos/49 URLs, versão e jurisdição | fonte, licença e direitos por CID, `HOLD` se indeterminado | CENSO CANDIDATO |
| P4-NORM-CROSSWALK | P4 / SPECIALIST | versões oficiais disponíveis ISO/COSO e aplicabilidade | cláusula→requisito→controle→evidência→responsável; não inventar texto licenciado | P4-D PENDENTE |
| P4-SEMANTIC-QA | P4 / VALIDATION | 285 ressalvas, 65 CE04, 7 grandes, M24 | claim/source/hold e referência ao FIND original | P4-F DEPENDENTE |
| P4-INGESTOR-LINEAGE | P4 / VALIDATION | segmentos/átomos de fontes autorizadas | hash, spans, UTF-8, subunidade, vínculo e relatório de perdas | M08-B HISTÓRICO A CONFRONTAR |
| P4-ATOMIZER-TRIAGE | P4 / SPECIALIST | candidatos com origem | classificação lexical conservadora, abstenção e revisões | M08-A HISTÓRICO A CONFRONTAR |
| P5-EVIDENCE-AUDITOR | P5 / AUDITOR | recibos, testes, inventários, fila | execução independente de gates e testes adversariais | P5-01 PENDENTE |
| P5-RELEASE-GUARD | P5 / GUARDIAN | dossiê F0–F11, direitos, clínica, CI/E2E | parecer PASS/FAIL/HOLD com riscos e autoridade final | P5-02 HOLD |

Os papéis são **contratos planejados**, não agentes implantados. Evitar duplicar designações legadas com os mesmos propósitos; antes de ativar, registrar alias para IDs dos planos P1–P5 e provar a implementação.

## 4. Contrato comum mínimo por agente

Todo agente requer:
`agent_id`, `agent_type`, `version`, `purpose`, `task_ids[]`, `owner_role`, `accountable_human`, `input_schema_ref`, `output_schema_ref`, `source_snapshot_sha`, `policy_refs[]`, `validator_refs[]`, `wo_ref`, `kernel_admission_receipt_ref`, `tools_allowlist[]`, `read_scope[]`, `write_scope[]`, `secrets_classification`, `data_rights`, `execution_mode`, `timeouts_and_budget`, `idempotency_key`, `concurrency_lock`, `prompt_or_rule_version`, `negative_tests_ref`, `audit_ref`, `deployment_ref`, `status`, `last_readback_sha`, `next_action`.

Campos desconhecidos devem ser `UNKNOWN`/`NOT_VERIFIED`, nunca preenchidos por presunção. Para agentes de IA, preservar versão exata de modelo/prompt, ferramentas e entradas/saídas auditáveis; algoritmo determinístico sempre que houver decisão de gate. O agente não pode acessar Drive neste ciclo nem gravar no Supabase.

## 5. Máquina de estados, admissão e execução

`SPEC_ONLY → CONTRACT_VALIDATED → LOCAL_CANDIDATE_TESTED → WO_KERNEL_ADMITTED → ISOLATED_EXECUTED → INDEPENDENTLY_AUDITED → DEPLOYED_VERIFIED`.

Cada seta exige evidência própria. `PRE_APPROVED` de criação isolada não é `APPROVED`; `exit 78` local M21 e testes 13/13 não provam autoridade do Kernel. Todos os executores novos ou reparos de código respeitam **FIND → política → validador → tarefa → WO → admissão Kernel por SHA → execução isolada → testes → auditoria → promoção autorizada**. Sem receipt válido: `DENY_PRODUCTIVE_EXECUTION`. Escrita documental excepcional só na branch PMO, por Publisher, com precondição, SHA e readback, sem promover `main`.

## 6. Evidência histórica recuperada pelo titular nesta conversa

Estas afirmações são **CONVERSATION_SUPPLIED_PENDING_FILE_READBACK**, não validação independente de artefatos (paths originais de outra sessão não são acessíveis automaticamente):

- **M08-B ingestor/linhagem:** MAN-MDM-002 DOCX 2.651 segmentos/2.651 átomos, 2 subunidades, 44 candidatos; SOP-PCNAC-001 Markdown dentro de ZIP 117/117, 31 subunidades, 43 candidatos; 0 falhas de integridade reportadas e 13/13 testes. **Limite:** normalização e omissão de unidades vazias impedem afirmar integridade textual integral.
- **M08-A atomizador:** 43 candidatos SOP (5 obrigações lexicais, 4 referências, 34 HOLD); 44 MAN (28 obrigações lexicais, 0 referências, 16 HOLD), 3/3 testes relatados. Não há obrigação confirmada nem aprovação normativa.
- **M17 corpus:** referência a 18.955 blobs de snapshot e cinco FINDs; não equivale ao universo final. Confrontar com 15 árvores completas atuais e suas populações distintas.
- **Branches/Kernel antigos:** 14 branches em corte anterior; 22 remoções candidatas; main/ruleset com proteção não comprovada/desabilitada no corte. Hoje o PMO registra 15 árvores e ruleset 25297030 `DISABLED`.
- **PMO:** 145 arquivos era seleção parcial; 768 baseline congelada, 771 agregado intermediário e 823 snapshot privado são cutoffs distintos. Nada autoriza deduzir os 55 nomes/deltas.
- **CE04:** 65 arquivos/15 domínios; 53 estruturais, sete grandes em HOLD, cinco M24 administrativos sem identidade técnica comprovada. Os nomes mencionados no histórico não bastam para conferir os cinco objetos originais.
- **P3:** 14 executores stub M20; M21 contém contenção local `exit78`; 164 WOs JSON no PR2 substituem o censo preliminar de 76, mantendo as 102 históricas separadas.

Documentos-fonte a localizar/verificar antes de converter em PASS: `CE_M08B_AUDITORIA_LINHAGEM_PONTA_A_PONTA_v0.1.0_CANDIDATE.md`, `ce_m08_lineage_validator_v01.py`, `test_ce_m08_lineage_validator_v01.py`, `CE_M08A_TRIAGEM_TIPO_DOCUMENTAL_v0.1.0_CANDIDATE.md`, `CE_M17_CORPUS_FULL_BRANCH_RECON_CANDIDATE.md`, `CE_BRANCH_RECON_READONLY_20261019_CANDIDATE.md`. Os caminhos transitórios fornecidos pertenciam a outra sessão, não constituem prova de existência neste workspace.

## 7. Gates, FINDs e handoff

1. Não reabrir `P1-B-ZIP-CRC`, `M24-HISTORICAL-LABEL` nem candidatos de fechamento sem FIND comprovado. O marco M24 é `CLOSED_ADMINISTRATIVE`, sem concluir cinco fontes.
2. Registrar ocorrência MeSH como recorrência `M42-F01`, não FIND independente sem prova de nova causa.
3. Próxima tarefa formal `P1-CD-01`: índice individual 1.295 ZIP × blobs/path/version, mantendo classes A=11, B=610, C=674 e 1.284 não provados perdidos. Sem manifesto privado item a item, estado `HOLD_EVIDENCE`, não PASS.
4. P2/P3/P4/P5 podem investigar independentemente em READ_ONLY, sem alterar ordem da fila. Descobertas pós-fechamento seguem `INV-QUEUE-POST-CLOSURE-001` e entram na cauda depois de POST-001.
5. Critérios mínimos de instalação futura: scripts/containers versionados, fixtures adversariais, schemas, manifesto de dependências, secrets sem exposição, RBAC por recurso, idempotência/fencing, logs auditáveis, admission receipt Kernel, CI efetiva, verificação segregada e rollback.
6. **Status global:** `PMO_TRUSTED=false`; `PROJECT_EXECUTION_ALLOWED=false`; oito gates em HOLD; aprovação geral pelo Leivis somente após dossiê final. Nenhum agente deste catálogo pode marcar seu próprio contrato ou tarefa como homologado.
