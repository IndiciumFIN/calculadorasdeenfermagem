# CKO W7 v0.2.3 — fontes oficiais e direitos W5/W6

**Estado: METADATA_AND_LOCATOR_REVIEWED / HOLD_FRAGMENT_SHA / HOLD_CURRENTNESS / HOLD_RIGHTS / HOLD_CLINICAL / NO_GO**

Nesta versão foram acrescentadas notas de auditoria para **8 átomos normativos W5** e **6 fontes W6**, com ligação às fontes oficiais. Sete dos oito localizadores W5 aparecem na cópia PDF da RDC 15/2012 no repositório do Ministério da Saúde. O oitavo aponta a notícia informativa da Anvisa, cuja página exibiu data 2022 em rota com 2016 e não basta como prova jurídica específica.

As seis fontes da W6 foram conferidas por identificador/documentação: 3 IDs exatos na tabela Supabase `cko_evidence.sources`, todos ainda `PENDING_BOARD_REVIEW`. O protocolo de cirurgia segura da Anvisa traz informação de licença CC BY-NC-ND 4.0; a OMS fornece manual 2009 de caráter orientativo, sem verificação de permissão de adaptação.

Nenhum download binário normativo ou fragmento primário foi reivindicado como recuperado. Todos os 14 objetos permanecem SEM hash de fragmento aprovado e SEM liberação editorial/clínica.

## Entregas desta versão
- `audit/W5_NORMATIVE_LOCATOR_REVIEW_v0.2.3.jsonl` (8 registros)
- `audit/W6_PRIMARY_SOURCES_CURRENT_REVIEW_v0.2.3.jsonl` (6 registros)
- `audit/W6_SUPABASE_EXACT_ID_CROSSWALK_v0.2.3.jsonl` (6 registros)
- `audit/PRIMARY_SOURCE_DISCOVERY_NOTES_v0.2.3.md`
- `audit/RIGHTS_NOTES_v0.2.3.md`
- `audit/FINDING_STATUS_DELTA_v0.2.3.json`
- `audit/WORK_ORDER_DELTA_v0.2.3.json`
- `audit/QA_W5_W6_REVIEW_v0.2.3.json`
- `README_v0.2.3.md`

As bases W7 v0.2.0–0.2.2 foram mantidas intactas. **Nenhum merge na main, deploy, SQL de escrita, ou modificação das branches de origem**.
