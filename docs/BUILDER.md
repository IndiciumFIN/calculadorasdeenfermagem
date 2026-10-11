# Builder de Camadas Canônicas

## Conceito

O Builder permite composição livre de peças a partir de uma biblioteca de camadas homologadas.

- Camadas são intercambiáveis.
- Tokens do design system são fixos.
- Usuário escolhe quais camadas usar, quais omitir e quais variantes.
- Resultado é determinístico (sem recriação por IA).

## Formato de composição (exemplo)

```json
{
  "id": "CE-POST-001",
  "version": "1.0.0",
  "canvas": { "width": 1080, "height": 1350 },
  "designSystem": "ce_institutional",
  "layers": [
    { "id": "background", "type": "shape", "variant": "gradient_official" },
    { "id": "headline", "type": "text", "editable": true },
    { "id": "logo", "type": "image", "locked": true }
  ]
}
```

## Regras

- Nunca promover peça não homologada a modelo canônico.
- Separar aprovação técnica de aprovação estética/institucional.
- Preferir fundos limpos quando o gradiente não for necessário.
