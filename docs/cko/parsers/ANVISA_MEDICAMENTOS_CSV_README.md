# Anvisa — dados abertos de medicamentos registrados, parser técnico

Status: **HOLD_SOURCE / HOLD_RIGHTS / HOLD_HUMAN / NO PUBLICATION**.

**Fonte oficial:** https://dados.anvisa.gov.br/dados/DADOS_ABERTOS_MEDICAMENTOS.csv

**Dicionário de dados da Anvisa, v1.0 (dezembro/2020):** https://dados.anvisa.gov.br/dados/Documentacao_e_Dicionario_de_Dados_Registros_Validos_Medicamento_V1.pdf

## Entrada canônica

Uma cópia imutável do arquivo oficial CSV, fornecida localmente e previamente custodiada. O parser não acessa rede. Requer `source_id`, `document_id`, `snapshot_month` (YYYY-MM) e `expected_sha256`. Aceita até 100 MB ou 500 mil registros em CSV com delimitador ponto e vírgula e codificação CP1252, usando os 11 nomes de coluna documentados (`TIPO_PRODUTO`, `NOME_PRODUTO`, `DATA_FINALIZACAO_PROCESSO`, `CATEGORIA_REGULATORIA`, `NUMERO_REGISTRO_PRODUTO`, `DATA_VENCIMENTO_REGISTRO`, `NUMERO_PROCESSO`, `CLASSE_TERAPEUTICA`, `EMPRESA_DETENTORA_REGISTRO`, `SITUACAO_REGISTRO`, `PRINCIPIO_ATIVO`).

Registros com campos descritivos nulos podem existir na base oficial; número de registro pode estar vazio. O parser mantém duplicações por produto/processo de forma ordenada com `occurrence_index` e preserva zeros à esquerda. Na saída ficam apenas número de registro/processo candidatos e hashes: não replica nomes de medicamentos, princípios ativos, indicações, classe terapêutica nem empresa.

## Restrições

- Nenhuma aprovação de produto, validade de registro, dose, eficácia, segurança ou autorização de prescrição é inferida do CSV.
- SHA-256 confere bytes, não autenticidade da origem nem a atualidade do registro.
- A documentação de 2020 informa atualização mensal; a captura usada pelo usuário precisa ser registrada individualmente.
- Política `KERNEL-POLICY-006@1.1.0` exige WO, revisão humana e direitos por operação; `schema_validator` e `ncm_validator` ainda são stubs não admitidos.
- Todos os registros ficam `HOLD_HUMAN`, sem publicação clínica/editorial, até verificar fonte, direitos, datas e homologação.
- Subconjunto técnico foi testado em fixtures sintéticas. Deve ser testado contra amostra oficialmente pinada antes de ser considerado apto para ingestão completa; nulidade de valores e codificações observadas em releases reais devem ser reconciliadas, não corrigidas por suposições.

**Arquivos:** `packages/cli/parsers/anvisa_med.py`, `tests/test_anvisa_med_parser.py`, `tests/test_anvisa_med_policy_failclosed.py`.
