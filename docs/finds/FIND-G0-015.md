# FIND-G0-015 — Planning stops despite independent tasks remaining

**Status:** OPEN
**Severidade:** HIGH
**Data:** 2026-10-17
**Origem:** inspeção estática GitHub, branch fix/ce05-kernel-ci-security-20261017

## Evidência
Arquivo: `contracts/wo/WO-G0-CORRECTIVE-20261017.json` (blob SHA `32f61923573e8b41f9a452a6a406155eccb4c650`).

## Falha
Planning stops despite independent tasks remaining. Evidência estática; impacto em runtime ainda requer teste isolado.

## Correção e teste obrigatório
Add per-task blocked status and continue independent preflight work; log every halt.

## Cadeia de governança
Política aplicável/ajuste controlado → validador e testes → tarefa homologada → WO no GitHub → admissão pelo Kernel vinculada ao blob SHA → execução isolada → testes → auditoria independente → fechamento.

## Estado de execução
**HOLD_HUMAN para mutações dependentes da WO não admitida.** Inspeção, preparação e testes locais independentes continuam permitidos. Sem alegação de fechamento.

## Lições aprendidas
Não confundir presença de contrato com enforcement, nem bloqueio de uma tarefa com paralisação do plano.
