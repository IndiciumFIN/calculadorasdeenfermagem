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
