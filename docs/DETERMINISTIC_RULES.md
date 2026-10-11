# Regras Determinísticas do Projeto

## Princípio

Exit code 0 só significa que **todos os critérios obrigatórios** da etapa foram atendidos.
Qualquer artefato sem registro, qualquer omissão crítica ou qualquer invariante violada gera exit 2.

## Combinações de comando obrigatórias

| Objetivo | Comando | Exit esperado se falhar |
|----------|---------|-------------------------|
| Ingerir | `python -m packages.cli.main ingest ...` | 1 ou 2 |
| Processar | `python -m packages.cli.main process ...` | 2 se omissão crítica for tratada como bloqueio |
| Validar | `python -m packages.cli.main validate ...` | 2 |
| Pipeline completo | `python packages/cli/pipeline.py run --source ...` | 2 se qualquer gate falhar |
| Verificar registry | Parte do pipeline | 2 se átomo sem registro |

## Controles que identificam problemas

1. **Máscara** — remove dados sensíveis antes de processar.
2. **Auditoria de omissão** — marca números/prazos que sumiram.
3. **Invariantes Pydantic** — rejeita formato, termos opinativos, fonte inválida.
4. **Registry check** — bloqueia se existir átomo sem registro correspondente.
5. **GitHub Actions** — roda compile + help + checagem de registry em todo push.

## O que ainda não é 0% de erro

- Extração semântica profunda (ainda é heurística simples).
- Homologação clínica/normativa (exige humano).
- Integração real com Drive (ainda não ligada).

O que está garantido agora é que **nada avança silenciosamente** se faltar registro, se a validação falhar ou se o formato estiver errado.
