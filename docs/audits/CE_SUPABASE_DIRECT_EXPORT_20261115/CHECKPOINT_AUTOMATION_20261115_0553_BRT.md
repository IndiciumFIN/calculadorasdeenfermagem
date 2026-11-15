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
