# CE — PMO: baseline de controle e critério de confiabilidade

**Corte:** 2026-10-19 (America/Sao_Paulo). **Estado:** `CANDIDATE_NOT_CANONICAL / STOP_WORK / NO_GO_EXECUTION`.

## Decisão de direção

Por determinação do responsável, suspender novos microlotes de atomização, aquisição, correção, integração, publicação, alteração de branches e mutações. A única atividade aberta é reconstrução, deduplicação e validação do PMO. A aprovação de negócio permanece reservada para o final do projeto. Nenhum resultado estrutural equivale a homologação clínica, jurídica, normativa ou à admissão do Kernel.

## Fontes existentes que devem ser reconciliadas, não recriadas

| Conjunto | População | Evidência identificada | Status atual do PMO |
| --- | --- | --- | --- |
| Repositório final | 14 branches, 4 PRs abertos na leitura de 19/10 | GitHub `IndiciumFIN/calculadorasdeenfermagem`; PR #2, #3, #4, #6; relatório `CE_BRANCH_RECON_READONLY_20261019_CANDIDATE.md` | `PARTIAL_READBACK`; main ruleset/CI sem readback conclusivo nesta rodada |
| CE04 tarefas | 38 tarefas | `CE04_TASK_REGISTER_READBACK.json`, contido em `CE_MASTER_CONTINUITY_20261018(1).zip` | 0 encerradas/0 admissões comprovadas no corte desse registro |
| CE04 conteúdo | 65 arquivos, 15 domínios | M10–M43, manifesto CE04 | 53 estruturais; 12 pendentes (7 grandes e 5 M24); 0 homologados nos gates clínico/direitos |
| Universos documentais | ~19.119 entradas de árvore, 1.020 metadados normativos, 8.982 Master Data históricos | ZIP de continuidade de 18/10 e handoffs CE02/CE04 | Denominadores independentes, não somar; integridade substantiva em HOLD |
| Contratos e WOs | 76 WOs do PR #2 e 102 WOs em auditoria histórica anterior | `contracts/work_orders/` no PR #2; memória do registro histórico | Escopos não reconciliados; WOs do PR #2 declaram `CKO-TAREFA-1.0.0` e não são diretamente compatíveis com schema específico GAP-01 de execução de agente; não inferir invalidade original |
| Kernel e agentes | 14 executores stub no pacote M20; 110 entradas de registro em PR #2 | `CE_M20_KERNEL_EXECUTORES_AUDIT_CANDIDATE.md`, `CE_M21_CONTENCAO_KERNEL_E_TRILHO_CONTEUDO_CANDIDATE.md`, PR #2 | Diferentes populações; contenção local `exit 78` em M21, runtime autoritativo não comprovado |
| Aquisição | 22 schemas, 454 campos; 10 fontes COFEN/MTE sob HOLD | M12, M14 | Registros candidatos; rights/source/Kernel não admitidos |
| Banco e publicação | 303 outbox pendentes, 61 proveniências não verificadas, site F4 parcialmente testado | CE03/F4 históricos | Não presumir leitura remota atual; nenhuma mutação até novos gates |
| Auditoria independente | 21 controles: 3 PASS, 6 FAIL, 12 HOLD_HUMAN no parecer histórico | CE06 | Recertificação e novo parecer necessários, sem autocertificação |
| Backups | ZIP completo até M39 | `CE_BACKUP_COMPLETO_POS_20261018_ATE_M39_20261019.zip` | M40–M43 não cobertos por esse checkpoint |

## Reconciliação obrigatória de FINDs duplicados/recorrentes

- `M42-F01`: erro `second-pass partial JSONL line before EOF`, correção `_read_complete_line()` e reteste positivo em M42.
- MeSH 19/10: o mesmo erro reapareceu na segunda passagem de `mesh/descritor_mesh.jsonl`; **classificar `RECURRENCE_UNDER_INVESTIGATION` vinculado a `M42-F01`**, e não criar FIND autoritativo independente sem confronto.
- `M20-FIND-001..008` e `M21-FIND-001..004`: diagnósticos/containment existentes; qualquer novo registro deve referenciar origem e delta, não duplicar.
- `FIND-A-006`: 76 WOs do PR #2 falham se aplicadas ao schema agent-only GAP-01; isso é desvio de roteamento/compatibilidade **sob investigação**, não defeito comprovado de 76 WOs perante o contrato `CKO-TAREFA-1.0.0`.

## Chave de identidade, deduplicação e trilha mínima

