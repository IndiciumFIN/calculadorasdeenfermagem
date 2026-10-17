# HANDOFF OPERACIONAL — Calculadoras de Enfermagem — GitHub / Supabase / CE-00–CE-06

**Corte documental:** 2026-10-17 · **Tipo:** handoff de continuidade, inventário e plano controlado · **Estado:** `HANDOFF_CANDIDATE_NOT_HOMOLOGATED`  
**Repositório:** [IndiciumFIN/calculadorasdeenfermagem](https://github.com/IndiciumFIN/calculadorasdeenfermagem) · **Fonte da verdade FINAL:** GitHub  
**Branch de controle da reconciliação:** `audit/ce04-reconciliation-tasks-20261017` · **WO:** `WO-CE04-RECON-20261017` — `DRAFT_NOT_ADMITTED`.  
**ALERTA AO PRÓXIMO ASSISTENTE:** **NÃO SOLICITAR ACESSO AO GOOGLE DRIVE NOVAMENTE. NÃO CHAMAR O CONECTOR DRIVE.** Trabalhar com o que já está no GitHub e com consultas autorizadas de leitura ao Supabase. Não esconder itens não verificáveis. Não perguntar novamente ao usuário o que já foi decidido.

> Este handoff não comprova homologação, execução produtiva, auditoria independente, admissão da WO nem finalização de FINDs. É documentação candidata persistida em GitHub, verificada por readback. Não assumir que todos os acervos históricos foram migrados.

## 1. Decisões consolidadas e não negociáveis

1. **GitHub é a única autoridade documental final:** políticas, WOs, tarefas, contratos, fontes, decisões versionadas, manifestos, código, evidências e relatórios devem ter caminhos e SHA Git. Um arquivo apenas no chat/ZIP/Supabase não é entrega documental.
2. **Supabase Calculadoras-Smart é apoio**, nunca fonte documental final: banco transacional para estados operacionais, filas, outbox, locks/fencing, idempotência, execução e registros de suporte; é também fonte auxiliar a confrontar com GitHub. Divergências não reescrevem Git automaticamente. Neste ciclo operar **READ_ONLY**.
3. **Drive: NÃO solicitar acesso e NÃO tentar nova conexão.** Duas raízes históricas estão registradas em `config/drive_inventory_roots_20261016.json` (CE_MASTER e CE_SITE); usar somente inventários/snapshots já preservados em GitHub, e dados de proveniência anteriores. Ausência de prova = `UNVERIFIABLE`/`HOLD_SOURCE`, jamais `PASS`.
4. **Kernel não pensante:** verifica políticas e validadores previamente definidos; controla identificadores/transições/admissão autorizadas de WO e FIND conforme contratos existentes. **Não fabrica evidência de teste**. A evidência nasce de aquisição, execução, CI, verificação de hash e auditoria independente, e é vinculada por referência verificável.
5. **Para criação de algo inexistente:** WO versionada no GitHub → validação dos requisitos mínimos de entrada → Kernel reserva ID determinística/transacionalmente e atribui `PRE_APPROVED` com direitos estritos de construção em isolamento. Não exigir o objeto acabado para permitir criá-lo. `PRE_APPROVED` ≠ `APPROVED`.
6. **Correção ou nova funcionalidade:** identificar política aplicável (ou candidate controlada), validador, tarefa, WO, admissão do Kernel vinculada ao **Git blob SHA exato**, execução isolada, testes positivos/negativos/regressão, evidência independente, auditoria, validação/encerramento de FIND pelo Kernel e promoção autorizada.
7. **FIND:** preservar origem original do erro (caminho, arquivo/linha, hash e versão, input, esperado/observado, política e validador, exit code e evidência bruta). O Kernel abre/fecha com base em regra e evidência verificável; IDs legados que foram abertos manualmente são *candidatos históricos*, não FINDs emitidos pelo Kernel. Recuperar padrão canônico, nunca inventar série.
8. **Conclusão da tarefa:** exige artefato Git persistido **e readback pós-escrita idêntico**, testes reais/resultados/exit codes, evidências hash e auditoria/revisão conforme política, FINDs pertinentes validados; só então o Kernel poderá registrar a transição. Nenhuma tarefa deve ser declarada `CLOSED` por declaração textual.
9. **Sem destruição/promoção presumida:** não apagar Drive, Supabase, branches, snapshots, ZIPs ou fontes; não deduplicar destrutivamente; não mergear na `main` sem gates.
10. **Registro de status honesto:** distinguir `PLANNED`, `PERSISTED`, `VALIDATED`, `TESTED`, `AUDITED`, `KERNEL_ADMITTED`, `HOMOLOGATED`, `PROMOTED`.

## 2. Fontes GitHub verificadas e branches

Branches listadas pelo GitHub neste corte (14):
`main`, `IndiciumFIN-patch-1`, `cursor/drive-sa-key-refactor`, `cursor/fix-governance-gaps-ec54`, `cursor/wf-gdrive-sakey`, `cursor/wf-v3`, `fix/ce05-kernel-ci-security-20261017`, `integration/canonical-main-20261017`, `migration/candidate-f08-20261017`, `migration/ce01-historical-evidence-b01-20261017`, `migration/full-directory-20261017`, `migration/pilot-policies-20261017`, `staging/wo-kernel-normativos-cli-20261016`, `audit/ce04-reconciliation-tasks-20261017`.

| Branch / objeto | Finalidade | Evidência / estado |
|---|---|---|
| `main` | Autoridade operacional do repositório | Git root tree `e0f62491b104f4a97c6025a6393cabc2e7ada30e`; 176 blobs na leitura |
| `migration/full-directory-20261017` | Preservação histórica integral de **5 árvores Git** | Tree `bad54d1d9b6d281a0a2bb8077895e2ad45571b68`; 19.119 blobs totais; 18.955 dentro de `migration/source_snapshots/` |
| `migration/candidate-f08-20261017` | Candidata sobre snapshots; manifesto | `migration/MANIFEST.json`, `migration/PATH_AND_CONFLICT_AUDIT.json`; **WO não admitida pelo Kernel** |
| `cursor/drive-sa-key-refactor` | Acervo de origem Git historicamente migrado | Root tree `fd5818f42c6a6f716996d8c9418ba87a079d0c59`; 9.366 blobs |
| `cursor/fix-governance-gaps-ec54` | Segundo snapshot volumoso | Root tree `1fe3a5ded9e543dcbcc6ba833afbd1931a1b76e1`; 9.363 blobs |
| `cursor/wf-gdrive-sakey` | Snapshot de workflows | Tree `16548d1bc7e08033d5ea21f5742ce0cfe6b4bac2`; 78 blobs |
| `cursor/wf-v3` | Snapshot de workflows | Tree `2c74e968365835b2154a3a2e9abdaff165272040`; 69 blobs |
| `staging/wo-kernel-normativos-cli-20261016` | Snapshot legado do Kernel/CLI | Tree `9ec730337f7069825e76a76f7a0ff90275e3d8eb`; 79 blobs |
| `migration/ce01-historical-evidence-b01-20261017` | Microlote CE-01, 5 JSON de evidência + relatório | Tree `4206865dc5f07f3ef4b36f04c2572b7224f713c1`; materialização não prova admissão do Kernel |
| `fix/ce05-kernel-ci-security-20261017` | Correções Kernel/CI candidatas | WO G0 e 17 rótulos FIND legados; preservar sem promoção |
| `integration/canonical-main-20261017` | Integração candidata histórica | Tree `c704c3cf9241cde7697acb860e598bd01bd58cf5`; não presumir versão canônica |
| `audit/ce04-reconciliation-tasks-20261017` | **Registro persistido da reconciliação CE-04** | WO candidata, 38 tarefas registradas e readback do GitHub; nenhum fechamento |

**Verificação feita neste turno:** confronto das cinco árvores com 18.955 paths de `migration/source_snapshots`, incluindo Git blob SHA-1 e tamanho, gerou 18.955/18.955 correspondências, 0 faltantes/alterados na cópia de árvore. **Isso não equivale** a SHA-256 de bytes dos arquivos originais Drive. O confronto da fonte volumosa com a `main` atual encontrou **22 divergências de blob no mesmo caminho**, enquanto o manifesto anterior citava 21 para um cutoff anterior. Não sobrescrever; comparar os dois cutoffs e classificar cada conflito.

**PR #6**: [PR DRAFT — 9 políticas JSON](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/6): `open=true`, `draft=true`, `merged=false`, HEAD lido `2fc555f854c64b9d44f778805fbfca7675bd3cce`. Não alterar estado nem mergear até gates. Outros PRs/branches exigem verificação de status no momento de promoção; não assumir que branch é obsoleta só pelo nome.

## 3. Supabase: autorização, uso permitido e observações verificadas

**Projeto identificado:** `Calculadoras-Smart` (`pgsybzggewhinaniybiy`), região `sa-east-1`, PostgreSQL 17.6 conforme leitura. Não confundir com o projeto separado `SOT-10-09-2026`.

### Contrato de uso

- **READ_ONLY nesta fase**: `list_projects`, `list_tables`, `execute_sql` **somente com SELECT**, sem alterar esquema, dados, índices, políticas, RLS, storage, funções, jobs, eventos ou permissões.
- Supabase fornece **registros de confronto, observações e estado de operação**, mas documentação final, baselines, políticas, WOs, matrizes e relatórios residem/versionam no GitHub.
- **Jamais** inferir que `technical_status='PASS_ESTRUTURAL'` signifique validação de bytes ou homologação clínica. Também `PLAN_ONLY` não é ingestão concluída.
- Em desenho futuro homologado, Kernel pode persistir eventos de admissão/FIND e locks transacionais no Supabase, ligados ao SHA da WO no Git. Não fabricar estados/eventos, não usar writes antes de política, WO e ambiente autorizado.

| Objeto Supabase | Uso |
|---|---|
| `calculadoras_de_enfermagem.file_integrity` | 65 registros de arquivo com nome, domínio, tamanho, SHA-256 declarado e `technical_status` |
| `calculadoras_de_enfermagem.file_delta_plan` | 65 planos `PLAN_ONLY`, nenhum `raw_data_loaded` e nenhuma autorização de publicação/write |
| `calculadoras_de_enfermagem.delta_assurance_snapshots` | snapshot do planejamento: 65 arquivos / 15 temas / 547.908 átomos **declarados**, sem semântica concluída |
| `calculadoras_de_enfermagem.source_lineage` | 61 relações; **0 `verified=true`**; não promover |
| `calculadoras_de_enfermagem.reconciliation_holds` | 9 `HOLD_HUMAN` (privacidade, clínica, direitos, equivalência, normativo) |
| `calculadoras_de_enfermagem.reconciliation_observations` | 17 observações históricas; interpretação depende de método/cutoff |
| `cko_orch.outbox_events` | **303 PENDING**, 15 PUBLISHED; investigar somente leitura, sem replay |
| `cko_orch.policy_registry` | registry de apoio para confrontar versão/estado com Git, não autoriza política por si só |
| `cko_governance.controlled_artifacts` / `cko_governance.change_audit_ledger` | inventário de controles e histórico de mutação, sujeito a validação |
| `ce_validation_hub.findings` / `inventory` | achados e inventário preexistentes, que não comprovam emissão/fechamento pelo Kernel |
| `cko_evidence.snapshots` e `storage.objects` | procedência e Storage; não substituir blob Git |

Contagem SQL confirmada: 65 arquivos em 15 temas = **770.659.606 bytes registrados** e 547.908 átomos declarados. 65/65 `PASS_ESTRUTURAL` apenas como metadado anterior, 65/65 `PLAN_ONLY`, 0 produção/liberação, 61 proveniências não verificadas, 9 holds ativos, 303 outbox pendentes. `public.ingest_artifacts` tinha 20 registros de ingestão para outros fluxos; não presumir equivalência com os 65 arquivos deste release.

**Consulta de controle reproduzível (somente leitura, sem dados pessoais):**

```sql
SELECT theme, file_name, file_size_bytes, sha256, atom_count,
       technical_status
FROM calculadoras_de_enfermagem.file_integrity
ORDER BY theme, file_name;

SELECT COUNT(*) AS total,
       COUNT(*) FILTER (WHERE verified IS TRUE) AS verified
FROM calculadoras_de_enfermagem.source_lineage;

SELECT status, COUNT(*) FROM cko_orch.outbox_events GROUP BY status;
```

Após consulta: vincular query, project, hora, quantidade, resultado sanitizado, executor e hash do arquivo de evidência sob Git. Não comitar dados de pacientes, chaves, URLs assinadas, logs com token ou credenciais em repositório público.

## 4. Resultado efetivamente obtido da reconciliação CE-04

- **5/5 árvores preservadas** no snapshot Git: 18.955/18.955 arquivos com SHA Git-1/tamanho iguais aos das árvores históricas. Validação de integridade de árvores **PASS**, mas não substitui rehash SHA-256 dos bytes Drive.
- **65 arquivos Supabase**: 59 possuem caminho final e tamanho exatos no primeiro snapshot `cursor/drive-sa-key-refactor`; **6 não têm o caminho exato esperado** nas comparações iniciais; não inferir ausência de conteúdo em outras localizações nem perda definitiva. Não houve conflito de tamanho entre as 59 correspondências.
- 15 manifestos `MANIFESTO.json` encontrados. **63/65** registros coincidem com os metadados desses manifestos-base. Os **2 restantes aparecem e coincidem em `MANIFESTO_v2.json`**, não são faltas do acervo: `sepse/definicao_transcrita_manualmente_v2.jsonl`, `sinais_vitais/classificacao_pa_dbha2020_transcrita_manualmente_v2.jsonl`. **65/65 metadados manifestos compatíveis quando respeitada a versão**.
- **3 arquivos pequenos testados com SHA-256 dos bytes de texto lidos via GitHub e comparados com manifestos:** `cid10/capitulo.jsonl`, `ferimentos/nome_tecnico_anvisa_curativo.jsonl`, `sinais_vitais/risco_news2_transcrito_manualmente.jsonl`. Esses **3/3** passaram; não extrapolar para 65.
- **Seis gaps de caminho exato**, todos preservados como pendências: `dispositivos/registro_anvisa_produto_saude.parte-0001.jsonl`, `medicamentos/apresentacao_cmed.jsonl`, `medicamentos/produto_fda_ndc.parte-0001.jsonl`, `medicamentos/produto_fda_ndc.parte-0002.jsonl`, `nutricao/alimento_usda_sr_legacy.jsonl`, `suprimentos/item_catmat.jsonl`. Suspeitas técnicas como limite de tamanho/caminho alternativo não são fatos comprovados; pesquisar todas as árvores Git e evidência histórica, sem reproduzir bytes fictícios.
- **22 conflitos de caminho** `main` atual vs `cursor/drive-sa-key-refactor`: `.github/workflows/drive-recursive-collect.yml`, `.gitignore`, `contracts/exemplo_atomo.json`, `docs/ARCHITECTURE.md`, `docs/FIND_TEMPLATE.md`, `docs/GOVERNANCE.md`, `docs/INVENTORY_INITIAL.md`, `docs/KERNEL.md`, `docs/PIPELINE.md`, `docs/REGISTRY.md`, `docs/TASKS.md`, `package.json`, `packages/cli/adapters/dou.py`, `packages/cli/adapters/secundaria.py`, `packages/cli/main.py`, `packages/cli/pipeline.py`, `packages/cli/registry.py`, `packages/cli/requirements.txt`, `packages/cli/utils.py`, `packages/schemas/atomo.py`, `packages/schemas/invariantes.py`, `tsconfig.json`. Manter versões divergentes; nenhuma escolha automática por commit mais recente.

**PENDÊNCIA DE PERSISTÊNCIA IDENTIFICADA:** arquivo proposto `docs/reconciliation/CE04_GIT_SUPABASE_MATRIX_20261017.json` **NÃO EXISTE** na branch no readback feito neste corte. Houve tentativa de composição/publicação mas **não há confirmação de gravação**. Próxima conversa deve recriar em microlote, gravar e validar por readback, sem marcar `TASK-CE04-004` fechada.

## 5. Governança: FIND / WO / políticas / validadores

- **WO CE-04:** [`contracts/wo/WO-CE04-RECON-20261017.candidate.json`](../..//contracts/wo/WO-CE04-RECON-20261017.candidate.json), status `DRAFT_NOT_ADMITTED`; não há admissão real vinculada ao seu Git blob. A forma `WO-CE04-RECON-20261017` é **ID candidato**, reconciliar com gramática canônica antes de admitir.
- **Tarefas CE-04:** `docs/tasks/CE04_RECON_TASK_REGISTER_20261017.json`; **38 registradas, 0 encerradas**, identificadores `TASK-CE04-001..038`, critérios, dependências e evidência por tarefa. `TASK-CE04-031` foi explicitamente corrigida: usar apenas arquivos históricos do Git, **não pedir acesso ao Drive novamente**. O registro recebeu readback de conteúdo e 38/38 IDs, sem fechar tarefas.
- **WO G0:** `fix/ce05-kernel-ci-security-20261017:contracts/wo/WO-G0-CORRECTIVE-20261017.json`, Git blob `f5743b450e71980086bb1c5d9effd65d5493216c`, `DRAFT_NOT_ADMITTED`, `execution_allowed=false`. Contém 17 rótulos `FIND-G0-001..017`, mas **não há prova de emissão desses FINDs pelo Kernel**; tratar como registros históricos/manuais, preservar, reconciliar nomenclatura e não fechar artificialmente. Sua própria lista de 17 contrasta com texto de aceite referente a 11; inconsistência a sanar com política/validador.
- **Política candidata** `contracts/policies/CE-GOV-WO-ADMISSION-001.candidate.json` na branch CE-05: `PROPOSED_NOT_HOMOLOGATED`; não há prova de enforcement no Kernel. **Não usá-la como permissão de execução por simples existência.**
- **FINDs adicionais legados** `docs/finds/FIND-CE-G0-011-wo-authority.md`, `docs/finds/FIND-G0-012.md` a `FIND-G0-017.md` e `migration/review_batches/CE-01-BATCH-01/FINDINGS-20261017.json` (quatro labels locais `FIND-001..004`): **múltiplas convenções e possíveis colisões**. Não renomear/destruir sem inventário e reconciliação de IDs e referências.
- **Padrão do template:** `docs/FIND_TEMPLATE.md` mostra `FIND-XXX` como exemplo; isso não comprova a gramática canônica completa. Recuperar `cko_governance.id_standards` e políticas Git **como evidência comparativa**, validar e resolver conflito com autoridade humana quando necessário.
- **Código Kernel CE-05**: `packages/cli/kernel/core.py` blob `c0f60b5b6f5b61ebc54e05f4b290ddb104e37919` na branch de correção. Import/registry de validadores, stub que aceita indiscriminadamente, policy registry permissivo, batch truncado, gates e critérios de review carecem testes reais. `docs/KERNEL.md` estipula "Kernel não pensa"; códigos operacionais não provam emissão de FINDs nem admissão transacional.
- **CI principal `.github/workflows/ci.yml`** apresenta `npx tsc --noEmit || echo ...` e `python packages/cli/main.py --help || echo ...`: **fail-open** nesses steps; corrigir por WO/Kernel isolado. Comprovar Actions reais com run IDs e logs antes de aceitar PR.
- **PR #6** permanece DRAFT/OPEN, não mergeado; nove políticas em piloto, sem autorização para aplicar políticas potencialmente destrutivas.

### Gate de encerramento FIND (sempre após a correção)

`ORIGINAL_ERROR_CAPTURED` → `POLICY_AND_VALIDATOR_IDENTIFIED` → `WO_GIT_VERSIONED_AND_ADMITTED` → `IMPLEMENTED_IN_ISOLATION` → `TESTS_POSITIVE_NEGATIVE_REGRESSION_PASS` → `EXTERNAL_TEST_RESULTS_INTEGRITY_PASS` → `ORIGINAL_FIND_CONDITION_REVALIDATED` → `INDEPENDENT_AUDIT_PASS` → `AUTHORIZED_REVIEW_PASS` → `KERNEL_CLOSES_FIND` → `RELEASE_GATE_CAN_RUN`.

Faltou qualquer gate? **Não fechar FIND, WO nem tarefa.** Registrar bloqueador/sua causa e continuar subfluxos de leitura e demais tarefas independentes. A decisão do Kernel não é a fonte da evidência externa.

## 6. Workflow integrado a implantar/homologar (não presumir operacional)

1. **Planejamento:** registry Git de fontes/processos, contrato e políticas vigentes; registrar requisito e critérios de aceite.
2. **WO no Git:** identificar objeto novo vs correção, tarefa e políticas aplicáveis; versão vinculada ao SHA Git; reservar ID via Kernel conforme regra existente, `PRE_APPROVED` para CREATE admissível.
3. **Kernel/admissão real:** resolver política e validador homologados e hashes; registrar autorização idempotente e transacional se previsto no Supabase; se falhar, FIND pelo Kernel quando política assim exigir. Não exigir que nova política já exista como produto final para admissão limitada de criação, mas exigir política de bootstrap aprovada.
4. **Execução:** agente/executor especializado consome tarefa determinística; workers com locks, fencing, backoff, checkpoints, lotes e proteção de concorrência; não gerar regras autonomamente.
5. **Evidence chain:** origem → aquisição → extração/ZIP/parsing → atomização → normalização → claims → validação técnica/clínica/normativa → proveniência → licenciamento/privacy → tradução → design/render → publicação. Registrar entradas/saídas/versões/SHA em Git, preservando originais e diferenças.
6. **Verificação externa:** runner/CI calcula hashes de bytes, compara manifestos e resultados, executa testes positivos/negativos/injeção de falhas e regressão, grava logs; auditor independente reproduz critérios.
7. **Kernel fechamento:** verifica evidências externa e autorização, fecha FIND via política/validador, conclui WO/tarefa quando permitido; não "assinar" como gerador da evidência técnica.
8. **PR DRAFT / gates CI reais / readback:** não merge até `REQUIRED × PRESENT × VALIDATED × PASS` por objeto e responsável. Só promoção homologada na main.
9. **Observabilidade:** execução monitorada e retomável, logs com redaction, outbox apenas quando authorized; estados no Supabase sincronizados com documentos Git, não o contrário.
10. **Portabilidade para próxima conversa:** todas as tarefas, decisões, bloqueadores e handoffs no repositório, **cada write seguido de GET/readback e comparação**.

## 7. Backlog integral de processos do projeto (18 frentes E2E candidatas)

Os 18 processos abaixo são **escopo inicial de trabalho**, não inventário comprovadamente exaustivo. Para cada um, produzir: inventário real, policy/schema/validator, WO, teste E2E com falha corrigida e regressão, logs/resultados independentes, evidência Git e auditoria. Nenhum piloto sintético equivale à integração homologada.

| Processo | Entrega para concluir |
|---|---|
| P01 FIND–WO–Kernel | bootstrap CREATE/`PRE_APPROVED`, autoridade de IDs/abertura/fechamento, admissão por blob, controles concorrentes e bateria adversarial real |
| P02 Fontes e aquisição | catálogo oficial e direitos, APIs, versão/URL, tempo/cutoff, original digital, falhas e aquisição incremental |
| P03 Extração | formatos CSV/XLS/PDF/DOCX/HTML/JSON/ZIP/JS/PY, detector fixo MIME/assinatura, extração determinística, hashes e limites |
| P04 Atomização | schemas, blocos, contexto/origem, nenhuma transformação não autorizada, reprocessamento determinístico |
| P05 Proveniência | source ID, work/snapshot/fragment/claim, hashes e vinculação a documento original verificável |
| P06 Validação clínica/normativa | protocolos, referências, direitos, jurisdição, casos limites/ambíguos, revisão habilitada |
| P07 Migração e reconciliação Git | 5 snapshots, 65 arquivos, 22 conflitos, 6 gaps, 61 vínculos, inventário todos tipos, 9 holds, histórico Drive preservado sem nova consulta |
| P08 Publicação | policies para render, versão, URL, impressão/exportações, cache, rollback e publicação com gate |
| P09 i18n | idiomas oficiais, traduções versionadas, equivalência terminológica e testes |
| P10 Design System / UI | recuperar tokens reais, acessibilidade e comparativos visuais, sem refazer estilo aprovado |
| P11 Calculadoras/escalas | 44 ferramentas por ondas, algoritmos, limites clínicos, test vectors e revisão habilitada |
| P12 Formulários | Aldrete v1.4.0 como referência, campos, impressão, data/hora, QR, acessibilidade, exportação e testes |
| P13 Simulados/treinos | pontuação, tempo, feedback, questões, fontes, direitos e separação dos projetos |
| P14 Segurança e LGPD | RLS, secrets, auth, PHI, licenças, DR, hardening e testes adversariais |
| P15 Agentes/orquestração | políticas de execução, worker idempotente, locks/fencing, observabilidade, retries e fail-closed |
| P16 Auditoria independente Genesis × ZEN | objetivos/assertions, RCM, ITGC, MRC (Management Review Control), IPE/CAAT, workpapers, pareceres e testes |
| P17 CI/CD e promoção | rulesets, branch protections, checks obrigatórios reais, PR draft, readback, rollback |
| P18 Direitos e licenciamento | origem e redistribuição, restrições, uso editorial/clinico, aprovação humana quando exigida |

**Ampliações transversais a inventorizar:** Knowledge Engine, CKO/NCOS/NIS, biblioteca de anatomia, PWA, SEO/claims, acessibilidade, documentação/publicações, políticas e validators, rastreabilidade de conteúdo, componentes web, analytics/cookies, segurança de dados, Atlas, recursos educativos, Vila do Cuidado, scripts legado Python/JS, API/infra, qualidade de dados, operações e administração. **Não tratar AuditEduca como parte de Genesis × ZEN**: AuditEduca é projeto separado; usar referências cruzadas quando aplicável.

## 8. As 38 tarefas CE-04 já gravadas no GitHub — nenhuma fechada

**Registro normativo candidato:** `docs/tasks/CE04_RECON_TASK_REGISTER_20261017.json`, validado por GET/readback. Ordenação permite leitura, não significa autorização de execução produtiva.

| ID | Entrega | Estado | Dependências |
|---|---|---|---|
| TASK-CE04-001 | Fixar escopo e baseline de GitHub e Supabase | PREFLIGHT_VERIFICATION_PENDING | — |
| TASK-CE04-002 | Reverificar os cinco snapshots sem perda | PREFLIGHT_VERIFICATION_PENDING | TASK-CE04-001 |
| TASK-CE04-003 | Reconciliar 22 versões divergentes da main | PENDING_KERNEL_ADMISSION | TASK-CE04-002 |
| TASK-CE04-004 | Conferir arquivos e hashes contra 65 registros Supabase | PENDING_KERNEL_ADMISSION | TASK-CE04-002 |
| TASK-CE04-005 | Reconciliar 15 manifestos por versão | PENDING_KERNEL_ADMISSION | TASK-CE04-004 |
| TASK-CE04-006 | Pesquisar e reconciliar faltas nas branches | PENDING_KERNEL_ADMISSION | TASK-CE04-004 |
| TASK-CE04-007 | Investigação de arquivo ausente: dispositivos/registro_anvisa_produto_saude.parte-0001.jsonl | PENDING_KERNEL_ADMISSION | TASK-CE04-006 |
| TASK-CE04-008 | Investigação de arquivo ausente: medicamentos/apresentacao_cmed.jsonl | PENDING_KERNEL_ADMISSION | TASK-CE04-006 |
| TASK-CE04-009 | Investigação de arquivo ausente: medicamentos/produto_fda_ndc.parte-0001.jsonl | PENDING_KERNEL_ADMISSION | TASK-CE04-006 |
| TASK-CE04-010 | Investigação de arquivo ausente: medicamentos/produto_fda_ndc.parte-0002.jsonl | PENDING_KERNEL_ADMISSION | TASK-CE04-006 |
| TASK-CE04-011 | Investigação de arquivo ausente: nutricao/alimento_usda_sr_legacy.jsonl | PENDING_KERNEL_ADMISSION | TASK-CE04-006 |
| TASK-CE04-012 | Investigação de arquivo ausente: suprimentos/item_catmat.jsonl | PENDING_KERNEL_ADMISSION | TASK-CE04-006 |
| TASK-CE04-013 | Reconciliação domínio cid10 (6 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-014 | Reconciliação domínio dispositivos (3 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-015 | Reconciliação domínio epidemiologico (9 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-016 | Reconciliação domínio ferimentos (5 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-017 | Reconciliação domínio icd11 (3 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-018 | Reconciliação domínio medicamentos (6 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-019 | Reconciliação domínio medlineplus (2 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-020 | Reconciliação domínio mesh (1 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-021 | Reconciliação domínio nutricao (4 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-022 | Reconciliação domínio protocolos_enfermagem (3 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-023 | Reconciliação domínio sepse (7 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-024 | Reconciliação domínio sinais_vitais (4 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-025 | Reconciliação domínio suprimentos (4 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-026 | Reconciliação domínio vacinal_brasil (4 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-027 | Reconciliação domínio vacinas (4 arquivos) | PENDING_KERNEL_ADMISSION | TASK-CE04-004, TASK-CE04-005 |
| TASK-CE04-028 | Validar os 61 vínculos de proveniência | PENDING_KERNEL_ADMISSION | TASK-CE04-005 |
| TASK-CE04-029 | Tratar nove HOLD_HUMAN existentes | PENDING_KERNEL_ADMISSION | TASK-CE04-005 |
| TASK-CE04-030 | Auditar 303 eventos outbox pendentes | PENDING_KERNEL_ADMISSION | TASK-CE04-001 |
| TASK-CE04-031 | Confrontar inventários históricos do Drive já preservados no GitHub (sem solicitar acesso ao Drive) | HOLD_SOURCE_EVIDENCE_NO_DRIVE_ACCESS_REQUEST | TASK-CE04-001 |
| TASK-CE04-032 | Reconciliar 102 WOs históricas e seus estados | PENDING_KERNEL_ADMISSION | TASK-CE04-002 |
| TASK-CE04-033 | Revisar segurança, segredos, licenças e dados pessoais | PENDING_KERNEL_ADMISSION | TASK-CE04-002 |
| TASK-CE04-034 | Submeter WO ao Kernel e obter admissão verificável | PENDING_KERNEL_ADMISSION | TASK-CE04-001 |
| TASK-CE04-035 | Executar testes positivos, negativos e integração | PENDING_KERNEL_ADMISSION | TASK-CE04-034 |
| TASK-CE04-036 | Auditoria independente e validação de FINDs | PENDING_KERNEL_ADMISSION | TASK-CE04-035, TASK-CE04-028, TASK-CE04-029 |
| TASK-CE04-037 | PR DRAFT de promoção controlada | PENDING_KERNEL_ADMISSION | TASK-CE04-034, TASK-CE04-036 |
| TASK-CE04-038 | Promoção autorizada após reconciliação | PENDING_KERNEL_ADMISSION | TASK-CE04-037, TASK-CE04-036 |

**Atenção à dependência:** Tarefa 031 está em `HOLD_SOURCE_EVIDENCE_NO_DRIVE_ACCESS_REQUEST`, e não pode se tornar requisito de "autorizar nova consulta Drive". Suprir com arquivos históricos existentes ou marcar não verificável, sem suspender frentes independentes.

## 9. Plano de execução determinística até encerramento

### Onda 0 — recuperação e integridade documental
- Revalidar branch/HEAD, arquivo WO e registro de 38 tarefas. Fazer readback **novamente** em cada sessão e registrar corte; não confiar só no texto deste handoff.
- Persistir `docs/reconciliation/CE04_GIT_SUPABASE_MATRIX_20261017.json` **ainda ausente**. Se o conector não aceitar grande payload, gravar microarquivos por domínio e um index agregador; cada arquivo recebe write, GET, comparação de conteúdo e blob.
- Gerar inventário das 14 branches; reconciliar estados e HEADs. Sem excluir branch.
- Revisar a gramática canônica de FIND, WO, tarefa via contratos Git e registros de apoio Supabase; abrir proposta de melhoria controlada quando necessário, não inventar nomes em produção.
- Verificar que todos os commits documentais ficaram na branch e não na main.

### Onda 1 — reconciliação Git × Supabase com o que já existe
- Atualizar matrizes de 15 domínios e 65 arquivos; recuperar versões `MANIFESTO_v2` para dois casos sem confundir com ausência.
- Pesquisar seis gaps com árvore recursiva exata nos cinco snapshots; comparar nomes alternativos, manifests, metadados e Git LFS pointers; não criar arquivos faltantes.
- Rehash SHA256 de bytes Git onde acessíveis, comparar com valor informado pelo manifesto e Supabase; **Git blob SHA1 não é SHA256**. Não marcar como aprovado se bytes não estiverem acessíveis.
- Auditar os 22 conflitos `main` atual versus árvore histórica, com SHA ambos e diff por tipo, decisão `KEEP_BOTH`/HOLD até revisão.
- Preservar quarentenas e ZIP members; verificar o que já consta no Git, sem pedir Drive.

### Onda 2 — reconciliação de proveniência, segurança e governança
- Analisar 61 relações `verified=false` uma a uma, exigir fonte/versão/vínculo/URL/citação/hash, sem inferir PASS.
- Consolidar 9 holds: clínica, direitos, privacidade, integração, normativa. Solicitar **apenas as decisões humanas que as políticas exigem**, nunca acesso Drive.
- Categorizar 303 outbox pendentes e avaliar riscos de replay; sem executar replay.
- Reconstruir 102 WOs históricas a partir dos artefatos Git, confrontar com evidência Kernel real; registros que dizem `PASS` sem logs/verificação continuam candidatos.
- Classificar licenças, PHI e segredos; garantir nenhum vazamento para o GitHub público.

### Onda 3 — Kernel, CI, testes e auditoria independente
- Prototipar e integrar fluxo `PRE_APPROVED` de criação, com prova de schema/policy/validator e IDs idempotentes; resolver bloqueio circular com bootstrap.
- Corrigir falhas técnicas CE-05 via WO admitida: validator registry, stubs, SHA enforcement, autorização humana, batch, concorrência, fencing, exceções e idempotência.
- Testar PostgreSQL em ambiente **isolado** e GitHub Actions reais; exit codes e logs preservados.
- Fazer CE-06 independente sobre as 21 assertions históricas (3 PASS, 6 FAIL, 12 HOLD_HUMAN reportados anteriormente); atualizar resultado apenas após novos testes/evidência.
- Kernel verifica FIND original→correção→revalidação→auditoria e fecha conforme política. Não transformar FIND manual em emitido pelo Kernel retrospectivamente.

### Onda 4 — reconciliação final + promoção
- Matriz global `REQUIRED × PRESENT × VALIDATED × PASS` para todos objetos/processos; zeros reais de faltas/bloqueadores *ou* exceção devidamente autorizada.
- Gerar relatório de diferenças, logs e hash corpus; confirmar consistência entre Git, Supabase e o legado já disponível; registrar limites de cobertura Drive.
- PR DRAFT isolado, CI real PASS, revisão independente, decisão humana e Kernel. Não mergear manualmente fora do contrato; preservar rollback.
- Após autorização: promover só conteúdo homologado, revisar navegação/render/i18n/acessibilidade/segurança, smoke real e replay de critérios positivos/negativos.
- Fechar tarefas/WO/FIND apenas com artefato verificável e readback. Atualizar handoff e backlog a cada microlote.

## 10. Contrato de aceite e protocolo obrigatório de salvamento

Para qualquer artefato de tarefa (`.md`, `.json`, `.py`, `.sql`, logs):
1. Confirmar branch autorizada e SHA atual; produzir o arquivo em path canônico candidato sem colisão.
2. Validar estrutura, contrato, ausência de segredos/dados sensíveis e hashes locais; sempre distinguir candidatos de artefatos homologados.
3. Fazer `create_file`/`update_file` ou commit Git controlado; capturar SHA do commit e blob.
4. **Obrigatório** `fetch_file` na MESMA branch; comparar texto exato, ID, campos, contador de tarefas e SHA. Se divergir ou retornar 404, **SALVAMENTO = FAIL**, não avançar como concluído.
5. Registrar receipt de write/readback com path, HEAD, commit, blob, data/cutoff, teste, verificador e resultado. Um recibo de persistência **não** significa homologação.
6. Executar testes positivos, negativos, regressão e integridade no artefato persistido; guardar logs/exit codes e evidência externa.
7. Auditar independentemente e submeter critérios ao Kernel; apenas após fechamento aplicável autorizar `COMPLETED`.
8. Reabrir/complementar tarefa sob governança se readback posterior mostrar drift; nunca sobrescrever fonte sem preservação.

**Gate final de processo/projeto:** `REQUIRED = PRESENT = VALIDATED = PASS` para escopo obrigatório, com evidências, sem FIND bloqueante; política de exceção aprovada quando explicitamente aplicável; CI PASS, auditoria PASS, Kernel PASS, revisão humana aplicável PASS e Git readback PASS. Para o corpus de origem Drive sem prova, o escopo integral permanece `UNVERIFIABLE`, sem narrativa de 100%.

## 11. Artefatos de origem prioritários (consultar diretamente)

- `docs/ARQUITETURA_KERNEL_UNIFICADA.md`, `docs/KERNEL.md`, `docs/GOVERNANCE.md`, `docs/FIND_TEMPLATE.md`, `docs/TASKS.md`, `docs/REGISTRY.md`.
- `docs/PLANO_EXECUCAO_WO_KERNEL_DETERMINISTICO.md` (afirma 102 WOs históricas, sendo 98 PASS / 2 PREAUTHORIZED / 2 BLOQUEADO; **números históricos não revalidados individualmente**).
- `contracts/policies/KERNEL-POLICY-001.json` a `KERNEL-POLICY-020.json`, política CE-05 candidata e `packages/cli/kernel/{core.py,policy_registry.py,cli.py}`.
- `migration/MANIFEST.json`, `migration/PATH_AND_CONFLICT_AUDIT.json`, `migration/README.md` na branch `migration/candidate-f08-20261017`; as árvores contêm versões originais Git.
- `migration/review_batches/CE-01-BATCH-01/FINDINGS-20261017.json` e cinco arquivos de evidência na branch `migration/ce01-historical-evidence-b01-20261017`.
- `fix/ce05-kernel-ci-security-20261017:contracts/wo/WO-G0-CORRECTIVE-20261017.json` e `docs/finds/` (candidatos não emitidos operacionalmente pelo Kernel).
- `config/drive_inventory_roots_20261016.json` (**registro histórico apenas — não executar conexão Drive**).
- Este próprio handoff, a WO candidata e o registro das 38 tarefas na branch auditável.

## 12. Instrução literal para iniciar a próxima conversa

> Continue o projeto **Calculadoras de Enfermagem** diretamente pelo handoff `docs/handoffs/CE_MASTER_HANDOFF_20261017.md` na branch `audit/ce04-reconciliation-tasks-20261017` de `IndiciumFIN/calculadorasdeenfermagem`. **NÃO solicite acesso ao Drive nem use conector Drive.** GitHub é a fonte documental da verdade; Supabase `Calculadoras-Smart` somente como apoio transacional e confronto read-only. Leia WO e 38 tarefas, confira HEAD/blobs por readback, reconstrua e salve a matriz de 65 arquivos em microlotes (artefato atualmente ausente), audite 22 conflitos/6 gaps/61 vínculos/9 holds/303 outbox. Continue pelas ondas até os 18 processos E2E, sem alegar homologação antes do Kernel, testes e auditoria. Grave cada tarefa/artefato no GitHub, faça readback imediatamente e só declare conclusão após salvar, testar e fechar FIND conforme política. Não promova na main, não exclua nem deduplique destrutivamente. Ao final de cada microlote atualize tarefas/handoff no repositório e comprove write→readback.

**Marco deste handoff:** GitHub documental de tarefas e WO = `PERSISTED_VERIFIED`; matriz individual de 65 registros = `NOT_PERSISTED`; Kernel admission = `NOT_REQUESTED`; liberação = `BLOCKED`. 


## Addendum operacional — 2026-10-17 — microlotes da matriz

- A pendência original de `docs/reconciliation/CE04_GIT_SUPABASE_MATRIX_20261017.json` foi superada **apenas no nível de índice documental de metadados**. Índice candidato criado no commit `606451862c7e219f6acf05f7052fc22d0ca4f4ee`, blob `bafcd0f6076cbce25cbd9917441e0cf7ae4017e4`, e confirmado por readback literal.
- Sete microlotes `docs/reconciliation/CE04_MATRIX_BATCH_01_CID10_20261017.candidate.json` a `CE04_MATRIX_BATCH_07_20261017.candidate.json` armazenam os 65 metadados da `file_integrity` de `Calculadoras-Smart` via `SELECT`, com readback e contagens 6+10+10+10+10+10+9=65.
- A matriz **não** comprova hash SHA-256 de bytes Git para os 65 arquivos, correspondência exata de caminhos, licenças, validação clínica, auditoria independente ou admissão pelo Kernel. Todos os itens mantêm `validated=false`, `pass=false`; 6 gaps e 22 conflitos históricos permanecem sem decisão.
- WO `WO-CE04-RECON-20261017` permanece `DRAFT_NOT_ADMITTED`. Tarefas registradas 38, fechadas 0; nenhuma FIND foi encerrada. Supabase permanece READ_ONLY. Nenhuma mutação da `main`.
- `docs/handoffs/CE_CONTINUATION_STATE_20261017.json` foi atualizado e confirmado por readback no commit `437349996fa74ff7bf80286f96d48e0ed7382063`.
- Próximo ciclo: usar as sete matrizes candidatas como base para varredura de Git Trees/manifests e rehash dos bytes disponíveis; não inferir `PASS` de `PASS_ESTRUTURAL`. Aplicar WO/política/validador/Kernel e auditoria independente antes de encerramento ou promoção.


### Addendum CE-04 — reconciliação estrutural das 15 áreas (2026-10-17)

- **Resultado novo:** 65/65 registros de `calculadoras_de_enfermagem.file_integrity` confrontados em consultas `SELECT` com metadados de `MANIFESTO.json` ou `MANIFESTO_v2.json` nas árvores Git da branch `cursor/drive-sa-key-refactor`. Identificados **59 blobs individuais** com tamanho declarado equivalente e **6 arquivos divididos em 14 blobs** com soma de tamanhos correspondente. O confronto de metadados (nome, SHA-256 declarado, bytes, átomos) apresentou 65 correspondências.
- **Seis gaps de caminho original explicados estruturalmente:** `docs/reconciliation/CE04_GAPS_06_CHUNKS_20261017.candidate.json` — commit `b5bfb5557694cbe16c722cdfa26a9cddbb853d2f`, blob `94f46a9aa68f3878f219baad0880259801854e60`. Manifestos de partes têm offsets contíguos, SHA-256 declarado compatível com Supabase e Git blob SHA-1 por parte. **Não houve cálculo independente do SHA-256 dos bytes concatenados.**
- **Microlotes de confronto:** `CE04_DOMAIN_TREE_MANIFEST_BATCH_01_20261017.candidate.json` (26 registros; commit `2187f43b94719bd3962a3636d8ddf59634ea964b`), `...BATCH_02...` (16; commit `fe01a4b7caace3e205e7a067104156eabc4ceb9c`) e `...BATCH_03...` (23; commit `7d86d2f19520aac92c70f6d0a02fbe283f47da77`). Todos receberam readback literal com igualdade exata. O primeiro usa chave `manifest_metadados_confere`; os outros usam `manifest_metadata_matches_supabase`. O agregador tratou ambos explicitamente, sem falsear resultados.
- **Índice consolidado:** `docs/reconciliation/CE04_GIT_SUPABASE_MATRIX_20261017.json` atualizado e confirmado no commit `f35ae3699d9b42e2d88c0125618d21665e5cd6dc`, blob `2bac4e9d0af0527e526e3adbd92b6fde61bdc475`. `docs/handoffs/CE_CONTINUATION_STATE_20261017.json` atualizado no commit `43ec1fe5207fa64a81e4c0a3d674041521c3ab0b`, readback PASS.
- **Gates não superados:** `DRAFT_NOT_ADMITTED`, 0/38 tarefas fechadas, nenhum FIND encerrado; verificação SHA-256 real integral 0/65 nesta sessão, 22 conflitos históricos ainda pendentes, 61 vínculos de origem não homologados, nove HOLD_HUMAN e 303 eventos outbox sem replay. Política/ferramenta de validação/Auditoria CE-06 e autorização de promoção continuam exigidas. Não acessar Drive, não escrever no Supabase, não alterar `main`.


### Addendum CE-04 — SHA-256 e comparação textual dos conflitos (2026-10-17)

- Git refs revalidadas: `main`=`e0f62491b104f4a97c6025a6393cabc2e7ada30e`, árvore histórica `cursor/drive-sa-key-refactor`=`fd5818f42c6a6f716996d8c9418ba87a079d0c59`. Árvores recursivas completas: 176 e 9.366 blobs, 74 caminhos compartilhados; **22 caminhos divergentes em SHA e tamanho**, preservados em dois lotes de 11 (`CE04_MAIN_VS_HISTORICAL_CONFLICTS_BATCH_01/02_20261017.candidate.json`; commits `5ffc93a9fc8538a70124c12bd874a19203039fa7` e `6794471d7f044c9e42ff0185c5f262fddac0a323`).
- As **22/22** divergências foram lidas nas duas versões por `fetch_file`, confrontadas com SHA Git esperado, comparadas por multiconjunto de linhas (não diff semântico, nem revisão de segurança funcional) e documentadas em quatro grupos: `CE04_CONFLICT_TEXT_DIFF_BATCH_01..04_20261017.candidate.json`; commits `c4c07c07b168886d28668f8e7fb8faa763c5d454`, `a9d8c8f73492c476c02afc92ecb9101ec872ecf5`, `873ee3d350c022a651ce414ef322a2461a0834f1`, `55ce4a028bc3b5f52a3af1b987a26a4fc3a62aa8`. Sem escolha de vencedor, `KEEP_BOTH_HOLD`, decisões pendentes.
- **Oito arquivos distintos** (amostra, não população) tiveram SHA-256 de bytes UTF-8 retornados pelo conector GitHub recalculado, com tamanho e hash iguais à referência dos manifestos/Supabase. Cinco no `CE04_GIT_BYTE_SHA256_MICROBATCH_01_20261017.candidate.json` (commit `faeb391622523ddd449e86abbeb93c02c5f2d8a0`), três no `CE04_GIT_BYTE_SHA256_MICROBATCH_02_20261017.candidate.json` (commit `d9bfb24f58c8f0fb77288226e465ba1af30c4a27`). A etapa do segundo lote capturou uma transcrição manual incorreta de hash esperado, abortou gravação na primeira tentativa e recuperou o valor do Git: evidência documentada, sem modificar fontes.
- Consultas agregadas **somente leitura** ao Supabase: `CE04_SUPABASE_READONLY_STATUS_20261017.candidate.json` commit `0bd537b56094a24f5c47ae33cc403188a8a74106`, com status da outbox, nove HOLD_HUMAN e 61 vínculos de origem `verified=false`. Nenhum evento reprocessado; nenhum registro ou política DB alterados.
- Manifesto de continuidade atualizado e readback confirmado no commit `bb38d60a6b957aeb039c9f02f3ebd3bfc5eff094`. Status: **8/65** SHA-256 revalidados nesta etapa, **57** pendentes; conflitos **22 inventariados e comparados, 0 resolvidos**; WO ainda `DRAFT_NOT_ADMITTED`, **0/38** tarefas fechadas, Kernel/auditoria/CI/autorizações ainda pendentes. Nenhum merge ou alteração da main, nenhum acesso ao Drive.
