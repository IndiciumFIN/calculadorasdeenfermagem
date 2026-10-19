# CE — Plano integrado P1–P5 com agentes especializados

**Cutoff:** 2026-10-19; reanálise read-only de `IndiciumFIN/calculadorasdeenfermagem` e evidências locais. **Escopo autorizado de gravação:** apenas candidatos documentais PMO na branch `pmo/recovery-controlled-20261019`, com guardião, SHA, commit e readback. Não autoriza CI produtiva, Kernel fictício, execução de conteúdo, merge, exclusão nem `main`.

## Situação recalculada neste ciclo

| Objeto medido | Progresso | Interpretação |
|---|---:|---|
| P1, seis checkpoints técnicos | **5/6 = 83,3%** | Inventário local, CRC ZIP, SHA local–ZIP, árvore Git, cruzamento Git blob concluidos tecnicamente; falta decisão de variantes/conflitos e custódia |
| Censo Git por branch fixada | **15/15 = 100%** | 58.710 *ocorrências* e **9.569 blobs únicos** entre as 15 árvores pinadas; não é cobertura clínica/documental |
| Integridade ZIP externa local | **13/13 = 100%** | 1.956 CRC verificados; nested ZIP e direitos não aceitos |
| CE04 estrutural histórico | **53/65 = 81,54%** | Não é aprovação clínica, de licença nem semântica |
| Gates PMO homologados | **0/8 = 0%** | Oito HOLD, ainda sem parecer final independente |
| Projeto CE integral | **indeterminado** | Não inventar percentual antes de população final reconciliada e critérios de aceite |

Novo P1-C-C: apurados SHA-1 no namespace real `git blob` dos arquivos locais e de cada membro ZIP (não confundir com SHA256). Na população pinada: **9.569** objetos Git únicos; **742** objetos locais únicos; **1.295** objetos ZIP únicos; interseção `Git∩local=30`, `Git∩ZIP=11`, `Git∩local∩ZIP=11`. Os **1.284 membros de conteúdo ZIP únicos sem blob individual equivalente no Git** não são presumidos perdidos: podem estar dentro de ZIP Git, serem transformações, LFS ou versões fora do tip. Classificá-los sob revisão e custódia antes de qualquer conclusão.

## Workstreams e delegação

| Frente | Executor(es) determinísticos propostos | Microlotes preparáveis agora | Dependências para homologação / produção |
|---|---|---|---|
| **P1 — Custódia e identidade** | `HASH-INDEXER`, `ZIP-INTEGRITY`, `GIT-BLOB-MAPPER`, `SNAPSHOT-CUSTODIAN` | P1-C-D variantes e aliases; P1-D manifesto privado imutável, triagem de direitos, recibos | Sem exclusão, precisa de P2 + auditor P5 |
| **P2 — Git e branches** | `GIT-CENSUS`, `SNAPSHOT-DIFF`, `PR-ANALYST`, `DELETE-GUARD`, `GIT-AUDITOR` | P2-00..P2-07: árvores, PRs, sobreposições, 22 remoções sob quarentena e decisões | P1 blobs; mudanças reais somente com WO/Kernel |
| **P3 — Contratos e executores** | `CONTRACT-REGISTRAR`, `WO-RECONCILER`, `POLICY-VALIDATOR`, `RUNTIME-GUARD`, `AGENT-AUDITOR` | P3-A..P3-F: separar 38 tarefas, 76 WOs PR2, 102 históricas; stubs, policies, teste negativo, anti-retrabalho | Admissão Kernel real antes de ativar executores e CI |
| **P4 — Conteúdo e normativos** | `SOURCE-REGISTRAR`, `RIGHTS-GUARDIAN`, `NORM-CROSSWALK`, `SEMANTIC-QA`, `INDEPENDENT-AUDITOR` | P4-A/B/C/D/F: fontes, 61 objetos/49 URLs, 285 semânticos, fontes normativas ISO/COSO, schema | P4-E1..E7 só com WO+Kernel; 5 M24 em HOLD |
| **P5 — Qualidade e auditoria** | `NEGATIVE-QA`, `EVIDENCE-AUDITOR`, `RECEIPT-CUSTODIAN`, `RELEASE-GUARD` | P5-01/02 e preparação P5-03..08; golden tests, verificações read-only, matriz por objeto | Não certifica P1–P4 incompletos; restauração, Kernel/CI/E2E e aprovação final pendentes |

