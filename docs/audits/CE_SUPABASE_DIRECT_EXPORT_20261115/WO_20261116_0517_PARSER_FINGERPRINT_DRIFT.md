# WO CE-20261116-0517 — verificação independente de contratos/parsers (READ_ONLY)

Projeto: CE/CKO/NCOS. PR #73 HEAD observado: 91550d1673f70bc4d391d2db83389f6528f70ef0, base main e0f62491b104f4a97c6025a6393cabc2e7ada30e. Branch fonte: integration/cko-parsers-catalog-20261114.

## Evidências e fingerprints
- Manifesto `governance/migrations/2026-11-14/legacy-fonts-reconciliation.json` blob SHA `9085556302394f1e40339a392b13e6b79bc66e78` declara 20 pares equivalentes; **não** se deve interpretar essa declaração como validação independente.
- `contracts/fontes/anvisa_dev.json` existe na branch fonte com blob SHA **54372d627c73a7b9ccdb8ce9b39281fd15d22e55**. Manifesto declara **902ae7991a116db4563b99daec9722a7cb87679c**: **FAIL_FINGERPRINT**, provável evolução após a geração do manifesto; exige diff e atualização rastreável antes de reutilização.
- `contracts/fontes/anvisa_dou.json` existe com blob SHA **7ad43853784754937320425833cebfd94c24f868**, igual ao manifesto: **PASS_BLOB_MATCH**, não equivalência semântica do par.
- `contracts/fonts/anvisa_dev.json` e `contracts/fonts/anvisa_dou.json`: **NOT_FOUND** na HEAD da branch fonte; o histórico/base pode conter as versões legadas. Portanto comparação semântica direta de ambos os pares: **0/2**, HOLD_VERIFY.
- `packages/cli/parsers/anvisa_dev.py` existe com blob SHA **9b9d899cd0d0cc791032630cac87b86f76ffbf9f**; `packages/cli/adapters/dou.py` existe com blob SHA **c0cde62ae2e32d244c2257dd942f014b41e50cea**. **PASS_EXISTENCE 2/2** apenas na branch fonte; não comprova importabilidade, testes ou disponibilidade na PR #73.

## Registro incremental
| Objeto | Fingerprint observado | Estado | Delta | Próxima ação |
|---|---|---|---|---|
| manifesto 20 pares | 9085556302394f1e40339a392b13e6b79bc66e78 | HOLD_VERIFY | 1 divergência observada em 2 contratos amostrados | revalidar os 20 blobs contra HEAD e base histórica |
| anvisa_dev contrato | 54372d627c73a7b9ccdb8ce9b39281fd15d22e55 | FAIL_FINGERPRINT | difere de 902ae799... | diff semântico contra manifesto e contrato histórico |
| anvisa_dou contrato | 7ad43853784754937320425833cebfd94c24f868 | PASS_BLOB_MATCH | sem diferença de hash | recuperar legado histórico para comparar JSON |
| anvisa_dev parser | 9b9d899cd0d0cc791032630cac87b86f76ffbf9f | PASS_EXISTENCE | candidato reutilizável | testes offline e diff PR #73 |
| dou adapter | c0cde62ae2e32d244c2257dd942f014b41e50cea | PASS_EXISTENCE | candidato reutilizável | testes offline e dependências |

## Gates e testes
Consulta GitHub read-only e commit exclusivamente documental. Testes executados: **0**; CI: **NOT_RUN**; Supabase: **NOT_QUERIED** nesta rodada. Nenhuma migration, seed, DDL/DML, merge ou alteração de RLS. Não promover artefatos clínicos: **HOLD_HUMAN**. Corrigir manifesto sem substituir provas históricas; validar diferenças antes de cherry-pick. Rollback: revert deste commit documental.
