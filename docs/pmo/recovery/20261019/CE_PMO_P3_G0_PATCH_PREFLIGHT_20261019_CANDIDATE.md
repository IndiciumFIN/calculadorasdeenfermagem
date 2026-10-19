# P3 / G0 — Preflight de patch e bloqueador de admissão
**Estado:** LOCAL_FIXTURE_TESTED / PRODUCTION_HOLD / DOCUMENTARY_CANDIDATE.

## Fonte e rastreabilidade
- WO de remediação existente `fix/ce05-kernel-ci-security-20261017:contracts/wo/WO-G0-CORRECTIVE-20261017.json`, Git blob `f5743b450e71980086bb1c5d9effd65d5493216c`, `DRAFT_NOT_ADMITTED`; tarefa existente `TASK-G0-B` trata especificamente registry e imports.
- WO CE04 `audit/ce04-reconciliation-tasks-20261017:contracts/wo/WO-CE04-RECON-20261017.candidate.json`, blob `19a37c6563ac0e54026c3dd49770438457f03f4c`, `DRAFT_NOT_ADMITTED`, `admission.status=NOT_REQUESTED`.
- `CE-GOV-WO-ADMISSION-001` permanece política candidata sem homologação, e o validador offline não constitui receipt do Kernel.
- Sources: `main:packages/cli/kernel/core.py` blob `7649f6e1f0160184e1014308cc05c90a5eb659e9`; `main:packages/cli/validators/registry.py` blob `e03e88a0ebe1179448883b7567d59e47193e3bd0`.

## Prova local delimitada
Executada fixture independente em Python 3 com rotina candidata `resolve_validators(module_imports,central_registry)`, sem carregar dependências do Kernel real, alterações de produção ou reconfiguração de paths. Algoritmo: chamar importador explícito, exigir registry não vazio e itens `name -> validator` com método `validate` invocável; devolver cópia ou falhar fechado.

Casos `unittest`: (1) registro válido, (2) registry vazio, (3) objeto sem validate, (4) erro de import propagado, (5) nome não string. **5/5 PASS local**, exit code 0. São testes da fixture isolada, **não** equivalem a 5/5 testes do Kernel integrado.

## Lacunas que impedem implantar
1. Não existe recibo verificável de admissão para as WOs atuais; correção G0 deve reutilizar `TASK-G0-B` em vez de duplicar trabalho.
2. Política e validador de bootstrap ainda não estão comprovadamente homologados; reconciliar dependência circular de CREATE/PRE_APPROVED por autoridade.
3. Falta patch integrado com imports compatíveis, testes do Kernel real, política malformada, SHA calculado de bytes, batch, autorização RBAC, concorrência, idempotência, fencing e CI não permissiva.
4. Auditoria segregada e promoção controlada são posteriores aos testes, sem merge automático.

## Decisão
`GO_LOCAL_PREPARATION`; `NO_GO_PRODUCTION`. Não publicar alterações em `main`, `fix/ce05-...`, Kernel, CI, Supabase ou fontes até admissão correta. PMO 12 tarefas e ordem da cauda inalteradas; preservar FINDs e WOs históricos.
