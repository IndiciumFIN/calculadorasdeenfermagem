# CKO W7 — reconciliação canônica e registro de achados v0.2.0

**CANDIDATE / HOLD_RIGHTS / HOLD_CURRICULUM / HOLD_NORMATIVE / HOLD_CLINICAL / HOLD_RULESET / NO_GO**

Esta é uma **prévia para versionamento na branch exclusiva** `review/cko-w7-public-evidence-20261114`. Ela não é uma publicação clínica, um laudo de revisão humana ou aprovação da grade curricular.

## O que foi conferido
- 46/46 claims M08/M09 ligados a evidências por IDs, localizadores, SHA-256 de texto e documento recalculados contra o corpus Drive **sem textos primários no Git**.
- 162/162 itens curriculares da seleção W7 com IDs conferidos contra `curriculum_items.jsonl`, `postgraduate_programs.jsonl` e seus **274 mapeamentos**; contexto curricular ≠ homologação.
- 9.102 links `EvidenceAtom→Topic` seguem candidatos, sem associação canônica aprovada.
- 8/8 NormAtoms W5 sem hash de trecho primário; 6/6 fontes W6 sem fragment SHA; nenhum encerramento por QA estrutural.
- Supabase: 17 PDFs atomizados em metadados, 25.508 átomos literais e 887 referências visuais; localização dos JSONLs não durável; não somar automaticamente com os 28.001 do Drive.
- **59 achados estruturados ({'P0': 29, 'P1': 28, 'P2': 2})** e **12 WOs** para tratamento por fonte, conteúdo e gate.

## Conteúdo e fronteiras
A pasta mantém o corpus W7 inicial mais os novos registros `audit/` (metadados, provas, WOs, histórico de fontes/PRs, QAs). Não há PDF/HTML integral de terceiros, texto literal dos 28.001 átomos ou segredos neste recorte.

Normativo/grade/clinical rights humanos independentes continuam pendentes. `RIGHTS_PASS` não é inferido de texto público; `EVIDENCE_BOUND` não é `ASSURED`.

## Histórico GitHub e bloqueio
- Repository: <https://github.com/IndiciumFIN/calculadorasdeenfermagem>; `main` observada no commit `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.
- Branch de destino: `review/cko-w7-public-evidence-20261114` (ainda **não criada no remoto**).
- Ruleset ativo [#25580067](https://github.com/IndiciumFIN/calculadorasdeenfermagem/rules/25580067) bloqueia `creation`, `update`, `deletion` e `non_fast_forward` para `~ALL`.
- Aberta [Issue #69](https://github.com/IndiciumFIN/calculadorasdeenfermagem/issues/69); este pacote é versão de trabalho, não commit remoto.
- Não desabilitar política nem alterar main: após exceção específica, aplicar patches testados à branch exclusiva e abrir PR draft se solicitado.

## Arquivos novos
- `audit/FINDINGS_REGISTER_v0.2.0.csv` / `.jsonl` — todos os achados W1–W7 identificados nos artefatos inspecionados, com severidade e provenance refs.
- `audit/WORK_ORDER_BACKLOG_v0.2.0.csv` — 12 microtarefas com cobertura mensurável, gates e owner_role.
- `audit/46_PROVENANCE_RECHECK_INDEPENDENT_v0.2.0.jsonl` — nova leitura dos 46 vínculos M08/M09 com hash recalculado.
- `audit/CURRICULUM_EXACT_JOIN_VERIFICATION_v0.2.0.jsonl` — 162 junções curriculares rechecadas.
- `audit/SOURCE_PACKAGE_INDEX_v0.2.0.csv` — inventário e SHA-256 de M08/M09 e W1–W7 (não anexar arquivos completos de origem).
- `audit/GITHUB_BASELINE_v0.2.0.json` e `audit/SUPABASE_READONLY_BASELINE_v0.2.0.json` — snapshots de inspeção, sem mutação.
- `audit/CURRICULUM_SOURCE_BASELINE_v0.2.0.json`, `audit/QA_EVIDENCE_REPLAY_v0.2.0.json`, `audit/EXECUTIVE_SUMMARY_v0.2.0.json`.
- `PUBLICATION_GATE_v0.2.0.json` — fail-closed até assinatura humana.

## Critério de integração futura
Após liberação **somente** da branch W7, conferir diff, subir commit, CI, review de rights e PR draft; merge na main apenas em atividade separada e autorizada. O fato de a branch ser pública não autoriza incorporar textos protegidos. 
