# CE — P3 | Contratos, WOs, executores e agentes determinísticos

**Data de corte:** 2026-10-19. **Status:** `CANDIDATE / READ_ONLY_PLAN / KERNEL_OPERATIONAL_HOLD`. **Branch documental proposta:** `pmo/recovery-controlled-20261019`. **Escopo:** P3 transversal às ondas P1–P5; nenhuma aprovação, execução produtiva, merge ou alteração de política é presumida.

## Evidência recuperada e limites

| Fonte/população | Evidência | Estado correto |
| --- | --- | --- |
| CE04 | Readback de `docs/tasks/CE04_RECON_TASK_REGISTER_20261017.json` na branch `audit/ce04-reconciliation-tasks-20261017`, Git blob `7085bf32d61daabae092fb97fb9ace1088f95918`; `task_count=38`, `completed=0`, `approved=0`, `CANDIDATE_REGISTERED_PENDING_KERNEL_ADMISSION` (corte 17/10) | 38 tarefas; não são 38 WOs e seu status histórico não é status atual sem nova leitura |
| PR #2 | Inventário PMO indica 76 documentos `contracts/work_orders/` com `CKO-TAREFA-1.0.0`, mais `contracts/work_order.schema.json` | Família de WO histórica; *não* validar indiscriminadamente pelo schema agent-only GAP-01; obter SHA fixo do head do PR e manifesto objeto a objeto |
| Auditoria histórica 16/10 | 102 WOs, com 98 PASS, 2 BLOCKED, 2 PREAUTHORIZED relatados no contexto anterior | **Somente contexto conversacional** até localizar artefato e cutoff autoritativos; não somar nem deduzir interseções |
| M20 | `CE_M20_KERNEL_EXECUTORES_AUDIT_CANDIDATE.md`: 8 FINDs; 14 contratos `ACTIVE` mas 14 executores stub; 11 contratos referenciam políticas faltantes (10 IDs distintos); parser YAML de primeiro nível; RBAC incompatível | Falhas conhecidas; não reabrir como novos FINDs sem evidência nova; execução Kernel `HOLD` |
| M21 | `CE_M21_CONTENCAO_KERNEL_E_TRILHO_CONTEUDO_CANDIDATE.md`: `cmdRun`/`cmdAdmit` abortam localmente com exit 78; 3 testes estáticos PASS; runtime Kernel E2E não demonstrado | Contenção **local candidata**, não prova de bloqueio no runtime autoritativo remoto |
| PMO | Plano de waves e registro mestre `PMO_TRUSTED=false` | Custódia documental explicitamente autorizada; promoção, atomização e mutações do projeto seguem bloqueadas até admissão separada |

## Modelo de agentes especializados

Agentes interpretativos podem produzir *propostas*; o fluxo decisório tem de ser determinístico com entrada imutável, algoritmo versionado, regras de empate, saída validada, hash e auditoria externa. Separar identidades e permissões:

| ID proposto | Frente | Entrada | Saída e teste obrigatório | Autoridade |
| --- | --- | --- | --- | --- |
| P3-CATALOGER | Inventário de contratos e fontes | Snapshot Git por SHA, corpus local com hash | `contracts_index.jsonl` com chave composta, contagens por família e proveniência; teste duplicados e arquivos ausentes | READ_ONLY |
| P3-MAPPER | Conciliação FIND→CAPA→tarefa→WO→política→validador | Índice congelado | `crosswalk.jsonl` com relações tipadas (`SAME_AS_CANDIDATE`, `SUPERSEDES`, `DERIVED_FROM`, `RECURRENCE`) e confiança; nunca fazer merge implícito | READ_ONLY |
| P3-SCHEMA-AUDITOR | Elegibilidade de contrato e política | Família/schema/versão explícitos | relatório por `family+id+version+source_sha`; teste positivo e negativo do validador correto | READ_ONLY |
| P3-EXECUTOR-BUILDER | Preparação técnica de executores | WO proposta e contrato admitido (ou fixture sintético) | código candidato + testes em ambiente isolado; nunca converter stub em `PASS` | LOCAL_CANDIDATE |
| P3-GUARDIAN | Bloqueio fail-closed | Plano de mutação e referências | `ALLOW_DOC_ONLY`, `DENY`, `NEEDS_KERNEL_PROOF` + motivo; testes adversariais | NEGAR por padrão; sem bypass próprio |
| P3-INDEPENDENT-AUDITOR | Contestação de evidências | Artefatos de todos os anteriores | parecer separado; executar novamente testes e hashes; impedir executor autoaprovar | READ_ONLY |

**Escritor único:** somente controlador PMO já designado integra resultados e o publicador versiona na branch documental; agentes de análise não fazem commits concorrentes. Nenhuma dessas funções pode atribuir a si mesma aprovação humana ou fabricar recibo Kernel.

## Contrato mínimo por unidade rastreável

Chave canônica proposta: `(artifact_family, native_namespace, native_id, semantic_version, origin_git_sha_or_file_sha)`. Campos mínimos: `source_id`, `source_path`, `source_url_or_repo`, `cutoff`, `content_sha256`, `declared_schema_id`, `schema_version`, `jurisdiction`, `license_or_rights_status`, `object_type`, `state`, `reason_code`, `parent_refs[]`, `policy_refs[]`, `validator_ref`, `validator_version`, `task_ref`, `wo_ref`, `kernel_admission_receipt_ref`, `executor_ref`, `independent_audit_ref`, `git_commit_sha`, `readback_sha`, `change_log` e `review_required`. `UNKNOWN`/`NOT_APPLICABLE` são estados tipados e não strings vazias presumidas como PASS.

