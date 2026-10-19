# CE — Readback cruzado P2/P3/P4 e bloqueador de retrabalho

**Corte:** 2026-10-19 · **Status:** `READ_ONLY_DOCUMENTARY_CANDIDATE` · **Branch:** `pmo/recovery-controlled-20261019`. Registro de inspeções independentes de função (não parecer externo segregado, não PASS de release). **Sem reexecução** de extração, atomização, inventário fechado ou implantação de agentes.

## 1. Preflight do PMO e anti-retrabalho

- Mestre Git blob `234400ddebe26c64141a706385a1cd098c818744`, fila blob `deb2f7d8079d0536b4846725e6bc82be0803f115`.
- 12 IDs de tarefa distintos, ordenados `P1-CD-01, P1-D-01, P2-00, P2-01, P3-A, P3-B, P4-A, P4-D, P4-F, P5-01, P5-02, POST-001`; nenhum ID de fonte referenciado no nível da fila ficou ausente do conjunto de IDs de fonte do mestre. **Esta é checagem de IDs**, não integridade de bytes.
- 23 agentes únicos no registry blob `6156c083b85c285f9acb438ea385344e71201a07` e catálogo blob `d84ea260b6da8523e92f86230fff3ee37f7e9e03`; todos expressamente `NOT_DEPLOYED`.
- **Lacuna de integração:** mestre ainda não referencia o novo registro dos 23 agentes. Tratar como tarefa documental candidata de vinculação controlada, não sobrescrever mestre sem precondition CAS e publicador único; antes de criar atividade, consultar FIND/tarefa equivalente e aplicar `INV-QUEUE-POST-CLOSURE-001` se for descoberta pós-fechamento.
- `PMO_TRUSTED=false`, `PROJECT_EXECUTION_ALLOWED=false`, oito gates HOLD. `AG-NR-01` possui ledger parcial (P1-A/P1-B/P1-C-C), logo este preflight **não substitui enforcement remoto**.

## 2. P2 — árvore, branches e preservação

- Listagem GitHub observou 15 branches (inclui PMO), coerente com manifesto `CE_PMO_GIT_BRANCH_TREES_P1CB_20261019_CANDIDATE.json` blob `98995b9391d4b51b8dad75a68ebac9d6283ba660`, com 15 árvores pinadas e 58.710 ocorrências. A listagem atual de nomes não equivale a reconfirmar 15 HEAD/tree SHAs.
- Comparação `main` vs `integration/canonical-main-20261017`: `diverged`, 8 commits adiante/6 atrás, merge base `39d4283ca7689b1028eb11d35f453908f922de9d` no momento da consulta; **22 exclusões propostas** (21 `contracts/fonts` e `test.txt`). Não excluir, fazer merge ou atribuir equivalência.
- PRs #2/#3/#6 seguem draft e #4 aparece não-draft com base em `cursor/fix-governance-gaps-ec54`; diferenças de bases/HEADs exigem corte e prova por path/blob antes de decisão. PR não-draft não significa autorizado.
- `P2-00`: evidência parcial, requer HEAD/base/tree de cada um com cutoff fixo. `P2-01`: ainda bloqueada pela dependência e ausência de matriz 22/22 old/new blobs. Manter FIND de preservação existente, sem duplicar.

## 3. P3 — agentes, políticas, contratos e Kernel

