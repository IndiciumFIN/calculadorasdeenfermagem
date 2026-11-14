# CKO COFEN/COR — piloto técnico isolado (P0, código somente)

**Status:** CANDIDATE/HOLD. Não é um segundo motor clínico, não substitui Kernel, CKO, pipelines, ou contratos canônicos. Código extraído do piloto enviado com hardening adicional; **sem documentos originais, átomos, claims clínicos, credenciais ou conteúdo protegido** neste diretório.

O executor aqui é um candidato isolado para teste e reconciliação, **não** integra comandos operacionais do projeto automaticamente. As cinco schemas são sidecars de ingestão (incluindo `CLM-*` legado) e `claim.schema.json` de `contracts/cko-schemas/` continua a autoridade downstream; a correspondência entre ambos exige crosswalk de IDs/versões, fonte, evidência, direitos e revisão humana.

As suites em `tests/test_p0_security.py` usam somente fixtures sintéticas, nunca rede. O workflow correspondente compila e executa esses testes com `contents:read`, sem secrets, sem deploy. Não invocar `fetch`/`run` para produção sem WO e política aceita.

- `run`: interromper qualquer rc != 0, inclusive aquisição parcial
- `validate`: exige os quatro schemas candidatos e não omite claims
- `G15`: só permite metadados HTTP tipados; cabeçalhos arbitrários, cookies, ETags brutos e URLs credenciadas bloqueados
- `G6`: aprovação humana independente não está satisfeita por PASS técnico

Não publicar, migrar banco, nem mesclar este piloto diretamente à `main` como ferramenta clínica.
