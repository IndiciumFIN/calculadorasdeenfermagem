# FIND-G0-017 — WO draft lacks real admission and homologated task evidence

**Status:** OPEN
**Severidade:** HIGH
**Data:** 2026-10-17
**Origem:** inspeção estática GitHub, branch fix/ce05-kernel-ci-security-20261017

## Evidência
Arquivo: `contracts/wo/WO-G0-CORRECTIVE-20261017.json` (blob SHA `32f61923573e8b41f9a452a6a406155eccb4c650`).

## Falha
WO draft lacks real admission and homologated task evidence. Evidência estática; impacto em runtime ainda requer teste isolado.

## Correção e teste obrigatório
Reconcile canonical WO schema, homologate tasks and bind Kernel admission to GitHub blob SHA.

## Cadeia de governança
Política aplicável/ajuste controlado → validador e testes → tarefa homologada → WO no GitHub → admissão pelo Kernel vinculada ao blob SHA → execução isolada → testes → auditoria independente → fechamento.

## Estado de execução
**HOLD_HUMAN para mutações dependentes da WO não admitida.** Inspeção, preparação e testes locais independentes continuam permitidos. Sem alegação de fechamento.

## Lições aprendidas
Não confundir presença de contrato com enforcement, nem bloqueio de uma tarefa com paralisação do plano.
