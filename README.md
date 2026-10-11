# Calculadoras de Enfermagem

Plataforma clínica de calculadoras, escalas, simulados e recursos baseados em evidências — **canônica e governada por normas**.

## Objetivo

Acabar com o caos de versões e vibecoding. Tudo nasce de fontes oficiais, vira átomo validado e alimenta o front de forma rastreável.

## Stack

- Next.js + TypeScript + Tailwind
- Supabase (Postgres + Auth + Storage + RLS)
- CLI Python (Typer) para ingestão e validação
- GitHub Actions
- Design system com tokens fixos

## Como usar a CLI agora

```bash
cd packages/cli
pip install -r requirements.txt

# Ingerir uma página ou arquivo
python main.py ingest --source https://www.cofen.gov.br --output ../../data/raw.json

# Gerar átomos
python main.py process --input ../../data/raw.json --output ../../data/atomos.json

# Validar
python main.py validate --input ../../data/atomos.json
```

## Documentação essencial

- [Arquitetura](docs/ARCHITECTURE.md)
- [Pipeline](docs/PIPELINE.md)
- [Governança](docs/GOVERNANCE.md)
- [Design System](docs/DESIGN_SYSTEM.md)
- [Builder](docs/BUILDER.md)
- [Inventário](docs/INVENTORY.md)

## Próximos passos

1. Criar projeto Supabase e rodar a migration.
2. Preencher `.env.local`.
3. `npm install && npm run dev`.
4. Começar a migrar calculadoras existentes para o modelo paramétrico.

**Tudo que entra passa por validação. Nada é publicado sem contrato.**
