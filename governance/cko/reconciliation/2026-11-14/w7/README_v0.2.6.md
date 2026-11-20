# CKO W7 v0.2.6 — correção do gate de execução do verificador

**CORREÇÃO DE SEGURANÇA / 10 TESTES LOCAIS PASS / HOLD_PRIMARY / NO_GO**

A v0.2.5 já distinguia dossiê secundário de publicação oficial no JSON, mas retornava código CLI 0 quando o hash do dossiê coincidia. Esse detalhe poderia permitir falso positivo numa integração que olhasse somente o código de saída.

A v0.2.6 corrige o contrato da CLI: `DERIVED_DOSSIER` e `OTHER_REFERENCE` retornam **exit 2**, mesmo com hash correto; um `OFFICIAL_PRIMARY_CANDIDATE` com bytes correspondentes pode retornar **exit 0 apenas para o teste de integridade binária**, nunca para homologação legal, rights ou publicação clínica. Qualquer hash/tamanho incompatível, arquivo ausente ou assinatura não-PDF mantém exit 2.

Foram executados **10 testes locais** (8 de v0.2.5 + 2 testes de execução real do comando), e a execução com o PDF do dossiê 736/2024 retornou o HOLD esperado. Código e testes possuem blobs Git exatos conferíveis.

A fonte primária de COFEN 736/2024 ainda não foi recuperada. Os resultados históricos da v0.2.5 permanecem no Git e no respectivo recibo. Sem merge, deploy ou escrita Supabase.