Arquivos-fonte dos planos especializados:

- `CE_PMO_PLANO_P2_RECON_20261019_CANDIDATE.md`
- `CE_PMO_PLANO_P3_AGENTES_20261019_CANDIDATE.md`
- `CE_PMO_PLANO_P4_CONTEUDO_20261019_CANDIDATE.md`
- `CE_PMO_PLANO_P5_AUDITORIA_20261019_CANDIDATE.md`

## Paralelismo efetivo e controle de publicação

1. **Quatro agentes especialistas analíticos** P2/P3/P4/P5 operam em READ_ONLY e arquivos candidatos separados. Eles já produziram os planos acima neste ciclo, mas **não** implantaram tarefas futuras.
2. **P1 e P2** trabalham sobre HEADs pinados e populações com `branch+commit+path+blob`, sem misturar ocorrências com objetos únicos.
3. **P3 e P4** podem criar catálogos normativos, direitos, schemas e golden fixtures em paralelo, mas nenhuma atomização/executor produtivo roda sem `FIND→política→validador→tarefa→WO→Kernel real→isolamento→testes→auditoria→publicação`.
4. **P5** analisa os artefatos após cada microlote sem ser o mesmo agente que produziu a evidência.
5. **GUARDIAN** emite `DENY/PASS_PREFLIGHT_ONLY`; **PUBLISHER** sozinho versiona documentos aprovados no escopo; **PMO-CONTROLLER** sozinho atualiza o mestre com CAS; recibo externo apend-only fecha cada grupo de commits.
6. Sem CI obrigatória instalada, o guardião ainda é uma etapa procedimental; **não anunciar enforcement servidor**. Instalação de workflow/branch protection é atividade operacional controlada.

## Prioridade por wave, sem esperar o encerramento integral de P1

| Ordem de início | Faixas paralelas | Saída objetiva |
|---|---|---|
| Imediato | P1-C-D; P2-00/01; P3-A/B; P4-A/D; P5-01 | Identidades e contratos, direitos, fixture e matriz de lacunas documentais |
| Após hashes e identidade | P2-02..05; P3-C/D; P4-B/C/F; P5-02/03 | Conflitos/versionamento, policies, cláusulas aplicáveis, regressão do PMO |
| Após classificação | P1-D; P2-06/07; P3-E/F preparatório; P4-F; P5-04/05 | Snapshot privado versionado, controles de segurança e pareceres preparatórios |
| Somente após autoridade técnica | P3 runtime/CI; P4-E1..E7; P5-06/07/08 | Execuções reais com WO/Kernel, testes independentes, restauração e aceite final |

## Segurança, HOLDs e prazo

- 22 propostas de exclusão da integração Git **bloqueadas** (21 `contracts/fonts/*` + `test.txt`). PR #4 depende de branch do PR #2; PR #3 CLI parcial 7/46; PR #6 9 políticas em HOLD.
- M20 encontrou 14/14 stubs e problemas policy/RBAC; M21 `exit 78` local não atesta runtime.
- P4: 7 arquivos grandes e 5 M24; 0/65 homologação clínica/legal comprovada pela cadeia M43, 285 ressalvas, 61 fontes sem licença explícita nos objetos; cláusulas ISO aplicáveis sem denominador validado, logo sem % normativa confiável.
- P5: 8/8 gates PMO HOLD; historicamente CE06 3 PASS/6 FAIL/12 HOLD não equivale a novo parecer; F4 E2E pendente.
- Percentuais são sempre por população e estado; não derivar “% do projeto” de subetapas heterogêneas.

**Decisão desta rodada:** planos P2–P5 produzidos e submetidos como candidatos documentais; P1-C-C concluiu comparação exata por identidade Git, mas ainda falta a matriz de variantes e custódia. Toda aprovação de negócio permanece reservada ao usuário no encerramento.
