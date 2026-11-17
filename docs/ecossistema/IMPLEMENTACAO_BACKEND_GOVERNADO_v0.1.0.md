# Backend canônico governado — execução candidata v0.1.0

Data: 2026-11-15  
Destino candidato: `IndiciumFIN/calculadorasdeenfermagem` (Next.js 15, Supabase).  
**Não implantado, não homologado, não publicado em `main` e não migrado no Supabase.**

## 1. Escopo executado em código

- Contratos tipados (`ToolDraft`, `ToolRelease`, `ToolPayload`) e validação de entrada.
- Backend com APIs públicas de **leitura apenas** de publicações.
- Backend administrativo com `GET`, `POST` de candidatos, `PATCH` de rascunhos e `POST` para submissão à revisão; sem endpoint para conceder aprovação ou publicar.
- Tela pública `/ferramentas` e `/ferramentas/[slug]` para somente ferramentas publicadas.
- Executador educativo compartilhado para referência, checklist, planejador e formulário guiado. Nenhum cálculo clínico dinâmico ou armazenamento de dados de paciente.
- Painel `/admin/ferramentas` com pesquisa, nova ferramenta, formulário de configuração, edição e submissão. Login por OTP em `/admin/acesso` e retorno `/auth/callback`.
- Banco SQL **candidato** com RLS, auditoria de alterações, gatilhos de proteção, snapshot de publicação imutável, revogação com registro independente, evidência e autorização do Kernel obrigatórias.
- 24 demandas da pesquisa v1.4.0 convertidas em registros **não publicados**. Classificação: público, assinante ou institucional.
- Inventário de reconciliação: 68 capacidades do catálogo anterior + 36 oportunidades UX + 24 demandas. **Não é prova de ausência de duplicatas.**
- Sem deleção de registros; sem alteração de preços, pagamentos, planos, área antiga de assinantes ou calculadoras clínicas.

## 2. Arquitetura de ciclo de vida

`estudo com evidência -> candidato -> rascunho -> revisão -> Kernel WO + assinatura + verificação independente -> grant -> release imutável -> API pública -> projeções por canal`

`ce_tool_drafts` é o Registry de trabalho; `ce_kernel_grants` armazena a referência do parecer externo; `ce_tool_releases` guarda os snapshots autorizados, e `ce_tool_publications` projeta exclusivamente publicações públicas. A área do assinante e workspaces institucionais usarão views/endpoints separados, com direitos de acesso revisados; esta versão **não** os abre ao público.

Nenhum `status: published` é criado por seed. Roles `admin/editor/auditor` não são concedidos por autodeclaração. Serviço privilegiado do Kernel **não está implementado nesta wave**, então não há publicação possível pelos endpoints.

## 3. Como instalar e testar em branch de validação (após WO)

1. Registrar WO no Kernel, com responsáveis, SHA dos arquivos e validação de risco.
2. Aplicar manualmente no ambiente de desenvolvimento a migração candidata `supabase/candidates/20261115_ce_tools_governed_candidate.sql` depois de conferida (não há execução automática).
3. Provisionar roles de equipe por mecanismo externo autorizado. Não transformar usuário comum em admin via interface.
4. Aplicar seed candidata `supabase/candidates/20261115_ce_tools_research_seed_candidate.sql` no ambiente isolado; conferir 24 registros em estado `candidate`.
5. Configurar `NEXT_PUBLIC_SUPABASE_URL` e `NEXT_PUBLIC_SUPABASE_ANON_KEY`. Não utilizar `service_role` no navegador.
6. Executar `python scripts/verify_governed_tools.py`, `npm run type-check`, `npm run build` e testes E2E reais com Supabase local antes da aprovação.
7. Verificar em dois perfis (anon e editor): anon só vê releases; editor não pode gravar release nem grants; auditor vê registros e logs apenas conforme políticas.
8. Comparar com o site publicado e realizar auditoria de DS, acessibilidade, LGPD, desempenho, PWA e regressão do núcleo clínico.
9. Exigir verificação criptográfica externa e aprovação do Kernel para qualquer release, inclusive textos educativos. Publicação sem WO deve falhar fechada.

## 4. Pendências explícitas

- Não conectado ao Supabase real; não há prova de persistência E2E nem aprovação pelo Kernel.
- Autenticação depende do provedor de e-mail/OTP e configuração de redirect. Perfis não provisionados.
- Nenhum conteúdo clínico, jurídico ou institucional foi homologado; scaffolds de pesquisa estão em HOLD.
- Não foi executado build Next.js ou testes de browser contra backend; somente gates estáticos locais.
- Ainda faltam: testes de webhook do Kernel e assinatura, integrações institucionais, dados versionados de conteúdo, widget/extensão/PWA, telemetria, administração avançada de permissões, direitos e pacotes, workspace protegido e tratamento de dados sensíveis.
- Nenhuma das 24 capacidades é uma ferramenta clínica concluída. O código implementa a **fábrica governada e os padrões de UI**, não 24 produtos completos.

## 5. Regras do Design System

O CSS consome `--ce-primary: #1A3E74`, tokens existentes e tipografia Inter; H1 Nunito Sans conforme contrato oficial. `src/app/globals.css` e a homepage original não são alterados. A extensão do frontend não reimplementa a biblioteca estática do site.

## 6. Segurança

- Fail-closed na ausência de variáveis de Supabase.
- RLS e `security_invoker` nas consultas públicas.
- CSRF: `Origin`/`Host` obrigatório nas operações de alteração de estado.
- RLS de staff, auditoria e triggers bloqueando DELETE e alterações a releases.
- Não coletar dados de pacientes no executor educativo.
- Candidatos de risco alto ficam em revisão; o módulo não concede acesso a conteúdos não aprovados.
- Mensageria e alertas clínicos estão fora do escopo; nenhuma funcionalidade de documentação assistencial é ativada.

## 7. Interpretação dos resultados

Este pacote é materializado em código, mas permanece **CANDIDATE / HOLD para produção**. Os testes estáticos não substituem CI, validação SQL em Supabase, testes de penetração, E2E nem homologação clínica.

## 8. Retirada de publicação por segurança

`ce_tool_revocations` permite retirar imediatamente um snapshot do catálogo público por um ato privilegiado com evidência de Kernel. O histórico da release permanece imutável. A view `ce_tool_publications` exclui versões revogadas via `NOT EXISTS`; o rol público só consulta `release_id` de revogação. Esta funcionalidade ainda precisa de teste E2E de RLS (inclusive cenário de revogação).
