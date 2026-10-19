# CE — P5: plano de auditoria independente, fechamento e autorização

**Data de referência:** 2026-10-19. **Classificação:** CANDIDATE / READ_ONLY_REVIEW / NO_KERNEL_ADMISSION / NO_RELEASE. **Repositório:** `IndiciumFIN/calculadorasdeenfermagem`. **Branch documental inspecionada:** `pmo/recovery-controlled-20261019`. Esta proposta não é parecer de homologação nem comprova execução de testes futuros.

## Fontes lidas e limites

- GitHub `docs/pmo/recovery/20261019/CE_PMO_REGISTRO_MESTRE_20261019_v0.1.0_CANDIDATE.json`, ref `pmo/recovery-controlled-20261019`, readback em 2026-10-19; contém `pmo_trusted=false`, `project_execution_allowed=false`, 8 gates HOLD, P1 4/6, 15/15 árvores fixadas e `POP-M24-HOLD` com 5 arquivos, 0 aprovados.
- GitHub `CE_PMO_PARECER_INDEPENDENTE_VALIDACAO_20261019_CANDIDATE.md`: 17 testes estruturais PASS, 4–5 HOLD de prova; o relatório foi emitido antes dos avanços P1-B/P1-C e deve ser reexecutado sobre versões/SHAs novos, não tratado como homologação corrente.
- GitHub `CE_PMO_GUARDIAN_POLICY_P1_20261019_CANDIDATE.md`: 15 testes históricos PASS locais; afirma expressamente que o guardião CLI ainda pode ser contornado e necessita integração verificada. Sua anotação de CRC pendente também é histórica (P1-B reporta verificação posterior); reconciliar a cronologia antes de encerrá-la.
- GitHub `CE_PMO_FIND_GIT_TREES_PROGRESSO_P1CB_20261019_CANDIDATE.md`: 15/15 árvores, 58.710 *ocorrências* de blob, 4/6 verificações técnicas P1; P1-C-C/D ainda pendentes.
- Local `CE_M20_KERNEL_EXECUTORES_AUDIT_CANDIDATE.md` e `CE_M21_CONTENCAO_KERNEL_E_TRILHO_CONTEUDO_CANDIDATE.md`: execução fictícia do Kernel contida por `exit 78`, mas dispatcher/admissão e testes reais não demonstrados; testes estáticos não são testes transacionais.
- Local `CE_M11_AUDITORIA_REAL_PROCESSO_DOCUMENTACAO_REFERENCIAIS_v0.1.0_CANDIDATE.md`: 27/27 objetos ZIP normativo conferidos, somente 10 atomizações normativas candidatas naquele pacote; textos ISO/COSO/COBIT, direitos e teste ponta a ponta incompletos. Resultados históricos requerem readback da versão vigente.
- **CE-06 histórico**: referência a 21 controles (3 PASS, 6 FAIL, 12 HOLD_HUMAN) aparece no handoff/contexto, mas o parecer autoritativo vigente e a reavaliação das 74 incorporações CE-02 ainda não foram lidos nesta revisão. **Não converter esse histórico em status atual ou 21/21 testados.**

## Agente P5: independência e limites

**P5-AUDITOR-INDEPENDENTE (ACK:AUDITOR/VALIDATION):** só lê snapshots imutáveis e emite parecer; jamais modifica evidências auditadas, aprova sua própria execução ou exerce papel de publicador. **P5-QA-NEGATIVO (ACK:VALIDATION):** roda testes controlados com fixtures sintéticos; não escreve nos dados reais. **P5-CUSTODIAN-RECEIPTS (ACK:WATCHER):** confere recibos externos de commit/sha/readback/restore, sem poder emitir sozinho PASS de gate. **P5-RELEASE-GUARD (ACK:GUARDIAN):** avalia policy-as-code fail-closed, emite DENY/ALLOW_CANDIDATE; não possui credencial de promoção ou bypass. **Único integrador/documentador:** PMO-CONTROLLER/PUBLISHER com serialização, guardião antes do commit e auditor depois. A identidade humana/aprovação de negócio permanece com Leivis ao final.

## Sequência de microtarefas P5 (pode preparar em paralelo com P1–P4)

