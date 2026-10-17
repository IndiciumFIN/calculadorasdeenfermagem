# Kernel (CLI) — Executor de Políticas

O Kernel **não pensa**. Ele só opera com base em políticas e contratos já definidos.

## O que ele faz

- Recebe um comando e um contrato.
- Aplica as políticas codificadas (máscara, auditoria, invariantes, registry check).
- Executa as etapas na ordem definida.
- Retorna exit 0 ou exit 2 conforme as políticas.

## O que ele não faz

- Não decide o que fazer.
- Não interpreta intenção.
- Não cria política nova.
- Não altera regras em tempo de execução.
- Não publica sem que a política permita.
- Não recebe escrita de `ingest`, `process`, `pipeline` nem `registry add` / `set-status`. Esses comandos saem com código 2. T01, T02, T04 e T07 continuam não qualificadas.

Políticas e contratos vivem em código e em arquivos versionados (`packages/schemas/`, `contracts/`, `docs/`). O Kernel apenas as executa.
