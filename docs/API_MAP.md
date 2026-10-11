# Mapa de APIs, Parsers e Controles de Entrada

**Regra central**: nada chega à fonte da verdade (Registry + Supabase) sem passar pelo Kernel (CLI) e pelos controles de validação.

## Fluxo obrigatório

```
Fonte externa (URL, PDF, Drive, API)
        ↓
   CLI Kernel (ingest)
        ↓
   Máscara / Template de extração
        ↓
   Parser específico (HTML, PDF, JSON, OCR)
        ↓
   Auditoria de omissão + Invariantes
        ↓
   Validate (exit 2 se falhar)
        ↓
   Registry (registro obrigatório)
        ↓
   Fonte da verdade (Supabase)
```

## Componentes e seus locais

| Componente | Local no repositório | Função | Status |
|------------|---------------------|--------|--------|
| Kernel (CLI) | `packages/cli/main.py` | Ponto único de entrada | Implementado |
| Máscara / Template | `packages/cli/utils.py` | Sanitiza e define o que pode entrar | Implementado |
| Auditoria de omissão | `packages/cli/auditor.py` | Detecta perda de números/prazos | Implementado |
| Invariantes | `packages/schemas/invariantes.py` | Rejeita formato inválido | Implementado |
| Pipeline | `packages/cli/pipeline.py` | Orquestra gates com exit 2 | Implementado |
| Registry local | `packages/cli/registry.py` | Registro obrigatório antes de avançar | Implementado |
| Schema Supabase | `supabase/migrations/` | Fonte da verdade persistente | Migration pronta |
| Prompts versionados | `prompts/` | Contratos de extração (temperatura 0) | Implementado |

## APIs e fontes externas (planejadas)

| Fonte | Tipo | Como entra | Controle |
|-------|------|------------|----------|
| COFEN (site) | HTML | CLI `ingest --source URL` | Parser HTML + máscara |
| DOU / in.gov.br | HTML/PDF | CLI `ingest` | Parser + OCR se necessário |
| Anvisa | HTML/API | CLI `ingest` ou adapter futuro | Schema + validate |
| Google Drive | Arquivo | Download controlado → CLI | Hash + registry |
| PDF escaneado | Imagem | OCR (futuro) → CLI | OCR controlado + validação |
| ChatGPT export | Markdown/JSON | CLI `ingest` arquivo local | Classificação posterior |

## O que a máscara realmente é

A máscara não é só redação de CPF. Ela é o **template de conteúdo validado** que define o que pode seguir adiante:

- Remove ruído (marcas d'água, cabeçalhos).
- Redige dados sensíveis.
- Garante que o texto que chega ao parser já está no formato esperado pelo contrato.

Tudo que entra via CLI passa por ela. Nada chega ao Registry sem ter passado pela máscara + validate.

## Possibilidade de tudo entrar via CLI

Sim. O desenho atual já permite:

```bash
# Qualquer fonte
python -m packages.cli.main ingest --source URL_OU_ARQUIVO --output data/raw.json
python -m packages.cli.main process --input data/raw.json --output data/atomos.json
python -m packages.cli.main validate --input data/atomos.json
# Só depois registrar e (futuramente) publicar
```

Parsers específicos (OCR, PDF complexo, APIs) serão adapters chamados pelo mesmo Kernel, não caminhos paralelos.