| ID | Microtarefa executável | Entrada congelada | Saída/evidência exigida | Estado atual |
|---|---|---|---|---|
| P5-01 | Contrato da auditoria e golden negative corpus | Schemas PMO, políticas, matriz gates, SHAs da branch | `P5_AUDIT_CONTRACT.json` + fixtures sintéticos e hashes | PREPARABLE_READ_ONLY |
| P5-02 | Regressão do inventário/PMO | P1 snapshots, ZIP CRC, branch tree, recibos | Test runner com verdict por caso, stdout, exit code, cutoff e versão do executor | P1_COMPLETENESS_HOLD |
| P5-03 | Reconciliação independente de provas e populações | P1/P2/P3/P4 outputs, CE-02/04/06, fontes originais por hash | `REQUIRED×PRESENT×VALIDATED×PASS` por fonte/ID e divergência classificada | DEPENDS_ON_P1_TO_P4 |
| P5-04 | Segurança/regras de publicação | Branch protection/rulesets readback, CI workflows, guardião CLI | Ensaios read-only de configuração e teste de PR isolado **somente após autorização da cadeia pertinente** | CONFIG_READ_ALLOWED; CI_WRITE_HOLD |
| P5-05 | Corpus clínico/documental e direitos | 65 itens CE04, fontes, licença, jur./edição, 7 grandes, M24 | Parecer de amostragem estratificada e exceções por cláusula/claim; dono clínico/jurídico distinto | M24_AND_SEMANTIC_HOLD |
| P5-06 | Kernel/WO e end-to-end operacional | FIND→política→validador→tarefa→WO→admissão Kernel, tickets, logs | Recibo autoritativo, testes concorrência/idempotência/segredo, logs em ambiente isolado | KERNEL_REAL_HOLD |
| P5-07 | Site e content-pack | F4 37/37 unit, build e E2E pendente; revisão atual do código | Testes Playwright E2E reais, checksum, i18n, accessibility, prevenção admin→public | E2E_HOLD |
| P5-08 | Restauração e parecer final PMO | Manifesto completo, hashes, recibos independentes, backup acessível | Restore controlado dos artefatos PMO, comparação byte-a-byte, parecer assinado e recomendação de gates | FINAL_HOLD |

### Matriz dos oito gates com regra objetiva

| Gate | Para sair de HOLD | Veto/independência |
|---|---|---|
| G-PMO-01 | Todo universo com população, cutoff, fonte, `path+sha256+size` e cobertura demonstrada Git/ZIP/ambiente; ausência explicada | `UNKNOWN`/árvore parcial/ZIP aninhado não verificado impede PASS |
| G-PMO-02 | Registro de identidades e aliases cruzando 15 branches observadas, quatro PRs, snapshots e WOs sem misturar populações | Mesma ID com SHA divergente sem conflito explícito impede PASS |
| G-PMO-03 | Recomputação independente dos bytes originais e correspondência Git blob/SHA256, incluindo payload ZIP | Somente CRC/metadados ou contagem agregada impede PASS |
| G-PMO-04 | Cada FIND aberto tem risco, política, validador, tarefa, WO, evidências, responsável e estado; histórico duplicado ligado sem encerramento indevido | Repetição M42/M44 ou WO admitida sem recibo impede PASS |
| G-PMO-05 | Prova de autorização específica para cada classe de ação; exceção documental PMO claramente apartada de produção | `NO_KERNEL` produtivo, bypass ou alteração main impede PASS |
| G-PMO-06 | Suíte adversarial determinística e reexecutada sobre versão corrente, com logs/exit codes e rejeição de casos negativos | Testes meramente estruturais ou executados em versão antiga impedem PASS |
| G-PMO-07 | Commits versionados, readbacks externos, recibos apend-only, restauração isolada e comparação exata; custódia de ZIP local comprovada externamente | Autocertificação, snapshot mutável e hash não conferido impedem PASS |
| G-PMO-08 | Parecer de auditor distinto de executor/publicador; evidências completas, ressalvas, responsabilidades e aprovação humana no momento correto | Auditor aprovando artefato próprio ou aprovação de negócio antecipada impede PASS |

## Regressão adversarial mínima (fixtures fabricados, nunca produção)

