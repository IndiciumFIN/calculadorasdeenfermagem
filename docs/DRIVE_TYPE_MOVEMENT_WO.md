# Movimentação por tipo — WOs + Kernel

Regra aprovada: **MOVER, NÃO COPIAR**. Escopo inicial: dois arquivos soltos na raiz secundária `1c9vErI_It3XwzAcAFOnbxw9V0Mn6xfB9`.

- Diretorio único: `00_ARQUIVOS_SOLTOS_CLASSIFICADOS/05_POR_TIPO__MOVIDOS_WO`.
- `MD`: `1HtmOws6k6c-jQ6x6FwScxh4n0djK9_mz`. WO 0234.
- `CSV`: `1PYFS29kjrFQVkR7fLE_OzDT3-hHMX3lY`. WO 0235.
- O ID do arquivo no Google Drive permanece idêntico; não há cópia e não há exclusão.
- Preflight: ler original autenticado, calcular SHA256, validar WO e destino com allowlist estática.
- Transferência: adaptador autenticado `files.update` com `addParents` do destino e `removeParents` da origem **apenas após preflight PASS**.
- Readback: verificar ID, tamanho, MIME, parentId antes/depois, rebaixar conteúdo autenticado e comparar SHA256.
- Reconciliação: `python -m packages.cli.kernel mover-drive --work-order ... --phase reconcile --receipt ...` produz evidência MOVE_CONFIRMED.
- Rollback preservado em cada receipt: addParents=origem, removeParents=destino, com nova WO se for preciso reverter.
- A origem da mudança (nome, parentId, MIME, bytes, hash e WO) deve permanecer no ledger.
- Não executar binários ou scripts durante identificação/classificação. Não mover PMO, registries ativos ou arquivos com dependências não verificadas.
