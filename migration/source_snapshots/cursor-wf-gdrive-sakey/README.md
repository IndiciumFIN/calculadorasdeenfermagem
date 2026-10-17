# Calculadoras de Enfermagem

Fonte canônica de governança, contratos, schemas e pipeline para o projeto.

## Princípio central

**Git é a fonte da verdade.** Drive, conversas e agentes são subordinados. Nada entra no Supabase ou no site sem passar por validação e Registry.

## Status atual do corpus (11/10/2026)

- Base estrutural grande (~547k átomos em lotes anteriores)
- Reconciliações parciais confirmadas (Anvisa 40k, CID, vacinas etc.)
- Homologação clínica/normativa **ainda não concluída**
- Drive desorganizado → precisa de inventário controlado

## Como começar a limpar

```bash
# 1. Clonar o repo
git clone https://github.com/IndiciumFIN/calculadorasdeenfermagem.git
cd calculadorasdeenfermagem

# 2. Instalar CLI
cd packages/cli && pip install -r requirements.txt && cd ../..

# 3. Registrar um item no Registry local
python packages/cli/registry.py add --id NORM-2026-001 --tipo normativo --origem https://www.cofen.gov.br --status bruto

# 4. Ingerir e processar
python packages/cli/main.py ingest --source URL --output data/raw.json
python packages/cli/main.py process --input data/raw.json --output data/atomos.json
python packages/cli/main.py validate --input data/atomos.json
```

## Documentos importantes

- [Contratos dos Agentes](docs/AGENTS.md)
- [Registry Canônico](docs/REGISTRY.md)
- [Controles Chave](docs/KEY_CONTROLS.md)
- [Pipeline Blindado](docs/PIPELINE.md)
- [Fontes Autorizadas](docs/SOURCES.md)

## Próximo passo prático

Criar projeto Supabase limpo, rodar as duas migrations e começar a popular o Registry com os itens mais críticos (Resolução 736/2024, escalas principais, calculadoras existentes).
