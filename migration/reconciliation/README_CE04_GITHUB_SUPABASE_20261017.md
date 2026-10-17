# CE-04 — Reconciliação GitHub × Supabase (candidata, somente leitura)

**Data:** 2026-10-17  
**WO referenciada no manifesto Git:** `CE-WO-GITHUB-FULL-DIRECTORY-20261017`  
**Verificação da WO formal separada:** não localizada na árvore examinada; `HOLD_WO_FILE_AND_KERNEL_ADMISSION`  
**Status da WO:** `WO_DOCUMENTED_GIT_NOT_KERNEL_ADMITTED`  
**Fonte documental da verdade:** GitHub `IndiciumFIN/calculadorasdeenfermagem`  
**Supabase:** `Calculadoras-Smart` como fonte secundária de confronto, nunca repositório canônico.  
**Implantação, merge, exclusão e mutação de produção:** NÃO AUTORIZADOS.

## Evidência primária

- [Matriz de 65 arquivos com paths, hashes declarados, Git blob SHA-1 e classificação](CE04_GITHUB_SUPABASE_READONLY_20261017.candidate.json).
- Git source tree `fd5818f42c6a6f716996d8c9418ba87a079d0c59`; Git main tree `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.
- Snapshot de cinco branches `bad54d1d9b6d281a0a2bb8077895e2ad45571b68` — comparação recursiva independente: **18.955/18.955** Git blobs copiados por SHA e tamanho; nenhum ausente, adicional ou alterado dentro das subárvores preservadas.
- Supabase: consulta somente leitura a `calculadoras_de_enfermagem.file_integrity` / `file_delta_plan` / `source_lineage` / `reconciliation_holds` e `cko_orch.outbox_events`.

## REQUIRED × PRESENT × VALIDATED × PASS

| Controle | REQUIRED | PRESENT | VALIDATED | PASS |
|---|---:|---:|---:|---|
| Preservação dos cinco snapshots Git | 18.955 | 18.955 | SHA de Git + tamanho 18.955/18.955 | **PASS** (apenas cópia de Git) |
| Arquivos CKO/GROK em Supabase | 65 | 65 (59 diretos; 6 fracionados) | Manifestos e tamanho 65/65 | **PASS estrutural** |
| Fragmentos dos seis arquivos grandes | 14 | 14 | Partes, offsets, ordem e tamanhos 14/14 | **PASS estrutural; SHA pendente** |
| SHA-256 recalculado dos originais | 65 | 65 metadados | 3 amostras de 65 verificadas | **HOLD** |
| Conflitos de caminho com `main` atual | 22 | 22 | Preservados, não resolvidos | **HOLD** |
| Relações de proveniência Supabase | 61 | 61 | 0 verificadas | **HOLD** |
| Outbox Supabase | 303 PENDING | 303 PENDING | Sem replay | **HOLD** |
| Holds humanos preexistentes | 9 | 9 | Não homologados | **HOLD** |
| WO de migração formal separada | 1 | ID referenciado em `migration/MANIFEST.json`, arquivo da WO não localizado | Não validado | **HOLD** |
| WO admitida pelo Kernel | 1 | Identificador no manifesto | Admissão não comprovada | **HOLD** |
| Completude das duas raízes originais do Drive | A inventariar | Não avaliado neste ciclo | Leitura Drive não realizada | **HOLD** |

## Resultados e correções do próprio preflight

1. O manifesto anterior contabilizava 21 divergências de caminho; a comparação com a `main` atual identificou **22**. A divergência adicional é `.github/workflows/drive-recursive-collect.yml`. Ambas as versões foram preservadas; a discrepância é candidata a tratamento por política/Kernel e **não foi registrada manualmente como FIND autorizado**.
2. Inicialmente, seis arquivos grandes não apareceram como nomes de arquivos diretos. Uma inspeção recursiva identificou **14 fragmentos Git**, com seis manifestos de reconstrução, totalizando **449.121.750 bytes**. Eles não devem ser classificados como desaparecidos.
3. Dois registros de versões `v2` inicialmente apontavam para blobs de manifestos-base anteriores. O readback detectou a falha e o arquivo JSON candidato foi corrigido no commit `c5414bf84d1899e4891af4f522e47ae2779f597b`.
4. Três arquivos pequenos tiveram o SHA-256 recalculado a partir do conteúdo obtido do GitHub e confrontado com a referência Supabase/manifesto, com 3/3 coincidências. **Os outros 62 ainda não tiveram o hash dos bytes originais recalculado**.
5. Todos os 65 registros na tabela `file_delta_plan` estão `PLAN_ONLY` e com `raw_data_loaded=false`, `production_write_allowed=false` e `public_release_allowed=false`. Esse é um controle de segurança, não uma validação clínica nem liberação de publicação.

6. A árvore Git examinada contém referência ao ID da WO de migração, mas **não foi localizado um arquivo autônomo versionado com esse identificador**. O contrato legado `work_order.schema.json` possui escopo explícito de execução de agentes; não presumi que seja o contrato adequado para a reconciliação. Esse item permanece bloqueado até identificação/homologação da WO aplicável.

## Próximo teste obrigatório

Em executor isolado previamente autorizado, obter a árvore Git ancorada pelo SHA, executar verificador de fragmentos em modo somente leitura, comparar SHA-256 de cada parte e da remontagem final, além de verificar os 56 arquivos diretos ainda pendentes. Produzir evidências externas ao Kernel. Depois, executar reconciliação de proveniência, licenças e conflitos, submeter aos validadores da política aplicável e solicitar admissão/homologação. O Kernel **não gera evidência**, apenas verifica.

> Este relatório é um **artefato de auditoria candidato**; não afirma conclusão, emissão de FIND, admissão de WO ou autorização de promoção. Nenhum conteúdo de origem do Supabase foi copiado para o Git; apenas metadados agregados e integridade necessários ao confronto.
