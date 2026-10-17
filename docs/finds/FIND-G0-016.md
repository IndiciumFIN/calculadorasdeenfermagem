# FIND-G0-016 — Governance candidate validator fails closed only after local bug fix; not integrated

**Status:** OPEN
**Severidade:** HIGH
**Data:** 2026-10-17
**Origem:** inspeção estática GitHub, branch fix/ce05-kernel-ci-security-20261017

## Evidência
Arquivo: `contracts/policies/CE-GOV-WO-ADMISSION-001.candidate.json` (blob SHA `2567e6c1f9f733042e1097e632f35bf2bde372d9`).

## Falha
Governance candidate validator fails closed only after local bug fix; not integrated. Evidência estática; impacto em runtime ainda requer teste isolado.

## Correção e teste obrigatório
Reproduce local tests, integrate only through admitted WO, record audit and version.

## Cadeia de governança
Política aplicável/ajuste controlado → validador e testes → tarefa homologada → WO no GitHub → admissão pelo Kernel vinculada ao blob SHA → execução isolada → testes → auditoria independente → fechamento.

## Estado de execução
**HOLD_HUMAN para mutações dependentes da WO não admitida.** Inspeção, preparação e testes locais independentes continuam permitidos. Sem alegação de fechamento.

## Lições aprendidas
Não confundir presença de contrato com enforcement, nem bloqueio de uma tarefa com paralisação do plano.
