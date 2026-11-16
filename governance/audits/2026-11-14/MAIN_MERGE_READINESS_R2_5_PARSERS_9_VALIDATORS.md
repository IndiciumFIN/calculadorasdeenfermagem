# CKO / NCOS — MAIN MERGE READINESS R2 — 2026-11-14

**Estado técnico:** `MAIN_MERGE_HOLD`. **Publicação clínica/editorial:** `NO_GO`.  
**Branch:** `integration/cko-parsers-catalog-20261114` — [PR #61](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/61) empilhada sobre [PR #60](https://github.com/IndiciumFIN/calculadorasdeenfermagem/pull/60).  
**Main em auditoria:** `e0f62491b104f4a97c6025a6393cabc2e7ada30e`.

## Nova execução — PNI 2026 e proteção de dados

**Fonte:** [Ministério da Saúde / DPNI — Doses aplicadas PNI 2026](https://dadosabertos.saude.gov.br/dataset/doses-aplicadas-pelo-programa-de-nacional-de-imunizacoes-pni-2026).  
**Dicionário normativo de 60 colunas:** https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/dbbni/Dicionario_tb_ria_rotina.pdf  
**Recurso oficial de outubro de 2026:** https://dadosabertos.saude.gov.br/dataset/doses-aplicadas-pelo-programa-de-nacional-de-imunizacoes-pni-2026/resource/c961ce88-7627-4cff-a1ef-82c98c4cb2e9

Arquivos efetivamente versionados:
- `packages/cli/parsers/pni.py`: CSV/ZIP local pinado por SHA-256; 60 colunas exatas; código vacinal e mês explícitos; sem exportação de `co_documento` ou `co_paciente`; rejeição de documentos RNDS repetidos; somente agregações por UF do estabelecimento, mês e código vacinal; limiar mínimo de 10 registros por célula; supressão total de células pequenas. Nenhum cálculo de cobertura nem alegação de anonimização formal.
- `contracts/policies/KERNEL-POLICY-012.json@1.1.0`: revisão LGPD e risco de reidentificação, privacidade, WO, direitos e revisão humana obrigatórios.
- `tests/test_pni_privacy_aggregate_parser.py` e `tests/test_pni_policy_failclosed.py`: dados sintéticos, ZIP path traversal, duplicate ID, mau CSV, SHA, supressão de células, encoding CP1252 e autorização falsa.
- `docs/cko/parsers/PNI_2026_PRIVACY_AGGREGATE_README.md`: proveniência, limites de tamanho, restrição de redistribuição e riscos de agregação.

## Progresso técnico e gates

| Dimensão | Evidência no HEAD da candidata | Libera a main? |
|---|---|---|
| Fonte–política | 20/20 contratos reconciliados, AST estrutural | Não, isoladamente |
| Parser candidates | 11/16 (incluindo PNI) | Não, faltam 5 |
| Parser subset test | Suite sintética/adversarial do candidato | Não prova ingestão de corpus real |
| Validadores incondicionais | 0; diretos negam entrada sem comprovação | Não, 9 ainda não implementados |
| Validadores em `HOLD` | 9, sendo 8 exigidos pelas políticas | Não |
| Revisão G6 independente | 0 revisões em PR #60/#61 na conferência anterior | Não |
| Claims M08/M09 | 46 exigindo evidência/revisor habilitado | Não |
| Proteção da main | Leitura de proteção não comprovada com conector GitHub | Não |
| Clinical/editorial release | FALSE / FALSE no gate | Não |

Último CI integrado PNI com evidência de referência: [Actions #43610388513](https://github.com/IndiciumFIN/calculadorasdeenfermagem/actions/runs/43610388513) — `combined-technical=PASS`, `strict-admission=FAIL` (5 `MISSING_PARSER`). Para atualizações subsequentes de encoding/tests, verificar o novo run ligado ao HEAD antes de declarar PASS.

**Faltam cinco parsers declarados nos contratos:** `atlas`, `cdsi`, `esavi`, `sinan`, `taco`.  
**Validações ainda sem homologação:** `catmat_validator`, `cid10_validator`, `cid11_validator`, `cvx_validator`, `human_review_validator`, `loinc_validator`, `mesh_validator`, `ncm_validator`, `schema_validator`.

### Fonte SINAN/dengue — impedimento específico de versão

O OpenDataSUS lista [Dengue 2026 em CSV ZIP](https://dadosabertos.saude.gov.br/dataset/arboviroses-dengue/resource/f71ec0f9-82eb-4177-bd6a-ff76f2dfa84d); o [dicionário Sinan Online v3 consultado](https://portalsinan.saude.gov.br/images/documentos/Agravos/Dengue/DIC_DADOS_ONLINE.pdf) foi revisado em **2015**, logo não se pode declarar compatibilidade com 2026 apenas pelos nomes antigos. Manter `HOLD_SOURCE_VERSION / HOLD_PRIVACY` até reconciliar layout, tipos, supressão de identificadores, direitos, prova de origem, hash e testes sobre amostras oficiais. Não criar parser falso para fazer contagem chegar a zero.

### Outras fontes

`atlas`: objeto oficial, edição e direito de uso não resolvidos; `cdsi`: export/versão e finalidade não reconciliados; `esavi`: esquema de vigilância/eventos adversos, proteção de dados e origem; `taco`: edição da tabela UNICAMP, direitos, formato de redistribuição. Todas permanecem em `HOLD_SOURCE`.

## Ordem de integração não dispensável

1. Resolver as cinco fontes com evidência de contrato/hash/versão/licença e os nove validadores com testes negativos **reais** — nunca `return True` ou regex sem membership.
2. Aprovar revisão de direitos e privacidade por operação e revisão independente GitHub vinculada ao HEAD; obter evidência de proteção da main.
3. Executar o gate estrito completo, com artifacts arquivados e `technical_admission_pass=true`.
4. Mesclar PR #61 na branch-base de PR #60 e retestar; mesclar PR #60 na `main` com `expected_head_sha` após todos os controles. Comprovar `main` novo SHA e CI após merge.
5. Homologação de conteúdo e deploy clínico/editorial seguem um **gate separado**: não assumidos por merge de código.

Este checkpoint substitui como visão corrente o dossiê histórico `MAIN_MERGE_READINESS_6_PARSERS_9_VALIDATORS.md`, que deve permanecer como evidência imutável da rodada anterior.
