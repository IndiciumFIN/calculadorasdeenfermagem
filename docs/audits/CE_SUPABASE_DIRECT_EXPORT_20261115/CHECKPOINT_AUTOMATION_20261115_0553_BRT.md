# Checkpoint CE / Supabase — 2026-11-15 05:53 BRT

Estado: READ_ONLY; HOLD_HUMAN para migrations, seeds e publicação. Projeto físico: `pgsybzggewhinaniybiy`. Sem Neon.

## Evidência conferida
- PR #73: https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/73, branch `audit/ce-supabase-migration-first-20261115`, OPEN/DRAFT, mergeable=true (não equivale a aprovação).
- Inventário `MANIFEST.json` (blob `8099e3ff225224eb00e8eb5accd6d8365ddfcf14`): 59 schemas, 612 tabelas, 49 views, 17 sequences = 678 relações, 7.246 colunas, 1.996 constraints, 1.268 índices, 100 RLS policies, 255 migrations; 22 arquivos com hashes.
- SELECT ao PostgreSQL nesta execução: 59 schemas, 661 relações com relkind r/p/v/m e 7.246 colunas. A diferença 678−661=17 é explicada pelas 17 sequences excluídas do SELECT, **não** é drift confirmado.
- PR #71 do workspace: https://github.com/IndiciumFIN/dev-chatgpt-workspace/pull/71 — OPEN/DRAFT; separa build e migrations; sem autorização de deploy.
- Crosswalk PR #73: `public.normatives`, `public.atoms`, `public.calculators`, `public.registry` não existem fisicamente; existem candidatos canônicos distintos e não intercambiáveis. `ce_platform.clinical_evidence_bindings` = 0 linhas no snapshot, bloqueio clínico.
- SQL candidato `supabase/candidates/20261115_ce_tools_governed_candidate.sql` da branch `feat/ce-tools-governed-backend-20261115`, blob `aa736b0d0f1d3487326d77f346e9f710d032346a`; seed `20261115_ce_tools_research_seed_candidate.sql`, blob `fd0f701c7737d3419dd6088216a3381980b1d046`. **Nenhum executado.**

## Achados novos: revisão estática do candidato de ferramentas
1. **HOLD_SECURITY_SCHEMA_DUPLICATION**: seis tabelas novas `public.ce_staff_memberships`, `ce_tool_drafts`, `ce_kernel_grants`, `ce_tool_releases`, `ce_tool_revocations`, `ce_tool_audit` propostas sem crosswalk de entidades com `ce_platform`, `cko_governance` e contratos de identidade. `CREATE TABLE IF NOT EXISTS` não demonstra compatibilidade semântica.
2. **HOLD_SECURITY_ACCESS**: a função `ce_release_guard` é `SECURITY INVOKER`, mas `ce_kernel_grants` não concede leitura a `authenticated`; a publicação depende de papel privilegiado explicitamente autorizado, que não está demonstrado. Validar papel de execução, RLS, grants e privilégio de INSERT em `ce_tool_releases` antes de promover.
3. **HOLD_PRIVACY**: `ce_draft_no_patient_info` apenas exige `payload->>'containsPatientData'='false'`, declaração fornecida pelo próprio payload, não inspeção efetiva de dados pessoais. Não considerar esse CHECK uma proteção LGPD suficiente.
4. **HOLD_SEED_AUTH**: os 24 INSERTs candidatos omitem `authored_by`; a policy de INSERT para `authenticated` exige `authored_by=auth.uid()`. Execução como usuário autenticado comum falharia; não contornar via `service_role` sem WO e evidência.
5. **HOLD_RISK_PUBLICATION**: `ce_tool_publications` expõe `payload` de releases `public`. Exige prova de que o payload está saneado, revisão de campos e de direitos de uso, além da revogação efetiva.
6. **PASS_BOUNDARY**: o seed permanece `candidate`, e não existe endpoint de publicação neste patch; manter esse isolamento.

