# WO — Controle de alterações CKO: ACL e RLS (2026-11-16 16:50 BRT)

## Origem / delta
- Projeto físico exclusivo: Supabase Calculadoras-Smart `pgsybzggewhinaniybiy`; consultas SELECT ao catálogo PostgreSQL.
- Branch de auditoria `audit/ce-supabase-migration-first-20261115`, comparada à `main` `e0f62491b104f4a97c6025a6393cabc2e7ada30e`: 47 commits ahead, 0 behind antes deste checkpoint.
- Checkpoint anterior: `WO_20261116_1549_DDL_AUTHORIZATION_CHAIN.md`, blob SHA `576add8e0fde04b417ca5077a0bc87bbc8787ad6`.
- Fingerprint lógico da nova consulta: project_id + schema `cko_governance` + relações `change_control_state`, `change_requests` + `pg_class.relacl/relrowsecurity/relforcerowsecurity`, `pg_policy`, `has_schema_privilege`, `has_table_privilege`. Fingerprint lógico não é hash criptográfico; resultado de consulta desta rodada.

## Resultado físico — novo delta
| Objeto | Owner (checkpoint anterior) | RLS | FORCE RLS | ACL explícita | Políticas | anon/auth USAGE schema | anon/auth privilégio SELECT/INSERT/UPDATE/DELETE |
|---|---|---|---|---|---:|---|---|
| `cko_governance.change_control_state` | postgres | off | off | NULL | 0 | false/false | false/false |
| `cko_governance.change_requests` | postgres | off | off | NULL | 0 | false/false | false/false |

- A consulta adicional individual de UPDATE também retornou false para ambos os papéis nas duas relações.
- **PASS limitado:** 2/2 relações sem privilégios efetivos examinados para `anon` e `authenticated`; não há acesso direto demonstrado para esses papéis.
- **HOLD_SECURITY:** RLS desabilitado em 2/2, sem que isso sozinho prove exposição; não foram verificados todos os papéis, memberships, funções invocadoras, privilégios do owner, APIs ou a capacidade de alterar o GUC `cko.change_request_id` e o estado `destructive_writes_blocked`.
- Não concluir que o atalho `destructive_writes_blocked=false` seja explorável sem rastrear os caminhos administrativos de alteração.

## Registro de objetos e programa
| Unidade | Denominador | Cobertura/aceite | Estado | Próxima ação |
|---|---:|---|---|---|
| ACL/RLS das 2 tabelas de change control | 2 | 2/2 inventariadas | PASS inventário; HOLD_SECURITY autorização ponta a ponta | Identificar papéis de serviço e funções com escrita |
| Segurança completa da cadeia DDL | 3 funções | 0/3 homologadas | HOLD_SECURITY | Testes negativos isolados e revisão GUC |
| Relações físicas | 678 | 678/678 contagem de checkpoint anterior | PASS quantitativo | Comparar semântica de PK/FK |
| Ferramentas clínicas | 24 | 0/24 homologadas | HOLD_HUMAN | Validar contratos/testes e evidência clínica |
| Contratos | 20 | 0/20 homologados | HOLD_VERIFY | CI dos parsers |
| CI nesta rodada | sem suíte executada | 0 executados | NOT_RUN | Executar suíte após revisão de branch |
| Percentual global | denominador de critérios de aceite não consolidado | não aferível | HOLD_METRICS | Definir matriz de aceite ponderada |

## Riscos, controles e rollback
- Consultas somente SELECT; nenhum DDL/DML, migration, seed, alteração de ACL ou merge.
- Este checkpoint é documental; rollback: reverter somente seu commit se necessário.
- Não promover candidatos. Preservar fail-closed, LGPD, direitos autorais, proveniência, gates clínicos/jurídicos e segurança.
- Próxima tarefa independente: confrontar branches das 24 ferramentas e parsers com SQL candidato, sem reprocessar fingerprints validados; priorizar correções funcionais com testes e CI.
