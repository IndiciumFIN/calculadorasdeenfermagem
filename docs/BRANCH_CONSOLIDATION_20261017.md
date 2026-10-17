# Conciliação de branches e fonte canônica — 2026-10-17

**WO candidata:** CE-WO-GITHUB-CANONICAL-20261017 · **Destino:** `main` · **Estado:** `PARTIAL_VERIFIED / HOLD_HUMAN`

## Inventário por SHA fixo (GitHub, leitura de árvores recursivas sem truncamento)

| Branch | SHA de referência | Arquivos | Situação |
|---|---|---:|---|
| main | `39d4283ca7689b1028eb11d35f453908f922de9d` | 151 | Base da integração; 3 commits próprios após ancestral compartilhado |
| cursor/fix-governance-gaps-ec54 | `5f1c03d5ed2f2d4ed583431fc50adced2daba21b` | 9.363 | 101 commits exclusivos em relação à base comum |
| cursor/drive-sa-key-refactor | `fc857df8306b81915f191d3f0744f7a322047b21` | 9.366 | Inclui a branch de governança; 22 arquivos alterados nos dois lados vs main |
| cursor/wf-gdrive-sakey | `4e3d4979e3da82c9fc7ff71beaf87fba73aa8702` | 78 | Artefatos e sondagens de workflow, não promovidos |
| cursor/wf-v3 | `8056d08a35cfb7932933fa330d8c902e5a465710` | 69 | Ancestral da main |
| staging/wo-kernel-normativos-cli-20261016 | `c54d416b7f4c8a465798ccbebad9973799dd07ab` | 79 | Staging incompleto: 7 de 46 arquivos originais transferidos |

> Totais são arquivos Git (`blob`), não contagem de conteúdos únicos aprovados. A branch grande declara aproximadamente 4,67 GB no somatório de tamanho de blobs. Arquivos clínicos/normativos não foram homologados por essa comparação.

## Normalização executada **somente na branch de integração**

- 20 pares `contracts/fonts/{slug}.json` e `contracts/fontes/{slug}.json` conferidos individualmente. São estruturalmente equivalentes ao remover o campo novo `source_contract`; o contrato canônico preserva a autorreferência corrigida.
- Removidos os 20 contratos da pasta obsoleta, `contracts/fonts/DIRECTORY_OBSOLETO.json` e `test.txt` (conteúdo `hello`): **22 caminhos**.
- Preservados os 20 `contracts/fontes/{slug}.json`, as 20 `contracts/policies/KERNEL-POLICY-{NNN}.json` e todo histórico Git. Nenhum arquivo clínico, normativo, ZIP, PDF ou DB foi removido.
- Convenção em vigor: fonte = `contracts/fontes/{slug}.json`; política = `contracts/policies/KERNEL-POLICY-NNN.json`; módulo Python = `snake_case.py`. Renomeação de fonte normativo exige lineage e hash, nunca transformação cega.

## Divergências que bloqueiam um merge integral

1. A main adicionou um novo Kernel `packages/cli/kernel/` e validadores, enquanto a branch grande possui `packages/cli/kernel.py` e pipeline/contratos diferentes. Requer estratégia de compatibilidade e testes de importação.
2. Imports absolutos `from kernel...` e `from validators...` no Kernel da main não acompanham o caminho do pacote `packages.cli.*` no uso documentado `python -m packages.cli.main`. Falha candidata de execução; teste de runtime obrigatório.
3. Contratos `contracts/fontes/` apontam para parsers não presentes no inventário de 151 arquivos da main. Não substituir automaticamente por stubs.
4. Gate Agregador histórico não prova os novos gates G1–G6 nem vigência clínica. WOs do registro anterior: 98 PASS, 2 BLOQUEADO, 2 PREAUTHORIZED; estados devem ser reconfirmados antes de executar.
5. As 9.299 entradas exclusivas da branch grande, incluindo documentos normativos e arquivos brutos, exigem reconciliação por ID, SHA-256 de conteúdo, licença, proveniência e revisão clínica antes de admissão canônica.
6. Staging CLI v0.6.0 está incompleto e não é executável isoladamente segundo seu manifesto; não mesclar até recompor os 39 arquivos restantes e reexecutar testes.
7. Duas branches de experimentos de workflow não demonstram implementação de produção; manter apenas evidências, sem importar arquivos de sonda.
8. Duplicidades por Git blob SHA na branch grande (51 grupos / 129 arquivos) são **candidatas a investigação**, não a eliminação de fontes com identificadores distintos.

## Controles e regra de promoção

- Git `main` é autoridade **apenas para componentes efetivamente admitidos e validados**; dados em branches, Drive e Supabase não são automaticamente canônicos.
- Para cada admissão: WO identificada, hash fixo, teste estrutural, teste de execução, lineage, direitos e aprovação humana conforme criticidade.
- Exclusão física de originais ou de branches históricas: somente após reconciliação `REQUIRED × PRESENT × VALIDATED × PASS`, relatório de delta, retenção e autorização humana.
- Em conflito, preservar versões e abrir `HOLD_HUMAN`; nenhum script `rm -rf` ou status `Vigente` presumido.
- Revisar merge de PRs abertos #2 (governança), #3 (staging incompleto) e #4 (Drive → governança) em sequência com testes; nenhum deles por si só resolve o conflito main × Kernel.
- A branch de integração é uma proposta auditável, não homologação final. Não promover o corpus de 4,67 GB sem gates completos.
