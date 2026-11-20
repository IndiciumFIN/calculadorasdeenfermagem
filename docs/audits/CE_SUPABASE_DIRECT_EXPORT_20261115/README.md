# Extração direta do Supabase CE — cobertura e limitações

**Fonte:** Supabase conectado, projeto `pgsybzggewhinaniybiy`. Executadas exclusivamente consultas `SELECT` contra catálogos PostgreSQL e um subconjunto de tabelas canônicas de referência. **Nenhuma alteração no banco de origem; nenhuma restauração; nenhum Neon.**

## Controle verificável

- Inventariados **59 schemas**, **678 relações** (612 tabelas físicas, 49 views e 17 sequências).
- **7.246 colunas**, **1.996 constraints** (incluindo PK/FK), **1.268 índices**, **100 políticas RLS**.
- **468 rotinas**, **199 triggers de usuário**, **49 views** e **7 extensões**.
- **255 migrations** remotas — versões, número de statements, tamanho e checksum MD5 dos scripts. **Não exportamos o SQL das migrations**, por cautela com segredos incorporados em código legado.
- **1.173 linhas de metadados de referência canônica** em seis tabelas selecionadas, sem copiar registros de pacientes, usuários, credenciais ou blobs de Storage.
- Cada arquivo está no `MANIFEST.json` com número de registros, tamanho em bytes e **hash Git blob SHA-1**, conferidos no GitHub. Execute `python scripts/verify_supabase_snapshot.py` para detectar alterações ou ausência de arquivos. O verificador executa **sem credenciais e sem acesso ao banco**.

**Limitação crítica:** este é um inventário **lógico de metadados com amostras selecionadas de referência**, NÃO um `pg_dump`, NÃO um backup/restauração completos e NÃO uma migração executável. As consultas foram feitas separadamente e **não têm a garantia de consistência de uma única transação/snapshot**. Não inferir equivalência semântica ou segurança por identidade de nomes.

## Controles de segurança observados

O analisador nativo do Supabase informou **245 tabelas com RLS ativo e sem policy (INFO)**; muitas podem estar deliberadamente fechadas, portanto **não criar políticas `USING(true)` para “resolver” o alerta**. Apontou ainda **quatro funções `cko_governance.b5_*_v1` com search_path mutável**, **`pg_net` em `public`** e a proteção contra senhas comprometidas desativada. Evidência em `docs/audits/CE_SUPABASE_SECURITY_ADVISORS_20261115.json`. Todos permanecem como **candidatos à revisão**, sem execução de DDL.

## Controle de conclusão

| Camada | Evidência | Status |
|---|---|---|
| Catálogo de objetos | `relations.json`, `schemas.json` | EXTRACTED |
| Dicionário físico | `columns-*.jsonl` | EXTRACTED; definições de default apenas em hash |
| PK/FK/constraints | `constraints.jsonl` | EXTRACTED |
| Índices | `indexes.jsonl` | EXTRACTED |
| Políticas RLS | `policies.jsonl` | EXTRACTED; revisão de permissões pendente |
| Funções/gatilhos/views | `routines.jsonl`, `triggers.jsonl`, `views.jsonl` | METADATA_EXTRACTED; corpos SQL não incluídos |
| Histórico de migrations | `migrations.json` | METADATA_EXTRACTED; plano de aplicação pendente |
| Objetos de referência CE | `reference/*.jsonl` | LIMITED_METADATA_EXTRACTED |
| Dados completos | Nenhum | **NOT EXPORTED**; risco de dados pessoais e licenças |
| Reconstituição/restore | Nenhum | **NOT TESTED** |
| Crosswalk de duplicidades e adequação | PR #73 | **IN PROGRESS / HOLD** |
| Neon | Não utilizado | **NOT MIGRATED** |

**Critério de conclusão real da migração:** recuperar DDL íntegro, dependências, permissões, dados autorizados e respectivas licenças; comparar com a camada canônica; fazer migração seletiva e teste real de restauração em ambiente isolado, com aprovação `HOLD_HUMAN`.