Todo registro do PMO exigirá `canonical_id`, `object_type`, `namespace`, `source_system`, `source_ref`, `source_commit_or_version`, `cutoff_utc`, `scope_population`, `evidence_ref`, `evidence_hash_when_verified`, `status`, `status_authority`, `owner`, `blocked_by`, `related_find_ids`, `related_task_ids`, `policy_ref`, `validator_ref`, `wo_ref`, `kernel_admission_receipt_ref`, `test_ref`, `independent_audit_ref`, `decision_ref`, `updated_at`, `next_action` e `confidence_basis`.

Nenhum campo de autoridade, aprovação ou evidência pode ser preenchido por presunção. `UNKNOWN`, `NOT_VERIFIED`, `HOLD`, `CANDIDATE` e `PASS_VERIFIED` devem permanecer distintos. Identificador textual sem bytes/ligações de SHA não prova integridade. Populações com cortes diferentes não podem ser agregadas.

**Identidade de FIND:** combinação de componente/artefato, assinatura do desvio, versão e fonte da evidência; incidentes posteriores são `occurrences` associados ao FIND existente até provar causa distinta. Manter a descrição original e histórico append-only.

**Identidade de tarefa:** namespace + ID histórico + sistema de origem; nunca somar WOs e tarefas CE04 como se pertencessem ao mesmo universo.

## Gates de aceite do PMO

1. `G-PMO-01 INVENTORY`: todas as fontes de controle conhecidas inventariadas e versionadas; cobertura e exceções explícitas por universo.
2. `G-PMO-02 IDENTITY`: IDs sem colisão não resolvida, aliases históricos e vinculação de versões divergentes.
3. `G-PMO-03 LINEAGE`: toda métrica tem população, cutoff, origem e evidência, com conflitos preservados.
4. `G-PMO-04 TASK_FIND`: tarefas e FINDs vinculados; zero fechamentos artificiais, ocorrências recorrentes deduplicadas.
5. `G-PMO-05 AUTHORITY`: política/validador/tarefa/WO/Kernel sem extrapolação de autoridade; admissões não comprovadas permanecem HOLD.
6. `G-PMO-06 QA`: testes negativos para ausência de fontes, contagem contraditória, hash falso, referência quebrada, status aprovado sem recibo, registro duplicado e regressão recorrente.
7. `G-PMO-07 READBACK`: publicação controlada em branch isolada somente após elegibilidade da cadeia de governança, testes e auditoria, seguida de conferência por SHA.
8. `G-PMO-08 INDEPENDENCE`: parecer independente do PMO e aceite do responsável apenas no fechamento do projeto.

**Condição de suspensão:** se algum gate 01–06 estiver incompleto, `PMO_TRUSTED=false`, `PROJECT_EXECUTION_ALLOWED=false` e todas as frentes operacionais seguem suspensas. O trabalho preparatório de PMO não concede admissão remota.

## Exceção de custódia documental — instrução expressa de 19/10/2026

O responsável autorizou **temporariamente dispensar a admissão Kernel apenas para salvar e organizar artefatos de PMO/recuperação no repositório**, com commit e readback a cada tarefa concluída, para conter retrabalho e risco de perda. Esta exceção não autoriza execução clínica, downloads, ingestão produtiva, replay de banco, exclusões, force-push, merge ou modificação da `main`.

- Destino: branch **isolada** `pmo/recovery-controlled-20261019`, baseada no HEAD conferido da `main`; arquivos sob `docs/pmo/recovery/20261019/`.
- Microlotes não destrutivos: registrar fontes, tamanho, SHA-256, corte, proprietário e status; comparar nomes e hashes antes de gravar.
- Cada microlote: salvar arquivos + atualizar índice/PMO → commit → readback dos bytes/SHAs → registrar resultado. Qualquer falha deixa a tarefa em HOLD sem alegação de persistência.
- Arquivos históricos, variantes, entradas do usuário e segredos nunca são removidos ou publicados automaticamente. "Limpeza" significa classificação e organização lógica até existir decisão separada por alvo.
- Registrar esta exceção como decisão operacional sujeita a auditoria posterior e reativar a cadeia regular de WO/Kernel para todas as demais mutações.

## Próxima execução permitida

Consolidar o registro de evidências do PMO com crosswalk dos PMOs e handoffs preexistentes; validar denominadores, hashes e duplicatas; emitir teste independente e apenas então preparar WO/Kernel de implantação do PMO. Não atomizar MeSH, não continuar M44, não recriar tarefas existentes enquanto `PMO_TRUSTED=false`.
