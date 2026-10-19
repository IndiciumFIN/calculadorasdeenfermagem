# CE PMO — P2-00: conferencia read-only de HEADs e PRs
**Corte:** 2026-10-19; **status:** CANDIDATE / PARTIAL_NOT_CLOSED. Fonte: GitHub branch list (15) e PR #2/#3/#4/#6, comparados ao manifesto P1-C-B (blob `98995b9391d4b51b8dad75a68ebac9d6283ba660`).

## Resultado
- 15/15 nomes de branches preservados; 0 desaparecimentos; 14 HEADs correspondem exatamente aos pinados.
- Apenas a branch documental PMO avançou: HEAD pinado `142987e59bbce7c7278fac1c26d71f8dbc1172c7`, HEAD consultado `724fc207b048d5a437abe5a6a663682b76f2c6c3`. Não misturar cutoffs.
- `main` na listagem: `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.

| PR | Estado | Base e base_sha relatado | Head e head_sha relatado |
|---|---|---|---|
| #2 | OPEN, DRAFT, não merged | main @ `8056d08a35cfb7932933fa330d8c902e5a465710` | cursor/fix-governance-gaps-ec54 @ `bb6debeef44a15964becd19990a502d7e0c0beaf` |
| #3 | OPEN, DRAFT, não merged | main @ `8056d08a35cfb7932933fa330d8c902e5a465710` | staging/wo-kernel-normativos-cli-20261016 @ `c54d416b7f4c8a465798ccbebad9973799dd07ab` |
| #4 | OPEN, não draft, não merged | cursor/fix-governance-gaps-ec54 @ `5f1c03d5ed2f2d4ed583431fc50adced2daba21b` | cursor/drive-sa-key-refactor @ `fc857df8306b81915f191d3f0744f7a322047b21` |
| #6 | OPEN, DRAFT, não merged | main @ `e0f62491b104f4a97c6025a6393cabc2e7ada30e` | migration/pilot-policies-20261017 @ `2fc555f854c64b9d44f778805fbfca7675bd3cce` |

**Divergencia sob investigacao:** base_sha de PR #2/#3 difere do HEAD atual de main; #4 tem outra base e SHA historico proprio. Nao concluir conflito, dano ou alteracao da main antes de inspecionar merge-base/ancestralidade, definicao do endpoint e cutoff. Vincular ao P2 existente, sem abrir FIND duplicado.

**P2-00 permanece parcial:** ainda faltam prova de ancestralidade e trees por PR/cutoff, testes adversariais e auditoria. 22 exclusoes sao escopo P2-01, ainda sem autorizacao de exclusao. Fila 12 com POST-001 ao final; oito gates PMO em HOLD; nenhum status mudado. Nenhuma alteracao em main, PRs, Kernel ou Supabase.
