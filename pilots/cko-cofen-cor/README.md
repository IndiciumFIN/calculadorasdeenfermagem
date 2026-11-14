# CKO COFEN/COR — piloto técnico isolado (P0, código somente)

**Status:** CANDIDATE/HOLD. Não é um segundo motor clínico, não substitui Kernel, CKO, pipelines, ou contratos canônicos. Código extraído do piloto enviado com hardening adicional; **sem documentos originais, átomos, claims clínicos, credenciais ou conteúdo protegido** neste diretório.

O executor aqui é um candidato isolado para teste e reconciliação, **não** integra comandos operacionais do projeto automaticamente. As cinco schemas são sidecars de ingestão (incluindo `CLM-*` legado) e `claim.schema.json` de `contracts/cko-schemas/` continua a autoridade downstream; a correspondência entre ambos exige crosswalk de IDs/versões, fonte, evidência, direitos e revisão humana.

As suites em `tests/test_p0_security.py e tests/test_p0_crosswalk.py` usam somente fixtures sintéticas, nunca rede. O workflow correspondente compila e executa esses testes com `contents:read`, sem secrets, sem deploy. Não invocar `fetch`/`run` para produção sem WO e política aceita.

- `run`: interromper qualquer rc != 0, inclusive aquisição parcial
- `validate`: exige os quatro schemas candidatos e não omite claims
- `G15`: só permite metadados HTTP tipados; cabeçalhos arbitrários, cookies, ETags brutos e URLs credenciadas bloqueados
- `G6`: aprovação humana independente não está satisfeita por PASS técnico

Não publicar, migrar banco, nem mesclar este piloto diretamente à `main` como ferramenta clínica.


## Crosswalk de claims e direitos (somente leitura)

`tools/rights_claim_crosswalk.py` cruza os IDs de claims `CLM-*` com evidence atoms, documentos e direitos por operação. O `rights_id` em `CLM-*` é uma referência **ao grupo da fonte**, não uma chave de linha única em `01_rights_by_operation.csv`. A identidade mínima do registro de direitos é composta por `source_id + document_version_id + operation` (ou, para esta amostra, `rights_id + document_version_id`). O script detecta referências órfãs, direitos faltantes ou múltiplos e autoliberação. Nunca escreve claims canônicos nem aprova direitos.