1. `NEG-01`: arquivo em manifesto com SHA256 falso → **DENY**.
2. `NEG-02`: o mesmo caminho repetido com conteúdo ou origem conflitante → **DENY**.
3. `NEG-03`: duas populações indevidamente somadas (`58.710` ocorrências de blob tratadas como 58.710 únicos; `768` snapshot substituído por `771`) → **DENY**.
4. `NEG-04`: ZIP traversal `../`, caminho absoluto, symlink, bomba de expansão, aninhado inseguro ou CRC corrupto → **DENY/HOLD**.
5. `NEG-05`: `M24` com 5 itens marcado como processado/approved → **DENY**.
6. `NEG-06`: gate PASS com prova ausente, URL quebrada ou cutoff incorreto → **DENY**.
7. `NEG-07`: recibo Git sem readback, arquivo modificado após hash, commit duplicado/obsoleto ou CAS inválido → **DENY**.
8. `NEG-08`: publicador ou executor emitindo seu próprio parecer independente → **DENY**.
9. `NEG-09`: API/WO Kernel simulado emitindo `SUCCESS` falso ou `exit 0` sem admissão → **DENY**.
10. `NEG-10`: publicação contendo segredo, dado sensível, licença não esclarecida ou conteúdo protegido não autorizado → **DENY**.
11. `NEG-11`: tentativa de merge, escrita na main, exclusão/force push ou promoção sem autorização → **DENY**.
12. `NEG-12`: conteúdo atomizado sem vínculo source→edição→licença→segmento→claim→revisão clínica; erro de calculadora clínica em golden cases → **DENY/HOLD**.
13. `NEG-13`: E2E Playwright falha ou checker de checksum desativado → **DENY RELEASE**, independentemente de unit tests/build PASS.
14. `NEG-14`: controle de CI somente documental mas anunciado como obrigatório, ou branch protection não lida → **DENY CLAIM**.

**Critério de aceitação da suíte:** 100% de rejeição dos casos proibidos, 100% de aceitação dos casos sintéticos válidos, registros completos de versão/input SHA/semente/runner/stdout/stderr/exit code; nenhum teste em produção sem a cadeia de governança. Testes PASS de scripts locais não certificam integração obrigatória à CI.

## Cadeia normativa e operacional antes de qualquer mutação não documental

`FIND → política aplicável → ajuste/criação do validador → tarefa → WO → admissão verificável do Kernel → execução isolada → testes → auditoria → promoção autorizada`. Caso o processo/política não exista, a WO de criação requer fluxo de pré-admissão governado; não presumir que ausência de política permite bypass. Exceção de 2026-10-19 cobre **somente publicação documental PMO** na branch dedicada com guard/readback; não libera conteúdo, banco, CI, Kernel, site público, main ou M24.

## Governança do progresso

- Publicar sempre denominador e objeto: P1 = **4/6 verificações técnicas (66,7%)** no snapshot inspecionado; PMO gate = **0/8 (0%)**; projeto CE completo = **sem denominador confiável**.
- P5 `PREPARABLE_READ_ONLY` não deve virar `EXECUTED` até existirem logs, hashes e recibos novos. Uma matriz pode conter `NOT_APPLICABLE` com justificativa, `HOLD`, `FAIL` ou `PASS` apenas quando a prova for inequívoca.
- M24: 5 arquivos `HOLD`, 0 aprovados. Sete arquivos grandes e direitos clínicos/legais devem permanecer segregados dos 53 itens apenas estruturalmente processados; nenhum deles é automaticamente homologado.
- Publicar `FIND_ID`, causa raiz, risco, correção proposta, teste de regressão, evidência e lição aprendida; manter apend-only e referência ao commit; não sobrescrever histórico.
- **STOP** se evidências de branch/PR forem truncadas, hashes divergirem, permissionamento não puder ser comprovado, segredo detectado, guard bypassado, executor=auditor ou runtime Kernel responder sucesso fictício.

## Entregáveis P5 finais

1. `CE_P5_AUDIT_CONTRACT_v01_CANDIDATE.json` e `CE_P5_GOLDEN_NEGATIVE_FIXTURES_v01`.
2. `CE_P5_MATRIX_REQUIRED_PRESENT_VALIDATED_PASS_v01_CANDIDATE.json` com IDs, evidência, cutoff, owner e resultado por controle.
3. `CE_P5_ADVERSARIAL_RUN_RECEIPTS_v01_CANDIDATE.jsonl` + executor/runner versionado e logs redigidos.
4. `CE_P5_GATES_VERDICT_v01_CANDIDATE.json` + `CE_P5_FIND_CAPA_LEDGER_v01_CANDIDATE.jsonl`.
5. `CE_P5_RESTORE_PROOF_v01_CANDIDATE.json` e `CE_P5_INDEPENDENT_OPINION_v01_CANDIDATE.md`.

**Nota de autoridade:** nenhum desses entregáveis foi executado ou publicado por este plano. Primeiro reproduzir P1-C-C/D e P2–P4 com evidência de corte; depois emitir parecer P5, mantendo os bloqueios reais e a aprovação final do proprietário.
