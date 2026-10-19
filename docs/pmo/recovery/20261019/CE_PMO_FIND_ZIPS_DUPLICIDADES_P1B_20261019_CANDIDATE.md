# CE PMO — Microlote P1-B: ZIPs e duplicidades

**Estado:** `ZIP_TECHNICAL_INTEGRITY_PASS / DOCUMENTARY_RECONCILIATION_IN_PROGRESS / RELEASE_HOLD`.

## Escopo e resultados observados

- Verificação de 13 contêineres ZIP locais, sem extração física nem alterações de fonte.
- 2.210 entradas declaradas (1.956 arquivos regulares); 63.658.956 bytes descomprimidos e lidos em streaming.
- 1.956 leituras de payload concluídas com verificação CRC pelo descompressor; nenhum erro observado nos 13 ZIPs deste escopo.
- Suíte `test_ce_pmo_zip_verify_v01.py`: 12 testes PASS, incluindo adulteração de CRC, path traversal, symlink, ZIP inválido e limites de tamanho.
- Novo confronto em memória do inventário recursivo: 23 grupos de hash idêntico, 71 caminhos associados, 4 grupos atravessando categorias de diretório. Esses grupos **não** são candidatos automaticamente autorizados à exclusão.

## FINDs e controles

| FIND | Risco | Resposta | Estado |
|---|---|---|---|
| PMO-FIND-P1B-001 | Diretório central ZIP legível com conteúdo corrompido. | Leitura integral em chunks; verificação CRC/size e teste de corrupção deliberada. | PASS no escopo local |
| PMO-FIND-P1B-002 | ZIP com paths perigosos ou symlinks. | Fail-closed antes da abertura dos membros; testes negativos de traversal, drive absoluto e links. | PASS nos 13 ZIPs externos |
| PMO-FIND-P1B-003 | Inferir equivalência documental somente por hash exato. | Grupos preservados por SHA, origem e categoria; sem exclusão, versionamento ou merge. | HOLD para decisão de reconciliação |
| PMO-FIND-P1B-004 | ZIP pode conter ZIP aninhado ou documento protegido. | Não extrair nem publicar payload; abrir work item para profundidade aninhada/direitos. | HOLD |
| PMO-FIND-P1B-005 | O scan local muda quando os próprios relatórios são gerados. | Baseline P1-A de 768 mantida congelada; evolução observada em P1-B não substitui o registro antigo. | HOLD até delta manifest persistente |

## Critério de interpretação

`PASS_TECHNICAL_ZIP_INTEGRITY_ONLY` atesta somente que os payloads dos ZIPs externos locais passaram por leitura/CRC sob orçamento de memória e tamanho. Não atesta autenticidade da origem, integridade anterior à migração, profundidade de ZIP aninhado, licença, semântica, aceitação clínica ou homologação do projeto.

Próxima ação: construir mapeamento de versões/aliases e matriz de duplicidade exata versus divergência documental com fontes GitHub, mantendo o detalhe sensível em manifesto privado e submetendo atos operacionais ao Kernel quando aplicável.
