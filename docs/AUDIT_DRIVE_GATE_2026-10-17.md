# Auditoria do gate Drive (17/10/2026)

Auditoria determinística do estado do gate `Drive recursive metadata candidate` na branch `cursor/fix-governance-gaps-ec54`, commit `d1c4e299`.

## Resumo executivo

| Item | Estado |
|------|--------|
| Gate Agregador (único obrigatório) | ✅ PASS (run #96, 8m49s) |
| Drive recursive metadata candidate | ❌ FAIL by design — `DRIVE_ACCESS_TOKEN` ausente |
| Drive inventory (WO-0104/0106) | ⏸️ Sem trigger de push desde 16/10 |
| Drive ZIP pilot (WO-0105) | ⏸️ Sem trigger de push desde 16/10 |
| Pipeline Determinístico | ⏸️ Sem trigger nesta branch |
| CI Validação | ⏸️ Substituído pelo Gate Agregador (GOV-002/GOV-003) |

## Causa raiz do FAIL do Drive recursive

O workflow `.github/workflows/drive-recursive-collect.yml` exige o passo explícito `Require scoped read-only credential`:

```
if [ -z "$DRIVE_ACCESS_TOKEN" ]; then
  echo "::error::DRIVE_ACCESS_TOKEN is not configured; fail closed"
  exit 2
fi
```

A ausência de `DRIVE_ACCESS_TOKEN` nos secrets do repositório é tratada como falha por design (gate fail-closed). O log do run #10 mostra exatamente isso:

```
2026-10-17T01:30:22.5751547Z ##[error]DRIVE_ACCESS_TOKEN is not configured; fail closed
2026-10-17T01:30:22.5759505Z ##[error]Process completed with exit code 2.
```

Os passos anteriores (testes pytest 16/16, compilação, push trigger) executaram sem erro. Apenas o gate de credencial barrou a aquisição, como pretendido.

## Por que isso não é um bug

1. **Política de governança**: o manual `docs/PIPELINE.md` e `docs/GAP_REMEDIATION.md` registram que os workflows dependentes de credencial devem falhar de forma fechada quando a credencial não está disponível. Isso evita gravação silenciosa em ambiente público.
2. **Apenas aquisição de metadados**: nada é publicado, movido ou apagado. O output, quando existe, é candidato raw (`status=COLLECTED_NOT_KERNEL_APPROVED`) que exige uma WO de Kernel independente para ser promovido.
3. **A WO de Kernel oficial não está qualificada**: o `docs/JOBS_STATUS.md` lista esteira Drive como `auditado, falhas encontradas`. A promoção só ocorre via `python -m packages.cli.kernel auditar-inventario --work-order contracts/work_orders/WO-2026_10_16_0104.json` com o checker de Kernel oficial. Por isso o pipeline correto é o `drive-inventory.yml`, não o `drive-recursive-collect.yml`.
4. **Gate Agregador é a única check obrigatória** (ver `gates/aggregate.sh` e `docs/GAP_REMEDIATION.md` GOV-002). O branch protection deve exigir apenas esse check.

## Ações pendentes (manuais, fora do alcance do agente)

| Ação | Responsável |
|------|-------------|
| Configurar `DRIVE_ACCESS_TOKEN` nos secrets do repositório (escopo read-only do Google Drive) | Admin do repositório |
| Ativar branch protection exigindo `Gate Agregador / aggregate` (GOV-001) | Admin do repositório |
| Aplicar `supabase/migrations/20261014000000_governance_fixes.sql` (GOV-004) | Admin do Supabase |
| Configurar `SUPABASE_URL` e `SUPABASE_ANON_KEY` (GAP-04) | Admin + TEC |
| Definir `DEEPSEEK_API_KEY` na Edge Function `cko-deepseek-gateway` (já feito em 15/10) | Governança de IA |

## Verificações executadas

- `actions_list` para todos os 6 workflows — 160 runs totais; Gate Agregador sucesso em todos os runs atuais da branch.
- `actions_get` para run #10 do Drive recursive — confirmou o gate explícito.
- `get_file_contents` em todos os workflows (gate, ci, pipeline, drive-inventory, drive-zip-pilot, drive-recursive-collect) — revisei gatilhos e comandos.
- `get_file_contents` em `gates/aggregate.sh`, `gate_python.sh`, `gate_typescript.sh`, `gate_secrets.sh`, `gate_deps_audit.sh`, `gate_workflow_lint.sh` — todos em conformidade com fail-closed.
- `get_file_contents` em todas as WO registradas (0104, 0105, 0106, EXEMPLO-001) — todas com `state=PREAUTHORIZED` e SHA-256 dos arquivos de entrada conferido.
- `get_file_contents` em `data/grc/drive_inventory_20261016_pilot.json` e `wave2.json` — payloads íntegros com root_id e SHA-256 correspondentes às WO.
- `test_drive_recursive_inventory.py` — 16 testes cobrindo fail-closed em todos os cenários (paginação repetida, metadados incompletos, ciclo, overlap, etc.).
- `test_regression_gaps.py` — testes de regressão de T1–T4/T9 e GOV/GAP-01/02/05/07/08/09.

## Conclusão

O estado da branch está coerente com a governança declarada. A falha do `Drive recursive metadata candidate` é a proteção de credencial funcionando como esperado. O Gate Agregador passa e os testes de regressão cobrem os contratos e invariantes. As próximas ações dependem de configuração manual de secrets e branch protection por parte do administrador do repositório.
