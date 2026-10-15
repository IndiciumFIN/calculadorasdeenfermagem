# Remediação de Gaps — 14/10/2026

Rastreabilidade entre os achados da auditoria (GOV-001 a GOV-008), os gaps da
revisão do plano (GAP-01 a GAP-11), as correções desta mudança e os testes
que as comprovam. Os cenários T1–T10 referem-se aos testes executados na
revisão; todos os reproduzíveis viraram testes de regressão permanentes em
`tests/test_regression_gaps.py`.

## Corrigido nesta mudança

| ID | Correção | Comprovação |
|----|----------|-------------|
| GOV-002 | `|| echo` removido; workflow único `gate.yml` fail-closed; lint de workflow proíbe mascaramento, exige `permissions:` e pinagem por SHA | `gates/gate_workflow_lint.sh` (autoaplicado no agregador) |
| GOV-003 | Gate agregador executa compilação, testes de regressão, fixtures negativas, type check, segredos e auditoria de dependências | `gates/aggregate.sh` |
| GOV-004 | Átomo nasce `Não verificado`; `Vigente` exige `data_verificacao` + domínio oficial (schema v1.2.0); migration proposta remove default do banco | `test_t4_process_sem_corte_e_sem_vigencia`, `test_vigente_sem_verificacao_reprova` |
| GOV-005 | Corte de 15 linhas e truncamentos de 30/40k chars removidos | `test_t4_process_sem_corte_e_sem_vigencia` |
| GOV-006 | Omissão crítica bloqueia por padrão; `validate` lê `_auditoria` antes de descartar; corpus vazio reprova | `test_t1_*`, `test_t2_*` |
| GOV-007 | Registry exige SHA-256 válido; status em allowlist; transições por máquina de estados com histórico | `test_t3_*`, `test_registry_transicao_invalida_reprova` |
| GOV-008 | Contrato único `AtomoBlindado` v1.2.0 com `extra='forbid'`; `AtomoNormativo` é alias | `test_propriedade_desconhecida_reprova` |
| GAP-01 | `packages/cli/llm_runner.py`: porta única de execução de modelo com Work Order, PEP deny-by-default; prompts com hash em `prompts/manifest.json` | testes `test_llm_runner_*` |
| GAP-02 | Hash duplo (`sha256_original` + `sha256_transformado`); original bruto preservado em `data/sources/` com manifesto | `test_ingest_local_preserva_original_com_hash_duplo` |
| GAP-03 | `.github/CODEOWNERS` cobre `.github/`, gates, contratos, schemas, agentes e prompts; workflows com `permissions` mínimos e actions por SHA | lint de workflow + arquivo CODEOWNERS |
| GAP-05 | `model_id` pinado na allowlist do agente; temperatura 0 obrigatória; manifesto de execução registra modelo e provider | `test_llm_runner_modelo_fora_da_allowlist_reprova` |
| GAP-06 | `packages/cli/recheck.py` + workflow semanal `recheck-vigencia.yml`: vigência verificada há mais de 90 dias reprova | verificação manual documentada (exit 2 com corpus vencido) |
| GAP-07 | gitleaks pinado por versão e checksum no gate de segredos | `gates/gate_secrets.sh` |
| GAP-08 | Máscara com diff auditável por padrão nomeado, anexado à evidência | `test_ingest_local_preserva_original_com_hash_duplo` |
| GAP-09 | `agents/registry.json` com recertificação obrigatória; PEP bloqueia agente vencido | `test_llm_runner_recertificacao_expirada_reprova` |
| GAP-10 | Workflow semanal `backup.yml` com snapshot + SHA-256 e retenção de 90 dias | arquivo do workflow |
| GAP-11 | `pip-audit --strict` + `npm audit` (produção, nível high) no agregador | `gates/gate_deps_audit.sh` |
| T9 | Grupos não-capturantes em `extrair_numeros_criticos` | `test_t9_regex_preserva_numeros` |
| Fontes | Allowlist executável de domínios oficiais; fora dela, `REFERENCE_ONLY` bloqueia extração | `test_ingest_dominio_fora_da_allowlist_reprova` |
| Lockfile | `package-lock.json` versionado (corrige a falha do setup-node no CI); `tsc --noEmit` passa sem mascaramento | gate TypeScript |

## Pendente de ação manual (fora do alcance desta mudança)

| ID | Ação necessária | Responsável |
|----|-----------------|-------------|
| GOV-001 | Ativar branch protection na `main`: exigir o check **Gate Agregador / aggregate**, exigir review de code owner e proibir push direto/force-push | Admin do repositório |
| GAP-04 | Configurar secrets `SUPABASE_URL` e `SUPABASE_ANON_KEY` e acoplar `sync-check.yml` ao pipeline de deploy do site (hoje é `workflow_dispatch`, fail-closed sem secrets) | Admin + TEC |
| Migration | Revisar e aplicar `supabase/migrations/20261014000000_governance_fixes.sql` no projeto Supabase (remove default `Vigente` e restringe RLS). O arquivo está versionado, mas **não aplicado** | Admin do Supabase |
| Modelos reais | ~~Autorizar um `model_id` real~~ **Feito**: `deepseek:deepseek-chat` autorizado via gateway Supabase (ver seção abaixo). Falta apenas definir o secret `DEEPSEEK_API_KEY` nas Edge Functions do Supabase | Governança de IA |
| DeepSeek secret | **Feito em 15/10/2026**: secret configurado no Supabase (nome `DeepseekAPI`; o gateway v3 aceita `DEEPSEEK_API_KEY` e `DeepseekAPI`). Execução real de ponta a ponta verificada: WO-DEEPSEEK-EXEMPLO-001 → exit 0, manifesto com `provider_meta` e request id do DeepSeek | — |

