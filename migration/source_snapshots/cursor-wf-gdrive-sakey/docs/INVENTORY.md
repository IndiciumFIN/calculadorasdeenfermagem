# Inventário Mestre — Template

Use esta estrutura para mapear tudo que está espalhado (site, Supabase, Drive, ChatGPT, local).

| id_canonico | tipo | localizacao_atual | hash_ou_versao | status | dependencias | ultima_verificacao | notas |
|-------------|------|-------------------|----------------|--------|--------------|--------------------|-------|
| NORM-2026-001 | normativo | Drive/NORMATIVOS/... | | fonte-primária | | 2026-10-11 | |
| CALC-DIMENSIONAMENTO | calculadora | site + local | | a-migrar | NORM-... | | |

## Status possíveis

- fonte-primária
- derivado
- legado
- a-migrar
- descartar

## Próximo passo

Preencher as primeiras 20–30 entradas críticas e depois migrar para uma tabela no Supabase.
