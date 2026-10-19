# CE PMO — Guardião determinístico v0.1.0 (candidato)

**Escopo:** apenas a recuperação documental PMO e o inventário CE. Este validador **não é o Kernel**, não é admissão de WO, não autoriza atomização, publicação produtiva ou promoção da `main`.

## Política de veto

1. Operações Git permitidas: somente `create` ou `update` em `pmo/recovery-controlled-20261019` e sob `docs/pmo/recovery/20261019/`. É veto: `main`, merge, delete, force push, reset, deduplicação destrutiva, overwrites de fontes e extração direta ZIP.
2. Antes da publicação, cada arquivo precisa de SHA256 de sua origem local, readback exigido e, se update, SHA do blob-base (controle de concorrência). O guardião não executa a publicação nem pode certificar readback futuro.
3. Informações privadas como nomes/hashes completos no manifesto local não podem constar no resumo público; somente contagens agregadas. O registro local permanece separado e é candidato até rastreabilidade externa.
4. Inventário: cada arquivo regular exige caminho relativo seguro, byte count, SHA256 e `external_persistence=NOT_PROVEN_BY_LOCAL_SCAN`; caminhos duplicados são vetados. Symlinks do workspace são excluídos do coletor, nunca seguidos.
5. ZIP: rejeição de caminhos absolutos, `../`, drive Windows e entradas Unix symlink. O cheque atual usa diretório central e **não** comprova CRC, extração íntegra, volume máximo ou pertinência semântica. Essas verificações permanecem **HOLD**.
6. PMO permanece `CANDIDATE_NOT_CANONICAL`, `pmo_trusted=false`, `project_execution_allowed=false`, todas as gates `HOLD` e `POP-M24-HOLD` explícita com zero aprovações. Qualquer PASS prematuro é veto.
7. As verificações são locais e recebem entradas explicitamente; saída `PASS_PREFLIGHT_ONLY` significa apenas ausência de violações detectadas **nos domínios fornecidos**. Não declara homologação do projeto.

## Execução de referência

```
python3 -B -m unittest -v test_ce_pmo_inventory_guard_v01
python3 -B ce_pmo_inventory_guard_v01.py \
  --summary CE_PMO_INVENTARIO_RECURSIVO_RESUMO_20261019_CANDIDATE.json \
  --pmo CE_PMO_REGISTRO_MESTRE_20261019_v0.1.0_CANDIDATE.json
python3 -B ce_pmo_inventory_guard_v01.py --publication /caminho/plano-publicacao.json
```

Formato mínimo para `plano-publicacao.json`:

```json
{
  "branch": "pmo/recovery-controlled-20261019",
  "operations": [{
    "action": "create",
    "path": "docs/pmo/recovery/20261019/RELATORIO_EXEMPLO.md",
    "sha256_local": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    "readback_required": true
  }]
}
```

Para `update`, acrescente `base_blob_sha` com o SHA Git de 40 hexadecimais. Os exemplos são **sintéticos**, não recibos de publicação.

## Evidências locais

- 15 testes executados em 2026-10-19; todos passaram, abrangendo falhas de hash, caminho duplicado, falsa custódia, conteúdo privado, manipulação de M24/gates, alteração `main`, exclusão/dedup destrutiva, ausência readback/CAS e ZIP traversal.
- Preflight sobre PMO mestre + resumo agregado locais: `PASS_PREFLIGHT_ONLY`, exit 0 e `findings=[]`.
- Nenhuma gravação remota efetuada por este agente. Os controles precisam ser inseridos na trilha de publicação e reforçados por CI/ruleset para bloquear operações fora deste processo.

## FIND/limitações pendentes

- `FIND-GUARD-001`: o guardião CLI pode ser ignorado por um operador; instalar em CI/publisher com evidência de execução, sem remover a proteção da `main`.
- `FIND-GUARD-002`: CRC e descompressão completa dos ZIPs permanecem pendentes; não equiparar leitura do diretório central a integridade real.
- `FIND-GUARD-003`: agregação atual verifica campos estruturados, mas não é solução universal de prevenção de vazamentos em texto livre. Pré-publicação deve incluir triagem de dados sensíveis independente.
- `FIND-GUARD-004`: declaração de hash no plano não substitui conferir o SHA256 do arquivo indicado, tampouco readback posterior; ambos devem ser atestados por executor/auditor independentes.
