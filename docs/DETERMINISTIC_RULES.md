# Regras Determinísticas

## Princípio

O Kernel não pensa. Ele só opera com base em políticas.

Qualquer ação só ocorre se:

1. Existir uma **tarefa explícita** (contrato ou comando).
2. A **política** permitir a operação.
3. O Kernel executar exatamente o que a política define.
4. Os gates retornarem exit 0.

Se a política não autorizar ou se um gate falhar, a execução para. Nada é escrito.

## Onde as políticas vivem

- Schemas e invariantes: `packages/schemas/`
- Contratos de tarefa: `contracts/`
- Regras de fonte e design system: `docs/` e `packages/design-system/`
- Código do Kernel: `packages/cli/`

Nenhuma política é criada ou alterada em tempo de execução. Tudo é versionado no Git.
