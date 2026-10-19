# CE PMO — Plano executável P4: conteúdo, aquisição, atomização e normas

**Corte:** 2026-10-19 (Brasil). **Estado:** `CANDIDATE / PLAN_ONLY`; diagnóstico read-only local, cotejado com Registro Mestre da branch `pmo/recovery-controlled-20261019` por `github_fetch_file`. **Não representa WO admitida, aprovação clínica/normativa, execução produtiva ou implantação em CI.** Sem consultas ao Drive, exclusão de fontes ou promoção à main.

## 1. Baseline por população — não confundir numeradores

| População | Numerador / denominador | Interpretação estrita | Fonte local |
| --- | ---: | --- | --- |
| CE04 processamento estrutural | **53/65 = 81,54%** | JSONL já verificados estruturalmente até M43; NÃO significa avaliação clínica, direitos ou publicação | `CE_M43_CID11_CATEGORIAS_STREAMING_SEMANTIC_HOLDS_v0.1.0_CANDIDATE.md` |
| CE04 saldo estrutural | **12/65 = 18,46%** | **7 grandes** elegíveis apenas para planejamento + **5 M24 HOLD** não executáveis | M43 |
| Grandes não-M24 | **0/7 finalizados neste plano**, 333.906 registros manifestados | Conteúdo pendente; bytes e registros são expectativa de manifesto, confirmar ao executar | `CE_M40_ULTIMO_MICROLOTE_MEDIO_INVENTARIO_REMANTENTE_v0.1.0_CANDIDATE.md` |
| M24 | **0/5 liberados** | Mantidos `HOLD_ENVIRONMENT` sem exceção implícita | M40–M43 |
| CID-11 ressalvas semânticas | **285/285 abertas para triagem neste corte** | 285 findings de saída de atomizador M43; não interpretar como 285 registros clínicos incorretos | M43 |
| Referências de origem CE04 | **61 objetos `fontes` / 49 URLs** | 61/61 sem *campo explícito* de licença **dentro desses objetos**; direitos podem constar em outra evidência | `CE_M26_PROVENIENCIA_DOMINIOS_CE04_READBACK_v0.1.0_CANDIDATE.md` |
| Aprovação clínica/legal CE04 | **0/65 comprovadas pela frente M43** | Denominador de fonte, não de revisão individual; evitar conclusão de ausência global | M43 |
| Cláusulas ISO e materiais normativos | **denominador desconhecido** | O ZIP de agentes tinha 10 instrumentos com átomos candidatos e 17 apenas metadados; pacote COSO separado: 734 átomos candidatos; sem texto e licença integrais elegíveis não calcular conformidade | `CE_M11_AUDITORIA_REAL_PROCESSO_DOCUMENTACAO_REFERENCIAIS_v0.1.0_CANDIDATE.md` |

Sete itens grandes ainda pendentes (manifesto M40): `mesh/descritor_mesh.jsonl` (40.798.270 bytes, 31.110 registros); `medicamentos/apresentacao_cmed.jsonl` (60.737.486, 26.635); `medicamentos/produto_fda_ndc.parte-0002.jsonl` (62.444.010, 56.492); `suprimentos/item_catmat.jsonl` (72.026.196, 59.938); `nutricao/alimento_usda_sr_legacy.jsonl` (73.915.846, 7.793); `dispositivos/registro_anvisa_produto_saude.parte-0001.jsonl` (89.998.991, 72.537); `medicamentos/produto_fda_ndc.parte-0001.jsonl` (89.999.221, 79.401). Somatório **333.906** registros declarados. Não processar pela exceção documental do PMO.

## 2. Agentes especializados e determinismo

| Agente / fronteira | Insumos imutáveis | Saídas candidatas; condição de PASS | Permissões |
| --- | --- | --- | --- |
| `P4-SOURCE-REGISTRAR` | Inventário P1, 15 manifestos de domínio Git SHA, referências normativas e fonte original | `source_id`, `source_cid` por fonte/edição, jurisdição, URI, snapshot, SHA256, license/rights/retention; zero fontes anônimas, sem associação 1:N inferida | READ_ONLY, documentos candidatos |
| `P4-RIGHTS-GUARDIAN` | 61 fontes CE04, 49 URLs, termos e licenças *efetivamente recuperados* | `rights_decision` com evidência de edição/URL/permissão/revisor; `HOLD_RIGHTS` quando ausente/ambíguo; impede redistribuição | READ_ONLY, pode vetar; não concede licenças |
| `P4-EXTRACTOR` | Job formal admitido, bytes da fonte pinada, perfil do formato, limites e hashes | Aquisição raw preservada, stream/2 passes, SHA/OID, contagem, offsets, fragmentos, idempotência, testes de memória | **NÃO EXECUTAR** novos fluxos produtivos antes WO+Kernel |
| `P4-SEMANTIC-QA` | Átomos candidatos existentes, especialmente 285 ressalvas M43, golden sets revisados | Uma decisão por finding + ancoragem, taxonomia, tradução/jurisdição, controle de falsos positivos, revisão especialista; sem autocertificação | READ_ONLY; não declara eficácia clínica |
| `P4-NORM-CROSSWALK` | Fontes normativas com acesso legítimo e versão, SOPs M01–M11, COSO/DeepSeek, RQM-001–020 | `source_cid` → cláusula → aplicabilidade → `requirement_id` → política/controle/validador/teste/evidência; `HOLD_LICENSE_OR_TEXT` se sem íntegra | READ_ONLY; não reproduz texto protegido |
| `P4-INDEPENDENT-AUDITOR` | Saídas dos demais + execuções/testes/recibos | Amostragem estratificada, testes negativos, matriz `REQUIRED×PRESENT×VALIDATED×PASS`, divergências e parecer | Segregado de executor/publicador; não promove |

