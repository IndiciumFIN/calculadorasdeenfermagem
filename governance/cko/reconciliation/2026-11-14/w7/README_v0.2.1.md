# W7 v0.2.1 — fechamento técnico de branch e crosswalk de fontes
**CANDIDATE / HOLD_SOURCE / HOLD_RIGHTS / HOLD_CLINICAL / NO_GO**

## Entrega real
- Preservada a versão v0.2.0 (59 achados, 12 ordens de trabalho) como baseline histórico, sem sobrescrever evidências.
- A branch remota `review/cko-w7-public-evidence-20261114` contém o commit v0.2.0 `7680ed090fe68c9e58c40d20f45655ef15f11c7d`. O bloqueio **histórico** W7-001 pode ser marcado tecnicamente resolvido; a proteção geral #25580067 aparece desativada e exige governança de restauração.
- Comparadas **118/118** fontes de `sources.jsonl` do corpus Drive contra **157** registros de `cko_evidence.sources` do Supabase, somente leitura: `0` IDs iguais, **3** aliases candidatos de URI única, **1** URI ambígua com 2 registros, **114** sem correspondência por ID/URI.
- O método é conservador: normaliza somente esquema e host, remove `www`, fragmento e barra final. Não altera path nem query. O cruzamento de URI nunca homologa identidade, vigência, direitos ou conteúdo.
- A diferença de contagens não implica que 114 fontes estejam ausentes do acervo principal: os escopos dos catálogos são distintos.

## Arquivos
- `audit/SOURCE_REGISTRY_URI_CROSSWALK_v0.2.1.jsonl`: 118 registros, metadados, classificação e bloqueios explícitos.
- `audit/SOURCE_REGISTRY_URI_SUMMARY_v0.2.1.json`: totais e quatro candidatos.
- `audit/SOURCE_REGISTRY_METHOD_v0.2.1.md`: método e limites.
- `audit/FINDING_STATUS_DELTA_v0.2.1.json`: atualização aditiva de 4 achados sem reescrever o baseline.
- `audit/WORK_ORDER_STATUS_DELTA_v0.2.1.json`: atualização de 2 WOs, nova tarefa de menor privilégio.
- `audit/QA_SOURCE_RECONCILIATION_v0.2.1.json`: 9 validações de integridade.
- `README_v0.2.1.md`: esta nota de versão.

## Pendências intactas
W5 oito NormAtoms sem fragment SHA; W6 seis fontes com fragment SHA ausente; colisão curricular UC08; 17 JSONLs de PDFs não duráveis no snapshot; 9.102 relações temáticas sem aprovação semântica; direitos e revisão clínica independentes ausentes.

**Sem merge, sem deploy, sem atualização do Supabase.** Só metadados de fonte; textos completos de terceiros continuam fora do repositório público.
