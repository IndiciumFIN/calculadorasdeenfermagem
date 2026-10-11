# Design System — Tokens Canônicos

Todos os materiais (site, posts, PDFs, capas) devem usar exclusivamente os tokens definidos em `packages/design-system/tokens.json`.

## Regras

- Não criar paletas alternativas.
- Gradientes institucionais usam apenas as cores primary documentadas.
- Elementos decorativos (brilhos, partículas, redes) são opcionais e não fazem parte do padrão base.
- Preferir clareza e espaço visual sobre efeitos tecnológicos.

## Uso

O Builder e os templates HTML/CSS devem referenciar esses tokens. Alterações no arquivo de tokens devem ser versionadas e regenerar assets quando necessário.