O comportamento **determinístico** decorre do contrato fixo `(source_id, source_revision, sha256, tool_version, policy_version, schema_version, run_id)`, regras transparentes, parser não inferencial, ordenação estável e testes de invariantes; os agentes de análise apoiam a classificação mas **não podem transformar incerteza em PASS**. Um integrador único escreve candidatos no GitHub após pré-verificações e readback. Não conceder autorização de produção por delegação.

## 3. Microlotes em paralelo com gates explícitos

| Lote | Prioridade / dependência | Trabalho e evidência produzida | Critério verificável / denominador | Estado inicial |
| --- | --- | --- | --- | --- |
| `P4-A` | P0; paralela a P1-C/P2 | Matriz 65 CE04 ↔ 61 referências ↔ 15 domínios ↔ proveniência; CIDs por fonte e edição; preservar relações não resolvidas | 65/65 entradas classificadas em `LINKED`, `AMBIGUOUS_HOLD`, `MISSING_HOLD`; 61/61 referências preservadas; zero link arbitrário | PLAN/READ_ONLY |
| `P4-B` | P0; paralela a A | Reconciliação das 27 entradas de ZIP normativo com COSO GenAI em pacote separado, DeepSeek, SOPs e requisito M02 | 27/27 entradas identificadas por edição+SHA; COSO candidato 734 átomos sem somar duplicados; número de cláusulas legalmente verificáveis declarado | PLAN/READ_ONLY |
| `P4-C` | P0; paralela a A/B | Investigação 285 ressalvas CID-11 por código/registro/categoria e decisão | 285/285 classificadas individualmente; `RESOLVED` exige evidence link + revisão independente; unresolved continua HOLD | PLAN/READ_ONLY |
| `P4-D` | P0; paralela a A/B/C | Matriz direitos e licenças das 61 fontes, sem confundir URL única com fonte única | 61/61 com registro `APPROVED_WITH_EVIDENCE` ou `HOLD_RIGHTS`; direitos aprovados só mediante fonte independente; 49 URLs auditadas separadamente | PLAN/READ_ONLY |
| `P4-E1..E7` | P1; **condicionada ao Kernel** | Sete fontes grandes, uma por lote, streaming+SQLite/índice externo, two-pass e readback, testes de teto e retentativa | 7/7 quando efetivamente executadas sob WO; cada lote bytes SHA256 esperados, registros, duplicados, contagem de erros, idempotência, peak-RSS; sem limite de escala declarado sem teste | BLOCKED_KERNEL |
| `P4-F` | P0 documental / P1 operacional | Evoluir schema mestre com 15 campos explicitamente ausentes no M11 e validar obrigatoriedade por perfil; cadeia normativa | 15/15 campos mapeados a caminhos de schema ou nova versão; cláusulas aplicáveis `N/N`; se N desconhecido => UNKNOWN, não 100% | SCHEMA_CANDIDATE |
| `P4-G` | Após E1..E7 e auditoria | Recalcular status estrutural CE04, sem absorver M24; revisar direitos, clínica, auditoria e publicação separadamente | Alvo estrutural máximo sem M24: 60/65 = 92,31%; 5/65 continuam HOLD. Indicador legal/clínico separado | BLOCKED_DEPENDENCIES |
| `P4-M24` | Condição própria | Cinco arquivos M24, inventário de bloqueio e ambiente, sem ingestão/atomização | 5/5 preservados em HOLD ou liberados apenas por política, validador, tarefa, WO e Kernel específicos | HOLD_M24 |

Cada lote antes de mutação: **FIND formal → política aplicável (ou change) → validador → tarefa → WO → admissão verificável do Kernel → execução isolada → testes → auditoria independente → publicação autorizada com readback**. Exceção existente só permite documentação PMO controlada, não atomização operacional. Retestar M43 sob limites de memória antes de arquivos de 60–90 MB; proteger M24 com whitelist/deny tests; testar corrupção, linhas fragmentadas, SHA/OID falso, 429/5xx, source revision drift e duplicação.

## 4. Normas e referenciais: trilha documental por fonte

