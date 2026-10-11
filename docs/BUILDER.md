# Builder de Camadas Canônicas

## Status

- Schema de composição definido (`packages/builder/composition.schema.json`).
- Exemplo de composição (`packages/builder/example_composition.json`).
- Preview React básico (`src/components/builder/CompositionPreview.tsx`).
- Tokens oficiais aplicados via CSS variables.

## Regras de consistência

1. Toda composição deve declarar `"designSystem": "ce_canonical"`.
2. Cores só podem vir dos tokens em `packages/design-system/tokens.json`.
3. Camadas marcadas como `optional: true` podem ser omitidas pelo usuário.
4. Fundo branco é institucional. Gradiente só se explicitamente escolhido.
5. Nenhum agente ou IA pode criar paleta ou efeito fora do design system.

## Como testar

```bash
npm install
npm run dev
# Acessar /builder
```
