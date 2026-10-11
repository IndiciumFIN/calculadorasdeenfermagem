# Calculadoras de Enfermagem

Plataforma clínica de calculadoras, escalas, simulados e recursos baseados em evidências.

**Objetivo deste repositório**: acabar com o vibecoding. Estrutura limpa, tipada, documentada e governada para que qualquer alteração (humana ou de agente) seja compreensível, revisável e segura.

## Stack

- **Frontend**: Next.js (App Router) + React + TypeScript (strict)
- **UI**: Tailwind CSS + design system próprio (tokens)
- **Backend / Dados**: Supabase (Postgres + Auth + Storage + RLS)
- **CLI**: Typer (Python) para ingestão, validação e geração de docs
- **Qualidade**: GitHub Actions (lint, type-check, schema validation)
- **Deploy**: Vercel

## Princípios

1. Fonte única de verdade (schemas no código geram docs).
2. Contratos de dados versionados.
3. Normativos atômicos alimentam calculadoras via JSON paramétrico.
4. Builder de camadas determinístico (sem recriar peças com IA).
5. Validção em múltiplas camadas antes de publicar.

## Começar

```bash
# Instalar dependências (depois de configurar package.json completo)
npm install

# Configurar Supabase
cp .env.example .env.local
# Preencher NEXT_PUBLIC_SUPABASE_URL e NEXT_PUBLIC_SUPABASE_ANON_KEY

npm run dev
```

Ver `docs/ARCHITECTURE.md` para a visão completa.