- Readback das 38 tarefas CE04: `docs/tasks/CE04_RECON_TASK_REGISTER_20261017.json` na branch `audit/ce04-reconciliation-tasks-20261017`, blob `7085bf32d61daabae092fb97fb9ace1088f95918`; zero CLOSED/aprovadas no corte 17/10.
- WO `contracts/wo/WO-CE04-RECON-20261017.candidate.json`, blob `19a37c6563ac0e54026c3dd49770438457f03f4c`, `DRAFT_NOT_ADMITTED`, sem receipt Kernel.
- Crosswalk PMO P3 blob `69d9422dbf585d66b741689f8cdce35c5bccc1bd`: 164 WO JSON em PR #2, 161 PREAUTHORIZED e três sem estado equivalente, zero match direto de ID com 38 tarefas. População histórica de 102 WOs continua distinta; similaridade numérica/prefixo não prova interseção.
- M20: 14 executores stub, 11 refs a políticas ausentes (10 IDs) e oito FINDs, conforme relatórios documentais históricos; M21: `exit 78` local, três testes estáticos, **não** prova Kernel remoto.
- `P3-A`: vincular identidades/versões preservando 102 `SOURCE_UNVERIFIED`; `P3-B`: testar schemas, RBAC, policy refs e stubs em isolamento quando inputs verificáveis estiverem acessíveis. Não iniciar runtime produtivo e não repetir censo fechado.
- Registro dos 23 agentes é especificação de papéis, não implementação real/implantação. Política, validador, tarefa, WO e admissão continuam obrigatórios para código e runtime.

## 4. P4 — fontes, conteúdo, direitos e semântica

- Crosswalk `CE_PMO_P4_CROSSWALK_FONTES_61_ARQUIVOS_65_20261019_CANDIDATE.json` (blob reportado em readback `45565772…`): 65 descritores, 61 registros de fonte, 15 domínios e 49 URLs. **61/61** fontes com `HOLD_RIGHTS`; zero parecer jurídico/clínico comprovado nesta frente.
- Dos 65 arquivos, 12 possuem fonte candidata única e 53 associação multifonte cuja atribuição por registro permanece HOLD. Não inferir que candidato único valida sua linhagem.
- `P4-A`: censo já feito; não repetir. `P4-D`: cláusulas, licenças e versões oficiais ainda requerem evidência de aplicabilidade. `P4-F`: 285 findings CID-11 M43 são ressalvas, não 285 erros confirmados; sete grandes com 333.906 registros declarados, sem reatomização autorizada; cinco históricos M24 HOLD administrativo.
- Antes de novos FINDs, confrontar `M11-F01..07`, `M26-F02/F03`, `M43-F01/F03/F04` e a recorrência MeSH vinculada a `M42-F01`.

## 5. Matriz de decisão deste readback

| Frente | Reutilizar sem reexecutar | Lacuna aberta | Decisão |
|---|---|---|---|
| P1 | Classes A=11/B=610/C=674; CRC delimitado | Índice privado por membro/versão/custódia | HOLD P1-CD-01 |
| P2 | 15 árvores históricas e 22 exclusões propostas | HEADs atuais e 22 old/new SHA por path | READ_ONLY CONTINUE |
| P3 | 38 CE04, 164 WO PR2, catálogo 23 agentes | 102 históricos, contratos e runtime Kernel | READ_ONLY CONTINUE; PRODUCTIVE HOLD |
| P4 | 61 fontes/49 URLs e 285 ressalvas | direitos, causalidade e semântica por registro | READ_ONLY CONTINUE; ATOMIZATION HOLD |
| P5 | fila e fontes-ID sem colisões neste exame | auditoria externa, hashes de cada objeto, negativos e E2E | NOT_CLOSED |

## 6. Handoff e limites

- Não foram modificadas fontes, branches de integração, Supabase ou `main`. Nenhuma tarefa foi marcada DONE; nenhuma aprovação foi criada.
- Novo achado precisa verificar identidade/recorrência antes de FIND; se de fato novo e posterior a fechamento, **investigação → correção → tarefa acrescentada ao final da fila**, depois de POST-001 e antes da homologação. Não inserir no meio e não bloquear trabalho independente.
- Publicação deste documento é somente preservação documental excepcional na branch PMO. **Não** altera o mestre por si só e exige readback após commit. P1-CD-01 segue primeira prioridade formal; P2/P3/P4 foram análises independentes sem consumir a fila.