## Plano técnico incremental e critérios
- P0: derivar matriz entidade/coluna/PK/FK/policy entre candidato e banco físico, por catálogo SELECT; classificar REUSE, EXTEND, NEW_ONLY_IF_PROVEN, HOLD.
- P1: reescrever candidato para reutilização do modelo canônico (não implantar seis tabelas `public` por padrão); preservar imutabilidade, revogação e trilha de auditoria.
- P2: testes negativos com RLS, usuários anon/authenticated/service controlado, inserts sem autoria, payload com dados pessoais, revogação e hashes; isolamento em banco descartável.
- P3: revisar fontes primárias, licenças, direitos e evidências clínicas por ferramenta; manter HOLD até homologação.
- P4: merge e migração só após CI PASS, diff semântico, rollback idempotente e autorização específica.

## Registro incremental de cobertura
| Artefato | Fingerprint Git | Resultado | Próxima ação |
|---|---|---|---|
| PR73/MANIFEST.json | 8099e3ff225224eb00e8eb5accd6d8365ddfcf14 | PASS_METADATA | verificar hashes dos 22 arquivos em CI |
| PR73/crosswalk | f78fea4f6f599aafd6502de34ce64cd6604e8b11 | HOLD_SEMANTIC | validar equivalências por coluna/FK |
| PR73/README | a0e074bf9da401a3d50dd761536bcad3a9b96150 | PASS_SCOPE | manter exclusões e limitações |
| ce-tools/governed SQL | aa736b0d0f1d3487326d77f346e9f710d032346a | HOLD_SECURITY | corrigir esquema e acesso |
| ce-tools/seed SQL | fd0f701c7737d3419dd6088216a3381980b1d046 | HOLD_AUTH | ajustar contrato de autoria |
| workspace PR71 | PR #71 | HOLD_DEPLOY | CI + preview e rotas |

**Progresso verificável desta rodada:** 3/3 metadados centrais da PR #73 lidos (manifest, readme, crosswalk); 2/2 SQL candidatos lidos; 0/2 migrations/seeds aplicados (intencional); 0/24 ferramentas homologadas nesta rodada. Nenhuma mudança no banco. O inventário físico não é backup completo.


## Incremento 2026-11-15 06:52 BRT — segurança de entrada, somente código
- **PASS_COMMIT**: branch `feat/ce-tools-governed-backend-20261115`, commit [8486daa008ef0332330b55d83de3b6e42715093a](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/8486daa008ef0332330b55d83de3b6e42715093a), arquivo `src/lib/ce-tools/security.ts`, blob `f29df94731edd81feed30d19fa9a29c65cb4049a` (anterior `22028c82b17d17be6790f2579da7127e8088fa29`).
- Endurecimento de requisições mutáveis: rejeitar origem HTTP em `NODE_ENV=production`, rejeitar credenciais na URL de Origin, rejeitar Content-Length não decimal ou acima de `Number.MAX_SAFE_INTEGER`; limite de 40.000 bytes permanece. Ausência de Content-Length segue permitida para transporte chunked, **sem substituir limite real de leitura do body**.
- **PASS_STATIC**: revisão textual das três novas condições após escrita; **NOT_RUN**: testes unitários, TypeScript, CI e integração, não reivindicar validação dinâmica.
- **PASS_DB_READONLY**: catálogo PostgreSQL SELECT confirmou `ce_platform.clinical_tools`, `ce_platform.tool_profiles`, `ce_platform.community_memberships`, `cko_governance.md_tool_registry_v2_candidate` e `cko_governance.md_tool_field_contract_v2_candidate`. As seis tabelas `public.ce_*` propostas não apareceram no filtro do catálogo; **HOLD_SEMANTIC** para crosswalk, não inferir equivalência apenas pelo nome.
- **PR_STATUS**: PR #73 OPEN/DRAFT head `198cdff96f38b16f72f9e94c239c231e1024f3e7`; workspace PR #71 OPEN/DRAFT head `1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d`. `mergeable=true` não libera promoção.
- **HOLD_HUMAN**: 2/2 SQL candidatos não aplicados; 0/24 ferramentas homologadas nesta rodada. Nenhum DDL/DML nem merge realizado. Próxima ação: testes de origem e Content-Length, proteção de tamanho real do body, crosswalk PK/FK e testes negativos de RLS antes de qualquer migração.

