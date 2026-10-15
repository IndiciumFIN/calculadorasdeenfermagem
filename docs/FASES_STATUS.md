# Status das Fases — CKO / Calculadoras de Enfermagem

Branch: `cursor/fix-governance-gaps-ec54`

| Fase | Descrição | Status |
|------|-----------|--------|
| 1 | CLI antigo recusa escrita antes de gravar | Código na branch; FIND-0001 aberto |
| 2 | IDs imutáveis (hash) + máscara lookaround | Concluída |
| 3 | Validador NORM- + 12 hex | Concluída |
| 4 | Proteção de status inicial | Concluída |
| 5 | Hash de proveniência | Concluída |
| 6 | Identity Issuer (ID da Fase 2 é o único aceito) | Concluída (validador ativo) |
| 7 | Status Registry — transição exclusiva via WO | Documentado (proteção mínima ativa) |
| 8 | Master Registry — igualdade verificável | Documentado |
| 9 | Recertificação de agentes | Documentado (agents/registry.json existente) |
| 10 | Backup e retenção | Documentado (workflow backup.yml existente) |
| 11 | Auditoria de dependências | Documentado (gate_deps_audit.sh existente) |
| 12 | Branch protection na main | Ação humana (GOV-001) |
| 13 | Migration Supabase | Ação humana (migration versionada) |

**Última atualização**: 2026-10-15

`ingest`, `process`, `pipeline run`, `registry add` e `registry set-status` saem com código 2 antes de gravar. T01, T02, T04 e T07 continuam não qualificadas. Nenhuma linha desta tabela homologa produção, aplica a migration nem ativa a proteção de branch.
