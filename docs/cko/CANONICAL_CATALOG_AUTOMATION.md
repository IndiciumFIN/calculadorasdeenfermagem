# Catálogo CKO e dicionário vivo — compilação automática

## Fonte de verdade e limitações

- **Primário estrutural:** `contracts/fontes/*.json` e `contracts/policies/*.json`, versionados no Git.
- **Proveniência normativa e editorial (opcional):** snapshot explícito e verificável do PMO, por exemplo `PMO_REGISTER_SNAPSHOT_M08_M09.json`, quando estiver disponível na mesma revisão de código ou fornecido por caminho conhecido.
- O catálogo **não inventa** vínculo de uma norma (`SRC-COFEN-736-2024`) com um contrato de fonte genérica (`cofen_dou`). Falta de crosswalk é registrada como `NORMATIVE_CROSSWALK_UNVERIFIED`.
- Metadados declarados (ex.: `fonte_oficial`) não são prova de vigência normativa, nem de direitos. `release_allowed` e `publication_allowed` permanecem **false** nos nós.
- Não se acessa Drive, Supabase, paciente, rede ou site; não se cria texto clínico ou editorial. Sem controle de revisão humana e direitos, **HOLD_HUMAN**.

## Pipeline automático, sem alterações silenciosas

1. Lê contratos, identifica divergências de chaves, formatos, aliases e links inversos.
2. Cria nós `SOURCE_CONTRACT`, `KERNEL_POLICY`, `SOURCE_PARSER` e `VALIDATOR`.
3. Vincula Fonte → Política → Validador e Fonte → Parser; identifica parsers ausentes, políticas enfraquecidas, validações divergentes e referências órfãs.
4. Quando um PMO verificado é fornecido, inclui Fonte normativa → Documento → Evidência → Claim → Conteúdo, com verificação bidirecional por ID e suporte para 1 evidência → N claims.
5. Deriva o dicionário de campos observados (tipos, presença, obrigatoriedade em todos os registros); não atribui definição clínica humana não documentada.
6. Gera `catalog.json`, `dictionary.md`, `relations.mmd` e `SUMMARY.md` em ordem determinística. Sempre executa testes negativos antes de materializar ou comparar.
7. GitHub Actions recalcula os quatro artefatos a cada push/PR relevante, verifica consistência e disponibiliza o pacote como artifact de diagnóstico. **Não altera automaticamente `main`, bancos de dados nem PRs de conteúdo.**

## Execução

```bash
python -m unittest discover -s tests -p 'test_cko_catalog.py' -v
python scripts/cko_catalog.py --out-dir /tmp/cko-catalog
python scripts/cko_catalog.py --out-dir /tmp/cko-catalog --check
# Só em uma revisão que contenha o snapshot:
python scripts/cko_catalog.py --pmo governance/cko/canonical-atomic/2026-11-14/PMO_REGISTER_SNAPSHOT_M08_M09.json --out-dir /tmp/cko-pmo
```

Exit 2 = inconsistências graves entre registros, vínculos órfãos ou drift ao usar `--check`. `PENDING` de parser, revisão e direitos significa que o catálogo foi produzido, **não** que o projeto está homologado.

## Contratos de relacionamento

| Origem | Relação | Destino | Controle |
|---|---|---|---|
| SOURCE_CONTRACT | GOVERNED_BY | KERNEL_POLICY | Chave e inverse obrigatórias |
| SOURCE_CONTRACT | PARSED_BY_CANDIDATE | SOURCE_PARSER | Existência distingue PENDING; execução clínica não homologada |
| KERNEL_POLICY | REQUIRES_VALIDATOR | VALIDATOR | Contrato determinístico, sem aprovação por mero registro |
| NORM_SOURCE | HAS_DOCUMENT | NORM_DOCUMENT | Somente PMO auditado |
| NORM_DOCUMENT | SUPPORTS_EVIDENCE | EVIDENCE_ATOM | Documento existente |
| EVIDENCE_ATOM | SUPPORTS_CLAIM | CANDIDATE_CLAIM | Zero IDs órfãos; suportados múltiplos claims |
| CANDIDATE_CLAIM | USED_BY_CONTENT_CANDIDATE | EDITORIAL_CONTENT | Nenhum objeto público sem gate humano e de direitos |

## Critério de promoção de um parser

A existência do arquivo `parser.py` nunca é PASS clínico. Implementação funcional, teste sintético positivo/negativo, versão/DTD/schema, provenance, aprovação por operação, licença, revisão humana e relatórios de CI são necessários. Os **outros 15/16 parsers não implementados** continuam em HOLD conforme a branch. A validação de estrutura do catálogo não altera essa contagem.

## Agentes / papéis

- **Agente de Fonte:** verifica documento normativo, jurisdição, versão e direitos por operação; sem aprovação autônoma.
- **Agente de Contratos:** reconcilia registry e policy, propõe alterações versionadas e detecta drift.
- **Agente de Linhagem:** só relaciona IDs presentes em evidências; não infere fonte legal sem crosswalk.
- **Agente de QA:** executa testes negativos e compara artefatos, bloqueando inconsistências.
- **Revisores humanos:** responsáveis pelas aprovações normativas, clínicas, editoriais e de direitos.

Estes são **contratos funcionais de responsabilidades**, não agentes autônomos ativados.
