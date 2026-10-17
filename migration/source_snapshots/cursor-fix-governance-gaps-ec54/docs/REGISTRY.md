# Registry Canônico

Tabela mínima no Supabase (ou planilha controlada) que é a fonte única de verdade para o corpus.

## Campos obrigatórios

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id_canonico | text unique | Ex: NORM-2026-001 |
| tipo | text | normativo, escala, calculadora, conteudo |
| hash_sha256 | text | Do texto sanitizado |
| status | text | bruto, atomizado, validado, fechado, publicado, quarentena |
| origem | text | URL ou caminho |
| drive_file_id | text | Opcional, se veio do Drive |
| versao_contrato | text | Ex: 1.1.0 |
| data_ingestao | date | |
| data_verificacao | date | |
| find_ids | text[] | Lista de FINDs abertos |
| notas | text | |

`packages/cli/registry.py` usa outra lista: `bruto`, `candidato`, `validado`, `canonico`, `quarentena`. As duas listas não foram unificadas. `registry add` e `registry set-status` saem com código 2 antes de gravar.

## Estados

- `bruto` → acabou de ser ingerido
- `atomizado` → passou por process
- `validado` → passou por invariantes
- `fechado` → revisão humana aprovada (não publicado)
- `publicado` → liberado para o front
- `quarentena` → problema detectado (não exclui)

## Regra de ouro

Nenhum arquivo novo no Drive ou no Supabase sem um registro correspondente no Registry com hash.
