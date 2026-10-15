# Status das Fases — CKO / Calculadoras de Enfermagem

Branch de referência: `cursor/fix-governance-gaps-ec54`

| Fase | Descrição | Status | Commit |
|------|-----------|--------|--------|
| 1 | CLI exige Work Order (exit 2 sem WO) | Concluída | 29fa705 |
| 2 | IDs imutáveis (hash) + máscara com lookaround | Concluída | c221521 |
| 3 | Validador rígido de ID (`NORM-` + 12 hex) | Concluída | 8d00906 |
| 4 | Proteção de status inicial (`Não verificado`) | Concluída | (este) |
| 5 | Checagem de hash de proveniência | Concluída | (este) |
| 6–13 | Itens restantes (branch protection, migration Supabase, Identity Issuer, Status Registry completo, etc.) | Pendente de ação humana / próxima WO | — |

**Pendente de ação manual (não automatizável via código):**
- GOV-001: branch protection na `main`
- Aplicação da migration `20261014000000_governance_fixes.sql` no Supabase
- Configuração de secrets e acoplamento de workflows de deploy

Última atualização: 2026-10-15
