# Inventário do Repositório Aberto do Site Homologado

**Fonte**: https://github.com/kauesp0007/calculadoras-de-enfermagem  
**Data**: 11/10/2026

## Estrutura relevante

- `AI_RULES.md` — prioridade máxima para IAs.
- `HTML_RULES.md`, `HTML_PAGE_TEMPLATE_RULES.md`
- `CATALOGO_DE_IDENTIDADE_VISUAL/CATALOGO_DO_DESIGN_SYSTEM.md`
- `CATALOGO_DE_IDENTIDADE_VISUAL/PADRAO_CANONICO_PAGINAS_HTML.md`
- Múltiplos catálogos (arquitetura, SEO, formulários, agentes, biblioteca, blog).

## Achado crítico do Design System

O catálogo reporta **450 cores únicas**. A cor oficial `#1A3E74` é a mais usada (65x), mas há grande proliferação de cores soltas.

Isso justifica o design system canônico que estamos construindo neste repositório, com tokens fixos e regras invioláveis.

## localStorage

Não documentado nos arquivos de regra lidos. No HTML público da homepage foram identificados apenas `fontSize` e `darkMode`.

## Uso deste inventário

Este repositório (`IndiciumFIN/calculadorasdeenfermagem`) é a fonte da verdade canônica para o novo pipeline. O repositório do site é referência histórica e de templates existentes, não fonte de verdade para novas produções.
