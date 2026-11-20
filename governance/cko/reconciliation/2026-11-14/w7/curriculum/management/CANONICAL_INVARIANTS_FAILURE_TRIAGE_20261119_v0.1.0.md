# Triagem de falhas reais dos invariantes canônicos — 19/11/2026

Escopo: EPIC #74, PR #70, branch `review/cko-w7-public-evidence-20261114`. **Diagnóstico candidato; não é correção nem autorização de merge.**

## Proveniência executada

- SHA analisado: `f4906d2a7d5244ba27fc93fb79d3dd548f4fa8f1`.
- Workflow **Canonical repository invariants**, run [44461190413](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/44461190413), conclusão **FAIL**.
- Logs consultados diretamente via GitHub Actions: job `135348089213` (**Canonical contracts and CLI smoke**) e job `135348089482` (**Full admission blockers (fail closed)**).
- O segundo job executou `python scripts/verify_repository_integrity.py --strict --output /tmp/canonical-strict.json` e terminou com **exit code 2**.
- O primeiro job passou testes unitários negativos do verificador, mas falhou em `Verify canonical source and policy references`; testes de smoke subsequentes não foram demonstrados como aprovados.
- No mesmo SHA, CKO Curriculum and Market Read-only Audit, CI - Validação e Pipeline Determinístico tiveram conclusão PASS. **Não substituem o gate canônico.**

## Inventário extraído dos logs (não inferido)

| Código | Severidade no relatório | Quantidade | Objetos |
|---|---|---:|---|
| `LEGACY_SOURCE_DIR` | error | 1 | `contracts/fonts`; o validador exige `contracts/fontes/` |
| `MISSING_PARSER` | pending | 16 | fontes enumeradas abaixo |
| `PACKAGE_IMPORT_NAMESPACE` | pending | 5 | arquivos enumerados abaixo |

Parsers ausentes segundo a execução: `anvisa_dev.py`, `anvisa_med.py`, `atlas.py`, `catmat.py`, `cdsi.py`, `cid10.py`, `icd11.py`, `esavi.py`, `fhir.py`, `medlineplus.py`, `mesh.py`, `pni.py`, `sies.py`, `sinan.py`, `taco.py`, `vacinas.py`. Os respectivos contratos estão em `contracts/fontes/`; **não criar stubs para satisfazer o verificador**.

Namespaces pendentes: `packages/cli/kernel/__init__.py`, `packages/cli/kernel/cli.py`, `packages/cli/kernel/core.py`, `packages/cli/main.py`, `packages/cli/validators/registry.py`. Exigem validação real do modo `python -m packages.cli.main`, não apenas alteração textual de imports.

## Plano de correção com testes de aceite

1. **P0 — fonte legada:** examinar a árvore de `contracts/fonts`, verificar referências e colisões de IDs com `contracts/fontes`; migrar/remover apenas após prova de equivalência, sem apagar fonte ou política válida. Aceite: ausência de `LEGACY_SOURCE_DIR` e referências válidas.
2. **P0 — parsers:** inventariar implementações existentes em branches (em especial FHIR, MedlinePlus e MeSH); comparar contrato de entrada, licença, proveniência, testes positivos/negativos e idempotência antes de integrar. Aceite individual: import funcional, parse de fixture permitido, falha fechada para entrada inválida, rastreabilidade; não aceitar arquivo vazio ou placeholder.
3. **P0 — CLI:** corrigir imports relativos/absolutos de forma consistente com empacotamento e executar `python -m packages.cli.main --help` e os testes do módulo. Aceite: cinco ocorrências resolvidas sem manipular resultado do validador.
4. **Gate final:** reexecutar `python scripts/verify_repository_integrity.py --strict`, testes unitários e workflow GitHub do SHA corrigido. Exigir evidências de execução e PASS; não declarar gate resolvido por planejamento.
5. **Independência:** bloqueios canônicos não impedem pesquisa WO-05, mas impedem promoção técnica; HOLD_RIGHTS/HOLD_HUMAN permanecem por objeto.

## Estado desta triagem

**Executado:** leitura dos logs reais, contagem de 1 erro estrutural + 21 pendências de parser/import, identificação de arquivos e comandos de teste. **Não executado:** alteração dos arquivos causadores, integração de parsers, teste local, reexecução de CI ou homologação. Estado: **FAIL/HOLD**, publicação clínica **NO-GO**.
