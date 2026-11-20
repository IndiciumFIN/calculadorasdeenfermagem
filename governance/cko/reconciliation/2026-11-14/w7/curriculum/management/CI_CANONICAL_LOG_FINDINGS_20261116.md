# Diagnóstico primário do gate canônico — findings extraídos do log GitHub Actions

Data: 16/11/2026. EPIC #74 / PR #70. Fonte primária: https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43932821589 (job 133529481976, etapa Reject unresolved parser or import dependencies; log decodificado via GitHub Actions). Não constitui aprovação de release.

## Contagem exata do validador

`counts = {error: 1, pending: 21}`; `structural_pass = false`; `strict_pass = false`. O erro bloqueante é **LEGACY_SOURCE_DIR** em `contracts/fonts`, cujo diagnóstico exige `contracts/fontes/`. Os 21 pendentes são **16 MISSING_PARSER** e **5 PACKAGE_IMPORT_NAMESPACE**. Não confundir 21 pendências com 21 erros ou afirmar que criar arquivos vazios resolveria o gate.

## Pendências de parser (16)

| Contrato | Parser requerido |
|---|---|
| contracts/fontes/anvisa_dev.json | packages/cli/parsers/anvisa_dev.py |
| contracts/fontes/anvisa_med.json | packages/cli/parsers/anvisa_med.py |
| contracts/fontes/atlas.json | packages/cli/parsers/atlas.py |
| contracts/fontes/catmat.json | packages/cli/parsers/catmat.py |
| contracts/fontes/cdsi.json | packages/cli/parsers/cdsi.py |
| contracts/fontes/cid10.json | packages/cli/parsers/cid10.py |
| contracts/fontes/cid11.json | packages/cli/parsers/icd11.py |
| contracts/fontes/esavi.json | packages/cli/parsers/esavi.py |
| contracts/fontes/fhir_vitais.json | packages/cli/parsers/fhir.py |
| contracts/fontes/medlineplus.json | packages/cli/parsers/medlineplus.py |
| contracts/fontes/mesh.json | packages/cli/parsers/mesh.py |
| contracts/fontes/pni.json | packages/cli/parsers/pni.py |
| contracts/fontes/sies.json | packages/cli/parsers/sies.py |
| contracts/fontes/sinan.json | packages/cli/parsers/sinan.py |
| contracts/fontes/taco.json | packages/cli/parsers/taco.py |
| contracts/fontes/vacinas_cdc.json | packages/cli/parsers/vacinas.py |

## Pendências de import namespace (5)

`packages/cli/kernel/__init__.py`, `packages/cli/kernel/cli.py`, `packages/cli/kernel/core.py`, `packages/cli/main.py`, `packages/cli/validators/registry.py`. Mensagem do validador: `Import top-level kernel/validators requer validação para python -m packages.cli.main`. Status PENDING, não execução do smoke validada.

## Segundo job

Job 133529482910 (`Canonical contracts and CLI smoke`) confirmou `compile imports, code and tests` PASS, `Run deterministic negative tests` PASS e `Verify canonical source and policy references` FAIL; passos seguintes de smoke SKIPPED. O log também contém findings `MISSING_PARSER`; não afirmar que a falha decorre exclusivamente de referências jurídicas sem análise adicional.

## Decisões e sequência

1. `HOLD_CI_CANONICAL` permanece: investigar por que `contracts/fonts` ainda existe, distinguir legado referenciado de artefato válido e propor migração segura, sem exclusão automática.
2. Validar contrato/implementação real de cada um dos 16 parsers, com fontes, licença, formatos e testes negativos; **não** criar stubs para fazer o gate passar.
3. Testar namespace com `python -m packages.cli.main` em ambiente isolado, com importação e smoke; não mascarar imports nem alterar checks.
4. Reconciliar 5 referências de namespace e 16 parsers com repositório, outros branches e manifesto antes de qualquer alteração de código.
5. Reexecutar gates obrigatórios e obter aceite humano. Sem merge na main, alteração de Supabase, publicação clínica ou promoção sem direitos.

Este relatório é um artefato documental de diagnóstico; CI do presente commit ainda não foi observado. Os denominadores curriculares baseline (65 especialidades, 114 programas, 14/65 representadas em anúncios, 38/1055 microaulas candidatas do subconjunto Trabalho/Urgência) não se alteram.
