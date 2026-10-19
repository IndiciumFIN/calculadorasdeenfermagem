# CE P1 — Validador ZIP de integridade e completude (candidato)

**Branch:** `feat/ce-local-agent-assurance-20261019`. **Estado:** LOCAL_CANDIDATE_TESTED; não autorizado em produção. Não substitui o catálogo histórico nem o inventário P1 já encerrado.

## Objetivo e escopo

Validar, em modo read-only e sem extração, cada membro de um ZIP contra manifesto fechado `members[{path,sha256,byte_length}]`, com hash opcional do ZIP inteiro. A validação compara o conjunto declarado com membros reais e recalcula SHA-256 do conteúdo descomprimido, em leitura em blocos. Não pressupõe que o manifesto foi gerado de uma população completa nem que o conteúdo é semanticamente correto.

## Contrato / comando

```sh
python tools/ce_agents/ce_p1_zip_guard.py --archive arquivo.zip --manifest manifest.json
python -m unittest discover -s tools/ce_agents -p 'test_*.py' -v
```

Saídas: JSON com `decision`, `errors`, `holds`, `entries_declared`, `entries_observed`, `entries_scanned`; exit code 0 `PASS_BOUNDED`, 2 `FAIL`, 78 `HOLD`. Sem gravação, extração ou upload.

## Riscos / controles

| Risco | Controle testado | Residual |
|---|---|---|
| Membro omitido/extra | igualdade de conjuntos de nomes | manifesto/origem podem omitir arquivos antes da compactação |
| Membro adulterado | SHA-256 bytes descompactados e comprimento | hash no manifesto depende de proveniência confiável |
| ZIP slip / path malicioso | rejeição de `..`, barras invertidas, absoluto, `:`, NUL | ausência de extração reduz superfície; segurança de outros consumidores permanece externa |
| Arquivos duplicados | nomes e colisão sem distinção de caixa | normalização Unicode, casefold de nomes pode demandar política por plataforma |
| Descompressão excessiva | limite 10 mil membros, 2 GiB total declarado, 512 MiB por membro, razão 1000:1 | overhead CPU/tempo, metadados maliciosos e limites de executor exigem sandbox/timeout externo |
| ZIP criptografado / link | reject | senha/links legítimos requerem tratamento separado |
| ZIP aninhado | `HOLD` | recursão controlada, limites acumulados pendentes |
| Falsos PASS | teste de adulteração, ausência, arquivo extra, CRC via leitura | ground truth original e revisão semântica pendentes |

A regra de limites é conservadora e candidata; não é uma norma universal. Antes do uso em produção, calibrar com população real e fazer ensaio de desempenho/riscos.

## Testes

- 16 testes Python de fixtures sintéticas aprovados em 2026-10-19, após correção do tamanho da fixture de compressão.
- 30 mutações surpresa de bytes com semente `20261019` verificadas.
- A primeira execução teve um teste FAIL porque a fixture de 200.000 bytes não alcançava razão >1000:1. Aumentada para 2.000.000 bytes e repetida: 16/16 PASS.
- CI remota e readback por GitHub exigidos após publicação.

## Fontes oficiais

- Python `zipfile` (CRC, limites e decompression bombs): https://docs.python.org/3.11/library/zipfile.html
- OWASP File Upload Cheat Sheet (bombas de arquivo, validação): https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html
- NIST SP 800-53 SI-7 (integridade da informação): https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final

## Critério de fechamento delimitado

Código publicado em branch isolada + readback exato + CI verde + ausência de regressões e riscos residuais explícitos. **Não** significa que P1 global, os 19.119/19.136 blobs ou os ZIPs históricos estão auditados de ponta a ponta nesta onda. P1 permanece aberto para prova de população independente, ZIPs reais autorizados, Git blob map, E2E de custódia e parecer independente.