## Incremento 2026-11-15 07:52 BRT — autorização de escrita e crosswalk de colunas

- **PASS_COMMIT**: branch `feat/ce-tools-governed-backend-20261115`, PATCH `src/app/api/admin/ferramentas/[key]/route.ts`, commit [3be097cae91a15d646dea48b6a37bfeb178d6410](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/3be097cae91a15d646dea48b6a37bfeb178d6410), blob `022dd6027994aacce32e6c2fcbd196f1060abd01`. O endpoint agora nega explicitamente o papel auditor; somente admin/editor podem editar.
- **PASS_COMMIT**: transição para revisão `src/app/api/admin/ferramentas/[key]/enviar-revisao/route.ts`, commit [6f56be0f8ea9c7d0973f3fbdd1ceae57eb5db1ef](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/6f56be0f8ea9c7d0973f3fbdd1ceae57eb5db1ef), blob `348ecf2839fc2750388172d2d1c8c61736bfbbdc`. Somente admin/editor podem solicitar revisão.
- **PASS_COMMIT**: teste estático de regressão em `tests/test_governed_tools.py`, commit [c43e349dce8b752b1da549989469ac177a209948](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/c43e349dce8b752b1da549989469ac177a209948), blob `dc1890fd0cc740385d7dde0e3948e595ec1bb804`. Verifica os três endpoints mutáveis para restrição admin/editor e verificação de origem.
- **PASS_DB_READONLY**: SELECT no catálogo de `pgsybzggewhinaniybiy` retornou 71 colunas físicas de cinco entidades existentes: `ce_platform.clinical_tools` (8), `ce_platform.tool_profiles` (7), `ce_platform.community_memberships` (5), `cko_governance.md_tool_field_contract_v2_candidate` (36), `cko_governance.md_tool_registry_v2_candidate` (15). Essas entidades cobrem capacidades, perfis, vínculos comunitários e contratos de campos, mas **não comprovam equivalência** com drafts/grants/releases/revocations/audit propostos. Classificação: REUSE_CANDIDATE para catálogo e contrato; HOLD_SEMANTIC para identidade editorial e ciclo de publicação.
- **PASS_STATIC**: alterações de código verificadas por leitura do conteúdo; **NOT_RUN**: testes Python/TS/CI e RLS negativos em execução real. Não afirmar PASS dinâmico.
- **HOLD_HUMAN**: 0/2 SQL candidato/seed executado; 0/24 ferramentas homologadas; 0 migrations e 0 merges. PR #73 e PR #71 seguem OPEN/DRAFT. Próxima ação: testar novos guards em CI, completar PK/FK e RLS crosswalk, corrigir limite real de body e plano de migração sem duplicações.

### Registro incremental 07:52
| Artefato | Fingerprint Git | Estado | Próxima ação |
|---|---|---|---|
| PATCH ferramentas | 022dd6027994aacce32e6c2fcbd196f1060abd01 | PASS_STATIC | testes de role negativo |
| POST enviar revisão | 348ecf2839fc2750388172d2d1c8c61736bfbbdc | PASS_STATIC | testes de role negativo |
| tests/test_governed_tools.py | dc1890fd0cc740385d7dde0e3948e595ec1bb804 | COMMITTED_NOT_RUN | CI Python |
| 5 tabelas físicas do catálogo | 71 colunas via SELECT | PASS_INVENTORY | PK/FK, RLS e equivalência semântica |

## Incremento 2026-11-15 08:55 BRT — limite real do corpo e PK/FK/RLS

