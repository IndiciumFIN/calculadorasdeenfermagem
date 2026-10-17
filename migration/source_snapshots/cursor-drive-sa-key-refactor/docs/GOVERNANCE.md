# Manual de Governança Normativa (MGN)
**Versão:** 2.0.0
**Data:** 2026-10-17

---

## Escopo

Este repositório e o Supabase associado armazenam e publicam apenas conteúdo derivado de fontes oficiais (COFEN, DOU, Planalto, ANVISA, Ministério da Saúde).

## Critério de atomicidade

Um átomo é válido se:
- Trata de uma única obrigação, direito, prazo ou regra.
- Pode ser compreendido isoladamente.
- Contém dispositivo legal exato + link da fonte.

## Status

- **Não verificado** ← status inicial de todo átomo进来的
- Vigente
- Alterado
- Revogado
- Sob discussão

## Regras

- Nunca publicar sem validação de schema.
- Nunca hardcodear parâmetros de calculadora.
- Toda peça visual deve referenciar tokens do design system.
- Aprovação técnica ≠ aprovação institucional.

---

## GOV-001 — Fail-Closed por Defeito

> Qualquer anomalia no pipeline deve causar `exit 2`, nunca silenciar ou continuar.

## GOV-002 — SHA256 como Identidade

> O SHA256 do texto de um átomo é sua identidade. SHA256 diferente = átomo diferente.

## GOV-003 — Arquivo = ID Canônico

> Cada átomo vive num arquivo nomeado pelo seu ID determinístico: `data/canonical/atoms/{id_atomo}.json`

## GOV-004 — Átomo Não Nasce Vigente

> A vigência é determinada pela comparação com o DOU oficial, nunca herdada da planilha do Drive. Todo átomo进来的 nasce com status `Não verificado` — a revisão humana é obrigatória antes de receber `Vigente`.

Fonte: `packages/cli/migrate_legado.py` (regra codificada)

## GOV-005 — Quarentena Sem Truncamento

> Texto com menos de 10 caracteres ou mais de 800 caracteres vai para a Quarentena com o texto integral preservado. Não há truncamento. O SHA256 do texto integral é registrado.

Fonte: `packages/cli/migrate_legado.py` (regra codificada)

## GOV-006 — Sem SHA256 Registrado = Fail-Closed

> Um commit que adiciona átomos ao corpus canonical sem SHA256 do fonte original registrado no MANIFESTO é rejeitado no CI (Gate G1). Isso impede que textos sem proveniência entrem no corpus.

Fonte: `data/legado/extracao_bruta/atomizado/verificar_v1.1.0.py`

## GOV-007 — WO Formalizada para Toda Ação

> Nada é baixado, atomizado, migrado ou removido do Drive sem uma Work Order versionada no Git (`data/legado/autorizacao_WO-{id}.json`). A WO é a trilha de auditoria que registra quem pediu, o quê, quando e para qual lote.

## GOV-008 — Quarentena É Append-Only

> Entradas添加到 Quarentena não são editadas ou apagadas — apenas novas entradas são acrescentadas. O histórico de rejeições é imutável.

## GOV-009 — Revisão Humana Exigida para `Vigente`

> Apenas átomos com status `Não verificado` que passaram pela revisão de um enfermeiro podem receber `Vigente`. A revisão requer `Reviewed-by:` no commit message (Gate G6).
