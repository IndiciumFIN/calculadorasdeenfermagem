# P0 — Recuperação e controle de aceite (14/11/2026)

**Escopo:** integridade e custódia dos 13 arquivos fornecidos + reconciliação do trabalho existente. **Não é aprovação clínica, não é alteração de produção e não é autorização de merge.**

## Evidência concluída: P0.00

- 13/13 anexos acessíveis: 12 ZIPs e 1 Python. 608 entradas ZIP e 6 ZIPs internos (290 entradas adicionais), auditados por CRC/SHA256 sem extração para disco nem execução de scripts recebidos.
- 7/7 testes adversariais locais PASS: ZIP slip, ZIP inválido, mutação de bytes, reordenação de entradas, ZIP aninhado, proibição de executar upload e proibição de aprovação clínica por mero inventário.
- 3 pares logicamente idênticos. `6a990df176437fa46470a74e(1).zip` é subconjunto exato da versão com espaço, que contém 100 entradas adicionais. 9 unidades lógicas distintas; nenhuma exclusão de originais.
- Snapshot compacto com nomes e SHA-256 em `P0_SOURCE_INPUT_SNAPSHOT.v1.json`. Não inclui os próprios ZIPs/terceiros, dados clínicos ou credenciais.

**PASS somente para integridade dos 13 anexos. O estado P0 GLOBAL é HOLD.**

## Reutilização identificada

| Frente | Já existe | Destino |
| --- | --- | --- |
| NURSE-OS | POL-001..025, 13 fabrics, seis verticais, uma prova histórica sintética de SAE | Confrontar evidência runtime, não reescrever |
| NORM-KERNEL | `pipeline.py` v0.7.5 e 16 gates alegados, 14 políticas, registries | Conferir gates efetivos; documento técnico antigo ainda diz 15 |
| CKO intake | 12 objetos candidatos; vínculo com libraries | Validar schema, `field_binding_ids` e `clinical_claim_ids` antes de admitir |
| CKO doenças | cinco objetos e extensão disease | Manter HOLD_CLINICAL / HOLD_RIGHTS |
| Medicamentos | conversor denso → `medication.schema.json` | Reter `held_blocks`; revisar direitos por campo, IDs e sem-registro |
| Drive | CORPUS & KNOWLEDGE PMO, abas SOURCE_REGISTER, DOCUMENT_REGISTER, EVIDENCE_ATOMS, CLAIM_LEDGER, RIGHTS_REGISTER, HOLD_HUMAN e mais | Reconciliar IDs/versões por linha, não confundir presença com aprovação |
| Supabase | Calculadoras-Smart com schemas CKO e funções | Validar contratos de integração e RBAC com leitura controlada |
| GitHub | `calculadorasdeenfermagem` #39/#40/#46–#49/#51/#52/#56; aplicativo #5/#6 | Selecionar código validado, preservar todos os HOLDs |

## Gates de P0 — não iniciar P1 até todos PASS