- **PASS_COMMIT**: `src/lib/ce-tools/security.ts` implementa `readBoundedJson` que lê o stream em blocos e rejeita o corpo real acima de 40.000 bytes mesmo sem `Content-Length` ou com cabeçalho incorreto. Commit [8349404c4e855b5d40470510aaf11fe76eaa0d52](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/8349404c4e855b5d40470510aaf11fe76eaa0d52), blob `d949fb50d8908e71c0b38b09101ab90a7d5f110e`.
- **PASS_COMMIT**: POST e PATCH de drafts passaram a utilizar o leitor limitado e a devolver HTTP 413 no estouro: [0c1e1b96ecad37f3afc83b48e235ca70c8e501db](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/0c1e1b96ecad37f3afc83b48e235ca70c8e501db), [daa49427a5e3e09274e888a0051b786f53afe402](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/daa49427a5e3e09274e888a0051b786f53afe402).
- **PASS_COMMIT**: novo teste estático de regressão de limite real, uso do leitor e retorno 413: [8fff20815a52af80cedef791130846f4beccd9ee](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/8fff20815a52af80cedef791130846f4beccd9ee), blob `26bf23c0447348ee4d96c90ae7c47efbc560cb39`. **NOT_RUN**: Python, TypeScript, testes dinâmicos de streaming e CI; não há PASS dinâmico.
- **PASS_DB_READONLY**: SELECT no catálogo físico confirmou PK/FK e RLS: `ce_platform.clinical_tools` PK `canonical_id`, FK para `canonical_objects`, RLS true, sem policy listada; `ce_platform.tool_profiles` PK `canonical_id`, FKs `canonical_objects` e `domains`, RLS true, sem policy listada; `ce_platform.community_memberships` PK `(space_id,user_id)`, FKs `community_spaces` e `auth.users`, RLS true, policy SELECT `community_memberships_own`. `cko_governance.md_tool_registry_v2_candidate` PK `tool_slug`, sem FK e RLS false; `md_tool_field_contract_v2_candidate` PK `field_id`, sem FK e RLS false. Estas duas últimas são **candidatas internas**, não autorizar exposição API.
- **HOLD_SEMANTIC**: as cinco entidades não comprovam substituição de drafts, grants, releases, revocations e audit. **HOLD_SECURITY**: ainda faltam testes negativos de RLS, autorização real, avaliação do acesso aos schemas candidatos, revisão clínica/jurídica e estratégia de migration sem duplicações.
- **HOLD_HUMAN**: 0/2 SQL/seed aplicados; 0/24 ferramentas homologadas; 0 merges. Nenhuma alteração no Supabase. Próximo passo: testes dinâmicos de streaming, CI e crosswalk detalhado por objeto.

## Incremento 2026-11-15 09:56 BRT — MIME JSON e reuso de auditoria

