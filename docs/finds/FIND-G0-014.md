# FIND-G0-014 — Kernel gate mutates filesystem during validation

**Status:** OPEN
**Severidade:** HIGH
**Data:** 2026-10-17
**Origem:** inspeção estática GitHub, branch fix/ce05-kernel-ci-security-20261017

## Evidência
Arquivo: `packages/cli/kernel/core.py` (blob SHA `c0f60b5b6f5b61ebc54e05f4b290ddb104e37919`).

## Falha
Kernel gate mutates filesystem during validation. Evidência estática; impacto em runtime ainda requer teste isolado.

## Correção e teste obrigatório
Separate pure validation from directory creation; test no side effects.

## Cadeia de governança
Política aplicável/ajuste controlado → validador e testes → tarefa homologada → WO no GitHub → admissão pelo Kernel vinculada ao blob SHA → execução isolada → testes → auditoria independente → fechamento.

## Estado de execução
**HOLD_HUMAN para mutações dependentes da WO não admitida.** Inspeção, preparação e testes locais independentes continuam permitidos. Sem alegação de fechamento.

## Lições aprendidas
Não confundir presença de contrato com enforcement, nem bloqueio de uma tarefa com paralisação do plano.
