# FIND-G0-013 — Policy registry silently skips malformed policy files

**Status:** OPEN
**Severidade:** HIGH
**Data:** 2026-10-17
**Origem:** inspeção estática GitHub, branch fix/ce05-kernel-ci-security-20261017

## Evidência
Arquivo: `packages/cli/kernel/policy_registry.py` (blob SHA `041bfaf4151effd05de7cb33a5458a53a2ab04af`).

## Falha
Policy registry silently skips malformed policy files. Evidência estática; impacto em runtime ainda requer teste isolado.

## Correção e teste obrigatório
Emit deterministic load errors, fail closed, test invalid JSON and duplicate IDs.

## Cadeia de governança
Política aplicável/ajuste controlado → validador e testes → tarefa homologada → WO no GitHub → admissão pelo Kernel vinculada ao blob SHA → execução isolada → testes → auditoria independente → fechamento.

## Estado de execução
**HOLD_HUMAN para mutações dependentes da WO não admitida.** Inspeção, preparação e testes locais independentes continuam permitidos. Sem alegação de fechamento.

## Lições aprendidas
Não confundir presença de contrato com enforcement, nem bloqueio de uma tarefa com paralisação do plano.
