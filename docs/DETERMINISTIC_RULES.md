# Regras Determinísticas

## Princípio fundamental

IA e agentes **não alteram** código, conteúdo, design system ou Registry por iniciativa própria.

Qualquer alteração só ocorre se:

1. Existir uma **tarefa explícita** (contrato em `contracts/` ou comando CLI).
2. O **Kernel** (CLI) executar a tarefa.
3. Os **gates** (validate, invariantes, registry check) passarem.

Se qualquer gate falhar, a execução para com exit 2. Nada é escrito na fonte da verdade.

## O que AI_RULES.md do site significa aqui

O `AI_RULES.md` do repositório do site é referência histórica. Neste repositório, a regra é mais restritiva:

- Não há alteração sem tarefa.
- Não há alteração sem Kernel.
- Não há alteração sem validação.

Agentes não "leem regras e decidem". Eles recebem um contrato e o Kernel executa ou bloqueia.

## Exit codes

| Código | Significado |
|--------|-------------|
| 0 | Todos os critérios obrigatórios atendidos |
| 2 | Bloqueio (validação, registry, omissão, invariante) |

Nenhum artefato chega ao Registry ou ao Supabase sem exit 0.
