# Gate G6 — verificação independente de revisão da PR (READ_ONLY / HOLD)

**Data:** 2026-11-14. **Ato:** nova auditoria, não autorização de publicação.

## Evidência real da PR #56

- Repo privado: \`IndiciumFIN/calculadorasdeenfermagem\`.
- PR #56: \`fix/cko-wo-g6-preflight-20261114\`, base na PR #40.
- HEAD no checkpoint: \`c8760221930023faae2a4f0e730b208dcd9a5f0e\`.
- GitHub REST \`GET /repos/IndiciumFIN/calculadorasdeenfermagem/pulls/56/reviews?per_page=100\`: **0 revisões** na consulta de 14/11/2026. Um commit com texto "Reviewed-by" NÃO substitui review do GitHub.
- \`GET .../branches/main/protection\`: HTTP **403** \`Resource not accessible by integration\`. Proteção efetiva da main **não verificável por esta conexão**.
- \`GET .../rulesets\`: HTTP **403**, mensagem de restrição de funcionalidade para repositório privado/plano. Não declarar que existe required check/ruleset.
- \`main\` anterior do checkpoint: \`e0f62491b104f4a97c6025a6393cabc2e7ada30e\`; inalterada pela auditoria.

## Implementação

- \`scripts/cko_g6_github_reviews.py\` consulta GitHub REST **autenticada e somente leitura**; não aceita HTML/texto de commit como revisão; valida owner/repo, PR numérica, head SHA exato, autor e reviewers por \`user.id\`, revisão final por data e ID, SHA exato do commit revisado, sinaliza CHANGES_REQUESTED, DISMISSED, review do próprio autor, Bot, campos inválidos e uso de revisão antiga após novo commit.
- A consulta é paginada e revalida o HEAD ao final para rejeitar alteração durante a coleta (**TOCTOU**).
- \`tests/test_cko_g6_github_reviews.py\`: testes sintéticos para rejeição de revisões ausentes, fraudadas, do autor, antigas, dispensadas, com pedidos de alteração, comentário sem aprovação, paginação incompleta, erro de origem e alteração concorrente do SHA.
- \`.github/workflows/cko-g6-github-review-evidence.yml\` executa testes em push e, em PR **interna do próprio repo**, usa token apenas de leitura de PR para consultar o review real; o relatório guarda apenas metadados de contagem/controle e não credenciais.
- Mesmo quando uma revisão GitHub real e atual é confirmada, a saída \`clinical_approval=false\`, \`publication_allowed=false\`, \`release_gate_exit_code=2\`. O flag \`--diagnostic-only\` retorna exit 0 APENAS quando a inspeção técnica está completa e o relatório mantém HOLD. Nenhuma admissão ao Kernel.

## Separação de poderes e evidências para o G6 completo

A avaliação GitHub é **somente um controle parcial de autoria e versão**. Para alcançar G6 efetivo:

1. **Identidade e habilitação profissional independente:** autoridade externa comprova credencial profissional vigente, escopo de competência e segregação revisor/executor; GitHub login e ID são só identidade de conta, não validação do conselho profissional.
2. **Aprovação por afirmação:** cada \`claim_id\` registra decisão explícita, revisão da fonte normativa oficial em versão vigente, citação por artigo, trechos/hash e contexto clínico.
3. **Licença/direitos por operação:** prova de autorização de ingestão, atomização, armazenamento privado, adaptação e publicação quando aplicável; não inferir de link público.
4. **Recibo inviolável:** autorização emitida e verificada por fonte de confiança fora da PR e do próprio arquivo WO, vinculando \`pr_head_sha\`, \`wo_git_blob_sha\`, \`source_document_sha256\`, \`claim_ids\`, identificador de aprovador, escopo, emissão, validade e revogação.
5. **Proteção real de branch:** administrador confere no GitHub as rules/required checks/revisões exigidos e comprova com configuração; se o plano ou permissões não permitir enforcement, **HOLD_ADMIN_BRANCH_PROTECTION** e escolher estratégia de integração segura sem fingir proteção.
6. **Reverificação pós-mudança:** edição de fonte, evidence span, claim, WO, PR HEAD, credencial ou licença invalida os recibos afetados. Sem aprovação prévia genérica.

## Critérios técnicos do auditor de revisões

- JSON da API ou export local sem cadeia de autenticação: **não gera aprovação clínica**.
- Reviewer diferente do autor e \`commit_id == PR_HEAD_SHA\` + última revisão vigente em APPROVED → somente evidência de review de código; nunca satisfaz G6 sozinho.
- Revisão DISMISSED/CHANGES_REQUESTED ou com \`commit_id\` anterior → **HOLD**.
- PR DRAFT, fechada, alterada durante consulta ou com SHA divergente → **HOLD**.
- HTTP 403/429, ausência de token, paginação incompleta ou falta de metadados → **HOLD_SOURCE**, nunca inferir sucesso.
- Não acessar Drive ou Supabase, não escrever no banco, não criar usuários, não alterar os reviews GitHub e não realizar merge.

**Estado de saída:** \`GO_READONLY_REVIEW_DIAGNOSTIC / HOLD_G6_HUMAN / HOLD_RIGHTS / HOLD_PROFESSIONAL_CREDENTIAL / HOLD_BRANCH_PROTECTION\`.

**Relacionados:** PRs #39, #40, #49, #51, #52, #56; WOs #50, #53, #54, #55. Não mover \`main\` até conclusão dos requisitos aplicáveis.
