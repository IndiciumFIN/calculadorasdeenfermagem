# Revisão de Políticas — Drive e Supabase (11/10/2026)

## Supabase (projeto aevqrmkdhffmursdtcmo)

Tabelas encontradas:
- `provas_enfermagem`
- `extracoes_enfermagem`
- `questoes_enfermagem`

**Aplicável**: não. Essas tabelas são de simulados/questões. Não contêm políticas de governança do corpus normativo.

## Google Drive

### Pasta Calculadoras_de_Enfermagem
- Contém FEDERAL, NORMATIVOS e planilha CORPUS & KNOWLEDGE PMO.
- Não foram encontrados arquivos de política (AGENTS.md, CE-DS-POL etc.) na busca por título.

### Pasta Audit Educa — Consolidado
- Contém documentos de arquitetura, visão geral, fluxo e auditoria (ex.: 00-VISAO-GERAL.md, 01-ARQUITETURA.md, AuditHub_Plano_Tecnico_Arquitetura_v1.md).
- Esses documentos são de outro contexto (Audit Educa) e não são políticas versionadas do Kernel.

### Pasta extracao bruta Grok Bot Danadão
- Contém subpastas de temas (atomizado, cid10, medicamentos, protocolos_enfermagem etc.).
- Não é repositório de políticas.

## O que é aplicável

Nenhuma política encontrada no Drive ou Supabase está versionada e pronta para o Kernel executar. As regras de agentes existentes (não apagar, não compartilhar, reportar ao Grok Bot) são operacionais, mas não estão codificadas como políticas no repositório Git.

## O que falta para o diretório ser determinístico

1. Políticas versionadas em `contracts/` e `packages/schemas/` (já iniciado).
2. Kernel que só executa o que as políticas permitem (já documentado).
3. Proibição explícita de agentes alterarem arquivos sem tarefa + Kernel.
4. GitHub Actions que bloqueiam merge se o design system ou schemas forem alterados sem contrato.
5. Registry obrigatório antes de qualquer artefato ser considerado válido.

## Resultado do teste de agentes

Agente de teste criado (`Teste Kernel Proibição`). As tentativas de ação proibida e permitida foram enviadas, mas não retornaram resultado textual no tempo da sessão. O teste deve ser reexecutado com observação direta dos commits no repositório.
