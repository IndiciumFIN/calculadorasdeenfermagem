# CKO/NCOS — separação entre Produção Editorial e Governança Técnica

**Status:** ACORDO_OPERACIONAL_CANDIDATO / NÃO É APROVAÇÃO DE PUBLICAÇÃO
**Data:** 14/11/2026
**Origem:** decisão do responsável pelo projeto de manter a criação de conteúdos em conversa distinta e continuar nesta trilha as pendências de governança, validação, Kernel e integração.

## Frente C — Conteúdo, taxonomia e reuso (outra conversa)

**Entregar:** recuperação real de M08/M09, conteúdos mestres, bibliotecas educativas, aulas, artigos, flashcards, quizzes, casos, checklists, planos de currículo e recursos por especialidade.

**Fontes a consultar:**
- CE privado PR #39, branch `feat/cko-m08-m09-corpus-atomic-20261114`; manifestos, dois ZIPs e snapshot PMO dos 46 claims/43 evidências.
- `IndiciumFIN/dev-chatgpt-workspace` PRs #66–#68, branch `cko/cardiologia-corpus-editorial-20261114`, pasta `cko/canonical-content/2026-11-14/`.
- Drive originais apenas quando o direito de acesso/uso estiver definido, sem publicar textos protegidos.

**Contrato de saída para a governança:** versão do conteúdo, `content_id`, `claim_ids`, `evidence_atom_ids`, `source_document_version_id`, `source_sha256`, contexto assistencial/especialidades, status de direitos/revisão e SHA da branch. Se uma fonte estiver incompleta, `HOLD_SOURCE` e nenhum claim clínico novo é promovido.

**Não alterar:** autorização WO, `main` do CE, produção, banco Supabase, WOs críticas, workflows de segurança ou reivindicar revisor profissional aprovado.

## Frente G — Governança, Kernel e engenharia (esta conversa)

**Entregar:** especificação e testes normativos, registro de FIND/política/validador/tarefa/WO, admissão confiável, revisão humana independente, gates G1–G6, comparações de branches e CI, dicionário/metamodelo, projeto de migração e integração quando todos os gates se cumprirem.

**Branches e PRs atuais:**
- #40: baseline CLI/Kernel, **DRAFT/HOLD**, base `main`.
- #46–#48: parsers separados, **DRAFT/HOLD**.
- #49: geração de dicionário/metamodelo, **DRAFT/HOLD**.
- #51: auditoria de branches e normativos, **DRAFT/HOLD**.
- #52: CI estrito, **DRAFT/HOLD**.
- #56: pré-gate WO/G6 e bloqueio de autoaprovação, **DRAFT/HOLD**.
- #57: auditoria autenticada de revisão GitHub e independência, **DRAFT/HOLD**.

**WOs abertas:** #41–#45, #50, #53–#55. A mera presença de PR ou CI verde não fecha WO.

**Não alterar:** conteúdo autoral final, textos originais de terceiros, documentos curriculares sem decisão institucional ou as branches de conteúdo enquanto em produção, salvo mudanças expressamente coordenadas e versionadas.

## Fronteira de integração

1. Cada frente registra SHA, escopo, diffs, relatórios de testes e artefatos derivados; não deve enviar ZIP protegido a repositório público.
2. Conteúdo fornece *candidatos* e evidências, governança decide apenas **conformidade técnica verificável**. Aprovação clínica e direitos exigem autoridades humanas independentes.
3. Conflitos de IDs/versões/fontes são **HOLD**, com relação de equivalência candidata, nunca sobrescrita silenciosa.
4. Mudanças de HEAD, source SHA, WO SHA ou licença invalidam aprovações associadas.
5. O banco Supabase e a `main` permanecem inalterados sem autorização formal e evidências de rollback.
6. O *status global* apresenta dois indicadores separados: `CONTENT_CREATED/DRAFT/REVIEWED/PUBLISHED` e `GOVERNANCE_IMPLEMENTED/TESTED/ADMITTED/RELEASE_ALLOWED`.
7. Nenhuma das duas frentes promete trabalho contínuo em segundo plano: cada conversa produz commits, relatórios e entregas durante execuções explícitas.

**Critério de conclusão compartilhado:** rastreabilidade ponta a ponta `CURRICULUM → TOPIC → SOURCE → DOCUMENT_VERSION → EVIDENCE_ATOM → CLAIM → KNOWLEDGE_ATOM → CONTENT → PUBLICATION`, sem quebrar segregação de deveres e sem promover conteúdo não homologado.