- **PASS_COMMIT**: branch `feat/ce-tools-governed-backend-20261115`, commit [d04e56f0a91f39c63618353963618161b2799a05](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/d04e56f0a91f39c63618353963618161b2799a05), `src/lib/ce-tools/security.ts`, blob `2a111d35dc0ae1c8d748281e2480d97a3f69760d`. Corrige a aceitação permissiva de `application/json-malicious` e de charset não suportado: agora aceita `application/json` e parâmetro UTF-8 explícito, rejeitando outras variantes.
- **PASS_COMMIT**: [fbf17c3af7fbb9e4e672cc4ce904b72b745eed73](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/fbf17c3af7fbb9e4e672cc4ce904b72b745eed73), `tests/test_governed_tools.py`, blob `afbe8037fe70e369bd435552ad7dd3d5f08a212e`. Adiciona teste estático de regressão contra `startsWith('application/json')`. **NOT_RUN**: teste Python, teste dinâmico MIME, CI/TypeScript; commit não significa aprovação.
- **PASS_DB_READONLY**: consulta ao catálogo PostgreSQL confirmou 8 tabelas relevantes ao filtro de ferramentas/auditoria: `ce_platform.clinical_tools` e `tool_profiles` com RLS habilitado e 0 policies; seis em `cko_governance` com RLS desabilitado e 0 policies: `change_audit_ledger`, `md_tool_field_contract_v2_candidate`, `md_tool_layer_applicability_v1_candidate`, `md_tool_layer_applicability_v2_candidate`, `md_tool_registry_v2_candidate`, `md_tool_universe_crosswalk_v2_candidate`. A presença de `cko_governance.change_audit_ledger` (colunas `old_hash,new_hash,old_data,new_data,actor,txid`) é nova candidata concreta a **REUSE_AUDIT**, sem equivalência funcional comprovada; requer revisar cobertura, sensibilidade e isolamento de schema.
- **HOLD_SECURITY**: não expor os seis objetos de `cko_governance` na API sem políticas de acesso adequadas; RLS desabilitado em schema interno não demonstra exposição pública. `ce_platform` com RLS true e 0 policies pode ser intencionalmente deny-by-default; não abrir acesso sem contrato.
- **HOLD_HUMAN**: 0/2 SQL candidatos/seed aplicados; 0/24 ferramentas homologadas; 0 merges. Sem alteração de banco. Próxima ação: testes dinâmicos de MIME/body e análise de `change_audit_ledger` versus `ce_tool_audit`, matriz de grants e direitos de publicação.

## Incremento 2026-11-15 10:53 BRT — charset estrito e crosswalk de auditoria

