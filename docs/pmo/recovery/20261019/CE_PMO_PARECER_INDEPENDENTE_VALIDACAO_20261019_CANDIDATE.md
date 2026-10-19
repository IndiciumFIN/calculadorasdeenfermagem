# CE PMO — Parecer independente de consistência (candidato)

Data de referência: 2026-10-19. Fronteira de autoridade: análise read-only, sem publicação ou certificação; auditor separado do publicador.

## Verificações efetuadas

- `python3 -B CE_PMO_VALIDADOR_INDEPENDENTE_20261019.py`: **17 PASS estruturais / 4 HOLD probatórios**, nenhum BLOCK lógico na versão local inspecionada.
- `python3 -B CE_PMO_VALIDADOR_INDEPENDENTE_20261019.py --rescan`: **17 PASS / 5 HOLD**, pois o universo recursivo mudou desde o snapshot.
- Resumo documentado: 768 arquivos, 40.897.025 bytes, 720 SHA256 únicos, 23 grupos de duplicatas exatas, 13 ZIPs com 1.956 arquivos declarados em diretórios centrais. O registro mestre associa `POP-LOCAL-RECURSIVE-REGULAR=768` ao mesmo resumo.
- Recontagem read-only durante a execução paralela: 771 arquivos, 40.920.694 bytes, 723 hashes únicos, 23 grupos de duplicatas. É **drift de snapshot**, não prova de perda/adulteração. Novos artefatos no mesmo workspace alteram o universo; exigir cutoff em nível de segundo/scan-id e manifesto imutável por microlote.
- Registro mantém `pmo_trusted=false`, `project_execution_allowed=false`, 8 gates PMO em HOLD; 5 itens M24 em HOLD; nenhuma contagem aprovada falsamente.

## Holds de evidência

1. **VAL-GAP-001:** o registro mestre incorpora comprovantes antigos de publicação de si próprio, e não há recibo independente de sua versão corrente. O readback externo do publicador não pode ser substituído por autocertificação no JSON.
2. **VAL-GAP-002:** resumo agregado não traz `scan_id`, instante preciso do cutoff nem referência verificável ao detalhamento local integral. Contagem é reprodutível em princípio, mas não congelada.
3. **VAL-GAP-003:** leitura do diretório central ZIP não valida conteúdo completo, CRC de cada membro, risco de zip-bomb, nem normalização de caminho inseguro. Não promover integridade de ZIP a PASS.
4. **VAL-GAP-004:** inventário local não comprova reconciliação externa GitHub/biblioteca/Supabase e não deve declarar universo integral fechado.
5. **VAL-RESCAN-001:** houve mudança real do inventário durante a rodada concorrente. Exige reconciliação incremental, nunca ajuste retroativo silencioso do snapshot antigo.

## Decisão independente

**ALLOW_DOCUMENTARY_CANDIDATE_ONLY / HOLD_RELEASE.** Permitido documentar e consolidar incrementalmente os resultados na branch documental autorizada, com commits e readback independentes. Proibido homologar cobertura integral, declarar gates PASS, promover main, apagar versões ou executar mutações produtivas pela força dessas 17 verificações estruturais. As 17 verificações medem consistência interna, não suficiência de evidência externa.

Próxima validação deve executar testes negativos com dados sintetizados (duplicação de IDs, corrupção de hashes, inconsistência de pop/summary, falsa aprovação, conflito de escopo e ZIP malicioso) sem modificar arquivos reais.
