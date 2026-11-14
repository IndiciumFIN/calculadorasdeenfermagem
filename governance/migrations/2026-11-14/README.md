# Migração canônica de contratos de fontes — 14/11/2026

Este commit remove as 20 cópias exatas da antiga pasta `contracts/fonts/` e seu marcador de obsolescência. A comparação campo a campo demonstrou equivalência dos 20 documentos, removendo **somente para comparação** o campo `source_contract` que existe nas versões canônicas.

- Fonte de verdade: `contracts/fontes/*.json` (20 contratos).
- Preservação: versões anteriores recuperáveis no Git pelo commit `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.
- Evidência reproduzível: `legacy-fonts-reconciliation.json` com blob SHA-1 de cada par.
- O saneamento não altera permissões, não cria parsers e **não autoriza ingestão nem publicação clínica**.
- Os 16 parsers ainda sem implementação continuam bloqueados pelo gate estrito.

Critério: qualquer nova referência a `contracts/fonts/` deve falhar no verificador de integridade.
