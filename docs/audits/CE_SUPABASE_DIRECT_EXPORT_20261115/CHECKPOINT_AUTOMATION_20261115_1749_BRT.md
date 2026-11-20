# CE / NCOS — checkpoint 2026-11-15 17:49 BRT — WO-CE-GUARD-STATE-11

Projeto físico: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`. Escopo somente SELECT, sem Neon/SOT/WU-TRIB.

## Origem e delta
- Continuação do checkpoint da branch `audit/ce-supabase-migration-first-20261115`, PR #73; último achado registrado: `guard_pilot_baseline_promotion()` e trigger `cko_guard_pilot_promotion`.
- SQL consultado no catálogo: `pg_trigger`, `pg_class`, `pg_namespace`, `pg_get_triggerdef`, `pg_get_functiondef`; objeto `cko_governance.controlled_artifacts`.
- SELECT direto: `cko_governance.change_control_state` retornou exatamente `singleton=true, baseline_promotion_guard=true` (1 linha observada).
- SELECT catálogo: `cko_governance.change_control_state` tem proprietário `postgres`, RLS desabilitada, UPDATE=false para `anon` e `authenticated`. Não equivale a demonstrar ausência de outros papéis privilegiados ou de caminhos SECURITY DEFINER.
- Trigger confirmado: BEFORE INSERT OR UPDATE em `controlled_artifacts`; função SECURITY DEFINER com search_path explícito `pg_catalog, cko_governance`.
- Expressão atual: `upper(new.status) ~ '(ACTIVE|ASSURED|APPROVED|PROMOTED|RELEASED|READY_FOR_RELEASE|CURRENT)'`. Regex não ancorada: valores com substring coincidente também acionam o guard. Não modificar sem inventário de valores canônicos e teste de regressão.

## Gates / riscos
- PASS: estado físico do guard ativo, 1/1 linha de configuração observada; catálogo de privilégios básicos, 2/2 papéis consultados sem UPDATE.
- HOLD_SEMANTIC: sem catálogo aprovado dos status; sem cobertura comprovada de publicação/revogação/INSERT no ledger.
- HOLD_SECURITY: RLS da tabela de estado desabilitada; investigar USAGE, grants de outros papéis, funções SECURITY DEFINER e acesso à API. Sem afirmação de exposição pública.
- HOLD_HUMAN: qualquer alteração de função, migrations, seeds, publicação e merge.
- NOT_RUN: testes negativos dinâmicos, Python, TypeScript, CI.
- Produção: 0 DDL, 0 DML, 0 migrations, 0 seeds; nenhuma tabela concorrente criada.

## Próxima ação incremental
1. Consultar pg_depend/pg_proc/pg_roles para todos os escritores indiretos de `change_control_state`; fingerprint por OID + definição e SHA em inventário versionado.
2. Obter enum/domínio e valores distintos de status de `controlled_artifacts` somente SELECT, com cuidado para não expor conteúdo sensível.
3. Escrever teste de regressão da semântica de status em branch de integração, sem alterar função de produção.
4. Confrontar cobertura do ledger com eventos editoriais, LGPD e RLS; manter HOLD até testes e autorização.

Checkpoint incremental; não substitui inventário global de 59 schemas/678 relações/255 migrations nem constitui homologação das 24 ferramentas.
