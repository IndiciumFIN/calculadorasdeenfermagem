# Inventário de comandos

A qualificação do procedimento está em `policies/definicoes_tarefa.json`. Esta tabela não autoriza execução. A Work Order pede permissão para uma definição já qualificada e não descreve o procedimento.

## Tarefas ativas

| ID | Tarefa | Comando | Critério de aceite | Status |
|----|--------|---------|---------------------|--------|
| T01 | Ingestão com máscara | `python -m packages.cli.main ingest --source <src> --output data/raw.json` | Arquivo gerado com hash e texto sanitizado | Implementada |
| T02 | Processamento + auditoria | `python -m packages.cli.main process --input data/raw.json --output data/atomos.json` | Átomos gerados + campo `_auditoria` | Implementada |
| T03 | Validação de invariantes | `python -m packages.cli.main validate --input data/atomos.json` | Exit 0 só se todos passarem | Implementada |
| T04 | Pipeline completo | `PYTHONPATH=. python packages/cli/pipeline.py run --source <src>` | Exit 0 só se todos os gates passarem | Implementada |
| T05 | Checagem de registry | Parte do pipeline ou GitHub Action | Exit 2 se átomo sem registro | Implementada |
| T06 | Bloqueio por omissão | `process --block-on-omission` | Exit 2 se houver omissão crítica | Implementada |
| T07 | Registro no registry local | `python packages/cli/registry.py add --id ...` | Item aparece em data/registry.json | Implementada |

## Tarefas pendentes (não pensantes)

| ID | Tarefa | Dependência | Critério |
|----|--------|-------------|----------|
| T08 | Publicar no Supabase | T03 + T07 | Registro no Supabase com status `validado` |
| T09 | Inventário Drive (somente leitura) | rclone ou API | CSV com ID, hash, status |
| T10 | Parser específico COFEN | T01 | Átomos da Resolução 736/2024 |
| T11 | Revisão humana (G12) | T03 | FIND resolvido ou aprovado |

## Regra de ouro

Nenhuma tarefa marca status `concluída` sem evidência de exit 0 e artefato registrado.
