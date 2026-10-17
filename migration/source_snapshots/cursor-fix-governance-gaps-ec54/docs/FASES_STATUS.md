# Status das Fases — CKO / Calculadoras de Enfermagem

Branch: `cursor/fix-governance-gaps-ec54`

| Fase | Descrição | Status |
|------|-----------|--------|
| 1 | CLI antigo recusa escrita antes de gravar | Código na branch; FIND-0001 aberto |
| 2 | IDs em hash na heurística + máscara lookaround | Harness; o schema canônico continua ano + sequência |
| 3 | Validador NORM- + 12 hex | Harness; não é o padrão de `AtomoBlindado` |
| 4 | Status inicial `Não verificado` | Heurística; o comando não grava |
| 5 | Hash de proveniência | Checagem no harness |
| 6 | Identity Issuer | Não comprovado |
| 7 | Status Registry | Comandos recusam; a máquina do código e a de `docs/REGISTRY.md` permanecem distintas |
| 8 | Master Registry | Não comprovado |
| 9 | Recertificação de agentes | Documentado (agents/registry.json existente) |
| 10 | Backup e retenção | Documentado (workflow backup.yml existente) |
| 11 | Auditoria de dependências | Documentado (gate_deps_audit.sh existente) |
| 12 | Branch protection na main | Ação humana (GOV-001) |
| 13 | Migration Supabase | Ação humana (migration versionada) |

**Última atualização**: 2026-10-15

`ingest`, `process`, `pipeline run`, `registry add` e `registry set-status` saem com código 2 antes de gravar. T01, T02, T04 e T07 continuam não qualificadas. Nenhuma linha desta tabela homologa produção, aplica a migration nem ativa a proteção de branch.
