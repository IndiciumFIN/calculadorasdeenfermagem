# WO 2026-11-16 17:51 — Matriz administrativa de ACL (somente leitura)

## Escopo e origem
Projeto físico Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; consulta direta a `pg_class`, `pg_namespace`, `pg_roles` e `has_table_privilege` em 2026-11-16. PR #73 observada aberta e draft. Continuidade do checkpoint `93aeb6a9e2a20cf6d4517fad0b0ff5ce36a34519` informado na rodada anterior; SHA atual da head não recuperado nesta execução. Fingerprint lógico desta consulta: `cko_governance/{change_control_state,change_requests}:roles[anon,authenticated,dashboard_user,postgres,service_role,supabase_admin]:SELECT,UPDATE,INSERT,DELETE:20261116`. Não é hash criptográfico do banco.

## Resultado físico
Duas tabelas `change_control_state` e `change_requests`, proprietário postgres, RLS desabilitado. Para ambas: `anon`, `authenticated`, `dashboard_user` e `service_role` sem SELECT/UPDATE/INSERT/DELETE efetivos; `postgres` e `supabase_admin` com todos os quatro privilégios. 12 combinações tabela/papel, 48 verificações de privilégio; 48/48 respostas de catálogo coletadas (PASS_INVENTORY). Não significa homologação da cadeia administrativa nem exposição API. Nenhuma linha de negócio foi consultada.

## Registro persistente de delta e gates
- Objeto: `cko_governance.change_control_state`; branch `audit/ce-supabase-migration-first-20261115`; estado PASS_INVENTORY / HOLD_SECURITY; risco: alteração administrativa de `destructive_writes_blocked`; delta: ampliação da matriz de 2 papéis para 6; próximo: auditar funções e concessões indiretas; aceite: provar cadeia de alteração e proteção com testes isolados.
- Objeto: `cko_governance.change_requests`; mesmo branch e estados; risco: manipulação de aprovação; delta: seis papéis; próximo: dependências de funções invocadoras; aceite: autorização efetiva comprovada.
- GitHub PR #73: OPEN/DRAFT observado; merge HOLD; branch SHA atual NOT_VERIFIED; próximo: conferir head e CI.
- Ferramentas: 0/24 homologadas (último checkpoint, não reavaliadas); contratos: 0/20 homologados (último checkpoint); relações físicas: 678/678 inventariadas anteriormente, sem reconciliação semântica nova. Global: não aferível por ausência de denominador de critérios de aceite.

## Testes e ações
- PASS: consultas SELECT de metadados, 12/12 pares papel/tabela e 48/48 respostas de privilégio.
- NOT_RUN: testes dinâmicos de autorização, CI, integração de parsers e ferramentas.
- HOLD_SECURITY: cadeia `SECURITY DEFINER`, invocação indireta e autorização de administrador.
- HOLD_HUMAN: publicação clínica/jurídica, migrations e merges bloqueados.
- Mudança: somente documento; sem DDL/DML, seeds, alterações de ACL ou merge. Rollback documental: reverter este commit; nenhuma reversão de banco necessária.