| Gate | Critério verificável | Estado |
| --- | --- | --- |
| P0.00 | 13/13 fontes íntegras e deduplicadas, negativos executados | PASS_METADATA_ONLY |
| P0.01 | Crosswalk por identidade/hashes entre Git, Drive, Supabase e Biblioteca; sem perda | HOLD_RECONCILIATION |
| P0.02 | CI determinístico: `npm ci`, TypeScript, CLI, Kernel e G1–G6 verdadeiros | HOLD_G6_MERGE_RULES (strict CI branch #52 PASS) |
| P0.03 | IAM/RBAC, first signup sem admin, papéis e branch protection com teste E2E | HOLD_SECURITY |
| P0.04 | Build separado do migrador, schema/RLS verificados e backup+rollback testados | HOLD_RELEASE |
| P0.05 | FIND→policy→validator→task→WO→Kernel receipt→audit; aprovação humana independente por SHA | HOLD_HUMAN |
| P0.06 | Direitos editoriais, proteção de dados e análise de exposição de fontes/segredos | HOLD_RIGHTS |
| P0.07 | E2E funcional conectado a API/DB/papéis com rastros de evidência | HOLD_E2E |

### Achados de contrato que impedem aceitação cega

1. No intake, `microorganism` e `vaccine` não correspondem ao enum do `canonical_object`; conversão para `other` é apenas candidato.
2. `route.schema.json` do site é rota WEB, não via de administração medicamentosa.
3. Converter medicamentos por princípio ativo e escolher um único registro pode eliminar apresentações/registros distintos; direitos não são resolvidos pelo nome da fonte.
4. A matriz NURSE-OS de setembro é um piloto, não prova de que os 13 fabrics e seis verticais funcionem hoje em produção.

## Regra de execução

Aplicar em ordem e por PRs independentes, sem merge em lote: proteger fontes → recuperar CI e segurança → provar contrato/runtime → homologar. P1 (motores clínicos) só após P0 totalmente aceita. **Templates continuam por último.** Recibo do Kernel ou declaração editorial NÃO substitui assinatura de revisor qualificado nem teste de ambiente.

**Revisão:** candidatos sem admissão; `main`, Supabase e Drive não alterados por este relatório.

## Reconciliação cruzada demonstrada (Git ↔ Drive ↔ Supabase)

- **104/104 células de registro M08/M09 (linhas completas)** em nove abas do `CORPUS & KNOWLEDGE PMO` foram comparadas diretamente ao snapshot da PR #39, fixado no Git blob `0275f657edd5b2e4ec4cd66cb99b760fa2807019`: 46 claims, 43 evidências, seis conteúdos, demais nove linhas. Comparação por chave exata e colunas normalizadas; **0 ausências / 0 divergências** nos intervalos examinados. Evidência `P0_PMO_GIT_DRIVE_M08_M09_ROW_EQUIVALENCE.v1.json`.
- Consulta **somente leitura** à tabela `cko_evidence.claims` do Supabase `Calculadoras-Smart`: 41 claims existentes, **0/46** IDs do snapshot M08/M09 encontrados por correspondência exata. Isso prova falta de correspondência de IDs; **não** prova ausência semântica, aprovação ou segurança para importação. Evidência `P0_SUPABASE_CLAIM_ID_CROSSWALK_HOLD.v1.json`.
- A planilha PMO contém **gates próprios G0–G9**. O quadro P0.00–P0.07 é a priorização desta execução, não substitui G0–G9 ou o Kernel. No PMO consultado G0 permanece `IN_PROGRESS`; nenhum gate foi artificialmente promovido.

## Diagnóstico estático do NORM-KERNEL do anexo

- `pipeline.py` declara versão 0.7.5 e duas fixtures; a leitura das chamadas revela **16 tipos distintos de gate**, com **17 registros emitidos** por conta da reconstrução individual de dois documentos. `docs/gates-technical.md` ainda informa versão 0.7.3 e 15 gates: documentação em drift, sem conclusão de comportamento runtime.
- `pipeline.py --os CI-NORM-KERNEL` não usa formato `^NK-OS-\\d{4}$` previsto para re-registro em caso de drift; a execução pode registrar finding/bloqueio. O código também escreve evidências/ledger na cópia local. Só testar em checkout isolado com diffs e política de não escrita remota.
- Nenhuma homologação dos 16 tipos de gate foi inferida apenas da leitura do código ou de README.

## P0.02 — execução estrita recuperada, não duplicar correção

Na branch existente `fix/cko-ci-no-masked-checks-20261114` (PR privada #52, baseada em #40), o workflow `CI - Validacao Estrita (sem bypass)` passou no SHA `12d41a620eb5a62fed3d97f2edd3ced213986a7b`: Python/CLI/Kernel negativos + `npm ci` e TypeScript. O erro histórico de lockfile foi corrigido nessa branch. `main` ainda não recebeu essa mudança; G6 clínico, rules obrigatórias e merge continuam pendentes. Evidência: `P0_STRICT_CI_BRANCH52_PASS_RELEASE_HOLD.v1.json`.

## Recuperação adicional do acervo canônico na Biblioteca

Inventário da Biblioteca (arquivos reais, não apenas títulos):
- `/Calculadoras de Enfermagem/Foundation/Canonical/CKO_FOUNDATION_FINAL_v1.1.0.zip`: SHA-256 `c013dee3af1438a8a02fda500cc5c86b018ea4f8c79f17ae457d3b8fc40bf442`, 47 entradas. Relatório interno afirma fundação técnica PASS e 25/25 testes internos PASS, mas a OS segue `HOLD_HUMAN_DECISION`; OPA oficial/pySHACL completo e E5 global não comprovados.
- `/Calculadoras de Enfermagem/Reconstrucao Canonica/Baselines/CKO_RECONSTRUCTION_BASELINE_v1.7.0.zip`: SHA-256 `057d3edab2466f98199f55658e5199aef0e2bf6b1dc87cc5a26d252644dad0ce`, 1.402 entradas. Evidência interna: 88 PASS, 0 FAIL, 14 HOLD; conclusão de produção `NO_GO`. Arquitetura histórica: 41 verticais, 29 fabrics horizontais, 22 domínios e 18 subsistemas, em granularidade distinta do recorte operacional 14/10.
- `/Calculadoras de Enfermagem/Backups/Normative Traceability R66-R72/STAGING_MANIFEST.json`: manifestação de custódia `LOCAL_STAGING_ONLY`, não promovida.

Contrato de aceitação: o estado histórico `COMPLETE_FOR_V1` de estruturas ou de testes sintéticos não equivale a validação no deploy atual. Antes de recriar artefatos, reconciliar ID, versão, hash, contratos, regras e recibos. Evidência exata em `P0_FOUNDATION_LIBRARY_HISTORY_CROSSWALK_HOLD.v1.json`.

**Nota de escopo:** a enumeração das versões v1.0.0–v1.7.0 não certifica equivalência semântica entre as versões. O censo de arquivos é preliminar para custódia; a matriz P0.01 ainda requer reconciliação granular por contrato.
