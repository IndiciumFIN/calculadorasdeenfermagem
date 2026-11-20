# CE / NCOS — checkpoint incremental 2026-11-15 13:55 BRT

## Escopo e proveniência
- Projeto consultado exclusivamente em modo SELECT: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`.
- PR #73 OPEN/DRAFT, head observado `cb7c6d8ec422ed5136936fe81913acb5b7fd1b35` antes deste commit.
- Continuar do checkpoint acumulado `CHECKPOINT_AUTOMATION_20261115_0553_BRT.md`; não substituir nem recalcular snapshots antigos.
- Esta rodada investigou especificamente a função `cko_governance.audit_protected_row_change()` e sua superfície de autorização; não executou DDL/DML nem tests de roles reais.

## Evidência SQL somente leitura
Consulta a `pg_proc`, `pg_namespace`, `pg_get_functiondef`, `has_function_privilege`, `has_schema_privilege`, `has_table_privilege`:
- `SECURITY DEFINER = true`, owner `postgres`, `proconfig = {search_path=pg_catalog, cko_governance, extensions}`; search_path explícito limita risco de resolução dinâmica.
- `proacl IS NULL` (privilégios padrão): `has_function_privilege('anon', oid, 'EXECUTE') = true` e `has_function_privilege('authenticated', oid, 'EXECUTE') = true`.
- Contudo, `has_schema_privilege('anon'/'authenticated','cko_governance','USAGE') = false`; `has_table_privilege(...,'change_audit_ledger','INSERT') = false` para ambos. **Não interpretar EXECUTE isolado como exposição remota explorável**: função é `RETURNS trigger`, não invocável diretamente como função comum, e schema não é utilizável por esses papéis.
- O corpo grava `old_data` e `new_data` completos como JSONB em UPDATE/DELETE (exceto `content_text` de `cko_evidence.snapshots`), com hash SHA-256 e `change_request_id` de setting. Não grava INSERT. `TG_OP` controla retorno OLD/NEW.
- Não há evidência de que o ledger cubra publicação, revogação ou aprovação editorial. Classificação: `HOLD_SEMANTIC`, `HOLD_PRIVACY`.

## Decisão e controles
- `PASS_DB_READONLY`: função, owner, proconfig, ACL efetiva e grants de schema/tabela inspecionados.
- `HOLD_SECURITY_REVIEW`: verificar grants indiretos via outros roles, papéis que podem alterar objetos protegidos e políticas de invocação, sem afirmar vulnerabilidade explorável.
- `HOLD_PRIVACY`: revisar minimização de campos JSONB, política de retenção e direitos de acesso antes de reaproveitar ledger para ferramentas.
- `HOLD_SEMANTIC`: não substituir `ce_tool_audit` sem matriz evento-a-evento e identidade editorial; evitar criar tabela duplicada.
- `NOT_RUN`: testes dinâmicos RLS, CI, Python e TypeScript.
- `HOLD_HUMAN`: 0/24 ferramentas homologadas; 0 migrations, 0 seeds, 0 merges, 0 publicações.

## Próxima ação verificável
1. Inspecionar todos os triggers e suas tabelas de origem e cruzar com eventos de INSERT/UPDATE/DELETE.
2. Determinar quais roles efetivamente podem escrever nas tabelas protegidas; simular somente em ambiente descartável.
3. Especificar testes negativos de RLS e política de minimização antes de adaptar o ledger.
4. Continuar correções seguras no código e testes das ferramentas, com commits separados e evidência CI.
