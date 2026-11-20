# CKO W7 v0.2.4 — bloqueio curricular UC08 fundamentado
**HOLD_CURRICULUM_CONFLICT / NO_GO**

Auditadas as 3 tabelas CSV originais da branch `cko/cardiologia-corpus-editorial-20261114` de `IndiciumFIN/dev-chatgpt-workspace`, com hashes de blob registrados.

**Amostra integral:** 10 UCs, 51 módulos, 295 tópicos. **300 horas declaradas**, mas apenas **270 horas** distribuídas pelos módulos. **A UC08 concentra os 30h não distribuídos**, sem módulos nem tópicos e título equivalente (sem diferença de capitalização) ao da UC09. O ledger W4 relatara sobreposição dos 8 eixos da UC08 com os da UC07.

A auditoria produziu uma tabela por UC, relatório de conflito, política de admissão fail-closed, delta de achados/WOs e QA. **9/9 verificações de detecção passaram**, mas a homologação curricular falhou deliberadamente: nenhuma alteração à fonte foi autorizada, nenhuma hora ou módulo foi inventado e nenhum conteúdo foi promovido.

Arquivos da versão em `audit/`: `CARDIOLOGIA_UC_MODULE_HOURS_v0.2.4.jsonl`, `UC08_COLLISION_EVIDENCE_v0.2.4.json`, `CURRICULUM_CANONICALIZATION_POLICY_v0.2.4.md`, `FINDING_STATUS_DELTA_v0.2.4.json`, `QA_CURRICULUM_UC08_v0.2.4.json`.

Permanece na branch W7 para revisão e integração posterior. Sem merge na main nem qualquer escrita no Supabase.
