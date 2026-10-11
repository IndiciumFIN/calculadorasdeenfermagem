# Pipeline Canônico — Da Fonte ao Front

## Fluxo completo

```bash
# 1. Ingestão (URL ou arquivo)
python -m packages.cli.main ingest --source https://www.cofen.gov.br/... --output data/raw.json

# 2. Processamento em átomos
python -m packages.cli.main process --input data/raw.json --output data/atomos.json

# 3. Validação
python -m packages.cli.main validate --input data/atomos.json

# 4. (Futuro) Push para Supabase
# python -m packages.cli.main publish --input data/atomos.json
```

## O que a CLI faz hoje

- **ingest**: baixa HTML ou lê arquivo, limpa texto, gera hash.
- **process**: extrai trechos que parecem artigos/dispositivos em átomos JSON.
- **validate**: valida contra o schema Pydantic.

## Próximas magias (implementáveis)

- Integração com APIs oficiais (quando existirem).
- Extração via LLM com temperatura 0 + validação cruzada.
- Publicação automática no Supabase.
- Geração de parâmetros para calculadoras/escalas.

## Recuperar conversas

Exporte históricos do ChatGPT (JSON ou Markdown) e rode:
```bash
python -m packages.cli.main ingest --source conversa.md --output data/conversa.json
```
Depois classifique manualmente ou via script quais trechos viram átomos ou conteúdos.
