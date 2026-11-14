# SIES/MS — dados de distribuição de insumos, candidato técnico

**Fonte oficial:** https://dadosabertos.saude.gov.br/dataset/sies  
**Recurso de distribuição:** https://dadosabertos.saude.gov.br/dataset/sies/resource/d827aab8-6240-47ff-9e03-cc762c59cb38  
**Dicionário de dados:** https://dadosabertos.saude.gov.br/dataset/sies/resource/98fa5a58-b2ce-49a2-920f-fb34dcbd8a82

O dicionário identifica os campos `TX_SIGLA`, `IBGE`, `TX_INSUMO`, `ANO`, `MES`, `QTDE`, `ORIGEM`, `TX_AREA`. O portal disponibiliza CSV em ZIP; a versão do snapshot, direitos e conteúdo de cada arquivo devem ser comprovados por manifesto.

**Parser candidato:** `packages/cli/parsers/sies.py` / `KERNEL-POLICY-016@1.1.0`, somente ingestão local. Aceita um CSV de um subconjunto explicitamente validado ou um ZIP com membros CSV seguros. O caller informa `source_id`, `document_id`, data `snapshot_date`, SHA-256 do snapshot e delimitador. O ZIP é verificado contra path traversal, symlinks, arquivos não CSV, criptografia, duplicação de nomes, excesso de membros e decompression bomb.

Para cada registro, verifica coluna, ano, mês, município, quantidade como texto e campos de tipo/área sem copiá-los integralmente. Lotes inválidos são rejeitados. Duplicatas preservam `source_occurrence_index` para não apagar evidência. A saída é de metadados candidatos; número/estado administrativo não equivale a dose aplicada, disponibilidade em estoque nem recomendação clínica.

**Restrições:** Este protótipo não autentica a origem do ZIP/CSV e não comprova que o esquema adotado cobre todos os releases reais; exige teste contra snapshot oficial pinado e revisão de licença. Pode bloquear linhas não conformes sem alterar a fonte. Não acessa rede, não publica dados nem faz inferência terapêutica. Cada registro mantém `HOLD_HUMAN`, `clinical_approved=false`, `publication_allowed=false`, `release_allowed=false`.

A política exige SHA, WO, revisão habilitada e direitos por operação. O `schema_validator` referenciado ainda não está homologado; nenhuma aprovação clínica ou editorial é inferida de teste sintético.

**Testes:** `tests/test_sies_parser.py`, `tests/test_sies_policy_failclosed.py`.