## Decisões de política registradas nesta mudança

1. `npm audit` do gate cobre dependências de **produção** em nível high. O
   tooling de lint (`eslint-config-next`) carrega advisory sem correção
   disponível em `braces`/`micromatch`; não é código de produção. Reavaliar a
   cada atualização de dependências.
2. O provider `mock:` do llm_runner só roda com `CE_ALLOW_MOCK=1`, grava
   `promotable=false` e existe exclusivamente para testar o harness.
3. `docs/` permanece descritivo nesta fase; a conversão de regras em
   policy-as-code (plano v0.1.x) segue pendente de aprovação do plano.

## Provider real: DeepSeek via Supabase (14/10/2026)

Decisão humana registrada: instrução do mantenedor nesta data para usar a
API do DeepSeek através do Supabase. Implementação:

- **Rota única**: `deepseek:deepseek-chat` roteia exclusivamente pela Edge
  Function `cko-deepseek-gateway` do projeto Supabase (endpoint pinado em
  `config/providers.json`). O runner nunca fala direto com `api.deepseek.com`
  e nunca vê a chave do provider.
- **Segredos**: a chave `DEEPSEEK_API_KEY` vive SOMENTE como secret das Edge
  Functions no Supabase. O runner local/CI usa apenas o token do projeto via
  variável de ambiente `CE_SUPABASE_ANON_KEY` (o gateway exige JWT,
  `verify_jwt=true`). Nenhum segredo no repositório (gate de secrets PASS).
- **Determinismo**: o runner envia `temperature: 0` explícito; o PEP continua
  exigindo Work Order, prompt com hash conferido e modelo pinado na allowlist
  do agente (`agents/registry.json` v1.1.0).
- **Fail-closed verificado contra o gateway real**: com o secret ausente no
  Supabase, o gateway responde `503 deepseek_secret_missing` e o runner
  termina com exit 2 (evidência no PR). TLS obrigatório; gateway `http://`
  só em `127.0.0.1` com `CE_ALLOW_TEST_GATEWAY=1` (teste do harness).
- **Execução real verificada (15/10/2026)**: com o secret configurado, a
  WO-DEEPSEEK-EXEMPLO-001 executou de ponta a ponta (exit 0), saída em
  `data/raw_llm/` (ignorada pelo Git — candidato raw nunca entra no repo) e
  manifesto com hashes, `usage` e request id do DeepSeek. A fonte do gateway
  (v3) está espelhada em `supabase/functions/cko-deepseek-gateway/index.ts`
  para rastreabilidade sob CODEOWNERS.
- **Credencial do runner**: `CE_SUPABASE_ANON_KEY` recebe a chave anon
  (publicável) do projeto Supabase — Dashboard → Settings → API Keys. Não é
  a chave do DeepSeek e não dá acesso privilegiado ao banco (RLS), mas fica
  fora do repositório para o gate de secrets não abrir exceções a JWTs.
- **Testes**: `tests/test_deepseek_provider.py` (5 casos) cobre credencial
  ausente, secret ausente no Supabase, TLS obrigatório, modelo não pinado e
  caminho feliz com manifesto (`provider_meta`, `promotable=true`,
  `estagio=raw`).

## Retirada do acervo legado (15/10/2026)

As 7 planilhas `NORMATIVE_ATOMS_COFEN` (V1 e lotes 1 a 6) saíram do Drive
para `data/legado/`. O Supabase (schema public) não tem tabela de normativos
— só provas e questões — então não havia o que retirar de lá, e nada foi
apagado. As planilhas originais continuam no Drive.

- Comando: `python -m packages.cli.migrate_legado run`
- 104.668 candidatos `AtomoBlindado`, todos `Não verificado`. Nenhum nasce
  `Vigente`: o `link_fonte` é a planilha de origem, não o diário oficial.
- 7.679 linhas em quarentena, texto integral, sem truncar: texto curto
  (5.718), texto acima de 800 caracteres (1.044), conflito de duplicata
  (752, nenhum lado escolhido), termo `recomenda-se` rejeitado pelo contrato
  mesmo quando é o verbo da norma (165) e duplicata idêntica deduplicada (44).
- Piloto de auditoria camada 2: Art. 1º da Resolução COFEN 800/2025
  confrontado com o PDF do DOU via `WO-AUDITORIA-RES800-001`.
- Índices `DOCUMENT_REGISTER` e `RELACOES_NORMATIVAS`, e o conjunto de PDFs
  oficiais, continuam no Drive. São o próximo lote, não átomos já extraídos.
- `.gitleaks.toml` ignora só o padrão `sha256_texto=` (hash de evidência das
  planilhas). Sem isso o gate acusava 2.311 falsos positivos. Nenhuma outra
  regra foi relaxada.