**Não afirmar 100% de aderência ISO** sem a íntegra da edição aplicável e a matriz cláusula→evidência. Referenciais candidatos a validar em sites oficiais, distinguindo obrigação jurídica no domínio (COFEN/ANVISA/LGPD) de boas práticas voluntárias e normas sob licença:

- **Registros, governança documental e qualidade:** ISO 15489-1, ISO 30301, ISO 9001, ISO 19011 (edição e vigência a conferir, incluindo menções históricas a versões 2026); proveniência W3C PROV; NIST AI RMF.
- **IA, segurança e risco:** ISO/IEC 42001, ISO/IEC 27001, ISO/IEC 23894 (versões vigentes a confirmar), COSO ICIF, COSO ERM, material COSO GenAI, IIA GIAS, COBIT (usar referência licenciada), OPA/Rego para política verificável.
- **Clínica e informação em saúde:** fontes oficiais aplicáveis COFEN, ANVISA, OMS/WHO, nomenclaturas CID-10/CID-11, normas de dados de saúde conforme perfil; não presumir que todos os referenciais se aplicam a cada arquivo. LGPD/segurança para dados pessoais e audit trail.

Campos mínimos da matriz normativa por átomo: `source_id`, `source_cid`, `edition`, `jurisdiction`, `official_uri`, `source_sha256`, `licensed_text_access`, `clause_locator`, `applicability_decision`, `obligation_level`, `requirement_id`, `risk_id`, `control_id`, `policy_id`, `validator_id`, `task_id`, `wo_id`, `kernel_receipt`, `evidence_sha256`, `test_result`, `auditor`, `rights_decision`, `status` e `cutoff`. Separar sempre cobertura **documental** de eficácia **operacional** e aprovação **clínica**.

## 5. Critérios e testes que impedem percentuais enganadores

1. **Estrutural**: `53/65` atual; só cresce com run+artefato+readback e testes reais. Não absorver M24 como concluído. Referência de progresso máximo pós 7 grandes `60/65`, mantendo gate HOLD para 5 restantes.
2. **Semântico**: `classified_semantic_findings / 285`; `resolved_and_independently_accepted / 285` distinto; nenhum agregado deve declarar 285 corrigidos apenas por classificação.
3. **Direitos**: `rights_evidence_verified / 61`, com `rights_unknown` contado; sem prova, `HOLD_RIGHTS`; URL repetida não altera denominador de objetos.
4. **Clínico**: `clinically_signed_off / 65`, começando de zero **comprovado neste corpus M43**, sem inferir ausência externa; não confundir QA estrutural com aprovação.
5. **Normativo**: `clauses_with_authorized_text_and_applicability_decision / applicable_clauses`; enquanto total desconhecido, percentual `null`, não `0%` nem `100%`.
6. **Linhagem/integração**: 65/65 itens com fonte ou HOLD explícito; uma linha sem link não pode ser autoassociada por domínio; cada saída exige SHA original/pinado + algoritmo/tool version + recibo.
7. **Testes negativos mínimos**: fonte revogada, licença ausente, CIDs trocados, edição incompatível, campo obrigatório omitido, SHA divergente, duas versões conflitantes, WO não admitida, Kernel inacessível, arquivo M24 indevidamente na whitelist, agente executor igual a auditor, divulgação de segredo/PHI, tentativa de publicação à main. Esperado = deny/HOLD; PASS falso equivale a bloqueio do lote.

## 6. FINDs a conciliar sem duplicar

- M11-F01 prioridade normativos/conteúdo (não trocar pela conveniência de CID); M11-F02 schema mestre incompleto; M11-F03/M11-F07 pacotes normativos fragmentados; M11-F04 ferramentas/APIs e prompts sem registro integral; M11-F05 multiformato; M11-F06 Kernel não comprovado.
- M26-F02 direitos não explícitos nos objetos fonte; M26-F03 61 registros/49 URLs não representam independência.
- M43-F01 285 ressalvas; M43-F03 escala O(1) não demonstrada; M43-F04 risco de incorporar M24 por reutilização de executor.
- M24 segue `HOLD_ENVIRONMENT`; emitir nova FIND apenas para causa nova, não duplicar identificadores históricos.

## 7. Interdependências e encaminhamento ao PMO central

- **P1/P2** entregam árvores Git e universos de SHA que fixam a população P4-A/B e impedem contagem de versões como novas fontes.
- **P3** entrega contratos `policy/schema/validator/task/WO/Kernel` e registro de ferramentas/APIs, requisito antes de P4-E1..E7.
- **P4-A/B/C/D/F** podem avançar já, read-only, de modo paralelo e versionados como candidatos no PMO mediante publicador central e auditor separado.
- **P5** recebe matriz de lacunas, 285 decisões de QA, direitos 61/61, testes adversariais e parecer independente; nenhuma promoção sem o usuário.

**Próxima microtarefa recomendada:** P4-A e P4-D em paralelo, seguido de P4-B/C/F com executores especializados. `P4-E1..E7` apenas preparar scripts e contratos até admissão formal. Nenhum arquivo de produção é alterado por este plano.
