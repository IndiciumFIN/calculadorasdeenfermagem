# Migração integral de diretórios Git — zona de quarentena

**WO candidata:** CE-WO-GITHUB-FULL-DIRECTORY-20261017. **Estado:** MIGRATION_SNAPSHOT_STAGED_NOT_CANONICAL.

As subárvores em `migration/source_snapshots/` são cópias **exatas** das árvores Git das cinco branches não principais (incluindo os arquivos brutos, sem renomeação destrutiva), ancoradas a commits imutáveis descritos em `MANIFEST.json`. O inventário completo é representado pelos próprios objetos tree/blobs do Git; não é um dump de arquivos reescritos.

## Isolamento

- Não importar diretamente caminhos `packages/`, `contracts/`, `docs/` e `data/` dos snapshots para o código operacional sem reconciliação.
- A branch de migração é uma proposta, **não** uma publicação aprovada nem novo código de produção.
- Não apagar as branches originais, os registros do Drive, a base Supabase ou arquivos de origem até completude e validação por hash/conteúdo, licenças, RCM e aprovação humana.
- A versão correta de um documento divergente não é determinada pela ordem do commit; resolva os 21 conflitos de caminho individualmente.
- A migração de Git não implica extração, deduplicação nem validação científica do conteúdo nos ZIPs do Drive.

## Padrão futuro de admissão

- Fonte = `contracts/fontes/{slug}.json`; política = `contracts/policies/KERNEL-POLICY-NNN.json`; Python = `snake_case.py`; arquivos normativos = identificador canônico + extensão + hash/versão em manifesto, sem perder nome original na proveniência.
- `REQUIRED × PRESENT × VALIDATED × PASS` por objeto e ligação de source, policy, schema e validator.
- Para arquivos digitais originais: verificação dos bytes, SHA-256, MIME, licença e proveniência; `HOLD_HUMAN` em ambiguidades.
- Para código: tests, lint, import smoke, fixtures negativos e compatibilidade de interfaces.
- Para produção na `main`: evitar ampliar desnecessariamente o checkout em vários GB; preferir referência imutável a snapshots remotos e somente importar conteúdos validados.

## Critério de encerramento

A árvore está **integralmente copiada para a branch de staging** quando todas as cinco entradas internas referenciam as árvores listadas e a comparação recursiva comprova o número de blobs exato. A `main` só será promovida quando as verificações estritas e as revisões necessárias passarem.
