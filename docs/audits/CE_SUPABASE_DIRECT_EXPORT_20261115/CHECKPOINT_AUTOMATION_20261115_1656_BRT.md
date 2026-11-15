# CE/CKO/NCOS — checkpoint incremental 2026-11-15 16:56 BRT

Escopo: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`, somente SELECT em catálogos. Sem Neon, SOT ou WU-TRIB. PR #73: https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/73. Referência anterior: commit de22948109e3646da967d17ee1c50c7afa1314b8 (histórico; não presumir head atual).

## WO-CE-20261115-1656 — promoção de baseline CKO

- PASS_DB_READONLY: `pg_proc` identifica `cko_governance.guard_pilot_baseline_promotion()` (SECURITY DEFINER; search_path `pg_catalog, cko_governance`).
- PASS_DB_READONLY: `pg_trigger` identifica exatamente um trigger não interno: `cko_guard_pilot_promotion`, habilitado (`tgenabled=O`), BEFORE INSERT OR UPDATE em `cko_governance.controlled_artifacts`.
- PASS_STATIC_CONTRACT: quando `artifact_class='PILOT_BASELINE'`, status corresponde ao regex de promoção e `baseline_promotion_guard` está ativo, a função exige `current_version_ref`, correspondência em `object_versions`, `schema_refs` não vazio e vínculo normativo ACTIVE da versão. Falhas usam SQLSTATE 23514.
- HOLD_FAIL_CLOSED: o controle é condicional a `change_control_state.baseline_promotion_guard`; não presumir que esteja ativo sem leitura do estado e controle de quem pode alterá-lo.
- HOLD_STATUS_MATCH: regex `(ACTIVE|ASSURED|APPROVED|PROMOTED|RELEASED|READY_FOR_RELEASE|CURRENT)` não está ancorado; pode corresponder a substrings de outros status. Necessário confrontar vocabulário canônico e testar casos negativos.
- HOLD_SEMANTIC: trigger verifica pré-condições de promoção, não demonstra gravação de evento de aprovação, publicação ou revogação no `change_audit_ledger`.
- NOT_RUN: testes dinâmicos/CI, testes negativos RLS, ensaio de rollback e validação clínica/jurídica.

## Registro de cobertura incremental
| Objeto | Fingerprint/identidade | Estado | Próxima ação |
|---|---|---|---|
| `cko_governance.guard_pilot_baseline_promotion()` | assinatura pg_proc, SECURITY DEFINER, search_path explícito | PASS_CATALOG / HOLD_SEMANTIC | revisar enum/status, guard state e privilégios |
| `cko_governance.controlled_artifacts` | trigger `cko_guard_pilot_promotion` enabled O | PASS_CATALOG | verificar grants, RLS e auditoria de INSERT |
| `cko_governance.object_versions` | dependência consultada no corpo da função | HOLD_CROSSWALK | verificar PK/FK e imutabilidade |
| `cko_governance.artifact_normative_bindings` | vínculo ACTIVE exigido | HOLD_CLINICAL | verificar proveniência, licenças e revogação |

## Gate e progresso
Consultas SELECT 3/3 PASS nesta rodada (descoberta de função, definição, trigger). Objetos de promoção examinados 2/2; equivalência editorial homologada 0/1; ferramentas homologadas 0/24. Migrations/seeds/DDL/DML: 0; merges: 0. Não calcular porcentagem global sem denominador de componentes e testes. Próxima WO independente: executar SELECT sobre estado do guard e ACLs; propor testes de status e evento sem implantar SQL candidato. HOLD_HUMAN para produção e publicação.