Conciliação com precedência: comparar *mesma família + ID + versão + SHA* para igualdade; diferença de hash no mesmo ID/versão = `CONFLICT`; nomes aproximados e relações semânticas = `CANDIDATE_LINK` até evidência; WOs de famílias distintas não compartilham validador só porque contêm a palavra `WO`. Números 38, 76 e 102 devem permanecer em três denominadores separados até matrizes de interseção comprovadas. O reaparecimento da leitura parcial MeSH deve ficar ligado a `M42-F01` como `RECURRENCE_UNDER_INVESTIGATION` até resolução, sem emissão automática de novo FIND.

## Microlotes e critérios objetivos de saída

| Micro | Tarefa de execução paralelizável | Critério de saída (`PASS` somente com evidência) | Dependência |
| --- | --- | --- | --- |
| P3-A | Fixar HEAD, path, blob e direitos de leitura de CE04, PR #2, Kernel/M20/M21 e fontes das 102 WOs | manifesto assinado por SHA; `missing_sources` explícito; PR #2 verificado; 102 ficam `EVIDENCE_MISSING` até fonte recuperada | P1 Git snapshot |
| P3-B | Normalizar schemas por família e índice de contratos/WOs/FIND/tarefas | JSON Schema estrito, validação por família, índices únicos, contagens reconferidas por fonte | P3-A |
| P3-C | Crosswalk com duplicidades, supersessões e recorrências | nenhum merge destrutivo; cada relação tem `evidence_refs`, motivo e revisão humana quando ambígua | P3-B; P2 conflitos |
| P3-D | Política-as-code + guard de publicação documental e do Kernel operacional | testes negativos para WO não admitida, executor stub, esquema incompatível, falso PASS, policy missing, alteração main e autoaprovação | P3-B/C |
| P3-E | Reparo candidato da CLI/schema/RBAC/dispatcher e contrato de agente real em ambiente isolado | parser YAML seguro, validação completa, identidade/papel/recurso, receipts verificáveis, idempotência, lock/fencing, custo/FIND reais e testes integração; não habilitar produção | WO admitida para código; ambiente de testes |
| P3-F | Auditoria independente e fechamento do P3 | crosswalk completo ou exceções individualizadas; testes regressivos e negativos; readback GitHub; parecer de segregação; nenhum status operacional fictício | P3-A–E |

## Testes adversariais inegociáveis

1. Mesmo `id/version` com hashes diferentes rejeita igualdade e mantém conflito.
2. `CKO-TAREFA-1.0.0` não é avaliado via schema agent-only GAP-01 sem roteamento explícito.
3. WO inexistente, `PREAUTHORIZED` histórico sem receipt ou `PENDING_KERNEL_ADMISSION` bloqueia executor produtivo.
4. Agente stub e receipt sintético `SUCCESS` falham fechado; `exit 78` local jamais equivale a admissão.
5. Política ausente, hash placeholder, YAML com chaves aninhadas descartadas ou RBAC incompatível bloqueiam.
6. O mesmo agente não publica e audita seu próprio resultado.
7. Testes não permitem substituição de manifesto devido a cutoff/HEAD móvel, nem gravação fora da branch documental autorizada.
8. Todas as 102 WOs históricas continuam `SOURCE_UNVERIFIED` até prova documental, mesmo que haja similaridade textual.
9. Duplicata de FIND recorrente é ligada à ocorrência original, não contabilizada duas vezes.
10. Secrets/licenças/dados clínicos sensíveis acionam triagem antes de qualquer publicação Git.

## Gates e não retrabalho

**Trilho autorizado documental:** READ_ONLY → precondition SHA → normalização determinística → guard → auditor independente → publicação candidato PMO (escritor único) → readback exato → recibo externo. Permanece `IN_PROGRESS`, sem homologação automática.

**Trilho produtivo obrigatório e distinto:** FIND formal → política aplicável ou proposta formal → schema/validador executável → tarefa versionada → WO formal → **admissão real do Kernel comprovada por receipt** → executor real em branch isolada → testes positivos, negativos, concorrência/segurança → auditoria independente → promoção sob autorização. Até lá: `HOLD` para mutações, atomização, execução e `main`.

O anti-retrabalho depende de `work_signature=SHA256(population_snapshot + policy_version + validator_version + task_id + intended_outputs)`, índice de resultados anteriores com status de auditoria, idempotency key e ledger de FIND/CAPA. Antes de iniciar, comparar `work_signature` e evidências: se resultado anterior está válido, ligar ao registro em vez de rerodar; se mudou fonte/versão, marcar `REVALIDATION_REQUIRED`. Não atribuir percentuais com denominadores misturados.

## Entrega a P1/P2/P4/P5

- **P1** fornece hashes, origem e snapshots que congelam insumos; P3 não inventaria o mesmo arquivo novamente.
- **P2** fornece decisões sobre conflitos, branches e PRs; P3 bloqueia contratos sem versão/autoridade clara.
- **P4** consome schemas e gates para aquisição, ingestão, atomização e evidência clínica; não inicia sobre stubs nem sem direitos comprovados.
- **P5** audita independência, provas de Kernel, consistência e elegibilidade de fechamento; PMO e projeto seguem com gates de homologação separados.

**Status desta proposta:** plano local de especialista, sem publicação remota nem execução de correção. A implementação requer integração controlada e verificações adicionais, não se pode alegar agentes permanentes ou proteção CI ativa com base apenas neste documento.
