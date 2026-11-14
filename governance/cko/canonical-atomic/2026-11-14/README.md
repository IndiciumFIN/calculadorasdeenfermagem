# Corpus CKO — conteúdo canônico e atômico M08/M09 (14/11/2026)

**REPOSITÓRIO PRIVADO — MATERIAL CANDIDATO / NÃO PUBLICAR.**

Esta branch agrega os **pacotes completos** do conteúdo autoral e dos índices de evidência produzidos a partir dos documentos normativos do corpus CKO.

- **M08:** 18 arquivos, 34 claims candidatos, 33 evidências únicas, três conteúdos mestres, oito questões, dez flashcards, índices de **28.001** átomos e **9.102** vínculos candidatos, sem textos integrais das fontes externas.
- **M09:** 16 arquivos, 12 claims e dez evidências adicionais, três revisões de conteúdos, três questões e quatro flashcards adicionais; acumulado **46 claims / 43 evidências distintas**.
- **Arquivo ZIP:** em `archives/`, com SHA-256 e Git blob SHA-1 no `GIT_SYNC_MANIFEST.json`. Conteúdo completo é acessível dentro dos ZIPs; não só ponteiros do Drive.
- **PMO:** registros de fontes, documentos, claims, evidências e conteúdos vinculados a `PMO-014` no Google Sheets; snapshot versionado em artefato complementar `PMO_REGISTER_SNAPSHOT_M08_M09.json` quando presente.

A rastreabilidade é **SOURCE → DOCUMENT → EVIDENCE_ATOM → CLAIM → KNOWLEDGE_ATOM → CONTENT_MASTER → RESOURCE**. `EVIDENCE_BOUND` **não** equivale a `ASSURED`; todas as saídas clínicas/editoriais seguem em HOLD.

**Fora do Git:** PDFs/HTML originais de terceiros e seus trechos integrais, SQLite bruto, credenciais, dados de pacientes e qualquer material sem permissão de distribuição. Esses ativos continuam no Drive e no corpus privado, identificados por hashes e IDs.

O GitHub Actions verifica integridade dos ZIPs, IDs e o impedimento de publicação, mas **não** homologa norma, conteúdo clínico, direitos ou segurança do SOT. `main` não deve receber os drafts antes das aprovações.

Documentação histórica: [PR #66](https://github.com/IndiciumFIN/dev-chatgpt-workspace/pull/66), [PR #67](https://github.com/IndiciumFIN/dev-chatgpt-workspace/pull/67) e [PR #68](https://github.com/IndiciumFIN/dev-chatgpt-workspace/pull/68).
