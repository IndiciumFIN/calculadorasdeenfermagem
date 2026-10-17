# Inventário Inicial — 11/10/2026

## Site homologado (calculadorasdeenfermagem.com.br)

- Tokens oficiais presentes no CSS: `#1A3E74`, `#1E4D8C`, `#163269` (confirmado via curl).
- localStorage identificado na homepage: `fontSize`, `darkMode`.
- **Limitação**: localStorage é client-side. Curl só vê o HTML/JS. Para inventário completo é necessário abrir o site no navegador (ou bot com acesso ao computador) e exportar Application → Local Storage.

## Supabase

Projetos encontrados:

| Projeto | ID | Status | Observação |
|---------|----|--------|-----------|
| auditeduca's Project | aevqrmkdhffmursdtcmo | ACTIVE_HEALTHY | Tabelas: provas_enfermagem, extracoes_enfermagem, questoes_enfermagem |
| simulados-para-enfermagem | bsawvgyideporzailnys | INACTIVE | - |

Tabelas públicas no projeto ativo são de simulados/questões, não do corpus normativo principal.

## Google Drive (raiz)

Pastas relevantes identificadas:

- `extracao bruta Grok Bot Danadão` (ID: 1l519_P-9o6bnQcItydKvEEDpEYeE8R8s) — contém subpastas: atomizado, cid10, dispositivos, epidemiologico, medicamentos, mesh, protocolos_enfermagem, raw, revisao, sepse, sinais_vitais etc.
- `Calculadoras_de_Enfermagem` (ID: 1FDBAMQ3-WT-8l6xU0664u7QjABd0FbEH) — contém FEDERAL, NORMATIVOS, CORPUS & KNOWLEDGE PMO (spreadsheet).
- `Calculadoras-de-Enfermagem` (ID: 1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9)
- `Audit Educa — Consolidado`
- `ESTEIRA_COFEN_BACKUP_20261010_1715`

## Próximos passos recomendados

1. Inventário completo da pasta `extracao bruta Grok Bot Danadão` (somente leitura).
2. Exportar localStorage do site no navegador (instrução já documentada).
3. Mapear quais pastas do Drive já têm correspondente no Registry do Git.
4. Não promover nada do Drive a canônico sem passar pelo Kernel + validate + Registry.
