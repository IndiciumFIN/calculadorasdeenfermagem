# CE P1 — Contrato de verificação commit → tree → blobs (v0.1.0 CANDIDATE)

**Corte:** 2026-10-19. **Objetivo:** confirmar que um JSON de commit Git obtido por SHA aponta à árvore esperada, que a resposta recursiva da árvore é completa (`truncated=false`) e que todas as entradas de blob correspondem ao manifesto pinado. Resultado `PASS_BOUNDED` apenas para consistência dos objetos fornecidos; não é prova de proveniência independente.

## Fontes e SHA pinados

- Repositório: `IndiciumFIN/calculadorasdeenfermagem`.
- Git commit principal fixado: `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.
- Tree associado: `bf5be2752ccdabada2a1dc602a71c9a15338c504`.
- API: `https://api.github.com/repos/IndiciumFIN/calculadorasdeenfermagem/git/commits/e0f62491b104f4a97c6025a6393cabc2e7ada30e`; `https://api.github.com/repos/IndiciumFIN/calculadorasdeenfermagem/git/trees/bf5be2752ccdabada2a1dc602a71c9a15338c504?recursive=1`.
- População da evidência: 210 entradas de árvore, 176 blobs, resposta não truncada. A contagem não representa o acervo completo migrado nem os 15 snapshots históricos.
- O manifesto de 176 blobs abaixo foi DERIVADO DA PRÓPRIA ÁRVORE e serve apenas para replay e teste estrutural. Não atribuir independência nem usar como denominador de completude do Drive.

## CLI e replay

```sh
python tools/ce_agents/ce_p1_pinned_tree_guard.py \
  --commit-json tests/fixtures/p1_pinned_main_commit.json \
  --tree-json tests/fixtures/p1_pinned_main_tree.json \
  --manifest tests/fixtures/p1_pinned_main_manifest.json
```

**Critérios:** identidade SHA do commit; vínculo commit/tree; identidade SHA da árvore; `truncated is False`; nomes de blob exatos; nenhum caminho duplicado; modo Git permitido; nenhum link simbólico `120000`; nenhum tipo inesperado `commit`; hash por caminho.

## Testes e FINDs

- Unit tests: 12/12 PASS, inclusive 50 hashes surpresa falsos.
- Prova de replay na árvore fixada: `PASS_BOUNDED`, 176/176.
- Teste adversarial no replay: um SHA alterado intencionalmente resulta `FAIL` `GIT_BLOB_MISMATCH:.env.example`.
- Riscos remanescentes: manifesto não independente, API response autenticada fora do CLI, nenhuma verificação criptográfica interna dos bytes de cada Git blob, população histórica Drive não demonstrada, confiança na conta GitHub, árvore isolada não prova toda a cadeia de custódia.
- Controlar como FIND de proveniência apenas após reconciliação com FINDs P1/P2 já existentes; não duplicar.

## Referências oficiais

- GitHub REST Git Trees, campo `truncated`: https://docs.github.com/en/rest/git/trees
- GitHub REST Git Commits: https://docs.github.com/en/rest/git/commits
- SLSA provenance verification: https://slsa.dev/spec/v1.2/

**Status:** read-only test candidate, sem WO produtiva, sem permissão de promoção. Exigir comparação com manifesto de origem verdadeiramente independente para avançar o gate de completude real.
