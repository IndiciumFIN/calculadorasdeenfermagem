# CE PMO — P2: reconciliação Git determinística (CANDIDATE)

Data de corte: 2026-10-19. Escopo: `IndiciumFIN/calculadorasdeenfermagem`. **READ_ONLY / SEM MERGE / SEM EXCLUSÃO / SEM PROMOÇÃO.** Esta é uma proposta técnica de execução, não uma admissão de WO ou homologação.

## Baseline verificada e distinção das populações

1. O manifesto [P1-C-B](CE_PMO_GIT_BRANCH_TREES_P1CB_20261019_CANDIDATE.json) fixa **15 branches/15 árvores completas** e **58.710 ocorrências de blobs** (soma das árvores, não quantidade de blobs únicos). As árvores gigantes foram enumeradas segmentadamente, não apenas pelo compare limitado a 300 arquivos. A branch de PMO era `142987e59bbce7c7278fac1c26d71f8dbc1172c7` nesse corte: deve ser recapturada por ser mutável.
2. `main`: `e0f62491b104f4a97c6025a6393cabc2e7ada30e`; `integration/canonical-main-20261017`: `c704c3cf9241cde7697acb860e598bd01bd58cf5`; `migration/candidate-f08-20261017`: `e7add8e510077c2ea4c0591cdafe2440c1ffd418` (19.136 ocorrências); `migration/full-directory-20261017`: `bad54d1d9b6d281a0a2bb8077895e2ad45571b68` (19.119 ocorrências); `cursor/drive-sa-key-refactor`: `fc857df8306b81915f191d3f0744f7a322047b21` (9.366); `cursor/fix-governance-gaps-ec54`: `bb6debeef44a15964becd19990a502d7e0c0beaf` (9.387).
3. Nova consulta da API GitHub `search_branches` em 19/10 retorna os mesmos **15 nomes**. A consulta não devolveu HEADs; não equivale a revalidação de imutabilidade, portanto comparar cada HEAD ao corte antes de classificar.
4. PRs consultados diretamente: [#2](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/2) aberto/draft, cabeça `cursor/fix-governance-gaps-ec54`, base `main`, `mergeable=false` no instante consultado; [#3](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/3) aberto/draft, CLI parcial **7/46** arquivos da distribuição; [#4](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/4) aberto/não draft, **base é `cursor/fix-governance-gaps-ec54` (não `main`)**, cabeça `cursor/drive-sa-key-refactor`, dez arquivos alterados; [#6](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/6) aberto/draft, nove políticas candidatas, `HOLD_HUMAN_NOT_CANONICAL`. Os estados `mergeable` não constituem autorização.
5. `compare(main, integration/canonical-main)` confirmado agora: 44 caminhos alterados incluindo **22 remoções propostas** (21 `contracts/fonts/*` e `test.txt`); adições/modificações no Kernel, validadores, workflows e scripts. **FIND-P2-DEL-001**, bloqueio de qualquer aplicação automática dessas exclusões.
6. PR #4 lista `.github/workflows/drive-recursive-collect.yml`, `config/drive_inventory_roots_20261016.json`, `docs/{DETERMINISTIC_RULES,GATES,GOVERNANCE,PLANO_EXECUCAO_WO_KERNEL_DETERMINISTICO}.md`, `packages/cli/{drive_recursive_inventory.py,requirements.txt}`, `tests/test_drive_recursive_inventory.py`, `wf_probe.md`. Mudança de autenticação/raízes requer segurança e confronto de sobreposição com #2. O corpo do PR relata alteração de quatro para duas raízes Drive; **não reabrir aquisição Drive neste plano**, apenas controlar a variante e risco de cobertura.

## Contrato de registro P2-OBJ v0.1

Cada unidade de reconciliação é uma **ocorrência de árvore**, identificada por `(repo, branch, pinned_head_sha, tree_sha, path, git_blob_sha, mode, size)`. Complementos exigidos: SHA-256 bruto quando bytes acessíveis; origem/snapshot e ZIP associado; tipo `CODE|POLICY|NORMATIVE|CONTENT|CI|EVIDENCE|BINARY|OTHER`; classificação `BYTE_IDENTICAL|SAME_PATH_DIFFERENT_BYTES|UNIQUE_PATH|RENAMED_CONTENT|PROPOSED_DELETION|UNKNOWN`; proveniência, licença/segredo e sensibilidade; status `OPEN|CLASSIFIED|CONFLICT_HOLD|APPROVED_WITH_EVIDENCE`; decisão não destrutiva com autor, data, FIND/WO, validadores, artefatos de teste e recibo de readback. Não presumir SHA-256 = blob SHA-1, nem somar versões como conteúdos únicos.

## Agentes especializados e microlotes concorrentes

| Microlote | Executor especializado | Trabalho determinístico / aceite | Dependência |
| --- | --- | --- | --- |
| P2-00 | Git Census | Revalidar 15 HEADs e árvore por SHA; status PR e ruleset CI; qualquer desvio gera corte novo e FIND | P1-C-B; somente leitura |
| P2-01 | Git Dedup | Exportar 58.710 ocorrências sob árvore congelada, agrupar por `(git_blob_sha,mode)` e depois SHA-256 de bytes; totais **únicos apurados**, não estimados | P2-00 |
| P2-02 | Snapshot Differential | Confrontar os dois snapshots `migration/*` por path+blob e os cinco snapshots históricos; cada variante e exclusivo rastreado | P2-01 |
| P2-03 | PR Change Analyst | Diffs completos #2/#3/#4/#6, matriz de sobreposição e dependência #4→#2; não tratar `changed_files=0` de #2 como ausência de alterações (metadado potencialmente truncado) | P2-00 |
| P2-04 | Guardião de Exclusões | Quarentena das 22 remoções, workflows CI removidos/alterados e operações `move/retirada`; teste negativo de proposta destrutiva | P2-00; P2-03 |
| P2-05 | Cross-source Mapper | Confrontar blob Git/bytes às populações P1: 768 arquivos locais (snapshot), 1.956 entradas ZIP, 674 conteúdos ZIP sem equivalente solto, sem equiparar universos | P2-01; P1-C-A |
| P2-06 | Decision Registrar | Produzir matriz por objeto e branch com status e FIND; nenhuma classificação omissa; conflitos preservados | P2-02..05 |
| P2-07 | Auditor independente | Recomputa números, provoca alterações de HEAD, remoção simulada, duplicidade, symlink, conflito path, segredo e auditor=executor; gera PASS/FAIL/HOLD por evidência | P2-06 |

Agentes executores leem e propõem artefatos isolados; apenas publicador designado atualiza **branch documental autorizada**, após guardião e auditor. Mutações operacionais exigem cadeia **FIND → política → validador → tarefa → WO → admissão real pelo Kernel → execução isolada → testes → auditoria → publicação/Readback**. Exceção vigente de PMO documental **não** libera merge/CI/rulesets/produção.

## Critérios de saída e gates

- `G-P2-01` PASS: 15/15 refs HEAD/tree validadas com cutoff e nenhuma árvore truncada, ou desvio explicitamente versionado.
- `G-P2-02` PASS: 100% das ocorrências de árvores com identidade de objeto e classificação; denominadores por população (**ocorrências**, **blobs únicos**, **paths únicos**, **versões divergentes**, **membros ZIP**) informados separadamente.
- `G-P2-03` PASS: PR #2/#3/#4/#6 avaliados com dependências; PR #4 nunca aplicado isoladamente contra `main`.
- `G-P2-04` PASS: 22/22 remoções candidatas e remoções de workflows classificadas sob quarentena, sem execução; revisão de segredos/direitos.
- `G-P2-05` PASS: matriz P1↔P2 por hash com `MISSING`, `MATCH`, `UNCONFIRMED`, sem afirmar que conteúdo exclusivo ZIP está ausente do Git.
- `G-P2-06` PASS: relatório de auditoria independente com testes negativos e recibos Git readback do PMO.
- **HOLD** obrigatório: ambiguidades materiais, variantes conflitantes, ausência de licença/admissão Kernel, tentativa de alteração em main, deleção ou force-push.

**Estado atual P2:** baseline de árvores e status PRs consultados; P2-01..07 não demonstrados como executados neste microlote. O corte do PMO deve ser atualizado pelo controlador ao integrar o plano. Este documento não certifica 100% de P2.
