# CE/CKO/NCOS — checkpoint 2026-11-15 15:54 BRT

Projeto físico: `pgsybzggewhinaniybiy`. Execução exclusivamente SELECT; nenhuma migration, seed, DDL, DML ou merge.

## WO CE-AUDIT-INSERT-20261115
**Estado: PASS_DB_READONLY / HOLD_SEMANTIC / HOLD_HUMAN**

Origem: catálogo PostgreSQL `pg_trigger`, `pg_class`, `pg_namespace`, `pg_proc`; consulta realizada em 2026-11-15. PR de referência: https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/73. Checkpoint anterior: commit `5a09a10e5eee8654d0156996f5043a17a681ec93`.

### Delta incremental (sem reprocessar os 47 triggers conhecidos)
- Os 47 triggers `audit_protected_row_change` permanecem associados a UPDATE/DELETE, sem INSERT; evidência anterior preservada.
- **Existem outros triggers de INSERT**, não pertencentes à função de auditoria: `cko_governance.controlled_artifacts` (`guard_pilot_baseline_promotion`, INSERT/UPDATE), `cko_orch.divergences`, `locks`, `proposals` (dois), `transition_log`, e `cko_validation.findings` (dois, INSERT/UPDATE). São controles de governança/orquestração, **não prova de registro no `change_audit_ledger`**.
- Consulta restrita por nome de trigger (`%audit%`, `%publish%`, `%revoke%`) encontrou somente os dois triggers de congelamento do ledger; nomes de trigger não são inventário exaustivo de cobertura de eventos.
- Resultado: a conclusão correta é **0/47 triggers da função de auditoria com INSERT**, e não “zero triggers de INSERT no ecossistema”.

### Matriz de evidências e decisão
| Objeto | Fingerprint lógico de catálogo | Estado | Delta | Próxima ação |
|---|---|---|---|---|
| `cko_governance.change_audit_ledger` | schema/table + freeze UPDATE/DELETE/TRUNCATE | PASS_CATALOG / HOLD_SEMANTIC | nenhum evento INSERT comprovado | examinar funções escritoras e cobertura de eventos |
| `cko_governance.controlled_artifacts` | trigger `cko_guard_pilot_promotion`, INSERT/UPDATE | PASS_CATALOG | controle de promoção identificado | ler definição e verificar efeito real |
| `cko_orch.proposals` | `trg_cko_orch_proposal_authority_guard` + `trg_cko_orch_proposal_governance`, INSERT | PASS_CATALOG | dois guards de proposta | verificar rastreabilidade sem presumir auditoria |
| `cko_validation.findings` | `cko_enqueue_material_finding_learning` + `cko_route_material_finding_super`, INSERT/UPDATE | PASS_CATALOG | rotas de achados identificadas | verificar dados e minimização LGPD |
| `public.ce_tool_audit` (candidato) | SQL candidato previamente identificado, blob `aa736b0d0f1d3487326d77f346e9f710d032346a` | HOLD_SEMANTIC | equivalência não comprovada | matriz CREATE/APPROVE/PUBLISH/REVOKE e retenção |

### Gates
- PASS: consulta física SELECT; inventário incremental de triggers não pertencentes à função de auditoria.
- NOT_RUN: Python, TypeScript, CI, testes negativos de RLS, testes dinâmicos.
- HOLD_SEMANTIC: cobertura de INSERT/publicação/revogação e reutilização do ledger.
- HOLD_PRIVACY: payload JSONB e minimização.
- HOLD_HUMAN: migrations, publicação, homologação clínica/jurídica.
- 0/24 ferramentas homologadas; 0/2 SQL candidatos executados.

Próximo trabalho independente: ler `pg_get_functiondef` dos guards de promoção e governança, confrontar com rotas editoriais; manter fail-closed. Não declarar percentual global sem denominador de critérios homologados.
