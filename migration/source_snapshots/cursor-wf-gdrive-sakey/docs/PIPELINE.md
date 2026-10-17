# Pipeline Blindado

```bash
# 1. Ingestão com máscara
python packages/cli/main.py ingest --source URL_OU_ARQUIVO --output data/raw.json

# 2. Processamento + auditoria de omissão
python packages/cli/main.py process --input data/raw.json --output data/atomos.json

# 3. Validação com invariantes (exit 2 se falhar)
python packages/cli/main.py validate --input data/atomos.json
```

## Controles ativos

- Máscara de CPF, telefone e marcas d'água.
- Auditoria de números/prazos omitidos.
- Invariantes: termos opinativos proibidos, fonte obrigatória se vigente, tamanho mínimo.
- Exit code 2 em falha de validação (ideal para CI).

## Próximo nível de blindagem

- Camada 2 de auditoria com segundo modelo (prompt de confrontação).
- Publicação no Supabase só se validação passar.
- Geração automática do dicionário a partir do schema.