- **PASS_COMMIT**: corrigido o regex do charset em `src/lib/ce-tools/security.ts` para aceitar `utf-8` ou `"utf-8"` com aspas balanceadas, rejeitando formas com aspas abertas/fechadas isoladamente. Commit [457f28317bc5c8608e20073545884cbe051398c8](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/457f28317bc5c8608e20073545884cbe051398c8); blob `c99056e712d8b1dc2c1f0af812f8a4191b8620d8`.
- **PASS_COMMIT**: teste estático de regressão no `tests/test_governed_tools.py` para o padrão estrito. Commit [eefe5f1c3f0cba4d8a2a580b063a5a60ad068ee1](https://github.com/IndiciumFIN/calculadorasdeenfermagem/commit/eefe5f1c3f0cba4d8a2a580b063a5a60ad068ee1); blob `b0350bbb14f3e6b70187d1f0eb4e55994de7ebc9`.
- **PASS_DB_READONLY**: `SELECT` ao catálogo físico confirmou 14 colunas de `cko_governance.change_audit_ledger`, 8 de `ce_platform.clinical_tools` e 7 de `ce_platform.tool_profiles` (29/29 colunas dos três objetos). O ledger inclui `audit_uuid`, `change_request_id`, `schema_name`, `table_name`, `operation`, `row_identity`, `old_hash`, `new_hash`, `old_data`, `new_data`, `actor`, `session_actor`, `txid`, `changed_at`.
- **HOLD_SEMANTIC**: o ledger físico oferece auditoria genérica de mutações, mas a mera existência de colunas de hash/identidade não demonstra semântica de eventos de publicação, revogação, autorização ou retenção; não substituir `ce_tool_audit` automaticamente. Avaliar regras de escrita, grants, políticas, triggers e minimização LGPD antes de decidir REUSE/EXTEND.
- **NOT_RUN**: testes dinâmicos Python/TypeScript, CI e RLS negativo; commits são verificáveis, mas não constituem aprovação de deploy. **HOLD_HUMAN**: 0/2 SQL candidatos executados, 0/24 ferramentas homologadas, 0 migrations, 0 merges. Supabase sem alterações.
- **Próxima ação**: executar testes negativos MIME/streaming e inspeção de triggers/grants/constraints do ledger por catálogo SELECT; comparar com `ce_tool_audit` por evento e não somente por campos.

### Fingerprints incrementais 10:53
| Objeto | Fingerprint | Status | Próxima ação |
|---|---|---|---|
| src/lib/ce-tools/security.ts | c99056e712d8b1dc2c1f0af812f8a4191b8620d8 | COMMITTED_NOT_RUN | teste MIME dinâmico |
| tests/test_governed_tools.py | b0350bbb14f3e6b70187d1f0eb4e55994de7ebc9 | COMMITTED_NOT_RUN | Python CI |
| cko_governance.change_audit_ledger | 14 colunas catálogo 2026-11-15 | REUSE_CANDIDATE_HOLD | grants/triggers e semântica |
| ce_platform.clinical_tools | 8 colunas catálogo 2026-11-15 | REUSE_CANDIDATE | cruzamento ferramenta |
| ce_platform.tool_profiles | 7 colunas catálogo 2026-11-15 | REUSE_CANDIDATE | cruzamento perfil |

## Incremento 2026-11-15 11:50 BRT — ledger append-only: restrições e permissões reais

- **PASS_PR_READ**: PR #73 OPEN/DRAFT, head `ef787f1d0d244a0d340490aca76ca805ec3cb709`, base `e0f62491b104f4a97c6025a6393cabc2e7ada30e`, `mergeable=true` (não é aprovação). Inspeção de 32 arquivos listados na PR, incluindo inventário, crosswalk, políticas e testes.
- **PASS_DB_READONLY**: consulta de catálogo `pg_trigger`, `pg_constraint`, `information_schema.role_table_grants` e `pg_proc` de `cko_governance.change_audit_ledger`. PK `audit_uuid`. Dois triggers de bloqueio: `cko_freeze_change_audit_ledger_ud` (BEFORE UPDATE/DELETE) e `cko_freeze_change_audit_ledger_tr` (BEFORE TRUNCATE). Ambos chamam `cko_governance.freeze_change_audit_ledger()`, que levanta SQLSTATE `42501` e impede essas operações; `search_path` da função fixado em `pg_catalog, cko_governance`. Isto confirma proteção append-only **no caminho de DML normal**, não proteção contra proprietário/superusuário que altere objetos.
- **PASS_DB_GRANTS**: `information_schema.role_table_grants` retornou somente `postgres` para SELECT/INSERT/UPDATE/DELETE/TRIGGER/TRUNCATE/REFERENCES sobre esse ledger. Não foram encontrados grants diretos para `anon` ou `authenticated` nesta consulta. Não concluir que todos os papéis efetivos estão excluídos sem análise de herança, schema USAGE e funções SECURITY DEFINER.
- **HOLD_SEMANTIC**: ledger é candidato a reaproveitamento para trilha de mutações, mas a ausência de trigger INSERT próprio e o escopo genérico `schema_name/table_name/operation` não comprovam eventos de publicação, revogação e revisão independentes. Não criar ponte de escrita nem eliminar `ce_tool_audit` por equivalência nominal. Analisar caminhos de inserção, minimização de `old_data/new_data`, retenção e vínculo WO/grant.
- **HOLD_CANDIDATE**: SQL candidato `aa736b0d0f1d3487326d77f346e9f710d032346a` continua a criar seis tabelas `public.ce_*` sem reconciliação completa; 24 seeds não aplicados. Nenhum SQL DDL/DML, merge ou deploy executado.
- **NOT_RUN**: Python, TS, CI, testes dinâmicos MIME/streaming, RLS negativo. Não inferir aprovação a partir da leitura do catálogo.
- **Próximo incremento**: mapear quem insere no ledger (dependências de funções/triggers) e a equivalência por evento; implementar teste dinâmico de request body/charset no código da branch candidata e executar CI. Só propor migração com rollback, RLS e autorização.

### Cobertura incremental 11:50
| Objeto | Evidência | Estado | Próxima ação |
|---|---|---|---|
| `cko_governance.change_audit_ledger` | PK + 2 triggers + função `freeze_change_audit_ledger()` + grants do catálogo | PASS_APPEND_ONLY_METADATA / HOLD_REUSE | mapear escritores e herança de grants |
| PR #73 | head `ef787f1`; OPEN/DRAFT; arquivos listados | PASS_STATUS / HOLD_MERGE | CI e revisão |
| `public.ce_tool_audit` | SQL candidato `aa736b0` (não aplicado) | HOLD_SEMANTIC | matriz por evento |
| Ferramentas de pesquisa | 24/24 candidatas, 0/24 homologadas | HOLD_HUMAN | evidências clínicas/licenças |


## Incremento 2026-11-15 12:49 BRT — escritores reais do ledger e risco LGPD

- **PASS_PR_READ**: PR #73 OPEN/DRAFT, head `aa261d579961d8be4ca835fd205661fa914877ab`, base `e0f62491b104f4a97c6025a6393cabc2e7ada30e`; PR workspace #71 OPEN/DRAFT, head `1976da6bf8cbb13a6547e2d7deed6ff3674f1d4d`. Nenhuma promoção autorizada.
- **PASS_DB_READONLY**: catálogo `pg_proc.prosrc` identifica `cko_governance.audit_protected_row_change()` como escritor efetivo de `cko_governance.change_audit_ledger`; função `SECURITY DEFINER`. Usa `TG_OP`, `TG_TABLE_SCHEMA`, `TG_TABLE_NAME`, `cko.change_request_id` e hashes SHA-256. Faz INSERT no ledger após UPDATE/DELETE de tabelas protegidas.
- **PASS_DB_READONLY**: `pg_trigger` confirmou triggers `AFTER DELETE OR UPDATE` em objetos `cko_ai`, `cko_evidence`, `cko_governance`, `cko_master` e `cko_regulatory` (entre outros); o escritor **não** cobre INSERT nem eventos de publicação/revogação como eventos próprios. O resultado observado contém pelo menos 40 triggers; o levantamento retornou amostra limitada e não é censo de cobertura.
- **HOLD_PRIVACY_HIGH**: o escritor serializa `OLD` e `NEW` integralmente para `old_data/new_data`, com exceção de `cko_evidence.snapshots.content_text`, que é retirado dos JSONs armazenados. Os hashes continuam calculados sobre o JSON completo. Isso exige inventário de campos pessoais/sensíveis, minimização, retenção, acesso e revisão LGPD antes de reutilização para ferramentas; **não copiar payloads de pacientes nem conceder leitura pública do ledger**.
- **HOLD_EVENT_EQUIVALENCE**: o ledger comprova auditoria técnica de UPDATE/DELETE, mas não comprova auditoria de INSERT, criação de draft, autorização, revisão, publicação ou revogação. Portanto, não substituir `ce_tool_audit` sem matriz de eventos, desenho de extensão segura e testes negativos.
- **NOT_RUN**: testes Python, TS, CI, integração RLS e testes dinâmicos MIME/streaming. Consulta inicial com `pg_get_functiondef` no predicado falhou (SQLSTATE 42809); consulta corrigida para `pg_proc.prosrc` e executada com sucesso. Nenhuma migration, seed, DML, DDL, merge ou deploy.
- **Próxima ação**: contar integralmente triggers por schema e mapear tabelas sem auditoria; conferir `SECURITY DEFINER` owner/search_path/EXECUTE grants e política de retenção; desenvolver testes dinâmicos no branch de ferramentas, sem promover SQL candidato.

### Registro incremental 12:49
| Objeto | Evidência | Estado | Próxima ação |
|---|---|---|---|
| `cko_governance.audit_protected_row_change()` | `pg_proc.prosrc`, `prosecdef=true` | PASS_WRITER_IDENTIFIED / HOLD_PRIVACY | revisar search_path, ownership, grants |
| `cko_governance.change_audit_ledger` | INSERT pela função de trigger; UPDATE/DELETE das fontes | REUSE_PARTIAL_HOLD | matriz por evento + minimização LGPD |
| PR #73 | head `aa261d579961d8be4ca835fd205661fa914877ab` antes deste checkpoint | OPEN_DRAFT | testes/CI + correções |
