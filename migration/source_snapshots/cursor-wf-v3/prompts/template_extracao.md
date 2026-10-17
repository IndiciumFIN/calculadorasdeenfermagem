# Template de Extração (Máscara de Conteúdo)

Este é o contrato do que pode entrar via CLI.

## O que a máscara garante

- Texto limpo (sem marcas d'água, CPF, telefones).
- Hash calculado.
- Origem registrada.
- Formato pronto para o parser.

## O que o parser deve devolver

Um JSON que passe em `AtomoBlindado`:

- `id_atomo` no padrão NORM-AAAA-NNN
- `texto_regra` (10–800 caracteres, sem termos opinativos)
- `dispositivo_legal`
- `link_fonte` válido (URL)
- `status` controlado
- `versao_contrato`

Qualquer saída que não atenda a isso é rejeitada no `validate` (exit 2) e não chega ao Registry.
