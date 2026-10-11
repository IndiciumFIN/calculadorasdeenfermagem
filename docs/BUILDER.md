# Builder de Camadas Canônicas

## Princípio

O Builder compõe peças a partir de uma biblioteca de camadas homologadas. Não depende de IA para recriar layouts. Tokens do design system são fixos.

## Regras

1. Toda composição referencia `designSystem: "ce_canonical"`.
2. Camadas são opcionais. O usuário pode omitir qualquer uma que não seja obrigatória.
3. Fundo branco é institucional. Gradiente só quando explicitamente escolhido.
4. Nenhum agente pode alterar cores ou criar variantes fora dos tokens.
5. Composição é definida em JSON (ver `packages/builder/composition.schema.json`).

## Formato

Ver exemplo em `packages/builder/example_composition.json`.

## Uso futuro

O front-end (ou ferramenta de renderização) lê o JSON e monta a peça usando os tokens. Não há chamada de IA na composição.
