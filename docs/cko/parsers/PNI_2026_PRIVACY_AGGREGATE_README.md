# PNI 2026 — parser técnico com proteção de privacidade

**Estado:** `HOLD_SOURCE` / `HOLD_LGPD` / `HOLD_RIGHTS` / `HOLD_HUMAN`. Nenhuma publicação ou validação clínica.

## Fontes oficiais (consultadas em 14/11/2026)

- Portal MS / DPNI: https://dadosabertos.saude.gov.br/dataset/doses-aplicadas-pelo-programa-de-nacional-de-imunizacoes-pni-2026
- Dicionário oficial 60 variáveis: https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/dbbni/Dicionario_tb_ria_rotina.pdf
- Exemplo de recurso oficial mensal de outubro/2026: https://dadosabertos.saude.gov.br/dataset/doses-aplicadas-pelo-programa-de-nacional-de-imunizacoes-pni-2026/resource/c961ce88-7627-4cff-a1ef-82c98c4cb2e9
- O portal MS informa atualização semanal do conjunto e CSV por ano e mês; os recursos podem mudar depois da captura.

## Escopo do parser e contrato

`packages/cli/parsers/pni.py@1.0.0` / `contracts/fontes/pni.json` / `KERNEL-POLICY-012@1.1.0`.

A entrada é **somente local**: snapshot CSV ou ZIP com um membro CSV, versionado e identificado por `source_id`, `document_id`, `snapshot_month` (YYYY-MM), `expected_sha256`, codificação e delimitador explícitos. O ZIP não pode possuir caminhos relativos, membros múltiplos, symlinks nem razão de expansão perigosa. O contrato para esse subconjunto exige os **60 nomes de colunas** do dicionário do MS, não uma aproximação de outros datasets SI-PNI/Covid-19.

As colunas podem incluir `co_documento`, `co_paciente`, residência, etnia, estabelecimento, lote, datas de vacinação, idade e outras variáveis potencialmente sensíveis ou reidentificáveis. **Não usar o rótulo “dados anonimizados” do portal como prova de risco zero.** O código verifica duplicidade do identificador RNDS `co_documento` em memória para evitar contagem repetida, mas nunca o grava nem o publica.

A saída tem somente **contagem agregada de registros de vacinação**, por mês, código de vacina e UF do estabelecimento, com supressão de grupos de menos de 10 registros. Não devolve nenhuma linha individual, pseudônimo, local de residência, município, CNES, lote, idade, sexo, raça/cor, datas diárias ou nome de vacina. Grupos suprimidos não deixam contagens ou chaves de dimensão na saída. O agrupamento não comprova 10 pessoas distintas nem anonimização formal, e múltiplas publicações podem introduzir ataque de diferença.

Todos os registros agregados têm `status=HOLD_HUMAN`, `publication_allowed=false`, `clinical_approved=false`, `release_allowed=false`, `data_privacy_release_reviewed=false`, `source_origin_verified=false` e `rights_verified=false`.

## Limitações e obrigações

1. O parser é **um subconjunto técnico limitado**, com teto de snapshot de 80 MB, descompressão de 100 MB e 250 mil registros. Muitos arquivos oficiais podem exceder esse limite; nesse caso rejeitar, não truncar ou inferir cobertura completa.
2. Testes com fixtures inteiramente sintéticas não comprovam compatibilidade com arquivos oficiais, integridade da publicação, direitos de uso e riscos residuais de reidentificação. Requer amostra oficial pinada, hashes e registro de fonte/versão.
3. Validar com DPO/responsável habilitado a finalidade, minimização, legítima base legal, retenção, redistribuição, difusão de agregados e ataques de ligação/diferença. Nenhuma exportação pública deve ocorrer antes disso.
4. `schema_validator` permanece em `HOLD` até validação real contra schema oficial e testes independentes. Política exige SHA, WO, revisão humana e direitos.
5. Não usar contagens para inferir cobertura vacinal, esquema de doses, efetividade, qualidade da assistência nem adequação terapêutica sem denominadores, método epidemiológico e homologação profissional.

**Testes:** `tests/test_pni_privacy_aggregate_parser.py`, `tests/test_pni_policy_failclosed.py`. **Dados reais de pacientes não integram o repositório.**
