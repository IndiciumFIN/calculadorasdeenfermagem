# Reutilização controlada do Supabase acessível — v0.1.1

## Decisão
Usar **`simulados-para-enfermagem`** (`bsawvgyideporzailnys`) **somente como ambiente temporário de desenvolvimento/validação**. Não alterar dados de simulados; manter todos os artefatos em schema privado `ce_tools_stage`. Isso **não** transforma o banco de simulados em Master Data canônico e não cria um segundo site.

## Condição real de acesso
Em 15/11/2026, a ferramenta de acesso ao Supabase retornou `link_id must identify an eligible linked account` ao tentar listar projetos e tabelas. Portanto **nada foi aplicado**. A existência do projeto foi observada em leitura anterior, mas permissão de escrita neste turno NÃO foi confirmada.

## Contratos
- `ce_tools_stage_schema_candidate.sql`: seis tabelas de registro, concessão Kernel, releases, revogações, staff e auditoria; RLS habilitado em todas; bloqueio por default sem concessão de uso a `anon` e `authenticated`; trigger de auditoria e proteção de identidade. **Não disponível via Data API.**
- `ce_tools_stage_seed_candidate.sql`: 24 registros de demandas da pesquisa, exclusivamente `candidate`, sem `published`.
- A aplicação Next.js atual usa `.from(...)` no schema `public`. **Não é compatível com este staging privado** sem adaptador de servidor revisado, autenticação e deploy autorizados. Não trocar variáveis de ambiente da aplicação atual.
- As funções dependem de `pgcrypto` com `extensions.digest(...)`; confirmar existência no alvo antes de aplicar. NÃO instalar extensões ou alterar o search_path do projeto como efeito colateral.

## Gates antes de qualquer DDL/DML
1. Conector precisa retornar acesso válido e leitura de schemas, RLS e migrações.
2. Identificar tabelas de simulados e confirmar ausência de `ce_tools_stage` e conflitos.
3. Kernel deve aprovar Work Order para schema isolado. Registros `grants/releases` não podem ser inseridos diretamente sem validação de evidências.
4. Fazer backup/diff e avaliar advisors de segurança e impacto de dependências.
5. Executar staging e confirmar: seis tabelas, RLS=true, nenhum `USAGE` de schema para anon/authenticated, zero releases, 24 drafts candidatos, nenhum objeto tocado fora do schema (exceto dependências existentes `auth.users`/`extensions.digest`).
6. Aprovar adaptador server-side separadamente. Não expor schema na Data API, não criar política permissiva.

## Situação
Apenas **preparação documental e técnica**. Não há alteração no Supabase, GitHub main, assinatura, produção, publicação de ferramenta ou dados de pacientes.
