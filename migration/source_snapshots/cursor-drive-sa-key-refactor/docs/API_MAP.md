# Mapa de APIs e Fontes

## Fonte primária
- **DOU** (`packages/cli/adapters/dou.py`) — fonte oficial. Adapter já implementado.

## Fontes secundárias
- **Secundária** (`packages/cli/adapters/secundaria.py`) — apoio e anexos. Nunca substitui DOU.

## Uso via CLI
```bash
# DOU (fonte primária)
python -m packages.cli.main ingest --source https://in.gov.br/... --fonte dou

# Secundária (apoio)
python -m packages.cli.main ingest --source https://www.cofen.gov.br/... --fonte secundaria
```

Tudo passa pela máscara, auditoria e validate. Divergência entre primária e secundária exige revisão humana (status `divergencia`).
