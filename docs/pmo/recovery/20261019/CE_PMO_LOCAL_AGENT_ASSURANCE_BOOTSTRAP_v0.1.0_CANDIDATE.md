# CE — Agentes locais, garantia determinística e bootstrap controlado (v0.1.0 CANDIDATE)

**Escopo:** 23 papéis já documentados no PMO (5 PMO, 4 P1, 3 P2, 4 P3, 5 P4, 2 P5). Não são 23 processos persistentes implantados. O censo legado de 110 entradas e os quatro papéis da CLI histórica são populações distintas; identidade SAME_AS continua não comprovada. Nenhum agente novo foi duplicado.

**Status:** LOCAL_CANDIDATE_TESTED; não homologado; nenhuma admissão Kernel; nenhum merge na main; zero alteração Supabase/Drive. O desenvolvimento local isolado constitui bootstrap técnico excepcional sem WO, **não** autoriza uso produtivo nem concessão de permissão. Ao habilitar Kernel, qualquer promoção/integração operacional exige WO, policy, validator e receipt vinculados ao SHA; resultado local anterior é apenas insumo de revisão.

## Fontes normativas e implementação adotada

- NIST AI RMF 1.0, Govern/Map/Measure/Manage: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/ — responsabilidades, risco documentado, avaliações repetíveis.
- NIST AI RMF Playbook: https://www.nist.gov/itl/ai-risk-management-framework/nist-ai-rmf-playbook — operacionalização e medição.
- OWASP Agentic Security Initiative: https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/ — superfície de ferramentas, permissões e encadeamento de agentes.
- SLSA 1.2: https://slsa.dev/spec/v1.2/ — proveniência verificável e controle de artefatos.
- Framework eve: https://eve.dev/docs — referência de durabilidade, ferramentas tipadas, evals; **não implantado** pois o repositório usa CLI Python existente, e migração de plataforma seria expansão desnecessária.

Estas fontes são referências de desenho; não conferem certificação, auditoria independente ou conformidade automática.

## Máquina sequencial comum por processo

1. SNAPSHOT: HEAD Git fixo, origem, hash/versão, direitos e população esperada.
2. ADMISSION_PREFLIGHT: localizar política+validador+tarefa+WO+status; candidato local pode avançar apenas para testes não produtivos; PROD requer receipt criptograficamente verificável, jamais `PREAUTHORIZED` documental.
3. ACQUIRE: agente de fonte/inventário somente leitura; verificar completude do universo, CRC/hash e provenance.
4. TRANSFORM: transformação determinística; preservar originais, conflitos, perdas e abstenções.
5. VALIDATE: controle independente por família, esquema, completude, precisão e regras de domínio; invalidação em falha/ambiguidade.
6. ADVERSARIAL: testes surpresa negativos, mutação de insumo, replay, permissões e limites.
7. AUDIT: recomputação independente e riscos residuais; produtor não assina o próprio output.
8. CANDIDATE_PUBLISH: somente branch isolada, readback SHA e evidência; nunca chamar isto de PROD.
9. AUTHORIZED_PROMOTION: após Kernel+WO+auditoria+aprovação humana, com rollback e observabilidade.

## Cobertura por família

| Frente | Agentes existentes reutilizados | Testes adicionais necessários para precisão |
|---|---|---|
| PMO | controller, publisher, reconciler, guardian, anti-retrabalho | unicidade de IDs, status/cronologia, assinatura de trabalho, readback |
| P1 | hash indexer, ZIP integrity, Git blob mapper, snapshot custodian | CRC real, ZIP slip, tamanho/descompressão, hash Git blob, cadeia de custódia |
| P2 | Git census, delete guard, PR analyst | árvore Git não truncada, ancestry, rename/conflict, retenção de versões, delete quarantine |
| P3 | contract registrar, schema auditor, executor builder, independent auditor | roteamento por schema, runtime validador real, import, exit codes, RBAC, fencing/idempotência |
| P4 | source registrar, norm crosswalk, semantic QA, ingestor lineage, atomizer triage | texto-fonte/direitos, span literal, recall/precision com ground truth, vigência e revisão especialista |
| P5 | evidence auditor, release guard | segregação, população da auditoria, não repúdio, CI efetivo, autorização de promoção |

