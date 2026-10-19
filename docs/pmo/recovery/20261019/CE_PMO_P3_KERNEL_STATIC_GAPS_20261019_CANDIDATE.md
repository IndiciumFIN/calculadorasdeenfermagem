# P3-B — Inspeção estática do Kernel (evidência candidata)
**Corte:** 2026-10-19. **READ_ONLY** nas fontes. Não é teste de import, invocação, RBAC, concorrência, rede, admissão nem execução produtiva.

## Referências exatas
- `main:packages/cli/kernel/core.py`, Git blob `7649f6e1f0160184e1014308cc05c90a5eb659e9`.
- `main:packages/cli/kernel/policy_registry.py`, Git blob `041bfaf4151effd05de7cb33a5458a53a2ab04af`.
- `cursor/fix-governance-gaps-ec54:packages/cli/kernel.py`, Git blob `87bb5f2e62bcc6a71e5ed995115921e031705700`.

## Observações da fonte (não achados confirmados de runtime)
1. O core faz `from validators import (...)` e `from kernel.policy_registry import ...`, exigindo validação de resolução de pacotes/import no ambiente real e em instalação limpa.
2. A função de importação de validadores filtra entradas por nome `_validator` e atributo `validate`; é necessária prova de registro efetivo dos validadores previstos, incluindo as classes importadas.
3. O PolicyRegistry possui `register()` em memória e `save()` em disco; isto, por si só, não configura autoridade transacional de WO/admissão nem Kernel de produção.
4. O carregamento de políticas trata determinados erros de parsing/tipo com `pass`, podendo omitir política defeituosa sem diagnóstico explícito; testar política inválida, ausência e falha fechada sem presumir resultado.
5. Há duas implementações de Kernel em branches diferentes. Não escolher por data/nome; aplicar testes de contrato de cada versão e política específica.
6. O relatório M20 de 14 executores stub e o M21 `exit 78` continuam evidências históricas em HOLD, ainda não reproduzidas neste microlote.

## Testes necessários, sem alegar execução
- Importação e descoberta de validadores em ambiente limpo (positivo/negativo, exit codes).
- Política ausente, malformada, versão incompatível e validator desconhecido.
- WO sem admissão; hash de WO alterado; replay; status PREAUTHORIZED isolado.
- RBAC por ação/recurso; ID collision; input truncado; idempotência, locks, fencing e concorrência.
- Separação entre test fixture e receipt Kernel real; segurança de segredos; auditor independente.

**Estado:** `P3-B=STATIC_REVIEW_PARTIAL_HOLD`; nenhum FIND oficial novo, tarefa encerrada ou gate aprovado. Próxima ação: localizar testes e executores reais, construir matriz de cobertura estática e de execução com evidência reproduzível. A fila de 12 tarefas e o POST-001 ao final permanecem inalterados.
