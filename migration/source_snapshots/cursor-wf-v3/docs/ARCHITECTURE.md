# Arquitetura — Calculadoras de Enfermagem

## Visão geral

O sistema é dividido em camadas claras:

1. **Ingestão de normativos** (bots + CLI) → átomos estruturados.
2. **Master Data** (Supabase) → fonte única.
3. **Contratos de dados** (Pydantic / JSON Schema) → validação.
4. **Frontend** (Next.js) → calculadoras e conteúdo.
5. **Builder de camadas** → produção visual determinística.
6. **Governança** → docs vivos + GitHub Actions.

## Fluxo principal

```
Normativo oficial → Extração (CLI/bots) → Átomo validado → Supabase
                                                              ↓
                                                    JSON paramétrico
                                                              ↓
                                                    Calculadora (front)
```

## Decisões importantes

- TypeScript strict + Pydantic para contratos.
- Temperatura 0 em prompts de extração.
- Documentação gerada a partir do código (não manual).
- Separar aprovação técnica de aprovação institucional/estética.
- Camadas do Builder são intercambiáveis, mas tokens são fixos.

Ver também:
- `docs/GOVERNANCE.md`
- `docs/DESIGN_SYSTEM.md`
- `docs/BUILDER.md`