### Critérios de eficácia de validação

- **Completude estrutural:** `expected_paths` == conjunto real de artefatos; ambas as listas sem duplicados.
- **Integridade de bytes:** SHA-256 e byte_length recalculados de arquivos efetivamente lidos, sem confiar no manifesto.
- **Precisão de domínio:** NÃO coberta pelo validador transversal; exige validador especializado com amostra-ouro independente, matriz de erros, critérios explícitos e revisão humana onde pertinente.
- **Risco residual:** `PASS_BOUNDED` só afirma completude de manifesto e integridade local; não afirma correção semântica, direitos, autenticidade do snapshot Git ou admissão Kernel.

## Matriz de riscos e controles

| Risco | Controle CLI atual | Risco remanescente | Etapa para fechamento |
|---|---|---|---|
| Excluir/omitir arquivos | confronto de conjuntos | população declarada pode estar incompleta | censo independente a partir da árvore Git completa |
| Alteração oculta de conteúdo | hash e tamanho recalculados | hash declarado pode vir de ator comprometido | assinatura de proveniência e referência imutável SLSA |
| Falsa precisão clínica/normativa | bloqueio de alegação sem evidência | qualidade semântica não medida | suítes por domínio com ground truth e perito |
| Autoaprovação | produtor != auditor | identidades são strings auto declaradas | IAM e política de separação com identidade autenticada |
| Receipt falso | PROD sem receipt é FAIL; com receipt não verificado é HOLD | assinatura não validada | integração autoritativa Kernel com assinatura e hash WO |
| Exfiltração/secrets | campo sensível e triagem explícita | triagem booleana auto declarada | scanner independente de conteúdo e direitos |
| Path traversal | path canônico e symlink guard | TOCTOU durante leitura | snapshot imutável e openat seguro |
| Replay e concorrência | nenhuma mutação CLI | locks/idempotência não implementados | transação e fencing em ambiente isolado |

## Execução e limites

```sh
python3 tools/ce_agents/ce_agent_assurance.py catalog-check --catalog contracts/agents/ce_local_catalog_v0.1.0_candidate.json
python3 tools/ce_agents/ce_agent_assurance.py audit --catalog contracts/agents/ce_local_catalog_v0.1.0_candidate.json --manifest SAMPLE.json --root IMMUTABLE_SNAPSHOT
python3 -m unittest discover -s tools/ce_agents -p 'test_*.py' -v
```

Exit codes: 0=PASS_BOUNDED; 2=FAIL; 78=HOLD. CLI não grava evidências nem cria arquivos. O resultado JSON deve ser armazenado separadamente pelo publicador, com commit/readback.

**Testes executados em 2026-10-19:** 16/16 testes Python de fixtures sintéticas PASS, em ambiente isolado; incluem arquivo adulterado/ausente, duplicata, autoauditoria, agente não registrado, receipt ausente e forjado, SHA de snapshot não fixo, triagem de secrets, revisão clínica, precisão sem lastro, path traversal, registro duplicado, falsa implantação e processo desconhecido. Evidência: saída Python `Ran 16 tests ... OK` observada nesta sessão. Não confundir com CI remoto executado.

**FINDs candidatos para reconciliação (sem duplicação):** CI/validator registry stubs; inconsistência de 17 versus 11 FINDs na WO; dependência de origem para snapshot; lacunas RBAC/concurrency; semântica P4. Referenciar FIND original antes de abrir IDs novos.

**Fila remanescente:** validações especializadas P1 a P5, provas de completude contra universos independentes, testes surpresa adicionais, CI real, auditoria independente, integração Kernel/WO, hardening e promoção. Nada foi declarado 100%.
