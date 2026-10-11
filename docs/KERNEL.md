# Kernel (CLI) — Ponto Único de Execução

O Kernel é a CLI em `packages/cli/`.

## O que ele faz

- Recebe uma tarefa (comando + contrato).
- Executa as etapas definidas (ingest, process, validate, registry).
- Bloqueia se qualquer gate falhar.

## O que ele não faz

- Não decide o que fazer.
- Não altera identidade visual.
- Não publica sem contrato e validação.
- Não age por conta própria.

Agentes e IAs podem propor ou preparar dados, mas só o Kernel escreve na fonte da verdade, e somente quando a tarefa estiver definida e os gates passarem.
